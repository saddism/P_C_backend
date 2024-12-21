from typing import List, Optional
from pydantic import BaseModel

class VideoListItem(BaseModel):
    id: str
    name: str
    description: str
    tags: List[str]
    icon: str
    bp: str
    prd: str

class VideoListResponse(BaseModel):
    products: List[VideoListItem]

class ErrorResponse(BaseModel):
    detail: str

class VideoResponse(BaseModel):
    video_id: str
    status: str

class DocumentResponse(BaseModel):
    business_plan: Optional[str] = None
    prd: Optional[str] = None
