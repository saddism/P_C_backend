from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
from ..database import get_db
from ..models import User, Video, Analysis
from ..services.video import save_video, extract_frames, perform_ocr
from ..services.gemini import GeminiService
from .auth import get_current_user
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/videos", tags=["视频分析"])
gemini_service = GeminiService()

@router.post("/upload",
    response_model=Dict,
    summary="上传视频进行分析",
    description="""
    上传APP操作录屏视频进行分析。系统会：
    1. 保存视频文件（最大500MB）
    2. 提取视频帧
    3. 使用OCR识别界面文本
    4. 生成PRD文档和商业计划书

    状态说明：
    - pending: 等待处理
    - processing: 正在处理
    - completed: 处理完成
    - failed: 处理失败
    """,
    responses={
        200: {
            "description": "上传成功",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Video uploaded and processed successfully",
                        "video_id": 1,
                        "status": "completed"
                    }
                }
            }
        },
        413: {
            "description": "文件过大（超过500MB）",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "File too large. Maximum size is 500MB"
                    }
                }
            }
        }
    }
)
async def upload_video(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Upload and process a video file."""
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

@router.get("/{video_id}/prd",
    response_model=Dict,
    summary="获取PRD文档",
    description="""
    获取基于视频分析生成的PRD文档。文档包含：
    - 应用定位与目标用户群分析
    - 完整的应用导航结构
    - 界面功能和操作流程说明
    - 技术功能清单
    - 数据流程设计
    - 具体的功能实现方案

    文档采用Markdown格式。
    """,
    responses={
        200: {
            "description": "成功获取PRD文档",
            "content": {
                "application/json": {
                    "example": {
                        "video_id": 1,
                        "prd_content": "# 产品需求文档\n\n## 1. 应用定位与目标用户群分析\n..."
                    }
                }
            }
        }
    }
)
async def get_prd(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Retrieve the PRD generated from video analysis."""
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

@router.get("/{video_id}/business-plan",
    response_model=Dict,
    summary="获取商业计划书",
    description="""
    获取基于视频分析生成的商业计划书。文档包含：
    - 市场定位分析（需求和规模）
    - 用户画像分析（特征和场景）
    - 问题解决方案（价值主张）
    - 盈利模式分析（收费策略）
    - 竞争对手分析
    - 营销策略建议

    文档采用Markdown格式。
    """,
    responses={
        200: {
            "description": "成功获取商业计划书",
            "content": {
                "application/json": {
                    "example": {
                        "video_id": 1,
                        "business_plan": "# 商业计划书\n\n## 1. 市场定位分析\n..."
                    }
                }
            }
        }
    }
)
async def get_business_plan(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Retrieve the Business Plan generated from video analysis."""
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
