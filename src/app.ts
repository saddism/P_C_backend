import express from 'express';
import cors from 'cors';
import swaggerUi from 'swagger-ui-express';
import { specs } from './config/swagger';
import authRoutes from './routes/auth.routes';
import { createTables } from './config/database';
import dotenv from 'dotenv';

dotenv.config();

const app = express();

// 中间件
app.use(cors());
app.use(express.json());

// 初始化数据库表
createTables().catch(console.error);

// API路由
app.use('/api/auth', authRoutes);

// Swagger文档
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(specs, {
  customCss: '.swagger-ui .topbar { display: none }',
  customSiteTitle: "认证API文档",
}));

export default app;
