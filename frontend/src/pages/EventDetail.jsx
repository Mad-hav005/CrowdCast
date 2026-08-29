import { useParams, useLocation, Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import DEMO_EVENTS, { eventToPayload } from '../data/demoEvents';
import { predictDemand } from '../services/api';
import RiskGauge from '../components/RiskGauge';
import RiskBadge from '../components/RiskBadge';
import MetricCard from '../components/MetricCard';
import './EventDetail.css';

const RISK_INFO = {
  LOW: {
    heading: 'Low Crowd Pressure',
    description: 'Ticket supply is comfortable relative to demand. No immediate risk of over-crowding.',
    recommendation: 'Continue monitoring. No urgent action is required.',
    color: '#10b981',
  },
  MODERATE: {
    heading: 'Moderate Crowd Pressure',
    description: 'Demand is building. Ticket listings are depleting at a noticeable rate.',
    recommendation: 'Review staffing plans and consider releasing additional inventory sections.',
    color: '#f59e0b',
  },
  HIGH: {
    heading: 'High Crowd Pressure',
    description: 'Significant listing depletion detected. The event is trending toward sell-out conditions.',
    recommendation: 'Increase on-site staff, activate overflow plans, and alert security teams.',
    color: '#f97316',
  },
  CRITICAL: {
    heading: 'Critical Crowd Pressure',
    description: 'Extreme demand-to-supply imbalance detected. Immediate operational response advised.',
    recommendation: 'Activate emergency crowd-management protocols. Consider capacity controls.',
    color: '#ef4444',
  },
};

export default function EventDetail() {
  const { id } = useParams();
  const location = useLocation();
  const [prediction, setPrediction] = useState(location.state?.prediction || null);
  const [loading, setLoading] = useState(!prediction);

  const event = location.state?.event || DEMO_EVENTS.find(e => e.id === id);

  useEffect(() => {
    if (prediction || !event) return;
    predictDemand(eventToPayload(event)).then(p => {
      setPrediction(p);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [event, prediction]);

  if (!event) return <div className="detail-page"><p>Event not found.</p><Link to="/events">← Back</Link></div>;

  const info = prediction ? RISK_INFO[prediction.risk_level] : null;
  const pct = prediction ? Math.round(prediction.demand_probability * 100) : null;

  return (
    <div className="detail-page">
      <Link to="/events" className="detail-page__back">← All Events</Link>

      {/* Header */}
      <header className="detail-header">
        <div className="detail-header__info">
          <span className="detail-header__category">{event.category}</span>
          <h1 className="detail-header__name">{event.name}</h1>
          <p className="detail-header__meta">{event.venue} &middot; {event.city}, {event.state}</p>
          <p className="detail-header__meta">{event.dateLabel} at {event.timeLabel}</p>
        </div>
        {prediction && (
          <div className="detail-header__gauge">
            <RiskGauge probability={prediction.demand_probability} level={prediction.risk_level} size={170} />
          </div>
        )}
      </header>

      {loading && <div className="detail-loading">Analysing event…</div>}

      {prediction && info && (
        <>
          {/* Risk explanation */}
          <section className="detail-risk-card" style={{ borderLeftColor: info.color }}>
            <div className="detail-risk-card__header">
              <RiskBadge level={prediction.risk_level} size="lg" />
              <h2 className="detail-risk-card__title">{info.heading}</h2>
            </div>
            <p className="detail-risk-card__desc">{info.description}</p>
            <div className="detail-risk-card__rec">
              <strong>Recommendation:</strong> {info.recommendation}
            </div>
          </section>

          {/* KPI row */}
          <section className="detail-metrics">
            <MetricCard label="Crowd Pressure" value={`${pct}%`} accent />
            <MetricCard label="Days Until Event" value={event.days_until_event} />
            <MetricCard label="Listings Available" value={event.listing_count} />
            <MetricCard label="Deal Rate" value={`${Math.round(event.deal_rate * 100)}%`} />
          </section>


          {/* Market detail table */}
          <section className="detail-table-box">
            <h3 className="detail-table-box__title">Market Snapshot</h3>
            <table className="detail-table">
              <tbody>
                <tr><td>Listing Count</td><td>{event.listing_count}</td></tr>
                <tr><td>Previous Listing Count</td><td>{event.listing_count_prev}</td></tr>
                <tr><td>Listing Change</td><td>{event.listing_change}</td></tr>
                <tr><td>Section Count</td><td>{event.section_count}</td></tr>
                <tr><td>Section Group Count</td><td>{event.section_group_count}</td></tr>
                <tr><td>Max Available Lot</td><td>{event.max_available_lot}</td></tr>
                <tr><td>Avg Max Available Lot</td><td>{event.avg_max_available_lot}</td></tr>
                <tr><td>Deal Rate</td><td>{(event.deal_rate * 100).toFixed(1)}%</td></tr>
                <tr><td>GA Listing Rate</td><td>{(event.ga_listing_rate * 100).toFixed(1)}%</td></tr>
              </tbody>
            </table>
          </section>
        </>
      )}
    </div>
  );
}
