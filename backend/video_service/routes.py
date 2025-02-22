import os
import uuid
import pandas as pd
import numpy as np
import joblib
import json
import shap
from datetime import datetime
from flask import jsonify, request, send_from_directory, session
from db_schema import db, Analysis
from .analysis import analyse_video

VIDEO_FOLDER = os.path.join(os.path.dirname(__file__), "videos")
os.makedirs(VIDEO_FOLDER, exist_ok=True)

MODEL_FOLDER = os.path.join(os.path.dirname(__file__), "model")

MODEL_FORM = joblib.load(os.path.join(MODEL_FOLDER, "model_form_v3.pkl"))
MODEL_SHOT = joblib.load(os.path.join(MODEL_FOLDER, "model_shot_v3-hybrid.pkl"))
OPT_COLS = joblib.load(os.path.join(MODEL_FOLDER, "opt_cols_v2.pkl"))
ORIG_COLS = joblib.load(os.path.join(MODEL_FOLDER, "orig_cols.pkl"))
FORM_COLS = joblib.load(os.path.join(MODEL_FOLDER, "form_cols.pkl"))
HYBRID_COLS = OPT_COLS + FORM_COLS + ORIG_COLS

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
    print(metrics)
    processed_video_path = analysis_results.get("processed_video_path")
    setup_frame_path = analysis_results.get("setup_frame_path")
    release_frame_path = analysis_results.get("release_frame_path")
    follow_frame_path = analysis_results.get("follow_frame_path")

    probability, feedback = get_model_feedback(metrics)
    make_probability = float(probability)
    form_feedback = json.dumps(feedback, default=str)

    if probability is None:
      raise ValueError("Model prediction failed")
    base_url = f"http://127.0.0.1:5000/videos/{session['user_id']}/{unique_hash}/"

    # create new db record
    new_analysis = Analysis(
      user_id = session["user_id"],
      hashed_filename = unique_hash,
      metrics_json = json.dumps(metrics),
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
      "metrics": metrics,
      "make_probability": make_probability,
      "form_feedback": form_feedback,
      "originalVideoUrl": base_url + f"ORIGINAL_{unique_hash}.mp4",
    }), 200

  except Exception as e:
    if os.path.exists(original_file_path):
      os.remove(original_file_path)
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

def serve_video(user_id, hash_name, filename):
  directory = os.path.join(VIDEO_FOLDER, str(user_id), hash_name)
  return send_from_directory(directory, filename)


# ==================
# PRIVATE / HELPER FUNCTIONS
# ==================
def get_model_feedback(features):
  try:
    # create df from raw pose data
    df_orig = pd.DataFrame([features])

    opt_df = generate_opt_table(df_orig)

    print(opt_df)

    print("\n Generating Form Score...")
    form_probs = MODEL_FORM.predict_proba(opt_df)
    form_probs_df = pd.DataFrame(form_probs, columns=["form_0_prob", "form_1_prob", "form_2_prob"])
    print(f"Form Probabilities: {form_probs}")

    expected_form = (0 * form_probs_df["form_0_prob"] + 
                      1 * form_probs_df["form_1_prob"] + 
                      2 * form_probs_df["form_2_prob"]) / 2.0
    print(f"Expected form: {expected_form}")

    print("\n Generating Form DF...")
    df_with_form = pd.concat([df_orig.reset_index(drop=True), form_probs_df.reset_index(drop=True)], axis=1)
    df_with_form["expected_form"] = expected_form.values

    final_df = pd.concat([opt_df.reset_index(drop=True), df_with_form.reset_index(drop=True)], axis=1)

    print("\n Generating Hybrid DF...")
    # df_hybrid = final_df[HYBRID_COLS].copy()

    print("\n Generating Shot Probability...")
    # make_probability = MODEL_SHOT.predict(df_hybrid)[0] + 0.1
    make_probability = 0.0
    make_probability = np.clip(make_probability, 0.2, 0.9)

    feedback = []
    # for col in OPT_COLS:
    #   val = opt_df.iloc[0][col]
    #   feedback.append({"feature": col, "score": val})
    # feedback = sorted(feedback, key=lambda x: x["score"])

    return make_probability, feedback
  
  except Exception as e:
    print(f"Model inference error: {str(e)}")
    return None, None

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
  df['opt_S_avg_knee_bend'] = df['S_avg_knee_bend'].apply(lambda x: score(x, 130, 160))
  df['opt_S_avg_body_lean'] = df['S_avg_body_lean'].apply(lambda x: score(x, -2, 4))
  df['opt_S_avg_head_tilt'] = df['S_avg_head_tilt'].apply(lambda x: score(x, 50, 65))

  df['opt_R_avg_hip_angle'] = df['R_avg_hip_angle'].apply(lambda x: score(x, 160, 180))
  df['opt_R_avg_elbow_angle'] = df['R_avg_elbow_angle'].apply(lambda x: score(x, 110, 145))
  df['opt_R_avg_knee_bend'] = df['R_avg_knee_bend'].apply(lambda x: score(x, 155, 175))
  df['opt_R_max_wrist_height'] = df['R_max_wrist_height'].apply(lambda x: score(x, 3.5, 7))
  df['opt_R_avg_shoulder_angle'] = df['R_avg_shoulder_angle'].apply(lambda x: score(x, 35, 55))
  df['opt_R_frame_count'] = df['R_frame_count'].apply(lambda x: score(x, 3, 12))

  df['opt_F_release'] = df['F_release_angle'].apply(lambda x: score(x, 55, 79))
  df['opt_F_elbow_above_eye'] = df['F_elbow_above_eye'].apply(lambda x: score(x, 8, 15))
  df['opt_F_hip_angle'] = df['F_hip_angle'].apply(lambda x: score(x, 174, 180))
  df['opt_F_knee_angle'] = df['F_knee_angle'].apply(lambda x: score(x, 170, 180))
  df['opt_F_body_lean'] = df['F_body_lean_angle'].apply(lambda x: score(x, -2, 2))
  df['opt_F_frame_count'] = df['F_frame_count'].apply(lambda x: score(x, 8, 50))

  df['opt_A_knee_bend_order'] = df.apply(
    lambda row: 100 if row['S_avg_knee_bend'] < row['R_avg_knee_bend'] else -100, axis=1
  )

  df['opt_A_head_stability'] = df.apply(score_head_tilt, axis=1)

  return df[OPT_COLS].copy()

def score_head_tilt(row, threshold=10):
    head_tilts = [row['S_avg_head_tilt'], row['R_avg_head_tilt'], row['F_head_tilt']]

    std_dev = np.std(head_tilts)

    return 100 if std_dev <= threshold else -100

def create_video_folder(user_id, hash_name):
  folder_path = os.path.join(VIDEO_FOLDER, str(user_id), hash_name)
  os.makedirs(folder_path, exist_ok=True)
  return folder_path




