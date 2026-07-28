from flask import Flask
from flask_cors import CORS
from app_config import Config
from db import db
from app_models import *
from app_routes import auth_bp, crop_bp, fertilizer_bp

app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Allow the React frontend (different origin/port) to call this API.
# In production, replace "*" with your actual deployed frontend URL.
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize database
db.init_app(app)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(crop_bp, url_prefix="/api/crop")
app.register_blueprint(fertilizer_bp, url_prefix="/api/fertilizer")

# Test database connection
with app.app_context():
    try:
        with db.engine.connect() as connection:
            print("✅ Database Connected Successfully!")
    except Exception as e:
        print("❌ Database Connection Failed!")
        print(e)


@app.route("/")
def home():
    return {
        "status": "success",
        "message": "Smart Agriculture AI Backend Running Successfully"
    }


@app.route("/api/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=True)