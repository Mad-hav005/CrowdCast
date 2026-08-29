import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Landing.css';

export default function Landing() {
  const { isLoggedIn, isOrganizer } = useAuth();

  return (
    <div className="landing">
      {/* Hero */}
      <section className="hero">
        <div className="hero__glow" />
        <div className="hero__content">
          <span className="hero__badge">AI-Powered Intelligence</span>
          <h1 className="hero__title">
            Predict Crowd Pressure<br />
            <span className="hero__accent">Before It Happens</span>
          </h1>
          <p className="hero__sub">
            CrowdCast analyses ticket-market signals in real-time to forecast
            event demand risk — helping organizers plan smarter and safer events.
          </p>
          <div className="hero__actions">
            {isLoggedIn ? (
              <>
                <Link to="/events" className="btn btn--primary btn--lg">Explore Events</Link>
                {isOrganizer && <Link to="/organizer" className="btn btn--ghost btn--lg">Organizer Dashboard</Link>}
              </>
            ) : (
              <Link to="/login" className="btn btn--primary btn--lg">Get Started</Link>
            )}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="features">
        <div className="features__grid">
          <div className="feature-box">
            <div className="feature-box__icon">📊</div>
            <h3 className="feature-box__title">Demand Forecasting</h3>
            <p className="feature-box__desc">
              Our Random Forest model evaluates 29 market features to produce
              calibrated crowd-pressure probabilities.
            </p>
          </div>
          <div className="feature-box">
            <div className="feature-box__icon">⚡</div>
            <h3 className="feature-box__title">Real-time Risk Levels</h3>
            <p className="feature-box__desc">
              Events are classified across four tiers — Low, Moderate, High,
              and Critical — so you can act instantly.
            </p>
          </div>
          <div className="feature-box">
            <div className="feature-box__icon">🎯</div>
            <h3 className="feature-box__title">Actionable Insights</h3>
            <p className="feature-box__desc">
              Every prediction comes with contextual recommendations tailored
              to your event's risk profile.
            </p>
          </div>
        </div>
      </section>

      {/* Stats strip */}
      <section className="stats-strip">
        <div className="stats-strip__item">
          <span className="stats-strip__value">29</span>
          <span className="stats-strip__label">ML Features</span>
        </div>
        <div className="stats-strip__item">
          <span className="stats-strip__value">4</span>
          <span className="stats-strip__label">Risk Tiers</span>
        </div>
        <div className="stats-strip__item">
          <span className="stats-strip__value">&lt;200ms</span>
          <span className="stats-strip__label">Inference</span>
        </div>
      </section>
    </div>
  );
}
