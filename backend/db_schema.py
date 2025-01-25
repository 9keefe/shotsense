from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
  __tablename__ = "users"

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50), nullable=False)
  email = db.Column(db.String(50), nullable=False, unique=True)
  password_hash = db.Column(db.String(255), nullable=False)

  # relationship: user can have multiple analysis videos
  analyses = db.relationship("Analysis", back_populates="user")

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

  # relationship to user
  user = db.relationship("User", back_populates="analyses")

def dbinit():
  # test users

  user_list = [
    User("Keefe", "test@email.com", "password",)
  ]
  db.session.add_all(user_list)
  db.session.commit()
  