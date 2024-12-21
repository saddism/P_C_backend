import pytest
from fastapi.testclient import TestClient
from main import app, ERROR_MESSAGES
from unittest.mock import patch, MagicMock
import io
import json

client = TestClient(app)

def create_test_file(size_mb, content_type="video/mp4", filename="test.mp4"):
    """Helper function to create test file with specified size"""
    # Create minimal content for the file
    content = b"0" * 1024  # Just 1KB of actual content
    return {
        "file": (filename, io.BytesIO(content), content_type)
    }, {
        "content-length": str(size_mb * 1024 * 1024)  # Set content-length header
    }

def test_unauthorized_access():
    """Test unauthorized access"""
    print("\nTesting unauthorized access...")
    files, _ = create_test_file(1)
    # Don't include authorization header
    response = client.post("/api/videos/upload", files=files)
    assert response.status_code == 401
    assert response.json()["message"] == ERROR_MESSAGES[401]

def test_file_size_limit():
    """Test file size limit (500MB)"""
    print("\nTesting file size limit...")
    files, headers = create_test_file(501)  # Create a file larger than 500MB
    headers["Authorization"] = "Bearer valid_token"  # Add authorization
    response = client.post("/api/videos/upload", files=files, headers=headers)
    assert response.status_code == 413
    assert response.json()["message"] == ERROR_MESSAGES[413]

def test_invalid_file_format():
    """Test invalid file format rejection"""
    print("\nTesting invalid file format...")
    files, headers = create_test_file(1, content_type="text/plain", filename="test.txt")
    headers["Authorization"] = "Bearer valid_token"  # Add authorization
    response = client.post("/api/videos/upload", files=files, headers=headers)
    assert response.status_code == 415
    assert response.json()["message"] == ERROR_MESSAGES[415]

@patch('main.analyze_video')
def test_processing_error(mock_analyze):
    """Test video processing error handling"""
    print("\nTesting processing error...")
    mock_analyze.side_effect = Exception("Processing failed")
    files, headers = create_test_file(1)
    headers["Authorization"] = "Bearer valid_token"  # Add authorization
    response = client.post("/api/videos/upload", files=files, headers=headers)
    assert response.status_code == 500
    assert response.json()["message"] == ERROR_MESSAGES[500]

def test_authorized_access():
    """Test authorized access with valid token"""
    print("\nTesting authorized access...")
    files, headers = create_test_file(1)
    headers["Authorization"] = "Bearer valid_token"  # Add authorization
    response = client.post("/api/videos/upload", files=files, headers=headers)
    assert response.status_code not in [401, 403]  # Should not be unauthorized

def run_all_tests():
    """Run all tests and save results"""
    results = {
        "unauthorized_access": None,
        "file_size_limit": None,
        "invalid_file_format": None,
        "processing_error": None,
        "authorized_access": None
    }

    # Run tests in order
    tests = [
        (test_unauthorized_access, "unauthorized_access"),
        (test_file_size_limit, "file_size_limit"),
        (test_invalid_file_format, "invalid_file_format"),
        (test_processing_error, "processing_error"),
        (test_authorized_access, "authorized_access")
    ]

    for test_func, test_name in tests:
        try:
            test_func()
            results[test_name] = "PASS"
            print(f"{test_name}: PASS")
        except AssertionError as e:
            results[test_name] = f"FAIL: {str(e)}"
            print(f"{test_name}: FAIL - {str(e)}")
        except Exception as e:
            results[test_name] = f"ERROR: {str(e)}"
            print(f"{test_name}: ERROR - {str(e)}")

    # Save results
    with open("error_test_results.json", "w") as f:
        json.dump(results, f, indent=2)

    return results

if __name__ == "__main__":
    run_all_tests()
