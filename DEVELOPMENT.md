# 开发指南

## 技术栈说明
本项目采用 Python/FastAPI 框架开发，相比原先的 Node.js/Express 实现，具有以下优势：

1. 更简洁的API实现
2. 自动生成的API文档
3. 内置的请求验证
4. 更好的类型提示
5. 更简单的部署流程

## 部署流程
1. 使用 fly.dev 进行部署
2. 部署后获得固定的API地址
3. API文档自动更新
4. 支持自动化部署

## 开发规范
1. 使用 Poetry 管理依赖
2. 遵循 PEP 8 代码规范
3. 使用 Pydantic 进行数据验证
4. 保持API文档及时更新

## 环境变量
- DATABASE_URL: PostgreSQL数据库连接
- SMTP配置：阿里云邮件服务
- JWT配置：认证相关

## API文档
所有API都通过 Swagger/OpenAPI 文档化，访问地址：
https://auth-api-nvdempim.fly.dev/docs
