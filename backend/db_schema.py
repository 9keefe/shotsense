from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):
  __tablename__ = "users"

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50), nullable=False)
  email = db.Column(db.String(50), nullable=False, unique=True)
  password_hash = db.Column(db.String(255), nullable=False)

  # relationship: user can have multiple analysis videos
  analyses = db.relationship("Analysis", back_populates="user")
  sessions = db.relationship("Session", back_populates="user")

  def __init__(self, name, email, password_hash):
    self.name = name
    self.email = email
    self.password_hash = password_hash

class Analysis(db.Model):
  __tablename__ = "analyses"

  id = db.Column(db.Integer, primary_key=True, index=True)
  user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
  hashed_filename = db.Column(db.String(255), nullable=False)
  metrics_json = db.Column(db.Text, nullable=False)
  created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
  make_probability = db.Column(db.Float)
  form_feedback_json = db.Column(db.Text)
  video_url = db.Column(db.String(512))
  original_video_url = db.Column(db.String(512))
  setup_frame_url = db.Column(db.String(512))
  release_frame_url = db.Column(db.String(512))
  follow_frame_url = db.Column(db.String(512))

  # relationship to user
  user = db.relationship("User", back_populates="analyses")


class Session(db.Model):
  __tablename__ = "sessions"

  id = db.Column(db.Integer, primary_key=True, index=True)
  user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
  hashed_filename = db.Column(db.String(255), nullable=False, unique=True)
  shooting_arm = db.Column(db.String(10), nullable=False)
  created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
  status = db.Column(db.String(20), nullable=False, default="processing")
  original_video_url = db.Column(db.String(512), nullable=False)
  shot_count = db.Column(db.Integer, nullable=False, default=0)
  total_frames = db.Column(db.Integer)
  processing_error = db.Column(db.Text)

  user = db.relationship("User", back_populates="sessions")
  shots = db.relationship(
    "ShotAnalysis",
    back_populates="session",
    cascade="all, delete-orphan",
    order_by="ShotAnalysis.shot_index"
  )


class ShotAnalysis(db.Model):
  __tablename__ = "shot_analyses"

  id = db.Column(db.Integer, primary_key=True, index=True)
  session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"), nullable=False)
  shot_index = db.Column(db.Integer, nullable=False)
  start_frame = db.Column(db.Integer, nullable=False)
  end_frame = db.Column(db.Integer, nullable=False)
  created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
  metrics_json = db.Column(db.Text, nullable=False)
  make_probability = db.Column(db.Float)
  form_feedback_json = db.Column(db.Text, nullable=False)
  video_url = db.Column(db.String(512))
  original_video_url = db.Column(db.String(512))
  setup_frame_url = db.Column(db.String(512))
  release_frame_url = db.Column(db.String(512))
  follow_frame_url = db.Column(db.String(512))

  session = db.relationship("Session", back_populates="shots")

def dbinit():
  # test users

  user_list = [
    User("Test", "test@email.com", "scrypt:32768:8:1$07M9upXmM8iTH641$fd3243b77a4893fefcb1dd378aee0c3a4afd4326804c5498321d3d831f21d616d4243656828f22da5671c096d3491575d53deb5063cba023de4dceff9931cbca",)
  ]
  db.session.add_all(user_list)
  db.session.commit()
  
