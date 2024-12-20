"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const video_controller_1 = require("../controllers/video.controller");
const auth_1 = require("../middleware/auth");
const upload_1 = require("../middleware/upload");
const router = (0, express_1.Router)();
// Video upload endpoint
router.post('/api/videos/upload', auth_1.auth, upload_1.uploadMiddleware, video_controller_1.videoController.upload);
// List all videos for authenticated user
router.get('/api/videos', auth_1.auth, video_controller_1.videoController.list);
// Get single video details
router.get('/api/videos/:id', auth_1.auth, video_controller_1.videoController.get);
// Get PRD document for video
router.get('/api/videos/:id/prd', auth_1.auth, video_controller_1.videoController.getPRD);
// Get business plan for video
router.get('/api/videos/:id/business-plan', auth_1.auth, video_controller_1.videoController.getBusinessPlan);
exports.default = router;
