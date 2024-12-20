import { Router } from 'express';
import { videoController } from '../controllers/video.controller';
import { auth } from '../middleware/auth';
import { uploadMiddleware } from '../middleware/upload';

const router = Router();

// Video upload endpoint
router.post('/api/videos/upload', auth, uploadMiddleware, videoController.upload);

// List all videos for authenticated user
router.get('/api/videos', auth, videoController.list);

// Get single video details
router.get('/api/videos/:id', auth, videoController.get);

// Get PRD document for video
router.get('/api/videos/:id/prd', auth, videoController.getPRD);

// Get business plan for video
router.get('/api/videos/:id/business-plan', auth, videoController.getBusinessPlan);

export default router;
