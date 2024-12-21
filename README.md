# P_C Backend

## 技术框架
本项目使用 Python/FastAPI 构建后端 RESTful API 服务，主要技术栈包括：

- **后端框架**：Python + FastAPI
- **数据库**：PostgreSQL (Supabase)
- **API文档**：Swagger/OpenAPI
- **邮件服务**：阿里云邮件推送服务
- **部署平台**：fly.dev

## API文档
- API文档地址：https://auth-api-nvdempim.fly.dev/docs
- 后端服务地址：https://auth-api-nvdempim.fly.dev

## 主要功能
- 用户注册与邮箱验证
- 用户登录与认证
- JWT token 认证
- 邮件验证码发送

## 开发环境配置
1. Python 3.12+
2. Poetry（包管理工具）
3. PostgreSQL

## 项目结构
```
fastapi_app/
├── app/
│   ├── main.py          # FastAPI 应用入口
│   ├── models.py        # 数据模型
│   ├── database.py      # 数据库配置
│   ├── services/        # 服务层
│   │   └── email.py     # 邮件服务
│   └── routers/         # 路由
│       └── auth.py      # 认证相关路由
└── pyproject.toml       # 项目依赖配置
```

## 部署说明
项目使用 fly.dev 进行部署，提供稳定的API服务和文档访问地址。部署后的服务地址保持不变，便于前端开发和接口调用。
