from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Dict, List, Optional
import uvicorn
import os
import glob

from models import VideoListResponse, VideoListItem, ErrorResponse, VideoResponse, DocumentResponse
from routes import router as videos_router

app = FastAPI(
    title="Video Analysis API",
    description="API for video analysis and document generation",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(videos_router, tags=["videos"])

# PLACEHOLDER: Existing API endpoints and configurations

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
