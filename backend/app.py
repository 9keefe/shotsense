from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from analysis import analyse_video

from werkzeug.utils import secure_filename

import uuid
import os

app = Flask(
            __name__,
            static_folder='../frontend/build',
            static_url_path=''
)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
VIDEO_FOLDER = os.path.join(BASE_DIR, "static", "videos")
os.makedirs(VIDEO_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload():
    # check for file
    if "video" not in request.files:
        return jsonify({"error": "No video file found"}), 400
    file = request.files["video"]

    # check empty file name
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400
    
    # get shooting arm
    shooting_arm = request.form.get("shootingArm", "RIGHT")

    # hash filename
    unique_id = uuid.uuid4().hex
    hashed_filename = f"{unique_id}.mp4"
    save_path = os.path.join(VIDEO_FOLDER, hashed_filename)

    video_input = save_path

    # save file
    file.save(save_path)

    try:
        metrics = analyse_video(
            video_input,
            shooting_arm=shooting_arm
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

    return jsonify({
        "originalVideoUrl": f"http://127.0.0.1:5000/videos/{hashed_filename}",
        "metrics": metrics
    }), 200

@app.route("/videos/<path:filename>")
def serve_video(filename):
    print("sending video")
    return send_from_directory(VIDEO_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)
