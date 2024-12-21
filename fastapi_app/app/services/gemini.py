import google.generativeai as genai
from os import getenv
from typing import List
from fastapi import HTTPException
import json

class GeminiService:
    def __init__(self):
        api_key = getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    async def generate_prd(self, ocr_results: List[str]) -> str:
        """
        Generate a Product Requirements Document (PRD) from OCR results.
        Returns markdown formatted string.
        """
        try:
            # Combine OCR results into a coherent text
            app_text = "\n".join(ocr_results)

            prompt = f"""
            Based on the following app interface text and elements, generate a detailed Product Requirements Document (PRD) in Markdown format.

            APP INTERFACE TEXT:
            {app_text}

            Generate a comprehensive PRD that includes:
            1. 应用定位与目标用户群分析
               - 应用的市场定位
               - 目标用户画像
               - 用户需求分析

            2. 完整的应用导航结构
               - 主要功能模块
               - 页面层级关系
               - 用户流程图

            3. 界面功能和操作流程
               - 每个界面的详细说明
               - 具体的交互元素描述
               - 用户操作流程

            4. 技术功能清单
               - 核心功能列表
               - API需求
               - 数据存储需求

            5. 数据流程设计
               - 数据处理流程
               - 数据模型设计
               - 安全性考虑

            6. 测试计划
               - 功能测试要点
               - 性能测试指标
               - 用户体验测试

            Format the response in Markdown with clear sections and subsections.
            Include specific details from the provided interface text.
            Focus on practical implementation details and user experience.
            """

            response = await self.model.generate_content(prompt)
            if not response.text:
                raise HTTPException(status_code=500, detail="Failed to generate PRD content")

            return response.text

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PRD generation failed: {str(e)}")

    async def generate_business_plan(self, prd_content: str) -> str:
        """
        Generate a Business Plan based on the PRD content.
        Returns markdown formatted string.
        """
        try:
            prompt = f"""
            Based on the following Product Requirements Document (PRD), generate a comprehensive Business Plan in Markdown format.

            PRD CONTENT:
            {prd_content}

            Generate a detailed business plan that includes:
            1. 市场定位分析
               - 市场需求分析
               - 市场规模评估
               - 竞争优势分析

            2. 用户画像分析
               - 目标用户特征
               - 用户使用场景
               - 用户痛点分析

            3. 问题解决方案
               - 核心价值主张
               - 解决方案详情
               - 创新点分析

            4. 盈利模式
               - 收费策略
               - 用户付费意愿分析
               - 收入预测

            5. 竞争对手分析
               - 主要竞争对手
               - 竞品对比分析
               - 市场差异化策略

            6. 营销策略
               - 推广渠道
               - 营销文案建议
               - 用户获取策略

            Format the response in Markdown with clear sections and subsections.
            Focus on practical business implementation and market potential.
            Include specific market analysis and revenue projections.
            """

            response = await self.model.generate_content(prompt)
            if not response.text:
                raise HTTPException(status_code=500, detail="Failed to generate Business Plan content")

            return response.text

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Business Plan generation failed: {str(e)}")
