import os
import cv2
import mediapipe as mp
import numpy as np

from .utils import ShootingAnalyzer

mp_pose = mp.solutions.pose

REQUIRED_FEATURES = [
  "S_avg_knee_bend",
  "S_max_knee_bend",
  "S_avg_body_lean",
  "S_max_body_lean",
  "S_min_body_lean",
  "S_frame_count",
  "R_avg_hip_angle",
  "R_avg_knee_bend",
  "R_avg_elbow_angle",
  "R_max_wrist_height",
  "R_avg_knee_velocity",
  "R_frame_count",
  "F_release_angle",
  "F_elbow_above_eye",
  "F_body_lean_angle",
  "F_hip_angle",
  "F_knee_angle",
]

def analyse_video(input_video_path, shooting_arm):
  metrics = {}

  # open video
  cap = cv2.VideoCapture(input_video_path)

  if not cap.isOpened():
    return {"error": f"Could not open video {input_video_path}"}
  
  target_fps=30
  actual_fps=cap.get(cv2.CAP_PROP_FPS) or target_fps
  frame_rate_ratio = target_fps/actual_fps
  delta_t = 1 / target_fps

  frame_skip = int(1 / frame_rate_ratio) if frame_rate_ratio < 1 else 1
  frame_count = 0

  # initialise pose
  pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
  )

  analyzer = ShootingAnalyzer(SHOOTING_ARM=shooting_arm, delta_t=delta_t)

  while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
      break

    if frame_count % frame_skip == 0:
      height, width, _ = frame.shape

      if shooting_arm == "RIGHT":
        crop_frame = frame[:, :width // 2]
        crop_x_offset = 0
      else:
        crop_frame = frame[:, width // 2:]
        crop_x_offset = width // 2
      
      rgb_frame = cv2.cvtColor(crop_frame, cv2.COLOR_BGR2RGB)
      results = pose.process(rgb_frame)

      if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        for lm in landmarks:
          lm.x = (lm.x * (width // 2) + crop_x_offset) / width
          lm.y = lm.y
          lm.z = lm.z
        
        # Select landmarks based on shooting arm
        if analyzer.SHOOTING_ARM == 'LEFT':
          shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
          elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
          wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
          index_finger = landmarks[mp_pose.PoseLandmark.LEFT_INDEX.value]
          hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
          knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
          ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
          eye = landmarks[mp_pose.PoseLandmark.LEFT_EYE.value]
          foot = landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value]
        else:
          shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
          elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
          wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
          index_finger = landmarks[mp_pose.PoseLandmark.RIGHT_INDEX.value]
          hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
          knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
          ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
          eye = landmarks[mp_pose.PoseLandmark.RIGHT_EYE.value]
          foot = landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value]
        
        # Both knees and hips
        left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
        right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
        left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
        right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]

        # Calculate angles
        elbow_angle = analyzer.calculate_angle(shoulder, elbow, wrist)
        shoulder_angle = analyzer.calculate_shoulder_angle(hip, shoulder, elbow)
        wrist_angle = analyzer.calculate_angle(elbow, wrist, index_finger)
        left_knee_angle = analyzer.calculate_angle(left_hip, left_knee, left_ankle)
        right_knee_angle = analyzer.calculate_angle(right_hip, right_knee, right_ankle)
        body_angle = analyzer.calculate_body_lean(shoulder, hip)
        hip_angle = analyzer.calculate_angle(shoulder, hip, knee)
        knee_angle = analyzer.calculate_angle(hip, knee, ankle)

        angles = {
          'elbow': elbow_angle,
          'shoulder': shoulder_angle,
          'wrist': wrist_angle,
          'left_knee': left_knee_angle,
          'right_knee': right_knee_angle,
          'body_lean': body_angle,
          'hip_angle': hip_angle,
          'dominant_knee': knee_angle
        }
        
        landmarks_dict = {
          'wrist': wrist,
          'eye': eye,
          'shoulder': shoulder,
          'hip': hip,
          'elbow': elbow
        }

        phase = analyzer.detect_phase(angles, landmarks_dict)

        if analyzer.shot_ended:
          analyzer.shot_ended = False

          for phase_name, phase_metrics in analyzer.metrics.items():
            prefix = phase_name[0] + "_"
            for key, value in phase_metrics.items():
              if key != 'stored' and not key.startswith('total'):
                key = prefix+key
                metrics[key] = value
    
    frame_count += 1

  cap.release()
  pose.close()

  for feat in REQUIRED_FEATURES:
    if feat not in metrics:
      metrics[feat] = 0.0
      print(f"Warning: Missing required feature {feat}")
      
  return metrics
