import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add application root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import get_db
from sqlalchemy.orm import Session
from app.models import User, Video, Analysis
from .generate_test_video import create_test_video

client = TestClient(app)

@pytest.fixture
def test_video():
    """Create a test video file for testing."""
    video_path = create_test_video(duration=3)  # 3-second test video
    yield video_path
    # Cleanup
    if os.path.exists(video_path):
        os.remove(video_path)

@pytest.fixture
def auth_headers():
    """Get authentication headers."""
    # Login with test user
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_video_upload(test_video, auth_headers):
    """Test video upload functionality."""
    with open(test_video, "rb") as f:
        response = client.post(
            "/api/videos/upload",
            files={"file": ("test.mp4", f, "video/mp4")},
            headers=auth_headers
        )
    assert response.status_code == 200
    data = response.json()
    assert "video_id" in data
    assert data["status"] in ["pending", "processing", "completed"]

def test_large_video_upload(auth_headers):
    """Test upload size limit (500MB)."""
    # Create a file slightly larger than 500MB
    large_file = "tests/test_files/large.mp4"
    with open(large_file, "wb") as f:
        f.seek(525_000_000)  # ~525MB
        f.write(b"\0")

    try:
        with open(large_file, "rb") as f:
            response = client.post(
                "/api/videos/upload",
                files={"file": ("large.mp4", f, "video/mp4")},
                headers=auth_headers
            )
        assert response.status_code == 413
        assert "File too large" in response.json()["detail"]
    finally:
        if os.path.exists(large_file):
            os.remove(large_file)

def test_invalid_file_type(auth_headers):
    """Test invalid file type rejection."""
    content = b"This is not a video file"
    response = client.post(
        "/api/videos/upload",
        files={"file": ("test.txt", content, "text/plain")},
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]

def test_unauthorized_upload():
    """Test upload without authentication."""
    with open("tests/test_files/test_video.mp4", "rb") as f:
        response = client.post(
            "/api/videos/upload",
            files={"file": ("test.mp4", f, "video/mp4")}
        )
    assert response.status_code == 401
