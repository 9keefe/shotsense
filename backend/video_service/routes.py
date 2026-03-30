import json
import os

from flask import jsonify, request, send_from_directory, session

from db_schema import Session as VideoSession, ShotAnalysis

from .config import OPT_SETTINGS, VIDEO_FOLDER
from .metric_explanations import METRIC_EXPLANATIONS
from .scoring import parse_metric
from .session_analysis import process_session_upload

METRIC_EXPLANATIONS_MAP = {
    parse_metric(metric_key): explanation
    for metric_key, explanation in METRIC_EXPLANATIONS.items()
}

METRIC_RANGES_MAP = {
    parse_metric(settings["orig"]): {
        "min": settings.get("min"),
        "max": settings.get("max"),
        "has_range": settings.get("min") is not None and settings.get("max") is not None,
    }
    for settings in OPT_SETTINGS.values()
    if settings.get("orig")
}


# ==================
# ROUTES / ENDPOINTS
# ==================
def upload_session_video():
    user_id = get_current_user_id()
    if user_id is None:
        return jsonify({"error": "Unauthorized"}), 401

    file = get_uploaded_video_file()
    if isinstance(file, tuple):
        return file

    shooting_arm = request.form.get("shootingArm", "RIGHT")

    try:
        # process uploaded session video
        session_record = process_session_upload(file=file, user_id=user_id, shooting_arm=shooting_arm)

        return jsonify(
            {
                "message": "Session analysis complete",
                "session_id": session_record.id,
                "status": session_record.status,
                "shot_count": session_record.shot_count,
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_sessions():
    user_id = get_current_user_id()
    if user_id is None:
        return jsonify({"error": "Unauthorised"}), 401

    user_sessions = (
        VideoSession.query.filter_by(user_id=user_id)
        .order_by(VideoSession.created_at.desc())
        .all()
    )

    return jsonify(
        [serialize_session_summary(session_record) for session_record in user_sessions]
    ), 200


def get_session(session_id):
    user_id = get_current_user_id()
    if user_id is None:
        return jsonify({"error": "Unauthorised"}), 401

    session_record = VideoSession.query.filter_by(id=session_id, user_id=user_id).first()
    if not session_record:
        return jsonify({"error": "Session not found"}), 404

    return jsonify(serialize_session_detail(session_record)), 200


def get_shot(shot_id):
    user_id = get_current_user_id()
    if user_id is None:
        return jsonify({"error": "Unauthorised"}), 401

    shot = (
        ShotAnalysis.query.join(VideoSession)
        .filter(
            ShotAnalysis.id == shot_id,
            VideoSession.user_id == user_id,
        )
        .first()
    )

    if not shot:
        return jsonify({"error": "Shot analysis not found"}), 404

    return jsonify(serialize_shot_detail(shot)), 200


def serve_video(user_id, hash_name, filename):
    directory = os.path.join(VIDEO_FOLDER, str(user_id), hash_name)
    return send_from_directory(directory, filename)


def serve_session_video(user_id, session_hash, filename):
    directory = os.path.join(VIDEO_FOLDER, str(user_id), "sessions", session_hash)
    return send_from_directory(directory, filename)


def serve_shot_video(user_id, session_hash, shot_folder, filename):
    directory = os.path.join(
        VIDEO_FOLDER,
        str(user_id),
        "sessions",
        session_hash,
        "shots",
        shot_folder,
    )
    return send_from_directory(directory, filename)


# ==================
# SERIALIZERS
# ==================
def serialize_session_summary(session_record):
    first_shot = session_record.shots[0] if session_record.shots else None
    return {
        "id": session_record.id,
        "created_at": session_record.created_at.isoformat(),
        "status": session_record.status,
        "shot_count": session_record.shot_count,
        "original_video_url": session_record.original_video_url,
        "preview_shot_id": first_shot.id if first_shot else None,
        "preview_video_url": first_shot.video_url if first_shot else None,
    }


def serialize_session_detail(session_record):
    return {
        "id": session_record.id,
        "created_at": session_record.created_at.isoformat(),
        "status": session_record.status,
        "shooting_arm": session_record.shooting_arm,
        "shot_count": session_record.shot_count,
        "original_video_url": session_record.original_video_url,
        "total_frames": session_record.total_frames,
        "processing_error": session_record.processing_error,
        "shots": [serialize_shot_summary(shot) for shot in session_record.shots],
    }


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


def serialize_shot_detail(shot):
    return {
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
        "metric_explanations": get_metric_explanations(),
        "metric_ranges": get_metric_ranges(),
        "make_probability": shot.make_probability,
        "form_feedback": json.loads(shot.form_feedback_json),
        "created_at": shot.created_at.isoformat(),
    }


# ==================
# PRIVATE / HELPER FUNCTIONS
# ==================
def get_current_user_id():
    return session.get("user_id")


def get_uploaded_video_file():
    if "video" not in request.files:
        return jsonify({"error": "No video file found"}), 400

    file = request.files["video"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    return file


def get_metric_explanations():
    return METRIC_EXPLANATIONS_MAP


def get_metric_ranges():
    return METRIC_RANGES_MAP
