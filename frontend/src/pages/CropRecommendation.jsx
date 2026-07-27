import { useState } from "react";
import { Sprout } from "lucide-react";
import { predictCrop } from "../api/client";

const FIELDS = [
  { name: "nitrogen", label: "Nitrogen (N)", placeholder: "e.g. 90", unit: "kg/ha" },
  { name: "phosphorus", label: "Phosphorus (P)", placeholder: "e.g. 42", unit: "kg/ha" },
  { name: "potassium", label: "Potassium (K)", placeholder: "e.g. 43", unit: "kg/ha" },
  { name: "temperature", label: "Temperature", placeholder: "e.g. 25.5", unit: "°C" },
  { name: "humidity", label: "Humidity", placeholder: "e.g. 82", unit: "%" },
  { name: "ph", label: "Soil pH", placeholder: "e.g. 6.5", unit: "" },
  { name: "rainfall", label: "Rainfall", placeholder: "e.g. 210", unit: "mm" },
];

const SAMPLE = {
  nitrogen: "90", phosphorus: "42", potassium: "43",
  temperature: "25.5", humidity: "82", ph: "6.5", rainfall: "210",
};

export default function CropRecommendation() {
  const [form, setForm] = useState(
    Object.fromEntries(FIELDS.map((f) => [f.name, ""]))
  );
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
      const data = await predictCrop(form);
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
        <span className="predict-page__eyebrow">Crop Recommendation</span>
        <h1>What should you plant?</h1>
        <p>Enter your soil and climate readings to get the recommended crop.</p>
      </div>

      <div className="predict-page__grid">
        <form className="predict-form" onSubmit={handleSubmit}>
          <div className="predict-form__fields">
            {FIELDS.map((f) => (
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
              {loading ? "Analyzing…" : "Recommend a crop"}
            </button>
            <button type="button" className="btn btn--ghost" onClick={handleSample}>
              Fill sample values
            </button>
          </div>
        </form>

        <div className="result-panel">
          {!result && !loading && (
            <div className="result-panel__empty">
              <Sprout size={40} strokeWidth={1.3} />
              <p>Your recommended crop will appear here.</p>
            </div>
          )}

          {loading && (
            <div className="result-panel__loading">
              <div className="loading-spinner" />
              <p>Analyzing soil and climate data…</p>
            </div>
          )}

          {result && !loading && (
            <div className="result-card result-card--crop">
              <span className="result-card__label">Recommended crop</span>
              <h2 className="result-card__value">{result.recommended_crop}</h2>
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
                        <span className="factor-list__value">
                          your value: {f.your_value}
                          {f.typical_for_this_crop != null && ` · typical: ${f.typical_for_this_crop}`}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {result.warnings && (
                <p className="result-card__warning">⚠ {result.warnings.join(" ")}</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
