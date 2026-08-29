import { Link } from 'react-router-dom';
import RiskBadge from './RiskBadge';
import './EventCard.css';

export default function EventCard({ event, prediction, variant = 'default' }) {
  const pct = prediction ? Math.round(prediction.demand_probability * 100) : null;
  const cardClass = `event-card event-card--${variant}`;
  return (
    <Link to={`/events/${event.id}`} className={cardClass} state={{ event, prediction }}>
      <div className="event-card__top">
        <span className="event-card__category">{event.category}</span>
        {prediction && <RiskBadge level={prediction.risk_level} size="sm" />}
      </div>
      <h3 className="event-card__name">{event.name}</h3>
      <p className="event-card__venue">{event.venue}</p>
      <p className="event-card__meta">{event.city}, {event.state} &middot; {event.dateLabel}</p>
      <p className="event-card__time">{event.timeLabel}</p>
      {pct !== null && (
        <div className="event-card__pressure">
          <span className="event-card__pressure-label">Crowd Pressure</span>
          <div className="event-card__bar-track">
            <div className="event-card__bar-fill" data-level={prediction.risk_level.toLowerCase()} style={{ width: `${pct}%` }} />
          </div>
          <span className="event-card__pressure-pct">{pct}%</span>
        </div>
      )}
    </Link>
  );
}
