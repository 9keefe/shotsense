import os
import uuid
from flask import jsonify, request, send_from_directory

from .analysis import analyse_video


VIDEO_FOLDER = os.path.join(os.path.dirname(__file__), "videos")
os.makedirs(VIDEO_FOLDER, exist_ok=True)

def save_uploaded_file(file, upload_folder):
  if file.filename == "":
    return None
  unique_id = uuid.uuid4().hex
  hashed_filename = f"{unique_id}.mp4"
  save_path = os.path.join(upload_folder, hashed_filename)
  file.save(save_path)
  return save_path

def upload_video():
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
    metrics = analyse_video(
      file_path,
      shooting_arm=shooting_arm
    )
  except Exception as e:
    return jsonify({"error": str(e)}), 500
  
  return jsonify({
    "message": "Video uploaded and analyzed successfully",
    "originalVideoUrl": f"http://127.0.0.1:5000/videos/{os.path.basename(file_path)}",
    "metrics": metrics
    }), 200

def serve_video(filename):
  print(filename)
  return send_from_directory(VIDEO_FOLDER, filename)



