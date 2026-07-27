import { Link } from "react-router-dom";
import { Sprout, FlaskConical, TrendingUp } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Home() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="home">
      <section className="hero">
        <span className="hero__eyebrow">Precision Agriculture Decision Support</span>
        <h1>
          Know what to plant.
          <br />
          Know what to feed it.
        </h1>
        <p className="hero__subtitle">
          Machine-learning recommendations for crop selection and fertilizer
          dosing, built on soil nutrients, weather, and decades of Pakistani
          agricultural data.
        </p>

        <div className="hero__actions">
          {isAuthenticated ? (
            <Link to="/crop" className="btn btn--primary">
              Get a recommendation
            </Link>
          ) : (
            <>
              <Link to="/register" className="btn btn--primary">
                Get started free
              </Link>
              <Link to="/login" className="btn btn--ghost">
                Sign in
              </Link>
            </>
          )}
        </div>
      </section>

      <section className="feature-grid">
        <div className="feature-card">
          <Sprout size={26} strokeWidth={1.8} />
          <h3>Crop Recommendation</h3>
          <p>
            Enter soil nutrients (N-P-K), temperature, humidity, pH, and
            rainfall — get the best-suited crop from 22 options, trained on a
            balanced 2,200-record dataset.
          </p>
        </div>

        <div className="feature-card">
          <FlaskConical size={26} strokeWidth={1.8} />
          <h3>Fertilizer Recommendation</h3>
          <p>
            Combine soil type, crop type, and nutrient levels to get a
            fertilizer recommendation from 7 formulations, powered by an
            XGBoost classifier.
          </p>
        </div>

        <div className="feature-card">
          <TrendingUp size={26} strokeWidth={1.8} />
          <h3>Yield Trends</h3>
          <p>
            Historical FAOSTAT yield data (1961–2023) for 9 major crops,
            modeled with a chronologically-validated forecasting pipeline.
          </p>
        </div>
      </section>
    </div>
  );
}
