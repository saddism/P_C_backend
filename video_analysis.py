import os
import google.generativeai as genai
import logging
import ffmpeg

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Google Gemini API
genai.configure(api_key='AIzaSyDBhwyLlC3jO1ek2g0UyK3lp11CO8v1alg')
model = genai.GenerativeModel('gemini-pro-vision',
                            safety_settings={
                                "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                                "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
                                "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
                                "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE"
                            })

def analyze_video(video_path):
    """Extract frames from video and analyze app functionality"""
    os.makedirs('data/frames', exist_ok=True)

    try:
        # Extract frames every 2 seconds
        stream = ffmpeg.input(video_path)
        stream = ffmpeg.filter(stream, 'fps', fps=0.5)
        stream = ffmpeg.output(stream, 'data/frames/frame_%d.jpg')
        ffmpeg.run(stream)

        # Get list of frame paths
        frames = []
        for frame in sorted(os.listdir('data/frames')):
            if frame.endswith('.jpg'):
                frames.append(os.path.join('data/frames', frame))

        return frames
    except Exception as e:
        logger.error(f"Error extracting frames: {e}")
        return []

def generate_prd(frames):
    """Generate PRD document from video frames in Chinese"""
    try:
        logger.info("Generating PRD document...")
        frame_parts = []
        for frame in frames:
            try:
                with open(frame, 'rb') as f:
                    frame_parts.append({
                        'mime_type': 'image/jpeg',
                        'data': f.read()
                    })
            except Exception as e:
                logger.error(f"Error reading frame {frame}: {str(e)}")
                continue

        prompt = """基于以下应用程序的界面截图，生成一份详细的产品需求文档（PRD），包括以下内容：

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

请基于提供的界面截图，详细分析每个页面的功能和交互设计，确保文档结构清晰，内容完整。重点关注用户体验和技术实现的可行性。"""

        response = model.generate_content([prompt] + frame_parts)
        prd_content = response.text

        # Save the PRD document
        prd_path = 'data/output/prd.md'
        with open(prd_path, 'w', encoding='utf-8') as f:
            f.write(prd_content)
        logger.info(f"PRD document saved to {prd_path}")

        return prd_content
    except Exception as e:
        logger.error(f"Error in generate_prd: {str(e)}")
        raise

def generate_business_plan(frames):
    """Generate business plan from video frames in Chinese"""
    try:
        logger.info("Generating business plan...")
        frame_parts = []
        for frame in frames:
            try:
                with open(frame, 'rb') as f:
                    frame_parts.append({
                        'mime_type': 'image/jpeg',
                        'data': f.read()
                    })
            except Exception as e:
                logger.error(f"Error reading frame {frame}: {str(e)}")
                continue

        prompt = """基于以下应用程序的界面截图，生成一份完整的商业计划书，包括以下内容：

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

请基于提供的界面截图，深入分析产品的商业价值和市场潜力，重点关注盈利模式和竞争策略。"""

        response = model.generate_content([prompt] + frame_parts)
        business_plan_content = response.text

        # Save the business plan document
        business_plan_path = 'data/output/business_plan.md'
        with open(business_plan_path, 'w', encoding='utf-8') as f:
            f.write(business_plan_content)
        logger.info(f"Business plan saved to {business_plan_path}")

        return business_plan_content
    except Exception as e:
        logger.error(f"Error in generate_business_plan: {str(e)}")
        raise
