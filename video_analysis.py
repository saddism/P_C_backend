import os
import cv2
import time
from PIL import Image
import google.generativeai as genai
from typing import List
import pytesseract

# Configure Gemini API
genai.configure(api_key='AIzaSyDBhwyLlC3jO1ek2g0UyK3lp11CO8v1alg')

def extract_frames(video_path: str, output_dir: str = 'frames') -> List[str]:
    """Extract frames from video file"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Also create frontend assets directory for frames
    frontend_frames_dir = '../P_C_frontend/public/frames'
    if not os.path.exists(frontend_frames_dir):
        os.makedirs(frontend_frames_dir)

    cap = cv2.VideoCapture(video_path)
    frame_paths = []
    count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if count % 30 == 0:  # Extract every 30th frame
            frame_path = os.path.join(output_dir, f'frame_{count}.jpg')
            frontend_frame_path = os.path.join(frontend_frames_dir, f'frame_{count}.jpg')
            cv2.imwrite(frame_path, frame)
            cv2.imwrite(frontend_frame_path, frame)
            frame_paths.append(frame_path)

        count += 1

    cap.release()
    return frame_paths

def analyze_frames(frames: List[str]) -> str:
    """Analyze app features from frames using OCR and text analysis"""
    analyses = []

    for i, frame_path in enumerate(frames[:5]):  # Analyze first 5 frames
        frame = cv2.imread(frame_path)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)

        # Extract text from frame using OCR
        text = pytesseract.image_to_string(pil_image, lang='chi_sim+eng')

        analysis_prompt = f"""
        基于以下界面文本分析这个APP的功能和特点:

        界面文本:
        {text}

        请分析:
        1. 界面布局和UI元素
        2. 主要功能和交互方式
        3. 用户操作流程
        4. 技术实现思路

        重点关注:
        - 界面的主要组件和布局结构
        - 用户可以执行的操作
        - 功能的实现逻辑
        - 数据流动方式
        """

        try:
            response = genai.GenerativeModel('gemini-pro').generate_content(analysis_prompt)
            analyses.append(response.text)
            time.sleep(1)  # Rate limiting
        except Exception as e:
            print(f"Error analyzing frame {i}: {str(e)}")
            continue

    return "\n\n".join(analyses)

def generate_prd(analysis: str, frame_paths: List[str]) -> str:
    """Generate PRD document based on analysis"""
    # Create frame references for markdown
    frame_refs = "\n\n### 界面截图\n\n"
    for i, path in enumerate(frame_paths[:5]):
        frame_name = os.path.basename(path)
        frame_refs += f"![界面截图 {i+1}](/frames/{frame_name})\n\n"

    prd_prompt = f"""
    基于以下APP分析和界面截图，生成一份完整的产品需求文档（PRD）:

    分析内容:
    {analysis}

    界面截图:
    {frame_refs}

    PRD需要包含以下内容:
    1. 应用定位与目标用户群分析
    2. 完整的应用导航结构
    3. 界面功能和操作流程说明（包含界面说明和对应截图）
    4. 详细的技术功能清单
    5. 数据流程设计
    6. 具体的功能实现方案
    7. 单元测试计划

    请使用Markdown格式输出，确保文档结构清晰，每个部分都有详细说明。
    在界面功能说明部分，请引用相关的界面截图。
    """

    try:
        response = genai.GenerativeModel('gemini-pro').generate_content(prd_prompt)
        return frame_refs + "\n" + response.text
    except Exception as e:
        print(f"Error generating PRD: {str(e)}")
        return ""

def generate_business_plan(analysis: str) -> str:
    """Generate business plan based on analysis"""
    plan_prompt = f"""
    基于以下APP分析，生成一份详细的商业计划书:

    {analysis}

    计划书需要包含以下内容:
    1. 市场定位
       - 目标需求分析
       - 市场空间规模评估
    2. 用户画像
       - 典型用户特征
       - 使用场景分析
       - 使用时机研究
    3. 问题解决
       - 用户痛点分析
       - 解决方案深度
    4. 盈利模式
       - 收费策略
       - 用户付费意愿分析
    5. 竞争分析
       - 竞争对手分析
       - 产品优劣势
       - 实现思路
    6. 营销策略
       - 营销文案
       - 推广渠道

    请使用Markdown格式输出，确保内容详实，分析深入。
    """

    try:
        response = genai.GenerativeModel('gemini-pro').generate_content(plan_prompt)
        return response.text
    except Exception as e:
        print(f"Error generating business plan: {str(e)}")
        return ""

def main():
    """Main execution flow"""
    video_path = '/home/ubuntu/attachments/ScreenRecording_12-16-2024+11-49-44_1.MP4'

    print("Extracting frames...")
    frames = extract_frames(video_path)

    print("Analyzing app features...")
    analysis = analyze_frames(frames)

    print("Generating PRD...")
    prd = generate_prd(analysis, frames)
    with open('prd.md', 'w', encoding='utf-8') as f:
        f.write(prd)

    print("Generating Business Plan...")
    plan = generate_business_plan(analysis)
    with open('business_plan.md', 'w', encoding='utf-8') as f:
        f.write(plan)

    print("Analysis complete!")

if __name__ == "__main__":
    main()
