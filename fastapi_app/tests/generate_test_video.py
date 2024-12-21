import cv2
import numpy as np
import os

def create_test_video(duration=10, fps=30, resolution=(640, 480)):
    """Create a test video with UI text for OCR testing."""
    # Ensure test_files directory exists
    os.makedirs("tests/test_files", exist_ok=True)

    # Create video writer
    output_path = "tests/test_files/test_video.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, resolution)

    # Generate frames
    frames = duration * fps
    for i in range(frames):
        # Create base frame
        frame = np.zeros((resolution[1], resolution[0], 3), np.uint8)

        # Add different UI elements for each second
        second = i // fps
        if second % 3 == 0:
            text = "登录界面"
            cv2.putText(frame, text, (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.rectangle(frame, (180, 200), (460, 280), (255, 255, 255), 2)
        elif second % 3 == 1:
            text = "主页面"
            cv2.putText(frame, text, (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            # Add mock UI elements
            cv2.rectangle(frame, (50, 50), (590, 430), (255, 255, 255), 2)
        else:
            text = "设置页面"
            cv2.putText(frame, text, (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            # Add mock settings buttons
            for y in range(3):
                cv2.rectangle(frame, (180, 150 + y*100), (460, 200 + y*100), (255, 255, 255), 2)

        out.write(frame)

    out.release()
    print(f"Test video created at {output_path}")
    return output_path

if __name__ == "__main__":
    create_test_video()
