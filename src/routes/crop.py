from flask import Blueprint, jsonify, request

from utils.auth_middleware import token_required
from utils.model_loader import crop_model, crop_label_encoder
from utils.explain import explain_crop_prediction

crop_bp = Blueprint("crop", __name__)

REQUIRED_FIELDS = {
    "nitrogen": "Nitrogen (N)",
    "phosphorus": "Phosphorus (P)",
    "potassium": "Potassium (K)",
    "temperature": "Temperature",
    "humidity": "Humidity",
    "ph": "Soil pH",
    "rainfall": "Rainfall",
}

# Roughly the ranges seen in the training data (Crop_recommendation.csv).
# Not a hard validation limit, just used to flag clearly out-of-range input
# so the person gets a helpful warning instead of a silently unreliable prediction.
PLAUSIBLE_RANGES = {
    "nitrogen": (0, 140),
    "phosphorus": (0, 145),
    "potassium": (0, 205),
    "temperature": (-10, 50),
    "humidity": (0, 100),
    "ph": (0, 14),
    "rainfall": (0, 300),
}


@crop_bp.route("/predict", methods=["POST"])
@token_required
def predict_crop(current_user):
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "status": "error",
            "message": "Request body must be valid JSON."
        }), 400

    # --- Field-level validation (replaces the old blanket try/except) ---
    missing = [label for key, label in REQUIRED_FIELDS.items() if key not in data or data[key] in (None, "")]
    if missing:
        return jsonify({
            "status": "error",
            "message": f"Missing required field(s): {', '.join(missing)}."
        }), 400

    values = {}
    invalid = []
    for key, label in REQUIRED_FIELDS.items():
        try:
            values[key] = float(data[key])
        except (TypeError, ValueError):
            invalid.append(f"{label} must be a number (got: {data[key]!r}).")

    if invalid:
        return jsonify({
            "status": "error",
            "message": " ".join(invalid)
        }), 400

    out_of_range = []
    for key, label in REQUIRED_FIELDS.items():
        low, high = PLAUSIBLE_RANGES[key]
        if not (low <= values[key] <= high):
            out_of_range.append(f"{label}={values[key]} is outside the typical {low}-{high} range")

    features = [[
        values["nitrogen"], values["phosphorus"], values["potassium"],
        values["temperature"], values["humidity"], values["ph"], values["rainfall"],
    ]]

    try:
        proba = crop_model.predict_proba(features)[0]
        predicted_idx = int(proba.argmax())
        crop_name = crop_label_encoder.inverse_transform([predicted_idx])[0]
        confidence = float(proba[predicted_idx])
    except Exception as e:
        # Any failure here is a genuine server-side/model problem, not bad
        # user input (that was already validated above) - report it plainly.
        return jsonify({
            "status": "error",
            "message": f"Prediction failed unexpectedly: {e}"
        }), 500

    try:
        explanation = explain_crop_prediction(
            crop_model, crop_label_encoder,
            {"N": values["nitrogen"], "P": values["phosphorus"], "K": values["potassium"],
             "temperature": values["temperature"], "humidity": values["humidity"],
             "ph": values["ph"], "rainfall": values["rainfall"]},
            crop_name, confidence,
        )
    except Exception:
        # Explanation is a nice-to-have; never let it break the core prediction.
        explanation = None

    response = {
        "status": "success",
        "recommended_crop": crop_name,
        "confidence": round(confidence, 4),
        "explanation": explanation,
    }
    if out_of_range:
        response["warnings"] = out_of_range

    return jsonify(response), 200


@crop_bp.route("/predict-regional", methods=["POST"])
@token_required
def predict_crop_regional(current_user):
    """
    Same input shape as /predict, but uses a model trained on Pakistan
    district-level data (13 locally-grown crops instead of the main
    model's 22 global crops). See notebooks/04_Regional_Crop_Model_Pakistan.ipynb.
    """
    from utils.model_loader import regional_crop_model, regional_crop_label_encoder

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"status": "error", "message": "Request body must be valid JSON."}), 400

    missing = [label for key, label in REQUIRED_FIELDS.items() if key not in data or data[key] in (None, "")]
    if missing:
        return jsonify({
            "status": "error",
            "message": f"Missing required field(s): {', '.join(missing)}."
        }), 400

    values = {}
    invalid = []
    for key, label in REQUIRED_FIELDS.items():
        try:
            values[key] = float(data[key])
        except (TypeError, ValueError):
            invalid.append(f"{label} must be a number (got: {data[key]!r}).")
    if invalid:
        return jsonify({"status": "error", "message": " ".join(invalid)}), 400

    features = [[
        values["nitrogen"], values["phosphorus"], values["potassium"],
        values["temperature"], values["humidity"], values["ph"], values["rainfall"],
    ]]

    try:
        proba = regional_crop_model.predict_proba(features)[0]
        predicted_idx = int(proba.argmax())
        crop_name = regional_crop_label_encoder.inverse_transform([predicted_idx])[0]
        confidence = float(proba[predicted_idx])
    except Exception as e:
        return jsonify({"status": "error", "message": f"Prediction failed unexpectedly: {e}"}), 500

    return jsonify({
        "status": "success",
        "recommended_crop": crop_name,
        "confidence": round(confidence, 4),
        "model": "regional-pakistan-13-crop",
    }), 200
