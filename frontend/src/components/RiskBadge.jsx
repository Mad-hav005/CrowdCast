import './RiskBadge.css';
export default function RiskBadge({ level, size = 'md' }) {
  const cls = `risk-badge risk-badge--${(level || 'unknown').toLowerCase()} risk-badge--${size}`;
  return <span className={cls}>{level || '—'}</span>;
}
