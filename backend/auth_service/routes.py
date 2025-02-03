from flask import request, jsonify, session, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from db_schema import db, User, Analysis

def signup():
  data = request.json
  name = data.get("name")
  email = data.get("email")
  password = data.get("password")

  if not name or not email or not password:
    return jsonify({"error": "All fields are required"}), 400
  
  if User.query.filter_by(email=email).first():
    return jsonify({"error": "Email already registered"}), 400
  
  hashed_password = generate_password_hash(password)
  user = User(name=name, email=email, password_hash=hashed_password)
  db.session.add(user)
  db.session.commit()

  session["user_id"] = user.id
  session["user_name"] = user.name

  return jsonify({"message": "User created successfully"}), 201

def signin():
  data = request.json
  email = data.get("email")
  password = data.get("password")

  if not email or not password:
    return jsonify({"error": "All fields are required"}), 400
  
  searched_user = User.query.filter_by(email=email).first()

  if not searched_user or not check_password_hash(searched_user.password_hash, password):
    return jsonify({"error": "Please check your login details and try again"})
  
  session["user_id"] = searched_user.id
  session["user_name"] = searched_user.name

  return jsonify({"message": "User successfully signed in"}), 201

def user():
  if "user_id" not in session:
    return jsonify({"error": "Unauthorized"}), 401
  
  user = User.query.get(session["user_id"])
  if not user:
    return jsonify({"error": "User not found"}), 404
  
  return jsonify({
    "name": user.name,
    "email": user.email,
  }), 200