import pytest
from fastapi.testclient import TestClient
from main import app
import os
import json
import shutil

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_test_data():
    """Setup test data directory with mock PRD and BP files"""
    os.makedirs("data", exist_ok=True)

    # Create test PRD file
    with open("data/prd_test123.md", "w") as f:
        f.write("# Test Product\nThis is a test PRD")

    # Create test business plan file
    with open("data/business_plan_test123.md", "w") as f:
        f.write("# Test Business Plan\nThis is a test business plan")

    yield

    # Cleanup
    if os.path.exists("data/prd_test123.md"):
        os.remove("data/prd_test123.md")
    if os.path.exists("data/business_plan_test123.md"):
        os.remove("data/business_plan_test123.md")

def test_get_videos_endpoint(setup_test_data):
    """Test the GET /api/videos endpoint with test data"""
    response = client.get("/api/videos")
    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "data" in data
    assert "products" in data["data"]
    products = data["data"]["products"]

    # Should find our test product
    assert len(products) > 0
    test_product = next((p for p in products if p["id"] == "test123"), None)
    assert test_product is not None

    # Verify product structure
    assert test_product["name"] == "Test Product"
    assert test_product["description"] == "AI分析生成的产品需求文档"
    assert isinstance(test_product["tags"], list)
    assert "PRD" in test_product["tags"]
    assert "商业计划书" in test_product["tags"]
    assert test_product["icon"] == "📄"
    assert test_product["bp"] == "test123"
    assert test_product["prd"] == "test123"

def test_get_videos_empty():
    """Test the GET /api/videos endpoint with empty data directory"""
    # Create empty data directory
    if os.path.exists("data"):
        # Save existing files
        if os.path.exists("data_backup"):
            shutil.rmtree("data_backup")
        shutil.copytree("data", "data_backup")
        # Clean data directory
        shutil.rmtree("data")
    os.makedirs("data")

    try:
        response = client.get("/api/videos")
        assert response.status_code == 200
        data = response.json()

        # Should return empty products list
        assert data["data"]["products"] == []

    finally:
        # Restore data directory
        shutil.rmtree("data")
        if os.path.exists("data_backup"):
            shutil.copytree("data_backup", "data")
            shutil.rmtree("data_backup")

def test_get_videos_error_handling():
    """Test error handling in GET /api/videos endpoint"""
    # Create data directory with unreadable permissions
    if os.path.exists("data"):
        # Save existing files
        if os.path.exists("data_backup"):
            shutil.rmtree("data_backup")
        shutil.copytree("data", "data_backup")
        # Make data directory unreadable
        os.chmod("data", 0o000)

    try:
        response = client.get("/api/videos")
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "获取视频列表失败" in data["detail"]

    finally:
        # Cleanup: restore permissions and data
        if os.path.exists("data"):
            os.chmod("data", 0o755)
        if os.path.exists("data_backup"):
            shutil.rmtree("data")
            shutil.copytree("data_backup", "data")
            shutil.rmtree("data_backup")
