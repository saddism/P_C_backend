"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.analysisService = exports.AnalysisService = void 0;
const generative_ai_1 = require("@google/generative-ai");
const ffmpeg_extract_frames_1 = __importDefault(require("ffmpeg-extract-frames"));
const tesseract_js_1 = require("tesseract.js");
const video_model_1 = __importDefault(require("../models/video.model"));
const analysis_model_1 = __importDefault(require("../models/analysis.model"));
const path_1 = __importDefault(require("path"));
const promises_1 = __importDefault(require("fs/promises"));
const GEMINI_API_KEY = 'AIzaSyDBhwyLlC3jO1ek2g0UyK3lp11CO8v1alg';
const genAI = new generative_ai_1.GoogleGenerativeAI(GEMINI_API_KEY);
class AnalysisService {
    async extractVideoFrames(videoPath) {
        const outputDir = path_1.default.join('uploads', 'frames');
        await promises_1.default.mkdir(outputDir, { recursive: true });
        // Extract one frame every 2 seconds
        await (0, ffmpeg_extract_frames_1.default)({
            input: videoPath,
            output: path_1.default.join(outputDir, 'frame-%d.jpg'),
            offsets: [0, 2000, 4000, 6000, 8000]
        });
        const frames = await promises_1.default.readdir(outputDir);
        return frames.map(frame => path_1.default.join(outputDir, frame));
    }
    async performOCR(imagePaths) {
        const worker = await (0, tesseract_js_1.createWorker)();
        const results = [];
        for (const imagePath of imagePaths) {
            const { data: { text } } = await worker.recognize(imagePath);
            results.push(text);
        }
        await worker.terminate();
        return results;
    }
    async generatePRD(ocrText, features) {
        const model = genAI.getGenerativeModel({ model: 'gemini-pro' });
        const prompt = `Based on the following app screen text and features, generate a detailed PRD document in markdown format:

Screen Text:
${ocrText.join('\n')}

Features:
${features.join('\n')}

The PRD should include:
1. Application Positioning
2. Target Audience
3. Navigation Structure
4. Interface Screenshots (reference the analyzed screens)
5. Technical Implementation
6. Data Flow
7. Test Plan

Format the output as a proper markdown document with sections and subsections.`;
        const result = await model.generateContent(prompt);
        const response = await result.response;
        return response.text();
    }
    async generateBusinessPlan(ocrText, features) {
        const model = genAI.getGenerativeModel({ model: 'gemini-pro' });
        const prompt = `Based on the following app screen text and features, generate a comprehensive business plan in markdown format:

Screen Text:
${ocrText.join('\n')}

Features:
${features.join('\n')}

The business plan should include:
1. Market Positioning
2. User Personas
3. Problem Solution
4. Revenue Model
5. Competitor Analysis
6. Marketing Strategy

Format the output as a proper markdown document with sections and subsections.`;
        const result = await model.generateContent(prompt);
        const response = await result.response;
        return response.text();
    }
    async analyzeFeatures(ocrText) {
        const model = genAI.getGenerativeModel({ model: 'gemini-pro' });
        const prompt = `Analyze the following app screen text and identify key features and user flows:

${ocrText.join('\n')}

List the main features and functionality you can identify.`;
        const result = await model.generateContent(prompt);
        const response = await result.response;
        return response.text().split('\n').filter(line => line.trim());
    }
    async analyzeVideo(videoId) {
        try {
            const video = await video_model_1.default.findByPk(videoId);
            if (!video)
                throw new Error('Video not found');
            // Extract frames from video
            const frames = await this.extractVideoFrames(video.filename);
            // Perform OCR on frames
            const ocrText = await this.performOCR(frames);
            // Analyze features
            const features = await this.analyzeFeatures(ocrText);
            // Generate PRD and Business Plan
            const [prdDocument, businessPlan] = await Promise.all([
                this.generatePRD(ocrText, features),
                this.generateBusinessPlan(ocrText, features)
            ]);
            // Save analysis results
            await analysis_model_1.default.create({
                videoId,
                frames,
                ocrText,
                features,
                userFlow: features // Using features as user flow for now
            });
            // Update video with documents
            await video.update({
                status: 'completed',
                prdDocument,
                businessPlan
            });
            // Clean up frames
            for (const frame of frames) {
                await promises_1.default.unlink(frame);
            }
            await promises_1.default.rmdir(path_1.default.join('uploads', 'frames'));
        }
        catch (error) {
            console.error('Error analyzing video:', error);
            await video_model_1.default.update({ status: 'failed' }, { where: { id: videoId } });
            throw error;
        }
    }
}
exports.AnalysisService = AnalysisService;
exports.analysisService = new AnalysisService();
