import os
import google.generativeai as genai
import logging
import ffmpeg
import cv2
import pytesseract
import numpy as np
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro-vision',
                            safety_settings={
                                "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                                "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
                                "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
                                "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE"
                            })

def extract_text_from_frame(frame_path: str) -> str:
    """Extract text from frame using OCR"""
    try:
        img = cv2.imread(frame_path)
        if img is None:
            logger.error(f"Failed to read image: {frame_path}")
            return ""

        # Preprocess image for better OCR
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # Extract text using Tesseract with Chinese and English support
        text = pytesseract.image_to_string(thresh, lang='chi_sim+eng')
        return text.strip()
    except Exception as e:
        logger.error(f"Error in OCR processing: {str(e)}")
        return ""

def analyze_video(video_path: str) -> List[Dict[str, Any]]:
    """Extract frames from video and analyze app functionality"""
    os.makedirs('data/frames', exist_ok=True)
    os.makedirs('data/output', exist_ok=True)

    try:
        # Extract frames with adaptive sampling
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Failed to open video file: {video_path}")
            return []

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps

        # Optimize sampling rate based on video duration
        if duration <= 30:  # Short videos (≤30s)
            interval = max(int(fps), total_frames // 30)  # At least 1 frame per second
        elif duration <= 120:  # Medium videos (30s-2min)
            interval = max(int(fps * 2), total_frames // 50)  # 1 frame per 2 seconds
        else:  # Long videos (>2min)
            interval = max(int(fps * 3), total_frames // 60)  # 1 frame per 3 seconds

        frames = []
        frame_count = 0
        frame_data = []
        last_scene_change = 0
        prev_frame = None

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Check for scene changes if we have a previous frame
            if prev_frame is not None and frame_count - last_scene_change >= interval:
                diff = cv2.absdiff(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
                                 cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY))
                non_zero = cv2.countNonZero(diff)
                if non_zero > frame.shape[0] * frame.shape[1] * 0.1:  # 10% change threshold
                    last_scene_change = frame_count
                    frame_path = f'data/frames/frame_{frame_count}.jpg'
                    cv2.imwrite(frame_path, frame)
                    text = extract_text_from_frame(frame_path)
                    frame_data.append({
                        'path': frame_path,
                        'timestamp': frame_count / fps,
                        'ocr_text': text,
                        'scene_change': True
                    })
                    frames.append(frame_path)

            # Regular interval sampling
            elif frame_count % interval == 0:
                frame_path = f'data/frames/frame_{frame_count}.jpg'
                cv2.imwrite(frame_path, frame)
                text = extract_text_from_frame(frame_path)
                frame_data.append({
                    'path': frame_path,
                    'timestamp': frame_count / fps,
                    'ocr_text': text,
                    'scene_change': False
                })
                frames.append(frame_path)

            prev_frame = frame.copy()
            frame_count += 1

        cap.release()
        logger.info(f"Extracted {len(frames)} frames from video")
        return frame_data
    except Exception as e:
        logger.error(f"Error extracting frames: {e}")
        return []

def generate_prd(frame_data: List[Dict[str, Any]]) -> str:
    """Generate PRD document from video frames and OCR data in Chinese"""
    try:
        logger.info("Generating PRD document...")
        frame_parts = []
        ocr_analysis = []

        for frame in frame_data:
            try:
                with open(frame['path'], 'rb') as f:
                    frame_parts.append({
                        'mime_type': 'image/jpeg',
                        'data': f.read()
                    })
                if frame['ocr_text']:
                    ocr_analysis.append(f"界面时间点 {frame['timestamp']:.2f}s:\n{frame['ocr_text']}\n")
            except Exception as e:
                logger.error(f"Error reading frame {frame['path']}: {str(e)}")
                continue

        # Combine OCR analysis with prompt
        ocr_context = "\n分析提取的界面文本：\n" + "\n".join(ocr_analysis) if ocr_analysis else ""

        prompt = f"""基于以下应用程序的界面截图和文本分析，生成一份详细的产品需求文档（PRD）。

提取的界面文本分析：
{ocr_context}

请包含以下内容：

1. 应用定位与目标用户群分析
   - 产品定位和价值主张
   - 目标用户群体画像
   - 核心应用场景分析

2. 完整的应用导航结构
   - 功能模块架构
   - 页面层级关系
   - 用户操作流程图

3. 界面功能和操作流程说明
   - 每个界面的详细截图说明
   - 界面元素和交互设计
   - 用户操作步骤和流程
   - 功能点细节描述

4. 技术功能清单
   - 核心功能模块列表
   - 数据处理流程
   - API接口设计
   - 数据库结构设计

5. 具体实现方案
   - 技术架构设计
   - 系统组件说明
   - 第三方服务集成
   - 性能优化方案

6. 测试计划
   - 功能测试用例
   - 性能测试指标
   - 安全测试要求
   - 兼容性测试范围

请基于提供的界面截图和文本分析，详细分析每个页面的功能和交互设计，确保文档结构清晰，内容完整。重点关注用户体验和技术实现的可行性。"""

        response = model.generate_content([prompt] + frame_parts)
        prd_content = response.text

        # Save the PRD document
        os.makedirs('data/output', exist_ok=True)
        prd_path = 'data/output/prd.md'
        with open(prd_path, 'w', encoding='utf-8') as f:
            f.write(prd_content)
        logger.info(f"PRD document saved to {prd_path}")

        return prd_content
    except Exception as e:
        logger.error(f"Error in generate_prd: {str(e)}")
        raise

def generate_business_plan(frame_data: List[Dict[str, Any]]) -> str:
    """Generate business plan from video frames and OCR data in Chinese"""
    try:
        logger.info("Generating business plan...")
        frame_parts = []
        ocr_analysis = []

        for frame in frame_data:
            try:
                with open(frame['path'], 'rb') as f:
                    frame_parts.append({
                        'mime_type': 'image/jpeg',
                        'data': f.read()
                    })
                if frame['ocr_text']:
                    ocr_analysis.append(f"界面时间点 {frame['timestamp']:.2f}s:\n{frame['ocr_text']}\n")
            except Exception as e:
                logger.error(f"Error reading frame {frame['path']}: {str(e)}")
                continue

        # Combine OCR analysis with prompt
        ocr_context = "\n分析提取的界面文本：\n" + "\n".join(ocr_analysis) if ocr_analysis else ""

        prompt = f"""基于以下应用程序的界面截图和文本分析，生成一份完整的商业计划书。

提取的界面文本分析：
{ocr_context}

请包含以下内容：

1. 市场定位分析
   - 目标市场需求和痛点
   - 市场规模评估
   - 发展趋势分析
   - 市场机会和挑战

2. 用户画像分析
   - 目标用户特征描述
   - 用户使用场景详解
   - 用户行为习惯分析
   - 用户需求层次

3. 价值主张
   - 核心问题解决方案
   - 用户痛点分析
   - 产品优势亮点
   - 差异化竞争力

4. 商业模式
   - 收入来源分析
   - 定价策略设计
   - 用户付费意愿评估
   - 成本结构分析

5. 竞争分析
   - 竞品对比分析
   - 竞争优势分析
   - 市场差异化策略
   - 发展机会分析

6. 营销推广
   - 营销策略规划
   - 推广渠道选择
   - 用户获取方案
   - 品牌建设策略

请基于提供的界面截图和文本分析，深入分析产品的商业价值和市场潜力，重点关注盈利模式和竞争策略。"""

        response = model.generate_content([prompt] + frame_parts)
        business_plan_content = response.text

        # Save the business plan document
        os.makedirs('data/output', exist_ok=True)
        business_plan_path = 'data/output/business_plan.md'
        with open(business_plan_path, 'w', encoding='utf-8') as f:
            f.write(business_plan_content)
        logger.info(f"Business plan saved to {business_plan_path}")

        return business_plan_content
    except Exception as e:
        logger.error(f"Error in generate_business_plan: {str(e)}")
        raise
