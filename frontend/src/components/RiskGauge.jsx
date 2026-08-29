import './RiskGauge.css';
const COLORS = { LOW:'#10b981', MODERATE:'#f59e0b', HIGH:'#f97316', CRITICAL:'#ef4444' };
export default function RiskGauge({ probability, level, size = 160 }) {
  const pct = Math.round((probability ?? 0) * 100);
  const r = 40;
  const c = 2 * Math.PI * r;
  const offset = c - c * (probability ?? 0);
  const col = COLORS[level] || '#6b7280';
  return (
    <div className="risk-gauge" style={{ width: size, height: size }}>
      <svg viewBox="0 0 100 100">
        <circle className="risk-gauge__bg" cx="50" cy="50" r={r} />
        <circle className="risk-gauge__fill" cx="50" cy="50" r={r}
          style={{ stroke: col, strokeDasharray: c, strokeDashoffset: offset }} />
      </svg>
      <div className="risk-gauge__label">
        <span className="risk-gauge__pct" style={{ color: col }}>{pct}%</span>
        <span className="risk-gauge__sub">Crowd Pressure</span>
      </div>
    </div>
  );
}
