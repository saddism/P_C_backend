"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.videoController = void 0;
const video_model_1 = require("../models/video.model");
const analysis_model_1 = require("../models/analysis.model");
const uuid_1 = require("uuid");
exports.videoController = {
    // Upload new video
    upload: async (req, res) => {
        try {
            const { userId } = req.user;
            const file = req.file;
            if (!file) {
                res.status(400).json({ message: 'No video file provided' });
                return;
            }
            const video = await video_model_1.Video.create({
                id: (0, uuid_1.v4)(),
                userId,
                filename: file.filename,
                status: 'processing',
                prdDocument: '',
                businessPlan: ''
            });
            // Start analysis process asynchronously
            // TODO: Implement video analysis service integration
            res.status(201).json({
                message: 'Video uploaded successfully',
                videoId: video.id
            });
        }
        catch (error) {
            console.error('Error uploading video:', error);
            res.status(500).json({ message: 'Error uploading video' });
        }
    },
    // List all videos for user
    list: async (req, res) => {
        try {
            const { userId } = req.user;
            const videos = await video_model_1.Video.findAll({
                where: { userId },
                order: [['createdAt', 'DESC']]
            });
            res.json({ videos });
        }
        catch (error) {
            console.error('Error listing videos:', error);
            res.status(500).json({ message: 'Error fetching videos' });
        }
    },
    // Get single video
    get: async (req, res) => {
        try {
            const { id } = req.params;
            const { userId } = req.user;
            const video = await video_model_1.Video.findOne({
                where: { id, userId },
                include: [analysis_model_1.Analysis]
            });
            if (!video) {
                res.status(404).json({ message: 'Video not found' });
                return;
            }
            res.json({ video });
        }
        catch (error) {
            console.error('Error fetching video:', error);
            res.status(500).json({ message: 'Error fetching video details' });
        }
    },
    // Get PRD document
    getPRD: async (req, res) => {
        try {
            const { id } = req.params;
            const { userId } = req.user;
            const video = await video_model_1.Video.findOne({
                where: { id, userId },
                attributes: ['prdDocument']
            });
            if (!video) {
                res.status(404).json({ message: 'PRD not found' });
                return;
            }
            res.json({ prd: video.prdDocument });
        }
        catch (error) {
            console.error('Error fetching PRD:', error);
            res.status(500).json({ message: 'Error fetching PRD' });
        }
    },
    // Get business plan
    getBusinessPlan: async (req, res) => {
        try {
            const { id } = req.params;
            const { userId } = req.user;
            const video = await video_model_1.Video.findOne({
                where: { id, userId },
                attributes: ['businessPlan']
            });
            if (!video) {
                res.status(404).json({ message: 'Business plan not found' });
                return;
            }
            res.json({ businessPlan: video.businessPlan });
        }
        catch (error) {
            console.error('Error fetching business plan:', error);
            res.status(500).json({ message: 'Error fetching business plan' });
        }
    }
};
