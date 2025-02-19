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

MODEL_FORM = joblib.load(os.path.join(MODEL_FOLDER, "model_form_v2.pkl"))
MODEL_SHOT = joblib.load(os.path.join(MODEL_FOLDER, "model_shot_v3-hybrid.pkl"))
OPT_COLS = joblib.load(os.path.join(MODEL_FOLDER, "opt_cols.pkl"))
ORIG_COLS = joblib.load(os.path.join(MODEL_FOLDER, "orig_cols.pkl"))
FORM_COLS = joblib.load(os.path.join(MODEL_FOLDER, "form_cols.pkl"))

MEAN_VALS = joblib.load(os.path.join(MODEL_FOLDER, "mean_vals.pkl"))

HYBRID_COLS = OPT_COLS + FORM_COLS + ORIG_COLS

def save_uploaded_file(file, upload_folder):
  if file.filename == "":
    return None
  unique_id = uuid.uuid4().hex
  hashed_filename = f"{unique_id}.mp4"
  save_path = os.path.join(upload_folder, hashed_filename)
  file.save(save_path)
  return save_path

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
  file_path = save_uploaded_file(file, VIDEO_FOLDER)

  # analyse video
  try:
    metrics = analyse_video(file_path, shooting_arm=shooting_arm)
    probability, feedback = get_model_feedback(metrics)

    make_probability = float(probability)
    form_feedback = json.dumps(feedback, default=str)

    if probability is None:
      raise ValueError("Model prediction failed")
    
    # create new db record
    new_analysis = Analysis(
      user_id = session["user_id"],
      hashed_filename = os.path.basename(file_path),
      metrics_json = json.dumps(metrics),
      make_probability = make_probability,
      form_feedback_json = form_feedback,
      video_url = f"http://127.0.0.1:5000/videos/{os.path.basename(file_path)}",
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
      "originalVideoUrl": f"http://127.0.0.1:5000/videos/{os.path.basename(file_path)}",
    }), 200

  except Exception as e:
    if os.path.exists(file_path):
      os.remove(file_path)
    return jsonify({"error": str(e)}), 500


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
    df_hybrid = final_df[HYBRID_COLS].copy()

    print("\n Generating Shot Probability...")
    make_probability = MODEL_SHOT.predict(df_hybrid)[0] + 0.1
    make_probability = np.clip(make_probability, 0.2, 0.9)

    feedback = []
    for col in OPT_COLS:
      val = opt_df.iloc[0][col]
      feedback.append({"feature": col, "score": val})
    feedback = sorted(feedback, key=lambda x: x["score"])

    return make_probability, feedback
  
  except Exception as e:
    print(f"Model inference error: {str(e)}")
    return None, None

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
  df['opt_S_min_body_lean'] = df['S_min_body_lean'].apply(lambda x: score(x, -4, 4))
  df['opt_S_avg_knee_bend'] = df['S_avg_knee_bend'].apply(lambda x: score(x, 140, 170))

  df['opt_R_avg_hip_angle'] = df['R_avg_hip_angle'].apply(lambda x: score(x, 175, 180))
  df['opt_R_avg_elbow_angle'] = df['R_avg_elbow_angle'].apply(lambda x: score(x, 100, 135))
  df['opt_R_avg_knee_bend'] = df['R_avg_knee_bend'].apply(lambda x: score(x, 160, 180))
  df['opt_R_max_wrist_height'] = df['R_max_wrist_height'].apply(lambda x: score(x, 4, 10))

  df['opt_F_release'] = df['F_release_angle'].apply(lambda x: score(x, 62, 70))
  df['opt_F_elbow_above_eye'] = df['F_elbow_above_eye'].apply(lambda x: score(x, 0, 10))
  df['opt_F_hip_angle'] = df['F_hip_angle'].apply(lambda x: score(x, 175, 180))
  df['opt_F_knee_angle'] = df['F_knee_angle'].apply(lambda x: score(x, 168, 180))
  df['opt_F_body_lean'] = df['F_body_lean_angle'].apply(lambda x: score(x, -1, 2))

  return df[OPT_COLS].copy()
  
def serve_video(filename):
  return send_from_directory(VIDEO_FOLDER, filename)

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
    "metrics": json.loads(analysis.metrics_json),
    "make_probability": analysis.make_probability,
    "form_feedback": json.loads(analysis.form_feedback_json),
    "created_at": analysis.created_at.isoformat()
  }), 200



