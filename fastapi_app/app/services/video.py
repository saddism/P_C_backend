from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
import cv2
import numpy as np
import pytesseract
from PIL import Image
import io
import os
from typing import List
from ..models import Video
from datetime import datetime

MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB in bytes
ALLOWED_EXTENSIONS = {'.mp4', '.avi', '.mov', '.wmv'}
UPLOAD_DIR = "/tmp/video_uploads"

async def save_video(file: UploadFile, user_id: int, db: Session) -> Video:
    """
    Save uploaded video file and create database entry.
    Implements file size limit and type validation.
    """
    # Validate file size
    file_size = 0
    chunk_size = 1024 * 1024  # 1MB chunks

    # Create upload directory if it doesn't exist
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Get file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type. Allowed types: mp4, avi, mov, wmv")

    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{user_id}_{timestamp}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        with open(file_path, "wb") as buffer:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                file_size += len(chunk)
                if file_size > MAX_VIDEO_SIZE:
                    os.remove(file_path)
                    raise HTTPException(status_code=400, detail="File too large. Maximum size is 500MB")
                buffer.write(chunk)

        # Create database entry
        video = Video(
            user_id=user_id,
            filename=filename,
            status="pending"
        )
        db.add(video)
        db.commit()
        db.refresh(video)

        return video

    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

async def extract_frames(video_path: str, max_frames: int = 30) -> List[Image.Image]:
    """
    Extract frames from video for OCR processing.
    Implements frame sampling to avoid processing every frame.
    """
    try:
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames == 0:
            raise HTTPException(status_code=400, detail="Invalid video file or empty video")

        # Calculate frame sampling interval
        interval = max(1, total_frames // max_frames)
        frames = []

        for frame_idx in range(0, total_frames, interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if not ret:
                continue

            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            frames.append(pil_image)

            if len(frames) >= max_frames:
                break

        cap.release()
        return frames

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Frame extraction failed: {str(e)}")

async def perform_ocr(frames: List[Image.Image]) -> List[str]:
    """
    Perform OCR on extracted frames to identify UI elements and text.
    Implements error handling and text cleaning.
    """
    try:
        text_results = []
        for frame in frames:
            # Convert to grayscale for better OCR
            gray_frame = frame.convert('L')

            # Perform OCR
            text = pytesseract.image_to_string(gray_frame, lang='eng+chi')

            # Clean and filter text
            if text.strip():
                text_results.append(text.strip())

        return text_results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")
