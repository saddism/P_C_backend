import { GoogleGenerativeAI } from '@google/generative-ai';
import extractFrames from 'ffmpeg-extract-frames';
import { createWorker } from 'tesseract.js';
import Video from '../models/video.model';
import Analysis from '../models/analysis.model';
import path from 'path';
import fs from 'fs/promises';

const GEMINI_API_KEY = 'AIzaSyDBhwyLlC3jO1ek2g0UyK3lp11CO8v1alg';
const genAI = new GoogleGenerativeAI(GEMINI_API_KEY);

export class AnalysisService {
  private async extractVideoFrames(videoPath: string): Promise<string[]> {
    const outputDir = path.join('uploads', 'frames');
    await fs.mkdir(outputDir, { recursive: true });

    // Extract one frame every 2 seconds
    await extractFrames({
      input: videoPath,
      output: path.join(outputDir, 'frame-%d.jpg'),
      offsets: [0, 2000, 4000, 6000, 8000]
    });

    const frames = await fs.readdir(outputDir);
    return frames.map(frame => path.join(outputDir, frame));
  }

  private async performOCR(imagePaths: string[]): Promise<string[]> {
    const worker = await createWorker();
    const results: string[] = [];

    for (const imagePath of imagePaths) {
      const { data: { text } } = await worker.recognize(imagePath);
      results.push(text);
    }

    await worker.terminate();
    return results;
  }

  private async generatePRD(ocrText: string[], features: string[]): Promise<string> {
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

  private async generateBusinessPlan(ocrText: string[], features: string[]): Promise<string> {
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

  private async analyzeFeatures(ocrText: string[]): Promise<string[]> {
    const model = genAI.getGenerativeModel({ model: 'gemini-pro' });

    const prompt = `Analyze the following app screen text and identify key features and user flows:

${ocrText.join('\n')}

List the main features and functionality you can identify.`;

    const result = await model.generateContent(prompt);
    const response = await result.response;
    return response.text().split('\n').filter(line => line.trim());
  }

  public async analyzeVideo(videoId: string): Promise<void> {
    try {
      const video = await Video.findByPk(videoId);
      if (!video) throw new Error('Video not found');

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
      await Analysis.create({
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
        await fs.unlink(frame);
      }
      await fs.rmdir(path.join('uploads', 'frames'));

    } catch (error) {
      console.error('Error analyzing video:', error);
      await Video.update(
        { status: 'failed' },
        { where: { id: videoId } }
      );
      throw error;
    }
  }
}

export const analysisService = new AnalysisService();
