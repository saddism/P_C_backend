import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from video_analysis import analyze_video, generate_prd, generate_business_plan

class VideoResponse(BaseModel):
    message: str
    prd: str
    business_plan: str

class DocumentResponse(BaseModel):
    prd: str | None = None
    business_plan: str | None = None

app = FastAPI(
    title="Video Analysis API",
    description="API for analyzing app screen recordings and generating PRD/Business Plan documents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Create required directories
os.makedirs("data/uploads", exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/videos/upload",
    response_model=VideoResponse,
    summary="Upload and analyze video",
    description="""
    Upload an app screen recording video for analysis.
    The video will be processed to:
    - Extract key frames
    - Analyze app functionality and user flow
    - Generate PRD document
    - Generate Business Plan
    Maximum file size: 500MB
    """,
    response_description="Returns generated PRD and Business Plan documents"
)
async def upload_video(file: UploadFile = File(..., description="App screen recording video file (MP4 format)")):
    try:
        # Save uploaded file
        file_path = f"data/uploads/{file.filename}"
        os.makedirs("data/uploads", exist_ok=True)

        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Analyze video
        frames = analyze_video(file_path)

        # Generate documents
        prd = generate_prd(frames)
        business_plan = generate_business_plan(frames)

        return {
            "message": "Video analyzed successfully",
            "prd": prd,
            "business_plan": business_plan
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/videos/{video_id}/prd",
    response_model=DocumentResponse,
    summary="Get PRD document",
    description="Retrieve the generated PRD document for a specific video",
    response_description="Returns the PRD document in markdown format"
)
async def get_prd(video_id: str):
    try:
        with open(f"data/prd_{video_id}.md", "r") as f:
            prd = f.read()
        return {"prd": prd}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="PRD not found")

@app.get("/api/videos/{video_id}/business-plan",
    response_model=DocumentResponse,
    summary="Get Business Plan document",
    description="Retrieve the generated Business Plan document for a specific video",
    response_description="Returns the Business Plan document in markdown format"
)
async def get_business_plan(video_id: str):
    try:
        with open(f"data/business_plan_{video_id}.md", "r") as f:
            business_plan = f.read()
        return {"business_plan": business_plan}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Business plan not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
