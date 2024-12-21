import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add application root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.services.video import extract_frames, perform_ocr
from app.services.gemini import GeminiService
from app.database import get_db
from app.models import User, Video, Analysis
from sqlalchemy.orm import Session
from .generate_test_video import create_test_video

client = TestClient(app)

@pytest.fixture
def test_video():
    """Create a test video file for testing."""
    video_path = create_test_video(duration=3)
    yield video_path
    if os.path.exists(video_path):
        os.remove(video_path)

@pytest.fixture
def auth_headers():
    """Get authentication headers."""
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_frame_extraction(test_video):
    """Test video frame extraction."""
    frames = extract_frames(test_video)
    assert len(frames) > 0
    assert all(frame.shape == (480, 640, 3) for frame in frames)

def test_ocr_accuracy(test_video):
    """Test OCR text recognition accuracy."""
    frames = extract_frames(test_video)
    texts = [perform_ocr(frame) for frame in frames]
    expected_texts = ["登录界面", "主页面", "设置页面"]
    assert any(any(expected in text for text in texts) for expected in expected_texts)

def test_prd_generation(test_video, auth_headers):
    """Test PRD document generation."""
    # Upload video first
    with open(test_video, "rb") as f:
        response = client.post(
            "/api/videos/upload",
            files={"file": ("test.mp4", f, "video/mp4")},
            headers=auth_headers
        )
    video_id = response.json()["video_id"]

    # Get PRD
    response = client.get(f"/api/videos/{video_id}/prd", headers=auth_headers)
    assert response.status_code == 200
    prd = response.json()["prd_content"]

    # Check PRD content
    required_sections = [
        "应用定位与目标用户群分析",
        "应用导航结构",
        "界面功能和操作流程",
        "技术功能清单",
        "数据流程设计",
        "功能实现方案"
    ]
    for section in required_sections:
        assert section in prd

def test_business_plan_generation(test_video, auth_headers):
    """Test Business Plan document generation."""
    # Upload video first
    with open(test_video, "rb") as f:
        response = client.post(
            "/api/videos/upload",
            files={"file": ("test.mp4", f, "video/mp4")},
            headers=auth_headers
        )
    video_id = response.json()["video_id"]

    # Get Business Plan
    response = client.get(f"/api/videos/{video_id}/business-plan", headers=auth_headers)
    assert response.status_code == 200
    plan = response.json()["business_plan"]

    # Check Business Plan content
    required_sections = [
        "市场定位分析",
        "用户画像分析",
        "问题解决方案",
        "盈利模式分析",
        "竞争对手分析",
        "营销策略建议"
    ]
    for section in required_sections:
        assert section in plan

def test_database_operations(test_video, auth_headers):
    """Test database operations for video analysis."""
    # Upload video
    with open(test_video, "rb") as f:
        response = client.post(
            "/api/videos/upload",
            files={"file": ("test.mp4", f, "video/mp4")},
            headers=auth_headers
        )
    video_id = response.json()["video_id"]

    # Check video entry
    db = next(get_db())
    video = db.query(Video).filter(Video.id == video_id).first()
    assert video is not None
    assert video.status in ["pending", "processing", "completed"]

    # Check analysis entry after processing
    analysis = db.query(Analysis).filter(Analysis.video_id == video_id).first()
    assert analysis is not None
    assert analysis.prd_content is not None
    assert analysis.business_plan is not None
