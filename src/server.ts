import app from './app';
import dotenv from 'dotenv';

dotenv.config();

const port = process.env.PORT || 3000;

app.listen(port, () => {
  console.log(`服务器运行在 http://localhost:${port}`);
  console.log(`API文档地址: http://localhost:${port}/api-docs`);
});
