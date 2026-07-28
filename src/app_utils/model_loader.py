import os
import joblib

# Base Project Directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# Models Folder
MODEL_DIR = os.path.join(BASE_DIR, "models")

# ==========================
# Crop Recommendation Model
# ==========================

crop_model = joblib.load(
    os.path.join(MODEL_DIR, "crop_recommendation_model.pkl")
)

crop_label_encoder = joblib.load(
    os.path.join(MODEL_DIR, "crop_label_encoder.pkl")
)

print("✅ Crop Model Loaded Successfully!")

# ==========================
# Fertilizer Recommendation Model
# ==========================

fertilizer_model = joblib.load(
    os.path.join(MODEL_DIR, "fertilizer_model.pkl")
)

fertilizer_label_encoder = joblib.load(
    os.path.join(MODEL_DIR, "fertilizer_label_encoder.pkl")
)

print("✅ Fertilizer Model Loaded Successfully!")

# ==========================
# Regional Crop Model (Pakistan district-level, 13 crops)
# ==========================

regional_crop_model = joblib.load(
    os.path.join(MODEL_DIR, "regional_crop_model.pkl")
)

regional_crop_label_encoder = joblib.load(
    os.path.join(MODEL_DIR, "regional_crop_label_encoder.pkl")
)

print("✅ Regional Crop Model Loaded Successfully!")