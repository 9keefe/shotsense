import os
import uuid
import pandas as pd
import numpy as np
import joblib
import json
import shap
from datetime import datetime
from flask import jsonify, request, send_from_directory, session
from db_schema import db, Analysis, Session as VideoSession, ShotAnalysis
from .analysis import analyse_video
from .session_analysis import VIDEO_FOLDER as SESSION_VIDEO_FOLDER, process_session_upload
from .config import OPT_SETTINGS, FEEDBACK_MESSAGES, FEEDBACK_COLS


# BASE_URL = "http://172.25.12.159:8080"
BASE_URL = "http://127.0.0.1:8080"

VIDEO_FOLDER = os.path.join(os.path.dirname(__file__), "videos")
os.makedirs(VIDEO_FOLDER, exist_ok=True)

MODEL_FOLDER = os.path.join(os.path.dirname(__file__), "model")

MODEL_FORM = joblib.load(os.path.join(MODEL_FOLDER, "model_form_6_scale.pkl"))
OPT_COLS = joblib.load(os.path.join(MODEL_FOLDER, "opt_cols_v3.pkl"))
ORIG_COLS  = [
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
ALL_OPT_COLS = joblib.load(os.path.join(MODEL_FOLDER, "all_opt_cols.pkl"))


# ==================
# ROUTES / ENDPOINTS
# ==================
def upload_video():
  if "user_id" not in session:
    return jsonify({"error": "Unauthorized"}), 401

  if "video" not in request.files:
    return jsonify({"error": "No video file found"}), 400
  
  file = request.files["video"]
  if file.filename == "":
    return jsonify({"error": "Empty filename"}), 400
  
  # get shooting arm
  shooting_arm = request.form.get("shootingArm", "RIGHT")

  # save uploaded video
  original_file_path, unique_hash = save_uploaded_file(file, VIDEO_FOLDER)
  if not original_file_path:
    return jsonify({"error": "Failed to save file"}), 500

  # analyse video
  try:
    analysis_results = analyse_video(original_file_path, shooting_arm=shooting_arm)
    metrics = analysis_results.get("metrics", {})
    parsed_metrics = parse_all_metrics(metrics)
    processed_video_path = analysis_results.get("processed_video_path")
    setup_frame_path = analysis_results.get("setup_frame_path")
    release_frame_path = analysis_results.get("release_frame_path")
    follow_frame_path = analysis_results.get("follow_frame_path")

    probability, feedback = get_model_feedback(metrics)
    make_probability = float(probability)
    form_feedback = json.dumps(feedback, default=str)

    if probability is None:
      raise ValueError("Model prediction failed")
    base_url = f"{BASE_URL}/videos/{session['user_id']}/{unique_hash}/"

    # create new db record
    new_analysis = Analysis(
      user_id = session["user_id"],
      hashed_filename = unique_hash,
      metrics_json = json.dumps(parsed_metrics),
      make_probability = make_probability,
      form_feedback_json = form_feedback,
      video_url = base_url + f"VIDEO_{unique_hash}.mp4",
      original_video_url = base_url + f"ORIGINAL_{unique_hash}.mp4",
      setup_frame_url = base_url + f"SETUP_{unique_hash}.png",
      release_frame_url = base_url + f"RELEASE_{unique_hash}.png",
      follow_frame_url = base_url + f"FOLLOW_{unique_hash}.png",
      created_at = datetime.utcnow()
    )
    db.session.add(new_analysis)
    db.session.commit()

    return jsonify({
      "message": "Analysis complete",
      "analysis_id": new_analysis.id,
      "metrics": parsed_metrics,
      "make_probability": make_probability,
      "form_feedback": form_feedback,
      "originalVideoUrl": base_url + f"ORIGINAL_{unique_hash}.mp4",
    }), 200

  except Exception as e:
    if os.path.exists(original_file_path):
      os.remove(original_file_path)
    return jsonify({"error": str(e)}), 500


def upload_session_video():
  if "user_id" not in session:
    return jsonify({"error": "Unauthorized"}), 401

  if "video" not in request.files:
    return jsonify({"error": "No video file found"}), 400

  file = request.files["video"]
  if file.filename == "":
    return jsonify({"error": "Empty filename"}), 400

  shooting_arm = request.form.get("shootingArm", "RIGHT")

  try:
    session_record = process_session_upload(
      file=file,
      user_id=session["user_id"],
      shooting_arm=shooting_arm,
    )

    return jsonify({
      "message": "Session analysis complete",
      "session_id": session_record.id,
      "status": session_record.status,
      "shot_count": session_record.shot_count,
    }), 200
  except Exception as e:
    return jsonify({"error": str(e)}), 500


def get_analyses():
  if "user_id" not in session:
    return jsonify({"error": "Unauthorised"}), 401

  user_analyses = Analysis.query.filter_by(
    user_id=session["user_id"]
  ).order_by(Analysis.created_at.desc()).all()

  analyses_data = []
  for analysis in user_analyses:
    analyses_data.append({
      "id": analysis.id,
      "created_at": analysis.created_at.isoformat(),
      "video_url": analysis.video_url,
      "original_video_url": analysis.original_video_url,
      "setup_frame_url": analysis.setup_frame_url,
      "release_frame_url": analysis.release_frame_url,
      "follow_frame_url": analysis.follow_frame_url,
      "make_probability": analysis.make_probability,
      "metrics": json.loads(analysis.metrics_json),
      "form_feedback": json.loads(analysis.form_feedback_json) 
    })
  
  return jsonify(analyses_data), 200

def get_analysis(analysis_id):
  if "user_id" not in session:
    return jsonify({"error": "Unauthorised"}), 401
  
  analysis = Analysis.query.filter_by(
    id=analysis_id,
    user_id=session["user_id"]
  ).first()

  if not analysis:
    return jsonify({"error": "Analysis not found"}), 404
  
  return jsonify({
    "id": analysis.id,
    "video_url": analysis.video_url,
    "original_video_url": analysis.original_video_url,
    "setup_frame_url": analysis.setup_frame_url,
    "release_frame_url": analysis.release_frame_url,
    "follow_frame_url": analysis.follow_frame_url,
    "metrics": json.loads(analysis.metrics_json),
    "make_probability": analysis.make_probability,
    "form_feedback": json.loads(analysis.form_feedback_json),
    "created_at": analysis.created_at.isoformat()
  }), 200


def get_sessions():
  if "user_id" not in session:
    return jsonify({"error": "Unauthorised"}), 401

  user_sessions = VideoSession.query.filter_by(
    user_id=session["user_id"]
  ).order_by(VideoSession.created_at.desc()).all()

  sessions_data = []
  for session_record in user_sessions:
    first_shot = session_record.shots[0] if session_record.shots else None
    sessions_data.append({
      "id": session_record.id,
      "created_at": session_record.created_at.isoformat(),
      "status": session_record.status,
      "shot_count": session_record.shot_count,
      "original_video_url": session_record.original_video_url,
      "preview_shot_id": first_shot.id if first_shot else None,
      "preview_video_url": first_shot.video_url if first_shot else None,
    })

  return jsonify(sessions_data), 200


def get_session(session_id):
  if "user_id" not in session:
    return jsonify({"error": "Unauthorised"}), 401

  session_record = VideoSession.query.filter_by(
    id=session_id,
    user_id=session["user_id"]
  ).first()

  if not session_record:
    return jsonify({"error": "Session not found"}), 404

  return jsonify({
    "id": session_record.id,
    "created_at": session_record.created_at.isoformat(),
    "status": session_record.status,
    "shooting_arm": session_record.shooting_arm,
    "shot_count": session_record.shot_count,
    "original_video_url": session_record.original_video_url,
    "total_frames": session_record.total_frames,
    "processing_error": session_record.processing_error,
    "shots": [serialize_shot_summary(shot) for shot in session_record.shots],
  }), 200


def get_shot(shot_id):
  if "user_id" not in session:
    return jsonify({"error": "Unauthorised"}), 401

  shot = ShotAnalysis.query.join(VideoSession).filter(
    ShotAnalysis.id == shot_id,
    VideoSession.user_id == session["user_id"],
  ).first()

  if not shot:
    return jsonify({"error": "Shot analysis not found"}), 404

  return jsonify({
    "id": shot.id,
    "session_id": shot.session_id,
    "shot_index": shot.shot_index,
    "start_frame": shot.start_frame,
    "end_frame": shot.end_frame,
    "video_url": shot.video_url,
    "original_video_url": shot.original_video_url,
    "setup_frame_url": shot.setup_frame_url,
    "release_frame_url": shot.release_frame_url,
    "follow_frame_url": shot.follow_frame_url,
    "metrics": json.loads(shot.metrics_json),
    "make_probability": shot.make_probability,
    "form_feedback": json.loads(shot.form_feedback_json),
    "created_at": shot.created_at.isoformat()
  }), 200

def serve_video(user_id, hash_name, filename):
  directory = os.path.join(VIDEO_FOLDER, str(user_id), hash_name)
  return send_from_directory(directory, filename)


def serve_session_video(user_id, session_hash, filename):
  directory = os.path.join(SESSION_VIDEO_FOLDER, str(user_id), "sessions", session_hash)
  return send_from_directory(directory, filename)


def serve_shot_video(user_id, session_hash, shot_folder, filename):
  directory = os.path.join(SESSION_VIDEO_FOLDER, str(user_id), "sessions", session_hash, "shots", shot_folder)
  return send_from_directory(directory, filename)


def serialize_shot_summary(shot):
  return {
    "id": shot.id,
    "shot_index": shot.shot_index,
    "start_frame": shot.start_frame,
    "end_frame": shot.end_frame,
    "video_url": shot.video_url,
    "original_video_url": shot.original_video_url,
    "setup_frame_url": shot.setup_frame_url,
    "release_frame_url": shot.release_frame_url,
    "follow_frame_url": shot.follow_frame_url,
    "make_probability": shot.make_probability,
    "created_at": shot.created_at.isoformat(),
  }


# ==================
# PRIVATE / HELPER FUNCTIONS
# ==================
def get_model_feedback(features):
  try:
    # create df from raw pose data
    df_orig = pd.DataFrame([features])

    all_opt_df = generate_opt_table(df_orig)
    model_opt_df = all_opt_df[OPT_COLS]

    # training_df = pd.concat([model_opt_df, df_orig], axis=1)
    training_df = model_opt_df

    form_probs = MODEL_FORM.predict_proba(training_df)
    form_probs_df = pd.DataFrame(form_probs, columns=["form_0_prob", "form_1_prob", "form_2_prob", "form_3_prob", "form_4_prob", "form_5_prob"])
    print(f"Form Probabilities: {form_probs}")

    expected_form = (0 * form_probs_df["form_0_prob"] + 
                         1 * form_probs_df["form_1_prob"] + 
                         2 * form_probs_df["form_2_prob"] +
                         3 * form_probs_df["form_3_prob"] +
                         4 * form_probs_df["form_4_prob"] +
                         5 * form_probs_df["form_5_prob"])
    
    final_form_score = (expected_form / 6.0) * 100
    final_form_score = np.clip(final_form_score, 10, 95)

    print(f"final form score (%): {final_form_score.values}")

    final_score = calculate_percentage(form_probs, 5)
    print(final_score)

    feedback_df = all_opt_df[FEEDBACK_COLS]
    top_feedback = get_top_feedback(feedback_df, df_orig, 5)

    return final_score, top_feedback
  
  
  except Exception as e:
    print(f"Model inference error: {str(e)}")
    return None, None
  
def get_top_feedback(opt_df, df_orig, top_n=10):
  scores = opt_df.iloc[0].to_dict()
  non_optimal = {col: score for col, score in scores.items() if score != 100}

  sorted_features = sorted(non_optimal.items(), key = lambda x: x[1])

  top_features = sorted_features[:top_n]

  feedback_list = []
  for feature, score in top_features:
    settings = OPT_SETTINGS.get(feature, {})
    raw_val = None
    direction = "optimal"

    if settings.get("orig"):
      raw_val = df_orig.iloc[0].get(settings["orig"])
      if raw_val < settings["min"]:
        direction = "low"
      else:
        direction = "high"
    else:
      direction = "special"
    
    optimal_range_str = ""
    if settings.get("min") is not None and settings.get("max") is not None:
      optimal_range_str = f"\nOptimal range: Between {round(settings['min'], 1)} and {round(settings['max'], 1)}"

    short_msg = ""
    detailed_msg = ""

    if feature in FEEDBACK_MESSAGES:
      feedback_for_feature = FEEDBACK_MESSAGES[feature]
      if direction in feedback_for_feature:
        feedback_item = feedback_for_feature[direction]
        print(feedback_item)
        if isinstance(feedback_item, dict):
          short_msg = feedback_item.get("short", "")
          detailed_msg = feedback_item.get("detailed", "")
        else:
          short_msg = feedback_item
          detailed_msg = feedback_item
      else:
        short_msg = "ERROR"
        detailed_msg = "ERROR"
    else:
      short_msg = "ERROR"
      detailed_msg = "ERROR"
    
    if raw_val is not None:
      feature_name = parse_metric(settings.get("orig", feature))[2:]
      detailed_msg += f"\n\n{feature_name}\nCurrent value: {round(raw_val, 1)} {optimal_range_str}"

    feedback_list.append({
      "feature": feature,
      "score": score,
      "direction": direction,
      "short": short_msg,
      "detailed": detailed_msg
    })

  return feedback_list


def save_uploaded_file(file, upload_folder):
  if file.filename == "":
    return None, None
  
  unique_id = uuid.uuid4().hex

  user_id = session["user_id"]
  folder_path = create_video_folder(user_id, unique_id)
  
  # save original upload
  original_filename = f"ORIGINAL_{unique_id}.mp4"
  original_path = os.path.join(folder_path, original_filename)
  file.save(original_path)
  
  return original_path, unique_id

def compare_to_mean(feature_val, mean_val):
  if mean_val is None or np.isnan(mean_val):
    return "N/A"
  if feature_val > mean_val:
    return "Too high"
  elif feature_val < mean_val:
    return "Too low"
  else:
    return "Equal"
  
def score(val, opt_min, opt_max):
  if val < opt_min:
    return -((opt_min - val) ** 2)
  elif val > opt_max:
    return -((val - opt_max) ** 2)
  else:
    return 100

def generate_opt_table(df):
  df = df.copy()
  df['opt_S_avg_knee_bend'] = df['S_avg_knee_bend'].apply(lambda x: score(x, 120, 160))
  df['opt_S_avg_body_lean'] = df['S_avg_body_lean'].apply(lambda x: score(x, -2, 4))
  df['opt_S_avg_head_tilt'] = df['S_avg_head_tilt'].apply(lambda x: score(x, 50, 65))
  df['opt_S_avg_elbow_angle'] = df['S_avg_elbow_angle'].apply(lambda x: score(x, 45, 90))

  df['opt_R_avg_hip_angle'] = df['R_avg_hip_angle'].apply(lambda x: score(x, 160, 180))
  df['opt_R_avg_elbow_angle'] = df['R_avg_elbow_angle'].apply(lambda x: score(x, 95, 145))
  df['opt_R_avg_knee_bend'] = df['R_avg_knee_bend'].apply(lambda x: score(x, 154, 166))
  df['opt_R_max_wrist_height'] = df['R_max_wrist_height'].apply(lambda x: score(x, 3.4, 7))
  df['opt_R_avg_shoulder_angle'] = df['R_avg_shoulder_angle'].apply(lambda x: score(x, 15, 55))
  df['opt_R_avg_body_lean'] = df['R_avg_body_lean'].apply(lambda x: score(x, -3, 5))
  df['opt_R_forearm_deviation'] = df['R_avg_forearm_deviation'].apply(lambda x: score(x, -40, 10))
  df['opt_R_max_setpoint'] = df['R_max_setpoint'].apply(lambda x: score(x, -4, 10))
  df['opt_R_frame_count'] = df['R_frame_count'].apply(lambda x: score(x, 3, 12))

  df['opt_F_release'] = df['F_release_angle'].apply(lambda x: score(x, 55, 79))
  df['opt_F_elbow_above_eye'] = df['F_elbow_above_eye'].apply(lambda x: score(x, 7, 15))
  df['opt_F_hip_angle'] = df['F_hip_angle'].apply(lambda x: score(x, 174, 180))
  df['opt_F_knee_angle'] = df['F_knee_angle'].apply(lambda x: score(x, 170, 180))
  df['opt_F_body_lean'] = df['F_body_lean_angle'].apply(lambda x: score(x, -2, 2.5))
  df['opt_F_frame_count'] = df['F_frame_count'].apply(lambda x: score(x, 8, 50))

  df['opt_A_knee_bend_order'] = df.apply(
      lambda row: 100 if row['S_avg_knee_bend'] < row['R_avg_knee_bend']+3 else -100, axis=1
  )

  df['opt_A_head_stability'] = df.apply(score_head_tilt, axis=1)

  return df[ALL_OPT_COLS].copy()

def score_head_tilt(row, threshold=15):
    head_tilts = [row['S_avg_head_tilt'], row['R_avg_head_tilt'], row['F_head_tilt']]

    std_dev = np.std(head_tilts)

    return 100 if std_dev <= threshold else -100

def create_video_folder(user_id, hash_name):
  folder_path = os.path.join(VIDEO_FOLDER, str(user_id), hash_name)
  os.makedirs(folder_path, exist_ok=True)
  return folder_path

def calculate_percentage(probabilities, max_class):
  label_scores = np.array([i / max_class * 100 for i in range(max_class + 1)])
  final_score = np.sum(probabilities * label_scores)
  return final_score + 10

def parse_metric(metric):
    parts = metric.split("_")
    new_parts = []
    for part in parts:
        if part.lower() == "avg":
            new_parts.append("Average")
        else:
            new_parts.append(part.capitalize())
    
    return " ".join(new_parts)

def parse_all_metrics(metrics_dict):
    parsed = {}
    for key, value in metrics_dict.items():
        parsed_key = parse_metric(key)
        parsed[parsed_key] = value
    return parsed