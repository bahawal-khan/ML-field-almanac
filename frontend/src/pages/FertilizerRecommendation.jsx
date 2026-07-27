import { useState } from "react";
import { FlaskConical } from "lucide-react";
import { predictFertilizer } from "../api/client";

const SOIL_TYPES = ["Black", "Clayey", "Loamy", "Red", "Sandy"];
const CROP_TYPES = [
  "Barley", "Cotton", "Ground Nuts", "Maize", "Millets",
  "Oil seeds", "Paddy", "Pulses", "Sugarcane", "Tobacco", "Wheat",
];

const NUMERIC_FIELDS = [
  { name: "temperature", label: "Temperature", placeholder: "e.g. 26", unit: "°C" },
  { name: "humidity", label: "Humidity", placeholder: "e.g. 52", unit: "%" },
  { name: "moisture", label: "Moisture", placeholder: "e.g. 38", unit: "%" },
  { name: "nitrogen", label: "Nitrogen (N)", placeholder: "e.g. 37", unit: "" },
  { name: "potassium", label: "Potassium (K)", placeholder: "e.g. 0", unit: "" },
  { name: "phosphorous", label: "Phosphorous (P)", placeholder: "e.g. 0", unit: "" },
];

const SAMPLE = {
  temperature: "26", humidity: "52", moisture: "38",
  nitrogen: "37", potassium: "0", phosphorous: "0",
  soil_type: "Sandy", crop_type: "Maize",
};

export default function FertilizerRecommendation() {
  const [form, setForm] = useState({
    ...Object.fromEntries(NUMERIC_FIELDS.map((f) => [f.name, ""])),
    soil_type: SOIL_TYPES[0],
    crop_type: CROP_TYPES[0],
  });
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSample = () => {
    setForm(SAMPLE);
    setResult(null);
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    setResult(null);
    try {
      const data = await predictFertilizer(form);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.message || "Prediction failed. Please check your input.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="predict-page">
      <div className="predict-page__header">
        <span className="predict-page__eyebrow">Fertilizer Recommendation</span>
        <h1>What should you feed it?</h1>
        <p>Enter soil, crop, and nutrient details to get a fertilizer recommendation.</p>
      </div>

      <div className="predict-page__grid">
        <form className="predict-form" onSubmit={handleSubmit}>
          <div className="predict-form__fields">
            <label className="field">
              <span>Soil Type</span>
              <select name="soil_type" value={form.soil_type} onChange={handleChange}>
                {SOIL_TYPES.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </label>

            <label className="field">
              <span>Crop Type</span>
              <select name="crop_type" value={form.crop_type} onChange={handleChange}>
                {CROP_TYPES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </label>

            {NUMERIC_FIELDS.map((f) => (
              <label className="field" key={f.name}>
                <span>
                  {f.label} {f.unit && <em>({f.unit})</em>}
                </span>
                <input
                  type="number"
                  step="any"
                  name={f.name}
                  value={form[f.name]}
                  onChange={handleChange}
                  placeholder={f.placeholder}
                  required
                />
              </label>
            ))}
          </div>

          {error && <p className="field__error">{error}</p>}

          <div className="predict-form__actions">
            <button type="submit" className="btn btn--primary" disabled={loading}>
              {loading ? "Analyzing…" : "Recommend a fertilizer"}
            </button>
            <button type="button" className="btn btn--ghost" onClick={handleSample}>
              Fill sample values
            </button>
          </div>
        </form>

        <div className="result-panel">
          {!result && !loading && (
            <div className="result-panel__empty">
              <FlaskConical size={40} strokeWidth={1.3} />
              <p>Your recommended fertilizer will appear here.</p>
            </div>
          )}

          {loading && (
            <div className="result-panel__loading">
              <div className="loading-spinner" />
              <p>Analyzing soil and crop data…</p>
            </div>
          )}

          {result && !loading && (
            <div className="result-card result-card--fertilizer">
              <span className="result-card__label">Recommended fertilizer</span>
              <h2 className="result-card__value">{result.recommended_fertilizer}</h2>
              {result.confidence != null && (
                <p className="result-card__confidence">
                  {(result.confidence * 100).toFixed(0)}% confidence
                </p>
              )}
              {result.explanation && (
                <div className="result-card__explanation">
                  <p className="result-card__why">{result.explanation.summary}</p>
                  <ul className="factor-list">
                    {result.explanation.top_factors.map((f, i) => (
                      <li key={i}>
                        <span className="factor-list__name">{f.feature}</span>
                        {f.your_value != null && (
                          <span className="factor-list__value">
                            your value: {f.your_value}
                            {f.typical_for_this_fertilizer != null &&
                              ` · typical: ${f.typical_for_this_fertilizer}`}
                          </span>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
