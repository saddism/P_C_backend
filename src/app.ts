import express from 'express';
import videoRoutes from './routes/video.routes';
import { sequelize } from './config/database';

const app = express();
const port = process.env.PORT || 3000;

app.use(express.json());
app.use('/api', videoRoutes);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Sync database and start server
sequelize.sync().then(() => {
  app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
  });
}).catch(err => {
  console.error('Unable to connect to the database:', err);
});

export default app;
