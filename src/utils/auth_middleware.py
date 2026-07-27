from functools import wraps
from flask import request, jsonify
import jwt

from config import Config
from models.user import User


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        # Get token from Authorization Header
        auth_header = request.headers.get("Authorization")

        if auth_header:
            parts = auth_header.split()

            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]

        if not token:
            return jsonify({
                "status": "error",
                "message": "Token is missing."
            }), 401

        try:
            data = jwt.decode(
                token,
                Config.JWT_SECRET_KEY,
                algorithms=["HS256"]
            )

            current_user = User.query.get(data["user_id"])

            if not current_user:
                return jsonify({
                    "status": "error",
                    "message": "User not found."
                }), 401

        except jwt.ExpiredSignatureError:
            return jsonify({
                "status": "error",
                "message": "Token has expired."
            }), 401

        except jwt.InvalidTokenError:
            return jsonify({
                "status": "error",
                "message": "Invalid token."
            }), 401

        return f(current_user, *args, **kwargs)

    return decorated