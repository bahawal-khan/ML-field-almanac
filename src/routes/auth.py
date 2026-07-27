from flask import Blueprint, jsonify, request
import bcrypt
import jwt
from datetime import datetime, timedelta

from config import Config
from database import db
from models.user import User
from utils.auth_middleware import token_required

auth_bp = Blueprint("auth", __name__)


# -----------------------------
# Test Route
# -----------------------------
@auth_bp.route("/test", methods=["GET"])
def test():
    return jsonify({
        "status": "success",
        "message": "Auth Route Working Successfully"
    })


# -----------------------------
# Register Route
# -----------------------------
@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    # Validation
    if not username or not email or not password:
        return jsonify({
            "status": "error",
            "message": "All fields are required."
        }), 400

    # Check existing email
    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({
            "status": "error",
            "message": "Email already exists."
        }), 409

    # Hash Password
    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    # Create User
    new_user = User(
        username=username,
        email=email,
        password_hash=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "User Registered Successfully"
    }), 201


# -----------------------------
# Login Route
# -----------------------------
@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "status": "error",
            "message": "Email and Password are required."
        }), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({
            "status": "error",
            "message": "Invalid Email or Password"
        }), 401

    if not bcrypt.checkpw(
        password.encode("utf-8"),
        user.password_hash.encode("utf-8")
    ):
        return jsonify({
            "status": "error",
            "message": "Invalid Email or Password"
        }), 401

    # Generate JWT Token
    token = jwt.encode(
        {
            "user_id": user.user_id,
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(days=1)
        },
        Config.JWT_SECRET_KEY,
        algorithm="HS256"
    )

    return jsonify({
        "status": "success",
        "message": "Login Successful",
        "token": token
    }), 200


# -----------------------------
# Protected Profile Route
# -----------------------------
@auth_bp.route("/profile", methods=["GET"])
@token_required
def profile(current_user):

    return jsonify({
        "status": "success",
        "message": "Protected Route Accessed Successfully",
        "user": {
            "user_id": current_user.user_id,
            "username": current_user.username,
            "email": current_user.email
        }
    }), 200