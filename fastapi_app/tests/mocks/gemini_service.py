"""Mock implementation of GeminiService for testing."""
from typing import List
from fastapi import HTTPException

class MockGeminiService:
    def __init__(self):
        """Initialize mock service without API key requirement."""
        pass

    async def generate_prd(self, ocr_results: List[str]) -> str:
        """Mock PRD generation with predefined content."""
        return """# 产品需求文档 (PRD)

## 1. 应用定位与目标用户群分析
- 应用定位：移动应用开发辅助工具
- 目标用户：产品经理、开发者
- 用户需求：快速生成产品文档

## 2. 应用导航结构
- 首页
- 视频上传页面
- 分析结果页面

## 3. 界面功能和操作流程
### 首页
- 头部展示区
- 产品列表
- 用户评价

### 视频上传
- 文件选择
- 上传进度
- 分析状态

## 4. 技术功能清单
- 视频上传
- OCR识别
- AI分析
- 文档生成

## 5. 数据流程
- 用户认证
- 视频处理
- 文档存储

## 6. 测试计划
- 功能测试
- 性能测试
- 用户体验测试"""

    async def generate_business_plan(self, prd_content: str) -> str:
        """Mock business plan generation with predefined content."""
        return """# 商业计划书

## 1. 市场定位分析
- 市场需求：自动化工具需求旺盛
- 市场规模：预计10亿规模
- 增长潜力：年增长率30%

## 2. 用户画像
- 产品经理
- 开发团队
- 创业者

## 3. 解决方案
- 自动化文档生成
- 降低人工成本
- 提高效率

## 4. 盈利模式
- 订阅制
- API调用计费
- 企业版本

## 5. 竞争分析
- 传统文档工具
- AI辅助工具
- 市场机会

## 6. 营销策略
- 技术社区推广
- 内容营销
- 用户案例分享"""
