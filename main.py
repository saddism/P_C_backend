import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from video_analysis import analyze_video, generate_prd, generate_business_plan

app = FastAPI(
    title="Video Analysis API",
    description="API for analyzing app screen recordings and generating PRD/Business Plan",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/videos/upload")
async def upload_video(file: UploadFile = File(...)):
    try:
        # Save uploaded file
        file_path = f"uploads/{file.filename}"
        os.makedirs("uploads", exist_ok=True)

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

@app.get("/api/videos/{video_id}/prd")
async def get_prd(video_id: str):
    try:
        with open("prd.md", "r") as f:
            prd = f.read()
        return {"prd": prd}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="PRD not found")

@app.get("/api/videos/{video_id}/business-plan")
async def get_business_plan(video_id: str):
    try:
        with open("business_plan.md", "r") as f:
            business_plan = f.read()
        return {"business_plan": business_plan}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Business plan not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
