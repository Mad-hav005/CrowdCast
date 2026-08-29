import { useState } from 'react';
import { Link } from 'react-router-dom';
import { predictDemand } from '../services/api';
import RiskGauge from '../components/RiskGauge';
import RiskBadge from '../components/RiskBadge';
import './AdvancedDiag.css';

const defaults = {
  days_until_event: 5, event_hour: 19, is_weekend: 1,
  day_of_week: 'Saturday', city: 'Dallas', state: 'TX',
  metro: 'dallas', timezone: 'America/Chicago', addressCountryCode: 'US',
  listing_count: 80, section_count: 10, section_group_count: 5,
  max_available_lot: 6, avg_max_available_lot: 3.0,
  deal_rate: 0.25, ga_listing_rate: 0.65,
  listing_count_prev: 120, listing_change: -40,
  latitude: 32.7767, longitude: -96.797,
};

const FIELDS = [
  { key:'days_until_event', label:'Days Until Event', type:'number' },
  { key:'event_hour', label:'Event Hour (0-23)', type:'number', min:0, max:23 },
  { key:'is_weekend', label:'Is Weekend (0/1)', type:'number', min:0, max:1 },
  { key:'day_of_week', label:'Day of Week', type:'text' },
  { key:'city', label:'City', type:'text' },
  { key:'state', label:'State', type:'text' },
  { key:'metro', label:'Metro', type:'text' },
  { key:'timezone', label:'Timezone', type:'text' },
  { key:'addressCountryCode', label:'Country Code', type:'text' },
  { key:'listing_count', label:'Listing Count', type:'number' },
  { key:'section_count', label:'Section Count', type:'number' },
  { key:'section_group_count', label:'Section Group Count', type:'number' },
  { key:'max_available_lot', label:'Max Available Lot', type:'number' },
  { key:'avg_max_available_lot', label:'Avg Max Available Lot', type:'number', step:'0.1' },
  { key:'deal_rate', label:'Deal Rate (0–1)', type:'number', step:'0.01', min:0, max:1 },
  { key:'ga_listing_rate', label:'GA Listing Rate (0–1)', type:'number', step:'0.01', min:0, max:1 },
  { key:'listing_count_prev', label:'Listing Count (prev)', type:'number' },
  { key:'listing_change', label:'Listing Change', type:'number' },
  { key:'latitude', label:'Latitude', type:'number', step:'0.0001' },
  { key:'longitude', label:'Longitude', type:'number', step:'0.0001' },
];

export default function AdvancedDiag() {
  const [form, setForm] = useState(defaults);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const update = (k, v) => setForm(f => ({ ...f, [k]: v }));

  async function submit(e) {
    e.preventDefault();
    setLoading(true); setError(''); setResult(null);
    const payload = {};
    FIELDS.forEach(f => {
      payload[f.key] = f.type === 'number' ? Number(form[f.key]) : form[f.key];
    });
    try {
      const pred = await predictDemand(payload);
      setResult(pred);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  }

  return (
    <div className="diag-page">
      <Link to="/organizer" className="diag-page__back">← Organizer Dashboard</Link>
      <h1 className="diag-page__title">Advanced ML Diagnostics</h1>
      <p className="diag-page__sub">Send raw feature vectors directly to the ML model for inspection.</p>

      <form className="diag-form" onSubmit={submit}>
        <div className="diag-form__grid">
          {FIELDS.map(f => (
            <label key={f.key} className="diag-form__field">
              <span>{f.label}</span>
              <input type={f.type} value={form[f.key]}
                onChange={e => update(f.key, e.target.value)}
                step={f.step} min={f.min} max={f.max} />
            </label>
          ))}
        </div>
        <button type="submit" className="btn btn--primary btn--lg" disabled={loading}>
          {loading ? 'Running inference…' : 'Run Prediction'}
        </button>
      </form>

      {error && <div className="diag-error">⚠️ {error}</div>}

      {result && (
        <section className="diag-result">
          <RiskGauge probability={result.demand_probability} level={result.risk_level} size={160} />
          <div className="diag-result__info">
            <RiskBadge level={result.risk_level} size="lg" />
            <p>Probability: <strong>{(result.demand_probability * 100).toFixed(2)}%</strong></p>
            <p>Binary prediction: <strong>{result.prediction}</strong></p>
          </div>
        </section>
      )}
    </div>
  );
}
