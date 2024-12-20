# P_C Backend

## 新增功能 (New Features)

### 1. 视频分析功能 (Video Analysis)
新增以下模型：
- `Video` - 视频信息存储
  - 文件信息
  - 上传状态
  - 分析状态
- `Analysis` - 分析结果存储
  - PRD文档
  - 商业计划书
  - 分析时间戳

### 2. 新增API端点 (New API Endpoints)
所有新增API端点：
```
GET /api/videos - 获取视频列表
POST /api/videos/upload - 上传视频文件
GET /api/videos/:id/analysis-status - 获取视频分析状态
GET /api/videos/:id/prd - 获取PRD文档
GET /api/videos/:id/business-plan - 获取商业计划书
```

### 3. 视频处理服务 (Video Processing)
新增功能：
- 视频文件上传（最大500MB）
- 视频帧提取
- OCR文本识别
- Google Gemini API集成
  - 场景分析
  - 功能识别
  - PRD文档生成
  - 商业计划书生成

### 4. 中间件 (Middleware)
新增：
- 文件上传中间件
- 视频大小限制验证
- 文件类型验证

### API文档 (API Documentation)
- API服务地址：https://auth-api-nvdempim.fly.dev
- API文档：https://auth-api-nvdempim.fly.dev/docs

### Google Gemini API配置 (API Configuration)
使用环境变量配置：
```
GEMINI_API_KEY=AIzaSyDBhwyLlC3jO1ek2g0UyK3lp11CO8v1alg
```

注意：所有API更改均为新增功能，未修改任何现有API。
