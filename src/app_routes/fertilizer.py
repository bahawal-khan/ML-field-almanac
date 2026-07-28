import pandas as pd
from flask import Blueprint, jsonify, request

from app_utils.auth_middleware import token_required
from app_utils.model_loader import fertilizer_model, fertilizer_label_encoder
from app_utils.explain import explain_fertilizer_prediction

fertilizer_bp = Blueprint("fertilizer", __name__)

NUMERIC_FIELDS = {
    "temperature": "Temperature",
    "humidity": "Humidity",
    "moisture": "Moisture",
    "nitrogen": "Nitrogen",
    "potassium": "Potassium",
    "phosphorous": "Phosphorous",
}

VALID_SOIL_TYPES = {"Black", "Clayey", "Loamy", "Red", "Sandy"}
VALID_CROP_TYPES = {
    "Barley", "Cotton", "Ground Nuts", "Maize", "Millets",
    "Oil seeds", "Paddy", "Pulses", "Sugarcane", "Tobacco", "Wheat",
}


@fertilizer_bp.route("/predict", methods=["POST"])
@token_required
def predict_fertilizer(current_user):
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "status": "error",
            "message": "Request body must be valid JSON."
        }), 400

    missing = [label for key, label in NUMERIC_FIELDS.items() if key not in data or data[key] in (None, "")]
    if "soil_type" not in data or not data.get("soil_type"):
        missing.append("Soil Type")
    if "crop_type" not in data or not data.get("crop_type"):
        missing.append("Crop Type")
    if missing:
        return jsonify({
            "status": "error",
            "message": f"Missing required field(s): {', '.join(missing)}."
        }), 400

    values = {}
    invalid = []
    for key, label in NUMERIC_FIELDS.items():
        try:
            values[key] = float(data[key])
        except (TypeError, ValueError):
            invalid.append(f"{label} must be a number (got: {data[key]!r}).")

    soil_type = data["soil_type"]
    crop_type = data["crop_type"]

    if soil_type not in VALID_SOIL_TYPES:
        invalid.append(f"Soil Type must be one of {sorted(VALID_SOIL_TYPES)} (got: {soil_type!r}).")
    if crop_type not in VALID_CROP_TYPES:
        invalid.append(f"Crop Type must be one of {sorted(VALID_CROP_TYPES)} (got: {crop_type!r}).")

    if invalid:
        return jsonify({
            "status": "error",
            "message": " ".join(invalid)
        }), 400

    features_dict = {
        "Temperature": values["temperature"],
        "Humidity": values["humidity"],
        "Moisture": values["moisture"],
        "Nitrogen": values["nitrogen"],
        "Potassium": values["potassium"],
        "Phosphorous": values["phosphorous"],
        "Soil Type": soil_type,
        "Crop Type": crop_type,
    }
    features_df = pd.DataFrame([features_dict])

    try:
        proba = fertilizer_model.predict_proba(features_df)[0]
        predicted_idx = int(proba.argmax())
        fertilizer_name = fertilizer_label_encoder.inverse_transform([predicted_idx])[0]
        confidence = float(proba[predicted_idx])
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Prediction failed unexpectedly: {e}"
        }), 500

    try:
        explanation = explain_fertilizer_prediction(
            fertilizer_model, fertilizer_label_encoder,
            features_dict, fertilizer_name, confidence,
        )
    except Exception:
        explanation = None

    return jsonify({
        "status": "success",
        "recommended_fertilizer": fertilizer_name,
        "confidence": round(confidence, 4),
        "explanation": explanation,
    }), 200