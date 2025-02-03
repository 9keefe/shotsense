import os
import uuid
import pandas as pd
import numpy as np
import joblib
import json
from datetime import datetime
from flask import jsonify, request, send_from_directory, session
from db_schema import db, Analysis


from .analysis import analyse_video


VIDEO_FOLDER = os.path.join(os.path.dirname(__file__), "videos")
os.makedirs(VIDEO_FOLDER, exist_ok=True)

MODEL_FOLDER = os.path.join(os.path.dirname(__file__), "model")

MODEL = joblib.load(os.path.join(MODEL_FOLDER, "model.pkl"))
SCALER = joblib.load(os.path.join(MODEL_FOLDER, "scaler.pkl"))
FEATURE_COLUMNS = joblib.load(os.path.join(MODEL_FOLDER, "feature_columns.pkl"))

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

    if probability is None:
      raise ValueError("Model prediction failed")
    
    # create new db record
    new_analysis = Analysis(
      user_id = session["user_id"],
      hashed_filename = os.path.basename(file_path),
      metrics_json = json.dumps(metrics),
      make_probability = probability,
      form_feedback_json = json.dumps(feedback),
      video_url = f"http://127.0.0.1:5000/videos/{os.path.basename(file_path)}",
      created_at = datetime.utcnow()
    )
    db.session.add(new_analysis)
    db.session.commit()


    return jsonify({
      "message": "Analysis complete",
      "analysis_id": new_analysis.id,
      "metrics": metrics,
      "make_probability": probability,
      "form_feedback": feedback,
      "originalVideoUrl": f"http://127.0.0.1:5000/videos/{os.path.basename(file_path)}",
    }), 200

  except Exception as e:
    if os.path.exists(file_path):
      os.remove(file_path)
    return jsonify({"error": str(e)}), 500


def get_model_feedback(features):
  try:
    # create dataframe with correct feature order
    df = pd.DataFrame([features])[FEATURE_COLUMNS]
    
    # scale features
    scaled_features = SCALER.transform(df)

    # get prediction
    make_probability = MODEL.predict_proba(scaled_features)[0][1]

    # Get feature importance feedback
    feature_importances = MODEL.feature_importances_
    sorted_idx = np.argsort(feature_importances)[::-1]

    feedback = []
    for idx in sorted_idx[:3]:
      feature_name = FEATURE_COLUMNS[idx]
      current_value = features[feature_name]
      feedback.append({
        "feature": feature_name,
        "value": current_value,
        "importance": float(feature_importances[idx])
      })
    
    return make_probability, feedback
  
  except Exception as e:
    print(f"Model inference error: {str(e)}")
    return None, None
  
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



