from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from video_service.routes import upload_video, serve_video
from db_schema import db, dbinit, User, Analysis

from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

import uuid
import os
import jwt

app = Flask(
            __name__,
            static_folder='../frontend/build',
            static_url_path=''
)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 

# config flask-sqlalchemy for sqlite
DATABASE_PATH = os.path.join(BASE_DIR, "database.sqlite")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

resetdb = True
if resetdb:
    with app.app_context():
        db.drop_all()
        db.create_all()
        dbinit()

@app.route("/upload", methods=["POST"])
def upload_route():
    return upload_video()

@app.route("/videos/<path:filename>")
def serve_video_route(filename):
    print("function called")
    return serve_video(filename)

if __name__ == "__main__":
    app.run(debug=True)
