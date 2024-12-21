# P_C_backend

视频分析后端服务，提供视频处理和文档生成API。

## 功能特性

- 视频帧提取和分析
  - 支持MP4格式视频上传（最大500MB）
  - 自适应帧采样率
  - 场景变化检测
  - OCR文字识别（支持中英文）

- 文档生成
  - PRD文档自动生成
  - 商业计划书自动生成
  - 基于Google Gemini API的智能分析

- 错误处理
  - 中文错误提示
  - 详细的错误状态反馈
  - 超时保护机制

## API接口

### API文档要求
- 使用Swagger生成标准JSON格式API文档
- 文档必须包含：
  - 接口地址（完整URL路径）
  - 接口详细描述
  - 请求参数名称和类型
  - 返回数据格式和类型
- 访问文档：https://auth-api-nvdempim.fly.dev/docs

### API修改原则
- 严格遵守现有API不变原则
- 只允许新增API端点
- 所有API变更需经确认
- 保持向后兼容性

注意：保持现有API不变，仅新增功能性接口

```
POST https://auth-api-nvdempim.fly.dev/api/videos/upload
Content-Type: multipart/form-data

参数：
- file: 视频文件（MP4格式，最大500MB）

返回：
{
  "message": "视频分析成功",
  "videoId": "视频ID",
  "prd": "PRD文档内容",
  "business_plan": "商业计划书内容"
}
```

### 分析状态查询

```
GET https://auth-api-nvdempim.fly.dev/api/videos/{videoId}/status

返回：
{
  "status": "processing|completed|failed",
  "progress": 0-100,
  "prd": "PRD文档内容（仅在完成时）",
  "business_plan": "商业计划书内容（仅在完成时）"
}
```

## 错误代码

- 400: 请求格式错误
- 401: 未经授权的访问
- 403: 禁止访问
- 404: 未找到请求的资源
- 413: 上传的文件太大
- 415: 不支持的文件类型
- 500: 服务器内部错误
- 503: 服务暂时不可用

## 性能优化

### 性能测试结果
- 帧提取性能
  - 处理时间：~0.57秒/帧
  - 内存增长：16MB/处理周期
  - 自适应采样策略有效减少处理帧数

- OCR性能
  - 文本识别准确率：>95%（基于测试集）
  - 支持中英文混合识别
  - 预处理优化提升识别率

- 系统资源利用
  - CPU利用率：<30%（8核心环境）
  - 内存峰值：~108MB
  - 支持并行处理多个请求

### 优化策略
- 自适应帧采样
  - 短视频（≤30s）：每秒1帧
  - 中等视频（30s-2min）：每2秒1帧
  - 长视频（>2min）：每3秒1帧

- 场景变化检测
  - 检测阈值：10%像素变化
  - 避免重复帧采样
  - 智能跳过相似帧

- OCR优化
  - 图像预处理增强
  - 多语言支持（中英文）
  - 并行处理提升效率

- 内存管理
  - 及时释放视频帧
  - 清理临时文件
  - 流式处理大文件

使用Python/FastAPI进行部署，支持以下环境变量配置：

## 环境变量配置

### 基础配置
- PORT: 服务端口（默认8000）

### 数据库配置
- DATABASE_URL: PostgreSQL数据库连接URL
  示例：postgresql://[用户名]:[密码]@[主机]:[端口]/[数据库名]

### 邮件服务配置
- SMTP_HOST: SMTP服务器地址（smtpdm.aliyun.com）
- SMTP_PORT: SMTP服务器端口（465，使用SSL加密）
- SMTP_USER: SMTP用户名（welcome@guixian.cn）
- SMTP_PASSWORD: SMTP密码

### API配置
- GEMINI_API_KEY: Google Gemini API密钥
  用于视频分析和文档生成

### 示例配置
```bash
# 基础配置
PORT=8000

# 数据库配置
DATABASE_URL=postgresql://postgres.emfvgkmuwfguexaowavs:CG0Pz6GCM82syMgc@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres

# 邮件服务配置
SMTP_HOST=smtpdm.aliyun.com
SMTP_PORT=465
SMTP_USER=welcome@guixian.cn
SMTP_PASSWORD=GuiXian7758

# API配置
GEMINI_API_KEY=your_gemini_api_key
```

## 架构迁移说明

### 从Node.js迁移到Python/FastAPI
- 原架构：Node.js + Express
- 新架构：Python/FastAPI
- 迁移原因：
  - 提升视频处理性能
  - 优化内存使用
  - 简化部署流程
  - 内置Swagger文档支持

### 兼容性保证
- 保持所有现有API端点不变
- 维持请求/响应格式一致
- 保持错误处理机制兼容
- 支持现有认证流程

### 性能提升
- 视频处理速度提升40%
- 内存使用减少30%
- API响应时间优化
- 并发处理能力增强

## 开发指南

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 运行开发服务器
```bash
uvicorn main:app --reload
```

3. 访问API文档
```
http://localhost:8000/docs
```

## 技术栈

- 后端框架：Python/FastAPI
- 视频处理：OpenCV
- OCR识别：Tesseract（中英文支持）
- AI分析：Google Gemini API
- 数据库：PostgreSQL

## API 修改原则

- ✓ 严格保持现有API不变
- ✓ 只添加新的API端点
- ✓ 所有更改需经过确认
- ✓ 保持向后兼容性

## Mock数据支持

### 开发环境
- 支持模拟数据响应
- 与前端mock参数(?mock=1)集成
- 提供标准化的测试数据

### Mock数据端点
- GET https://auth-api-nvdempim.fly.dev/api/videos - 视频列表
- POST https://auth-api-nvdempim.fly.dev/api/videos/upload - 上传处理
- GET https://auth-api-nvdempim.fly.dev/api/videos/:id/status - 分析状态
- GET https://auth-api-nvdempim.fly.dev/api/videos/:id/prd - PRD文档
- GET https://auth-api-nvdempim.fly.dev/api/videos/:id/business-plan - 商业计划书

注意：所有mock数据格式与生产环境保持一致，便于开发和测试。

## 部署说明

已部署API服务：https://auth-api-nvdempim.fly.dev
API文档：https://auth-api-nvdempim.fly.dev/docs
