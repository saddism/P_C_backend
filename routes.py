from fastapi import APIRouter, HTTPException
from typing import Dict
import glob
import os
from models import VideoListResponse, VideoListItem

router = APIRouter()

@router.get("/api/videos",
    response_model=Dict[str, VideoListResponse],
    summary="Get analyzed videos list",
    description="Retrieve list of analyzed videos with their PRD and Business Plan links",
    response_description="Returns list of analyzed videos"
)
async def get_videos():
    try:
        # If data directory doesn't exist, return empty list
        if not os.path.exists("data"):
            return {
                "data": VideoListResponse(
                    products=[]
                )
            }

        # If data directory exists but is not readable, that's an error
        if not os.access("data", os.R_OK):
            raise HTTPException(
                status_code=500,
                detail="获取视频列表失败: 无法访问数据目录"
            )

        # List all files in data directory
        video_files = glob.glob("data/prd_*.md")
        products = []

        for prd_file in video_files:
            video_id = prd_file.split("prd_")[1].split(".md")[0]

            # Check if business plan exists
            bp_file = f"data/business_plan_{video_id}.md"
            if not os.path.exists(bp_file):
                continue

            # Read first line of PRD for name
            with open(prd_file, "r") as f:
                first_line = f.readline().strip()
                name = first_line.replace("# ", "")

            products.append(VideoListItem(
                id=video_id,
                name=name,
                description="AI分析生成的产品需求文档",
                tags=["PRD", "商业计划书"],
                icon="📄",
                bp=video_id,
                prd=video_id
            ))

        return {
            "data": VideoListResponse(
                products=products
            )
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取视频列表失败: {str(e)}"
        )
