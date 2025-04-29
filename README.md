# Basketball Shooting Form Analysis System

This repository contains the full pipeline implementation for an AI-powered basketball shooting form analysis system. It includes pose estimation, motion phase segmentation, biomechanical metric extraction, and personalised feedback generation — all integrated into a lightweight web application.

---

## System Overview

The system consists of five major components:

1. **Pose Estimation**

   - Framework: MediaPipe BlazePose
   - Output: 2D body landmarks (33 keypoints)

2. **Phase Segmentation**

   - Methods: Rule-Based System (main), LSTM-based model (experimental)
   - Phases: Setup → Release → Follow-through

3. **Biomechanical Feature Extraction**

   - Joint angles, sequencing metrics, and phase-specific features
   - Based on sagittal plane (side-on) view

4. **Feedback Generation**

   - Rule-based evaluation using deviation from optimal biomechanical thresholds
   - ML-based shot scoring (0–10) via Random Forest

5. **Web Application**
   - Frontend: React.js + TailwindCSS
   - Backend: Flask API
   - Output: Phase-specific feedback, score, visual skeleton overlay
