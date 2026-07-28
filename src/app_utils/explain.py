"""
Prediction explainability using SHAP.

Answers "why was this crop/fertilizer recommended, and not something else?"
by computing per-prediction SHAP values (exact, fast for tree models) and
comparing the user's input against the typical (mean) values for the
predicted class, pulled from the training data.
"""

import os
import numpy as np
import pandas as pd
import shap

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")

# Human-readable labels for each raw feature name
CROP_FEATURE_LABELS = {
    "N": "nitrogen level",
    "P": "phosphorus level",
    "K": "potassium level",
    "temperature": "temperature",
    "humidity": "humidity",
    "ph": "soil pH",
    "rainfall": "rainfall",
}

FERTILIZER_FEATURE_LABELS = {
    "Temperature": "temperature",
    "Humidity": "humidity",
    "Moisture": "soil moisture",
    "Nitrogen": "nitrogen level",
    "Potassium": "potassium level",
    "Phosphorous": "phosphorous level",
}

_crop_stats = None
_fertilizer_stats = None


def _load_crop_stats():
    global _crop_stats
    if _crop_stats is None:
        _crop_stats = pd.read_csv(os.path.join(MODEL_DIR, "crop_feature_stats.csv"), index_col=0)
    return _crop_stats


def _load_fertilizer_stats():
    global _fertilizer_stats
    if _fertilizer_stats is None:
        _fertilizer_stats = pd.read_csv(
            os.path.join(MODEL_DIR, "fertilizer_feature_stats.csv"), index_col=0
        )
    return _fertilizer_stats


def _direction_phrase(user_value, class_mean, class_std):
    """Describe how the user's value compares to what's typical for this class."""
    if class_std is None or class_std == 0 or pd.isna(class_std):
        return "in line with"
    z = (user_value - class_mean) / class_std
    if z > 0.75:
        return "notably higher than"
    if z < -0.75:
        return "notably lower than"
    return "in line with"


def explain_crop_prediction(model, label_encoder, features_dict, predicted_crop, proba):
    """
    Returns a dict with the top contributing factors and a plain-language
    summary for why `predicted_crop` was recommended.
    """
    feature_order = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
    sample = pd.DataFrame([[features_dict[f] for f in feature_order]], columns=feature_order)

    predicted_idx = int(label_encoder.transform([predicted_crop])[0])

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(sample)  # shape: (1, n_features, n_classes)
    class_shap = shap_values[0, :, predicted_idx]

    stats = _load_crop_stats()
    class_row = stats.loc[predicted_crop] if predicted_crop in stats.index else None

    contributions = []
    for i, feat in enumerate(feature_order):
        contributions.append({
            "feature": feat,
            "label": CROP_FEATURE_LABELS.get(feat, feat),
            "value": features_dict[feat],
            "shap_value": float(class_shap[i]),
        })

    contributions.sort(key=lambda c: abs(c["shap_value"]), reverse=True)
    top = [c for c in contributions if c["shap_value"] > 0][:3]
    if not top:
        top = contributions[:3]

    factors = []
    sentence_parts = []
    for c in top:
        mean_key, std_key = f"{c['feature']}_mean", f"{c['feature']}_std"
        mean_val = class_row[mean_key] if class_row is not None and mean_key in class_row else None
        std_val = class_row[std_key] if class_row is not None and std_key in class_row else None
        direction = _direction_phrase(c["value"], mean_val, std_val) if mean_val is not None else "a key factor for"

        factors.append({
            "feature": c["label"],
            "your_value": c["value"],
            "typical_for_this_crop": round(float(mean_val), 1) if mean_val is not None else None,
            "impact": "increases likelihood" if c["shap_value"] > 0 else "decreases likelihood",
        })
        sentence_parts.append(f"your {c['label']} ({c['value']}) is {direction} typical {predicted_crop} conditions")

    confidence = float(proba)
    summary = (
        f"{predicted_crop.capitalize()} was recommended with {confidence*100:.0f}% confidence, "
        f"mainly because {', '.join(sentence_parts)}."
    )

    return {"top_factors": factors, "summary": summary}


def explain_fertilizer_prediction(model, label_encoder, features_dict, predicted_fertilizer, proba):
    """Same idea as explain_crop_prediction, for the fertilizer pipeline model."""
    sample = pd.DataFrame([features_dict])

    prep = model.named_steps["preprocessor"]
    clf = model.named_steps["classifier"]

    X_transformed = prep.transform(sample)
    feat_names = prep.get_feature_names_out()

    predicted_idx = int(label_encoder.transform([predicted_fertilizer])[0])

    explainer = shap.TreeExplainer(clf)
    shap_values = explainer.shap_values(X_transformed)
    class_shap = shap_values[0, :, predicted_idx]

    stats = _load_fertilizer_stats()
    class_row = stats.loc[predicted_fertilizer] if predicted_fertilizer in stats.index else None

    contributions = []
    for i, raw_name in enumerate(feat_names):
        # raw_name looks like "num__Temperature" or "cat__Soil Type_Sandy"
        clean_name = raw_name.split("__", 1)[-1]
        contributions.append({
            "raw": clean_name,
            "shap_value": float(class_shap[i]),
        })

    contributions.sort(key=lambda c: abs(c["shap_value"]), reverse=True)
    top = [c for c in contributions if c["shap_value"] > 0][:3]
    if not top:
        top = contributions[:3]

    factors = []
    sentence_parts = []
    for c in top:
        raw = c["raw"]
        # Numeric feature (matches FERTILIZER_FEATURE_LABELS keys directly)
        if raw in FERTILIZER_FEATURE_LABELS:
            label = FERTILIZER_FEATURE_LABELS[raw]
            user_val = features_dict.get(raw)
            mean_key, std_key = f"{raw}_mean", f"{raw}_std"
            mean_val = class_row[mean_key] if class_row is not None and mean_key in class_row else None
            std_val = class_row[std_key] if class_row is not None and std_key in class_row else None
            direction = _direction_phrase(user_val, mean_val, std_val) if mean_val is not None else "a key factor for"
            factors.append({
                "feature": label,
                "your_value": user_val,
                "typical_for_this_fertilizer": round(float(mean_val), 1) if mean_val is not None else None,
                "impact": "increases likelihood" if c["shap_value"] > 0 else "decreases likelihood",
            })
            sentence_parts.append(f"your {label} ({user_val}) is {direction} typical values for {predicted_fertilizer}")
        else:
            # Categorical (soil type / crop type) - just name it directly
            pretty = raw.replace("_", ": ", 1)
            factors.append({
                "feature": pretty,
                "impact": "increases likelihood" if c["shap_value"] > 0 else "decreases likelihood",
            })
            sentence_parts.append(f"your {pretty.lower()} strongly matches this fertilizer's typical use case")

    confidence = float(proba)
    summary = (
        f"{predicted_fertilizer} was recommended with {confidence*100:.0f}% confidence, "
        f"mainly because {', '.join(sentence_parts)}."
    )

    return {"top_factors": factors, "summary": summary}
