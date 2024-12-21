from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
from ..database import get_db
from ..models import User, Video, Analysis
from ..services.video import save_video, extract_frames, perform_ocr
from ..services.gemini import GeminiService
from .auth import get_current_user

router = APIRouter(prefix="/api/videos", tags=["视频分析"])
gemini_service = GeminiService()

@router.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Upload and process a video file for analysis.
    Maximum file size: 500MB
    """
    try:
        # Save video and create database entry
        video = await save_video(file, current_user.id, db)

        # Start asynchronous processing
        try:
            # Extract frames
            video_path = f"/tmp/video_uploads/{video.filename}"
            frames = await extract_frames(video_path)

            # Perform OCR
            ocr_results = await perform_ocr(frames)

            # Generate PRD
            prd_content = await gemini_service.generate_prd(ocr_results)

            # Generate Business Plan
            business_plan = await gemini_service.generate_business_plan(prd_content)

            # Create analysis entry
            analysis = Analysis(
                video_id=video.id,
                prd_content=prd_content,
                business_plan=business_plan
            )
            db.add(analysis)

            # Update video status
            video.status = "completed"
            db.commit()
            db.refresh(video)
            db.refresh(analysis)

        except Exception as e:
            # Update video status on failure
            video.status = "failed"
            db.commit()
            raise HTTPException(status_code=500, detail=str(e))

        return {
            "message": "Video uploaded and processed successfully",
            "video_id": video.id,
            "status": video.status
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{video_id}/prd")
async def get_prd(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Retrieve the PRD generated from video analysis.
    """
    # Get video and verify ownership
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    if video.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this video")

    # Get analysis
    analysis = db.query(Analysis).filter(Analysis.video_id == video_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    if not analysis.prd_content:
        raise HTTPException(status_code=404, detail="PRD not generated yet")

    return {
        "video_id": video_id,
        "prd_content": analysis.prd_content
    }

@router.get("/{video_id}/business-plan")
async def get_business_plan(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Retrieve the Business Plan generated from video analysis.
    """
    # Get video and verify ownership
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    if video.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this video")

    # Get analysis
    analysis = db.query(Analysis).filter(Analysis.video_id == video_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    if not analysis.business_plan:
        raise HTTPException(status_code=404, detail="Business Plan not generated yet")

    return {
        "video_id": video_id,
        "business_plan": analysis.business_plan
    }
