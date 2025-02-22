from flask import Flask, jsonify, request, send_from_directory, session
from flask_cors import CORS

from video_service.routes import upload_video, serve_video, get_analyses, get_analysis
from auth_service.routes import signup, signin, user

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
CORS(app, supports_credentials=True, origins=["http://127.0.0.1:5173"])
app.secret_key = "u22058"

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 

# config flask-sqlalchemy for sqlite
DATABASE_PATH = os.path.join(BASE_DIR, "database.sqlite")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  
app.config["SESSION_COOKIE_SECURE"] = False

db.init_app(app)

resetdb = True
if resetdb:
    with app.app_context():
        db.drop_all()
        db.create_all()
        dbinit()

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:5173"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    return response

@app.route("/upload", methods=["POST"])
def upload_route():
    return upload_video()

@app.route("/videos/<int:user_id>/<hash_name>/<filename>")
def serve_video_route(user_id, hash_name, filename):
    return serve_video(user_id, hash_name, filename)

@app.route("/get-analyses", methods=["GET"])
def get_analyses_route():
    return get_analyses()

@app.route("/analyses/<int:analysis_id>", methods=["GET"])
def get_analysis_route(analysis_id):
    return get_analysis(analysis_id)

@app.route("/user", methods=["GET"])
def user_route():
    return user()

@app.route("/signup", methods=["POST"])
def signup_route():
    return signup()

@app.route("/signin", methods=["POST"])
def signin_route():
    return signin()


if __name__ == "__main__":
    app.run(debug=True)
