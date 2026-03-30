import os
import cv2
import mediapipe as mp
import numpy as np

from .utils import ShootingAnalyzer

mp_pose = mp.solutions.pose
lm_enum = mp_pose.PoseLandmark # Shortcut to make the arrays cleaner

# --- CONSTANTS & CONFIGURATION ---

REQUIRED_FEATURES = [
    "S_avg_knee_bend", 
    "S_max_knee_bend", 
    "S_avg_body_lean", 
    "S_max_body_lean", 
    "S_min_body_lean", 
    "S_avg_head_tilt", 
    "S_frame_count", 
    "R_avg_hip_angle", 
    "R_avg_knee_bend", 
    "R_avg_elbow_angle", 
    "R_max_wrist_height", 
    "R_avg_shoulder_angle", 
    "R_avg_head_tilt", 
    "R_avg_body_lean", 
    "R_frame_count", 
    "F_release_angle", 
    "F_elbow_above_eye", 
    "F_body_lean_angle", 
    "F_hip_angle", 
    "F_knee_angle", 
    "F_head_tilt", 
    "F_frame_count"
]

_PHASE_COLORS = {
    "Setup": (0, 0, 255),          # RED
    "Release": (0, 255, 255),      # YELLOW
    "Follow-through": (0, 255, 0), # GREEN
}
_DEFAULT_COLOR = (255, 255, 255)   # WHITE


# --- PRE-COMPUTED MEDIAPIPE INDICES ---

_DRAWING_POINTS_LEFT = [
    lm_enum.LEFT_SHOULDER.value, 
    lm_enum.LEFT_ELBOW.value, 
    lm_enum.LEFT_WRIST.value, 
    lm_enum.LEFT_INDEX.value,
    lm_enum.RIGHT_SHOULDER.value,
    lm_enum.LEFT_HIP.value, 
    lm_enum.RIGHT_HIP.value,
    lm_enum.LEFT_KNEE.value, 
    lm_enum.RIGHT_KNEE.value,
    lm_enum.LEFT_ANKLE.value, 
    lm_enum.RIGHT_ANKLE.value,
    lm_enum.LEFT_HEEL.value, 
    lm_enum.RIGHT_HEEL.value,
    lm_enum.LEFT_FOOT_INDEX.value, 
    lm_enum.RIGHT_FOOT_INDEX.value,
    lm_enum.LEFT_EYE.value, 
    lm_enum.LEFT_EAR.value
]

_DRAWING_POINTS_RIGHT = [
    lm_enum.RIGHT_SHOULDER.value, 
    lm_enum.RIGHT_ELBOW.value, 
    lm_enum.RIGHT_WRIST.value, 
    lm_enum.RIGHT_INDEX.value,
    lm_enum.LEFT_SHOULDER.value,
    lm_enum.LEFT_HIP.value, 
    lm_enum.RIGHT_HIP.value,
    lm_enum.LEFT_KNEE.value, 
    lm_enum.RIGHT_KNEE.value,
    lm_enum.LEFT_ANKLE.value, 
    lm_enum.RIGHT_ANKLE.value,
    lm_enum.LEFT_HEEL.value, 
    lm_enum.RIGHT_HEEL.value,
    lm_enum.LEFT_FOOT_INDEX.value, 
    lm_enum.RIGHT_FOOT_INDEX.value,
    lm_enum.RIGHT_EYE.value, 
    lm_enum.RIGHT_EAR.value
]

_BASE_CONNECTIONS = [
    (lm_enum.LEFT_HIP.value, lm_enum.LEFT_KNEE.value), 
    (lm_enum.LEFT_KNEE.value, lm_enum.LEFT_ANKLE.value),
    (lm_enum.LEFT_ANKLE.value, lm_enum.LEFT_HEEL.value), 
    (lm_enum.LEFT_HEEL.value, lm_enum.LEFT_FOOT_INDEX.value),
    (lm_enum.RIGHT_HIP.value, lm_enum.RIGHT_KNEE.value), 
    (lm_enum.RIGHT_KNEE.value, lm_enum.RIGHT_ANKLE.value),
    (lm_enum.RIGHT_ANKLE.value, lm_enum.RIGHT_HEEL.value), 
    (lm_enum.RIGHT_HEEL.value, lm_enum.RIGHT_FOOT_INDEX.value),
    (lm_enum.LEFT_SHOULDER.value, lm_enum.LEFT_HIP.value), 
    (lm_enum.RIGHT_SHOULDER.value, lm_enum.RIGHT_HIP.value),
    (lm_enum.LEFT_HIP.value, lm_enum.RIGHT_HIP.value), 
    (lm_enum.LEFT_SHOULDER.value, lm_enum.RIGHT_SHOULDER.value)
]

_CONNECTIONS_LEFT = _BASE_CONNECTIONS + [
    (lm_enum.LEFT_SHOULDER.value, lm_enum.LEFT_ELBOW.value), 
    (lm_enum.LEFT_ELBOW.value, lm_enum.LEFT_WRIST.value), 
    (lm_enum.LEFT_WRIST.value, lm_enum.LEFT_INDEX.value), 
    (lm_enum.LEFT_EYE.value, lm_enum.LEFT_EAR.value)
]

_CONNECTIONS_RIGHT = _BASE_CONNECTIONS + [
    (lm_enum.RIGHT_SHOULDER.value, lm_enum.RIGHT_ELBOW.value), 
    (lm_enum.RIGHT_ELBOW.value, lm_enum.RIGHT_WRIST.value), 
    (lm_enum.RIGHT_WRIST.value, lm_enum.RIGHT_INDEX.value), 
    (lm_enum.RIGHT_EYE.value, lm_enum.RIGHT_EAR.value)
]

# --- HELPER FUNCTIONS ---

def get_active_landmarks(landmarks, shooting_arm):
    """
    Gets specific shooting arm joints needed based on dominant hand.

    Returns dictionary of key joints required for analysis
    """
    l_hip, r_hip = landmarks[lm_enum.LEFT_HIP.value], landmarks[lm_enum.RIGHT_HIP.value]
    l_knee, r_knee = landmarks[lm_enum.LEFT_KNEE.value], landmarks[lm_enum.RIGHT_KNEE.value]
    l_ankle, r_ankle = landmarks[lm_enum.LEFT_ANKLE.value], landmarks[lm_enum.RIGHT_ANKLE.value]

    if shooting_arm == 'LEFT':
        return {
            "shoulder": landmarks[lm_enum.LEFT_SHOULDER.value], 
            "elbow": landmarks[lm_enum.LEFT_ELBOW.value], 
            "wrist": landmarks[lm_enum.LEFT_WRIST.value], 
            "index_finger": landmarks[lm_enum.LEFT_INDEX.value], 
            "hip": l_hip, 
            "knee": l_knee, 
            "ankle": l_ankle, 
            "eye": landmarks[lm_enum.LEFT_EYE.value], 
            "ear": landmarks[lm_enum.LEFT_EAR.value], 
            "left_hip": l_hip, 
            "right_hip": r_hip, 
            "left_knee": l_knee, 
            "right_knee": r_knee, 
            "left_ankle": l_ankle, 
            "right_ankle": r_ankle
        }
    
    return {
        "shoulder": landmarks[lm_enum.RIGHT_SHOULDER.value], 
        "elbow": landmarks[lm_enum.RIGHT_ELBOW.value], 
        "wrist": landmarks[lm_enum.RIGHT_WRIST.value], 
        "index_finger": landmarks[lm_enum.RIGHT_INDEX.value], 
        "hip": r_hip, 
        "knee": r_knee, 
        "ankle": r_ankle, 
        "eye": landmarks[lm_enum.RIGHT_EYE.value], 
        "ear": landmarks[lm_enum.RIGHT_EAR.value], 
        "left_hip": l_hip, 
        "right_hip": r_hip, 
        "left_knee": l_knee, 
        "right_knee": r_knee, 
        "left_ankle": l_ankle, 
        "right_ankle": r_ankle
    }

def calculate_all_angles(analyzer, lm):
    """
    Runs all biomechanical calculations for the current frame.
    
    Returns dictionary of all calculated angles and metrics needed for analysis.
    """
    return {
        'elbow': analyzer.calculate_angle(lm["shoulder"], lm["elbow"], lm["wrist"]),
        'shoulder': analyzer.calculate_shoulder_angle(lm["hip"], lm["shoulder"], lm["elbow"]),
        'wrist': analyzer.calculate_angle(lm["elbow"], lm["wrist"], lm["index_finger"]),
        'left_knee': analyzer.calculate_angle(lm["left_hip"], lm["left_knee"], lm["left_ankle"]),
        'right_knee': analyzer.calculate_angle(lm["right_hip"], lm["right_knee"], lm["right_ankle"]),
        'body_lean': analyzer.calculate_body_lean(lm["shoulder"], lm["hip"]),
        'hip_angle': analyzer.calculate_angle(lm["shoulder"], lm["hip"], lm["knee"]),
        'dominant_knee': analyzer.calculate_angle(lm["hip"], lm["knee"], lm["ankle"]),
        'head_tilt': analyzer.calculate_head_angle(lm["eye"], lm["ear"]),
        'forearm_alignment': analyzer.calculate_forearm_alignment(lm["elbow"], lm["wrist"]),
        'setpoint': analyzer.calculate_release_setpoint(lm["index_finger"], lm["eye"])
    }

def draw_pose_annotations(frame, landmarks, width, height, shooting_arm, color):
    """
    Draws the skeleton on the video frame using the pre-computed arrays.
    """
    pts_to_draw = _DRAWING_POINTS_LEFT if shooting_arm == "LEFT" else _DRAWING_POINTS_RIGHT
    connections = _CONNECTIONS_LEFT if shooting_arm == "LEFT" else _CONNECTIONS_RIGHT

    # Draw Nodes
    for idx in pts_to_draw:
        lm = landmarks[idx]
        x, y = int(lm.x * width), int(lm.y * height)
        cv2.circle(frame, (x, y), 3, color, -1)

    # Draw Lines
    for start_idx, end_idx in connections:
        start_lm, end_lm = landmarks[start_idx], landmarks[end_idx]
        x1, y1 = int(start_lm.x * width), int(start_lm.y * height)
        x2, y2 = int(end_lm.x * width), int(end_lm.y * height)
        cv2.line(frame, (x1, y1), (x2, y2), color, 1)


# --- MAIN ORCHESTRATOR ---

def analyse_video(input_video_path, shooting_arm):
    """
    Main function to run the video analysis pipeline on the input video.

    Returns dictionary containing all calculated metrics, file paths to processed video and key frames.
    """
    metrics = {}
    cap = cv2.VideoCapture(input_video_path)

    if not cap.isOpened():
        return {"error": f"Could not open video {input_video_path}"}
    
    target_fps = 30
    actual_fps = cap.get(cv2.CAP_PROP_FPS) or target_fps
    frame_rate_ratio = target_fps / actual_fps
    frame_skip = int(1 / frame_rate_ratio) if frame_rate_ratio < 1 else 1
    delta_t = 1 / target_fps

    # File Path Setup
    folder_path = os.path.dirname(input_video_path)
    unique_hash = os.path.basename(folder_path)
    processed_video_path = os.path.join(folder_path, f"VIDEO_{unique_hash}.mp4")
    setup_frame_path = os.path.join(folder_path, f"SETUP_{unique_hash}.png")
    release_frame_path = os.path.join(folder_path, f"RELEASE_{unique_hash}.png")
    follow_frame_path = os.path.join(folder_path, f"FOLLOW_{unique_hash}.png")

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    out = cv2.VideoWriter(processed_video_path, fourcc, target_fps, (frame_width, frame_height))

    pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
    analyzer = ShootingAnalyzer(SHOOTING_ARM=shooting_arm, delta_t=delta_t)

    first_frames = {"Setup": None, "Release": None, "Follow-through": None}
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_skip != 0:
            frame_count += 1
            continue

        # 1. crop to just shooter region
        height, width, _ = frame.shape 
        
        if shooting_arm == "RIGHT":
            crop_frame, crop_x_offset = frame[:, :width // 2], 0
        else:
            crop_frame, crop_x_offset = frame[:, width // 2:], width // 2
        
        rgb_frame = cv2.cvtColor(crop_frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)

        # 2. process landmarks
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            
            # normalize coordinates back to full-frame dimensions
            for lm in landmarks:
                lm.x = (lm.x * (width // 2) + crop_x_offset) / width

            # get landmarks and angles
            active_lm = get_active_landmarks(landmarks, shooting_arm)
            angles = calculate_all_angles(analyzer, active_lm)
            # generate subset of landmarks needed for phase detection
            tracking_subset = {k: active_lm[k] for k in ['wrist', 'eye', 'shoulder', 'hip', 'elbow', 'index_finger']}

            # detect current shooting phase
            phase = analyzer.detect_phase(angles, tracking_subset)

            # 3. update metrics state
            if analyzer.shot_ended:
                analyzer.shot_ended = False

                # store final metrics for analysis
                for phase_name, phase_metrics in analyzer.metrics.items():
                    prefix = phase_name[0] + "_"
                    for key, value in phase_metrics.items():
                        if key != 'stored' and not key.startswith('total'):
                            metrics[prefix + key] = value
            
            # 4. draw overlays
            color = _PHASE_COLORS.get(phase, _DEFAULT_COLOR)
            draw_pose_annotations(frame, landmarks, width, height, shooting_arm, color)

            # 5. get images for first frame in each phase
            if phase in first_frames and first_frames[phase] is None:
                first_frames[phase] = frame.copy()

        # write frame to output video
        out.write(frame)
        frame_count += 1

    # cleanup
    cap.release()
    pose.close()
    out.release()

    # save first frame for each phase
    if first_frames["Setup"] is not None: cv2.imwrite(setup_frame_path, first_frames["Setup"])
    if first_frames["Release"] is not None: cv2.imwrite(release_frame_path, first_frames["Release"])
    if first_frames["Follow-through"] is not None: cv2.imwrite(follow_frame_path, first_frames["Follow-through"])

    # ensure all required features are present
    for feat in REQUIRED_FEATURES:
        if feat not in metrics:
            metrics[feat] = 0.0
            print(f"Warning: Missing required feature {feat}")
        
    return {
        "metrics": metrics,
        "processed_video_path": processed_video_path,
        "setup_frame_path": setup_frame_path,
        "release_frame_path": release_frame_path,
        "follow_frame_path": follow_frame_path
    }