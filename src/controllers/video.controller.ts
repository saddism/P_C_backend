import { Request, Response } from 'express';
import Video from '../models/video.model';
import Analysis from '../models/analysis.model';

export const videoController = {
  // Upload new video
  upload: async (req: Request, res: Response) => {
    try {
      const { userId } = req.user as { userId: string };
      const file = req.file;

      if (!file) {
        return res.status(400).json({ message: 'No video file provided' });
      }

      const video = await Video.create({
        userId,
        filename: file.filename,
        status: 'processing'
      });

      // Start analysis process asynchronously
      // TODO: Implement video analysis service integration

      return res.status(201).json({
        message: 'Video uploaded successfully',
        videoId: video.id
      });
    } catch (error) {
      console.error('Error uploading video:', error);
      return res.status(500).json({ message: 'Error uploading video' });
    }
  },

  // List all videos for user
  list: async (req: Request, res: Response) => {
    try {
      const { userId } = req.user as { userId: string };

      const videos = await Video.findAll({
        where: { userId },
        order: [['createdAt', 'DESC']]
      });

      return res.json({ videos });
    } catch (error) {
      console.error('Error listing videos:', error);
      return res.status(500).json({ message: 'Error fetching videos' });
    }
  },

  // Get single video
  get: async (req: Request, res: Response) => {
    try {
      const { id } = req.params;
      const { userId } = req.user as { userId: string };

      const video = await Video.findOne({
        where: { id, userId },
        include: [Analysis]
      });

      if (!video) {
        return res.status(404).json({ message: 'Video not found' });
      }

      return res.json({ video });
    } catch (error) {
      console.error('Error fetching video:', error);
      return res.status(500).json({ message: 'Error fetching video details' });
    }
  },

  // Get PRD document
  getPRD: async (req: Request, res: Response) => {
    try {
      const { id } = req.params;
      const { userId } = req.user as { userId: string };

      const video = await Video.findOne({
        where: { id, userId },
        attributes: ['prdDocument']
      });

      if (!video) {
        return res.status(404).json({ message: 'PRD not found' });
      }

      return res.json({ prd: video.prdDocument });
    } catch (error) {
      console.error('Error fetching PRD:', error);
      return res.status(500).json({ message: 'Error fetching PRD' });
    }
  },

  // Get business plan
  getBusinessPlan: async (req: Request, res: Response) => {
    try {
      const { id } = req.params;
      const { userId } = req.user as { userId: string };

      const video = await Video.findOne({
        where: { id, userId },
        attributes: ['businessPlan']
      });

      if (!video) {
        return res.status(404).json({ message: 'Business plan not found' });
      }

      return res.json({ businessPlan: video.businessPlan });
    } catch (error) {
      console.error('Error fetching business plan:', error);
      return res.status(500).json({ message: 'Error fetching business plan' });
    }
  }
};
