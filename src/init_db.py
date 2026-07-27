"""
One-time database setup script.

Creates all tables defined by the SQLAlchemy models (users, crops,
soil_types, fertilizers, crop_predictions, fertilizer_predictions) in the
PostgreSQL database configured in your .env file.

Run this once after setting up a fresh database:

    python src/init_db.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import app, db  # noqa: E402

with app.app_context():
    db.create_all()
    print("✅ All tables created successfully.")
