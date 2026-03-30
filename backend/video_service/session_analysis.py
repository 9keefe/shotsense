import json
import os
import uuid
from datetime import datetime, timezone

import cv2
import mediapipe as mp

from db_schema import Session as VideoSession, ShotAnalysis, db
from .analysis import analyse_video
from .config import BASE_URL, VIDEO_FOLDER
from .scoring import get_model_feedback, parse_all_metrics
from .utils import ShootingAnalyzer

mp_pose = mp.solutions.pose

# --- CONFIGURATION & CONSTANTS ---
TARGET_FPS = 30
START_PADDING = 20
END_PADDING = 30
MIN_SHOT_FRAMES = 30
MAX_SHOT_FRAMES = 200
MIN_GAP_BETWEEN_SHOTS = 60

os.makedirs(VIDEO_FOLDER, exist_ok=True)

# --- HELPER FUNCTIONS: PATHS & URLS ---

def create_session_folder(user_id, session_hash):
    folder_path = os.path.join(VIDEO_FOLDER, str(user_id), "sessions", session_hash)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def create_shot_folder(user_id, session_hash, shot_index):
    folder_path = os.path.join(VIDEO_FOLDER, str(user_id), "sessions", session_hash, "shots", f"shot_{shot_index}")
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def build_session_base_url(user_id, session_hash):
    return f"{BASE_URL}/videos/{user_id}/sessions/{session_hash}/"

def build_shot_base_url(user_id, session_hash, shot_index):
    return f"{BASE_URL}/videos/{user_id}/sessions/{session_hash}/shots/shot_{shot_index}/"


# --- HELPER FUNCTIONS: MATH & MEDIAPIPE ---

_LANDMARK_MAP_LEFT = {
    "shoulder": mp_pose.PoseLandmark.LEFT_SHOULDER.value,
    "elbow": mp_pose.PoseLandmark.LEFT_ELBOW.value,
    "wrist": mp_pose.PoseLandmark.LEFT_WRIST.value,
    "index_finger": mp_pose.PoseLandmark.LEFT_INDEX.value,
    "hip": mp_pose.PoseLandmark.LEFT_HIP.value,
    "knee": mp_pose.PoseLandmark.LEFT_KNEE.value,
    "ankle": mp_pose.PoseLandmark.LEFT_ANKLE.value,
    "eye": mp_pose.PoseLandmark.LEFT_EYE.value,
    "ear": mp_pose.PoseLandmark.LEFT_EAR.value,
}

_LANDMARK_MAP_RIGHT = {
    "shoulder": mp_pose.PoseLandmark.RIGHT_SHOULDER.value,
    "elbow": mp_pose.PoseLandmark.RIGHT_ELBOW.value,
    "wrist": mp_pose.PoseLandmark.RIGHT_WRIST.value,
    "index_finger": mp_pose.PoseLandmark.RIGHT_INDEX.value,
    "hip": mp_pose.PoseLandmark.RIGHT_HIP.value,
    "knee": mp_pose.PoseLandmark.RIGHT_KNEE.value,
    "ankle": mp_pose.PoseLandmark.RIGHT_ANKLE.value,
    "eye": mp_pose.PoseLandmark.RIGHT_EYE.value,
    "ear": mp_pose.PoseLandmark.RIGHT_EAR.value,
}

def get_shooting_side_landmarks(landmarks, shooting_arm):
    """
    Get only the joints needed whether the shooter is left or right-handed
    
    Returns simplified dict of key landmarks with actual coordinates
    """
    active_map = _LANDMARK_MAP_LEFT if shooting_arm == ShootingAnalyzer.ARM_LEFT else _LANDMARK_MAP_RIGHT
    # We only do the extraction here, no dictionary building!
    return {key: landmarks[idx] for key, idx in active_map.items()}

def build_angles(analyzer, side_landmarks):
    """
    Calculates all the biomechanical angles needed for the shot analysis
    
    Returns map of metric to value
    """
    sl = side_landmarks # shortened
    return {
        "elbow": analyzer.calculate_angle(sl["shoulder"], sl["elbow"], sl["wrist"]),
        "shoulder": analyzer.calculate_shoulder_angle(sl["hip"], sl["shoulder"], sl["elbow"]),
        "wrist": analyzer.calculate_angle(sl["elbow"], sl["wrist"], sl["index_finger"]),
        "body_lean": analyzer.calculate_body_lean(sl["shoulder"], sl["hip"]),
        "hip_angle": analyzer.calculate_angle(sl["shoulder"], sl["hip"], sl["knee"]),
        "dominant_knee": analyzer.calculate_angle(sl["hip"], sl["knee"], sl["ankle"]),
        "head_tilt": analyzer.calculate_head_angle(sl["eye"], sl["ear"]),
        "forearm_alignment": analyzer.calculate_forearm_alignment(sl["elbow"], sl["wrist"]),
        "setpoint": analyzer.calculate_release_setpoint(sl["index_finger"], sl["eye"]),
    }


# --- CORE DETECTION LOGIC ---

class MultiShotDetector(ShootingAnalyzer):
    """
    Track movement frame-by-frame to isolate individual shots from a continuous video.
    We use same logic as ShootingAnalyzer to detect phases, but add state to track when a shot starts and ends.
    """
    ACTIVE_PHASES = {
        ShootingAnalyzer.PHASE_SETUP,
        ShootingAnalyzer.PHASE_RELEASE,
        ShootingAnalyzer.PHASE_FOLLOW_THROUGH,
    }

    def __init__(self, shooting_arm="RIGHT", start_padding=START_PADDING, end_padding=END_PADDING, delta_t=1 / TARGET_FPS):
        super().__init__(SHOOTING_ARM=shooting_arm, delta_t=delta_t)
        self.start_padding = start_padding
        self.end_padding = end_padding
        # array to store detected shots with start and end frames
        self.shots = []
        self.current_shot_start = None

    def _is_valid_shot_window(self, shot_window):
        """
        Safeguard: Ensures detected window is a valid a shot.
        
        Returns True if shot window is valid, False otherwise.
        """
        shot_length = shot_window["end_frame"] - shot_window["start_frame"] + 1

        if not (MIN_SHOT_FRAMES <= shot_length <= MAX_SHOT_FRAMES):
            return False

        if self.shots:
            previous_shot = self.shots[-1]
            gap_between_shots = shot_window["start_frame"] - previous_shot["end_frame"]
            if gap_between_shots < MIN_GAP_BETWEEN_SHOTS:
                return False

        return True

    def reset_for_next_shot(self):
        """
        Resets state trackers to prepare for new shot, preserving historical data.
        """
        # Calling super().__init__ to reset parent's tracking logic without destroying child properties.
        super().__init__(SHOOTING_ARM=self.SHOOTING_ARM, delta_t=self.delta_t)
        self.current_shot_start = None

    def update(self, frame_index, angles, landmarks):
        """
        Main update function called for each frame. Detects phase and tracks shot start/end.
        
        Returns detected phase (Start/End) for the current frame.
        """
        previous_phase = self.current_phase
        phase = self.detect_phase(angles, landmarks)

        # Detect shot start
        if self.current_shot_start is None and previous_phase == self.PHASE_NULL and phase in self.ACTIVE_PHASES:
            self.current_shot_start = frame_index

        # Detect shot end
        if self.shot_ended:
            detected_start = self.current_shot_start if self.current_shot_start is not None else frame_index
            candidate_shot = {
                "shot_index": len(self.shots) + 1,
                "start_frame": max(0, detected_start - self.start_padding),
                "end_frame": frame_index + self.end_padding,
            }

			# check if detected shot is valid, if so add to list
            if self._is_valid_shot_window(candidate_shot):
                self.shots.append(candidate_shot)

            self.reset_for_next_shot()

        return phase


# --- FULL VIDEO PROCESSING PIPELINE ---

def save_session_upload(file, user_id):
    if file.filename == "":
        return None, None

    session_hash = uuid.uuid4().hex
    session_folder_path = create_session_folder(user_id, session_hash)
    
    original_path = os.path.join(session_folder_path, f"ORIGINAL_{session_hash}.mp4")
    file.save(original_path)

    return original_path, session_hash

def get_video_total_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open uploaded session video: {video_path}")
    try:
        return int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    finally:
        cap.release()

def detect_shots(video_path, shooting_arm="RIGHT", start_padding=START_PADDING, end_padding=END_PADDING):
    """
    Scans full video, processes poses, and returns a list of valid shot timestamps.

    Returns list of detected shots with start and end frames
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    actual_fps = cap.get(cv2.CAP_PROP_FPS) or TARGET_FPS
    frame_rate_ratio = TARGET_FPS / actual_fps
    frame_skip = int(1 / frame_rate_ratio) if frame_rate_ratio < 1 else 1

    detector = MultiShotDetector(shooting_arm=shooting_arm, start_padding=start_padding, end_padding=end_padding, delta_t=1/TARGET_FPS)
    pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)

    frame_index = 0

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_index % frame_skip == 0:
                _, width, _ = frame.shape

                # crop to focus on the active shooting arm side
                if shooting_arm == ShootingAnalyzer.ARM_RIGHT:
                    crop_frame, crop_x_offset = frame[:, : width // 2], 0
                else:
                    crop_frame, crop_x_offset = frame[:, width // 2 :], width // 2

                rgb_frame = cv2.cvtColor(crop_frame, cv2.COLOR_BGR2RGB)
                results = pose.process(rgb_frame)

                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark
                    # normalize landmarks back to full frame dimensions
                    for lm in landmarks:
                        lm.x = ((lm.x * (width // 2)) + crop_x_offset) / width

                    side_landmarks = get_shooting_side_landmarks(landmarks, detector.SHOOTING_ARM)
                    angles = build_angles(detector, side_landmarks)

                    # sub-selection needed by the tracking algorithm
                    tracking_landmarks = {
                        "wrist": side_landmarks["wrist"],
                        "eye": side_landmarks["eye"],
                        "shoulder": side_landmarks["shoulder"],
                        "hip": side_landmarks["hip"],
                        "elbow": side_landmarks["elbow"],
                        "index_finger": side_landmarks["index_finger"],
                    }
                    detector.update(frame_index, angles, tracking_landmarks)

            frame_index += 1
    finally:
        cap.release()
        pose.close()

    return detector.shots

def extract_frame_range_to_video(input_path, output_path, start_frame, end_frame):
    """
    Crop video into a smaller clip based on start and end frames and saves.

	Returns path to the saved clip.
    """
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video for clip extraction: {input_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or TARGET_FPS
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # ensure valid frame range
    start_frame = max(0, start_frame)
    end_frame = min(end_frame, max(0, total_frames - 1))
    if end_frame < start_frame:
        cap.release()
        raise ValueError(f"Invalid frame range: start={start_frame}, end={end_frame}")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    current_frame = start_frame

    try:
        while current_frame <= end_frame:
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
            current_frame += 1
    finally:
        cap.release()
        out.release()

    return output_path


# --- MAIN ENTRY POINTS ---

def process_session_upload(file, user_id, shooting_arm="RIGHT"):
    """
    Main Orchestrator: Saves file, initializes DB, detects shots, and spawns processing for each shot.
    """
    original_file_path, session_hash = save_session_upload(file, user_id)
    if not original_file_path:
        raise ValueError("Failed to save session upload")

    # create url to store original video
    session_url = f"{build_session_base_url(user_id, session_hash)}ORIGINAL_{session_hash}.mp4"
    
	# create initial record for session
    session_record = VideoSession(
        user_id=user_id,
        hashed_filename=session_hash,
        shooting_arm=shooting_arm,
        status="processing",
        original_video_url=session_url,
        shot_count=0,
        total_frames=get_video_total_frames(original_file_path),
        created_at=datetime.now(timezone.utc),
    )
    db.session.add(session_record)
    db.session.commit()

    try:
        # detect shots and process each one
        detected_shots = detect_shots(original_file_path, shooting_arm=shooting_arm)
        
        for shot in detected_shots:
            shot_record = process_detected_shot(session_record, original_file_path, session_hash, user_id, shot, shooting_arm)
            db.session.add(shot_record)
        
		# update session record with final shot count and set status to complete
        session_record.shot_count = len(detected_shots)
        session_record.status = "complete"
        
        db.session.commit()
        return session_record

    except Exception as e:
        db.session.rollback()
        session_record.status = "failed"
        session_record.processing_error = str(e)
        db.session.commit()
        raise

def process_detected_shot(session_record, full_video_path, session_hash, user_id, shot, shooting_arm):
    """
    Sub-Orchestrator: Perform analysis on a single detected shot and saves results to DB.
    """
    shot_index = shot["shot_index"]
    shot_folder_path = create_shot_folder(user_id, session_hash, shot_index)
    shot_folder_name = os.path.basename(shot_folder_path)

    original_clip_filename = f"ORIGINAL_{shot_folder_name}.mp4"
    original_clip_path = os.path.join(shot_folder_path, original_clip_filename)

    # 1. get clip
    extract_frame_range_to_video(full_video_path, original_clip_path, shot["start_frame"], shot["end_frame"])

    # 2. run form analysis 
    analysis_results = analyse_video(original_clip_path, shooting_arm=shooting_arm)
    if "error" in analysis_results:
        raise ValueError(analysis_results["error"])

    # 3. parse metrics and get model feedback
    metrics = analysis_results.get("metrics", {})
    parsed_metrics = parse_all_metrics(metrics)
    probability, feedback = get_model_feedback(metrics)

    if probability is None:
        raise ValueError(f"Model prediction failed for shot {shot_index}")

    shot_base_url = build_shot_base_url(user_id, session_hash, shot_index)

    # 4. Create and return the DB record for individual shot analysis
    return ShotAnalysis(
        session_id=session_record.id,
        shot_index=shot_index,
        start_frame=shot["start_frame"],
        end_frame=shot["end_frame"],
        created_at=datetime.now(timezone.utc),
        metrics_json=json.dumps(parsed_metrics),
        make_probability=float(probability),
        form_feedback_json=json.dumps(feedback, default=str),
        video_url=f"{shot_base_url}VIDEO_{shot_folder_name}.mp4",
        original_video_url=f"{shot_base_url}{original_clip_filename}",
        setup_frame_url=f"{shot_base_url}SETUP_{shot_folder_name}.png",
        release_frame_url=f"{shot_base_url}RELEASE_{shot_folder_name}.png",
        follow_frame_url=f"{shot_base_url}FOLLOW_{shot_folder_name}.png",
    )
