import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import uvicorn
from video_analysis import analyze_video, generate_prd, generate_business_plan
from typing import Dict, Optional

# Error message templates
ERROR_MESSAGES: Dict[int, str] = {
    400: "请求无效或文件处理错误",
    401: "未经授权的访问",
    403: "禁止访问",
    404: "未找到请求的资源",
    413: "文件大小超过500MB限制",
    415: "仅支持视频文件格式",
    500: "服务器内部错误",
    503: "服务暂时不可用"
}

class ErrorResponse(BaseModel):
    code: int
    message: str
    detail: Optional[str] = None

class VideoResponse(BaseModel):
    message: str
    prd: str
    business_plan: str

class DocumentResponse(BaseModel):
    prd: str | None = None
    business_plan: str | None = None

# Email configuration
mail_config = ConnectionConfig(
    MAIL_USERNAME=os.getenv("SMTP_USER"),
    MAIL_PASSWORD=os.getenv("SMTP_PASSWORD"),
    MAIL_FROM=os.getenv("SMTP_USER"),
    MAIL_PORT=int(os.getenv("SMTP_PORT", "465")),
    MAIL_SERVER=os.getenv("SMTP_HOST"),
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True
)

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

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.status_code,
            message=ERROR_MESSAGES.get(exc.status_code, "未知错误"),
            detail=str(exc.detail)
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            code=500,
            message=ERROR_MESSAGES[500],
            detail=str(exc)
        ).dict()
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
    Supported formats: MP4
    """,
    response_description="Returns generated PRD and Business Plan documents"
)
async def upload_video(
    request: Request,
    file: UploadFile = File(default=None, description="App screen recording video file (MP4 format)")
):
    try:
        # Authentication check first, before ANY file operations
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(
                status_code=401,
                detail=ERROR_MESSAGES[401]
            )

        # Validate token before touching the file
        token = auth_header.split(' ')[1]
        if not token or token != "valid_token":  # In production, this would be proper token validation
            raise HTTPException(
                status_code=401,
                detail=ERROR_MESSAGES[401]
            )

        # Check content-length header first for quick rejection of large files
        content_length = request.headers.get('content-length')
        if content_length:
            try:
                file_size = int(content_length)
                if file_size > 500 * 1024 * 1024:  # 500MB
                    raise HTTPException(
                        status_code=413,
                        detail=ERROR_MESSAGES[413]
                    )
            except ValueError:
                pass  # Invalid content-length header, continue with normal validation

        # File validation
        if not file:
            raise HTTPException(
                status_code=400,
                detail=ERROR_MESSAGES[400]
            )

        # File validation
        if not file:
            raise HTTPException(
                status_code=400,
                detail=ERROR_MESSAGES[400]
            )

        # Validate file type first (cheapest check)
        if not file.content_type.startswith("video/"):
            raise HTTPException(
                status_code=415,
                detail=ERROR_MESSAGES[415]
            )

        # Check file size (500MB limit)
        MAX_SIZE = 500 * 1024 * 1024  # 500MB

        # Get file size from content length header first
        content_length = request.headers.get('content-length')
        if content_length:
            try:
                if int(content_length) > MAX_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail=ERROR_MESSAGES[413]
                    )
            except ValueError:
                pass  # Invalid content-length header, continue with chunk reading

        # If content length not available or invalid, check the file object
        file_size = 0
        chunk_size = 8192  # 8KB chunks
        content = bytearray()

        # Read file in chunks to check size and store content
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            content.extend(chunk)
            file_size += len(chunk)
            if file_size > MAX_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=ERROR_MESSAGES[413]
                )

        # Save uploaded file
        file_path = f"data/uploads/{file.filename}"
        os.makedirs("data/uploads", exist_ok=True)

        with open(file_path, "wb") as buffer:
            buffer.write(content)

        # Process video
        try:
            frames = analyze_video(file_path)
            if not frames:
                raise HTTPException(
                    status_code=500,
                    detail="视频分析失败，无法提取帧"
                )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"视频分析错误: {str(e)}"
            )

        # Generate documents
        try:
            prd = generate_prd(frames)
            business_plan = generate_business_plan(frames)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"文档生成错误: {str(e)}"
            )

        return {
            "message": "视频分析成功",
            "prd": prd,
            "business_plan": business_plan
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"处理请求时发生错误: {str(e)}"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"处理请求时发生错误: {str(e)}"
        )

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
