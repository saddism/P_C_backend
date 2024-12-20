import google.generativeai as genai
import os

# Configure Google Gemini API
genai.configure(api_key='AIzaSyDBhwyLlC3jO1ek2g0UyK3lp11CO8v1alg')
model = genai.GenerativeModel('gemini-pro')

def analyze_video(video_path):
    """Extract frames from video and return list of frame paths"""
    os.makedirs('data/frames', exist_ok=True)
    frames = []
    # For testing, just return empty list since we can't process video yet
    return frames

def generate_prd(frames):
    """Generate PRD document from video frames"""
    prompt = """
    Based on the app screen recording, generate a detailed PRD document that includes:
    1. Application Overview
       - Purpose and target audience
       - Key features and functionality
    2. User Interface
       - Screen layouts and navigation flow
       - UI components and interactions
    3. Technical Requirements
       - System architecture
       - Data flow and storage
       - Integration points
    4. Testing Strategy
       - Test cases and scenarios
       - Quality assurance process
    """
    response = model.generate_content(prompt)
    return response.text

def generate_business_plan(frames):
    """Generate business plan from video frames"""
    prompt = """
    Based on the app screen recording, generate a comprehensive business plan that includes:
    1. Market Analysis
       - Target market size and demographics
       - Competitor analysis
    2. Value Proposition
       - User pain points addressed
       - Unique selling points
    3. Revenue Model
       - Pricing strategy
       - Monetization approach
    4. Marketing Strategy
       - Marketing channels
       - User acquisition plan
    5. Implementation Plan
       - Technical requirements
       - Development roadmap
    """
    response = model.generate_content(prompt)
    return response.text
