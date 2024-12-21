from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, videos

app = FastAPI(
    title="Authentication and Video Analysis API",
    description="""
    User authentication with email verification and video analysis for PRD/BP generation.

    ## 视频分析功能

    上传视频后，系统会：
    1. 分析录屏视频中每个APP页面的功能
    2. 分析应用场景和流程
    3. 生成PRD文档，包含：
       - 应用定位与目标用户群分析
       - 完整的应用导航结构
       - 界面功能和操作流程说明
       - 技术功能清单
       - 数据流程设计
       - 具体的功能实现方案

    4. 生成商业计划书，包含：
       - 市场定位分析（需求和市场规模）
       - 用户画像分析（特征和使用场景）
       - 问题解决方案（价值主张）
       - 盈利模式分析
       - 竞争对手分析
       - 营销策略建议

    注意：视频大小限制为500MB
    """,
    version="1.0.0",
    servers=[{"url": "https://auth-api-nvdempim.fly.dev", "description": "Production server"}]
)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(auth.router, tags=["认证"])
app.include_router(videos.router, tags=["视频分析"])

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
