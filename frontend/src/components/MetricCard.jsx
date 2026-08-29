import './MetricCard.css';
export default function MetricCard({ label, value, sub, accent }) {
  return (
    <div className={`metric-card ${accent ? 'metric-card--accent' : ''}`}>
      <span className="metric-card__value">{value}</span>
      <span className="metric-card__label">{label}</span>
      {sub && <span className="metric-card__sub">{sub}</span>}
    </div>
  );
}
