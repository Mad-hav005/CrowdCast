import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import DEMO_EVENTS, { eventToPayload } from '../data/demoEvents';
import { predictDemand } from '../services/api';
import EventCard from '../components/EventCard';
import RiskGauge from '../components/RiskGauge';
import RiskBadge from '../components/RiskBadge';
import MetricCard from '../components/MetricCard';
import './Organizer.css';

/* ── city → default metadata lookup ── */
const CITY_META = {
  Dallas:    { state:'TX', metro:'dallas',      tz:'America/Chicago',      lat:32.7767,  lng:-96.7970 },
  Houston:   { state:'TX', metro:'houston',     tz:'America/Chicago',      lat:29.7604,  lng:-95.3698 },
  Austin:    { state:'TX', metro:'austin',      tz:'America/Chicago',      lat:30.2672,  lng:-97.7431 },
  Phoenix:   { state:'AZ', metro:'phoenix',     tz:'America/Phoenix',      lat:33.4484,  lng:-112.0740 },
  Boston:    { state:'MA', metro:'boston',       tz:'America/New_York',     lat:42.3601,  lng:-71.0589 },
  'San Jose':{ state:'CA', metro:'sanfrancisco',tz:'America/Los_Angeles',  lat:37.3382,  lng:-121.8863 },
  'New York':{ state:'NY', metro:'newyork',     tz:'America/New_York',     lat:40.7128,  lng:-74.0060 },
  Chicago:   { state:'IL', metro:'chicago',     tz:'America/Chicago',      lat:41.8781,  lng:-87.6298 },
  'Los Angeles':{ state:'CA', metro:'losangeles', tz:'America/Los_Angeles', lat:34.0522, lng:-118.2437 },
};

const DAYS_OF_WEEK = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];

const initialForm = {
  name: '', venue: '', city: 'Dallas', category: 'Concert',
  dateStr: '', timeStr: '19:00',
  listing_count: 100, listing_count_prev: 120,
  section_count: 10, section_group_count: 5,
  max_available_lot: 6, avg_max_available_lot: 3.0,
  deal_rate: 25, ga_listing_rate: 65,
};

export default function Organizer() {
  const [events, setEvents] = useState(DEMO_EVENTS);
  const [predictions, setPredictions] = useState({});
  const [form, setForm] = useState(initialForm);
  const [showForm, setShowForm] = useState(false);
  const [createResult, setCreateResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  /* fetch predictions for the event list */
  useEffect(() => {
    let cancelled = false;
    (async () => {
      const res = {};
      for (const evt of events) {
        try {
          const p = await predictDemand(eventToPayload(evt));
          if (!cancelled) res[evt.id] = p;
        } catch { /* skip */ }
      }
      if (!cancelled) setPredictions(res);
    })();
    return () => { cancelled = true; };
  }, [events]);

  const update = (key, val) => setForm(f => ({ ...f, [key]: val }));

  async function handleCreate(e) {
    e.preventDefault();
    setSubmitting(true);
    setCreateResult(null);

    const meta = CITY_META[form.city] || CITY_META.Dallas;
    const evtDate = form.dateStr ? new Date(form.dateStr + 'T' + form.timeStr) : new Date();
    const now = new Date();
    const daysUntil = Math.max(0, Math.round((evtDate - now) / 86400000));
    const [hh] = form.timeStr.split(':').map(Number);
    const dow = DAYS_OF_WEEK[evtDate.getDay()];
    const isWknd = evtDate.getDay() === 0 || evtDate.getDay() === 6 ? 1 : 0;

    const listingCount = Number(form.listing_count);
    const listingCountPrev = Number(form.listing_count_prev);
    const listingChange = listingCount - listingCountPrev;

    const payload = {
      days_until_event: daysUntil,
      event_hour: hh,
      is_weekend: isWknd,
      day_of_week: dow,
      city: form.city,
      state: meta.state,
      metro: meta.metro,
      timezone: meta.tz,
      addressCountryCode: 'US',
      listing_count: listingCount,
      section_count: Number(form.section_count),
      section_group_count: Number(form.section_group_count),
      max_available_lot: Number(form.max_available_lot),
      avg_max_available_lot: Number(form.avg_max_available_lot),
      deal_rate: Number(form.deal_rate) / 100,
      ga_listing_rate: Number(form.ga_listing_rate) / 100,
      listing_count_prev: listingCountPrev,
      listing_change: listingChange,
      latitude: meta.lat,
      longitude: meta.lng,
    };

    try {
      const pred = await predictDemand(payload);
      const newEvt = {
        id: `org-${Date.now()}`,
        name: form.name || 'Untitled Event',
        venue: form.venue || 'TBD',
        city: form.city,
        state: meta.state,
        country: 'US',
        metro: meta.metro,
        timezone: meta.tz,
        latitude: meta.lat,
        longitude: meta.lng,
        dateLabel: evtDate.toLocaleDateString('en-US', { month:'short', day:'numeric', year:'numeric' }),
        timeLabel: evtDate.toLocaleTimeString('en-US', { hour:'numeric', minute:'2-digit' }),
        category: form.category,
        ...payload,
      };
      setEvents(prev => [newEvt, ...prev]);
      setPredictions(prev => ({ ...prev, [newEvt.id]: pred }));
      setCreateResult(pred);
      setShowForm(false);
    } catch (err) {
      setCreateResult({ error: err.message });
    }
    setSubmitting(false);
  }

  function handleDelete(id) {
    setEvents(prev => prev.filter(e => e.id !== id));
    setPredictions(prev => { const c = { ...prev }; delete c[id]; return c; });
  }

  /* Aggregate stats */
  const predArr = Object.values(predictions);
  const critCount = predArr.filter(p => p.risk_level === 'CRITICAL' || p.risk_level === 'HIGH').length;
  const avgPressure = predArr.length
    ? Math.round(predArr.reduce((s, p) => s + p.demand_probability, 0) / predArr.length * 100)
    : 0;

  return (
    <div className="org-page">
      <header className="org-page__header">
        <div>
          <h1 className="org-page__title">Organizer Dashboard</h1>
          <p className="org-page__sub">Manage events and monitor crowd-pressure forecasts</p>
        </div>
        <div className="org-page__actions">
          <button className="btn btn--primary btn--md" onClick={() => { setShowForm(s => !s); setCreateResult(null); }}>
            {showForm ? 'Cancel' : '+ New Event'}
          </button>
          <Link to="/organizer/advanced" className="btn btn--ghost btn--md">Advanced Diagnostics</Link>
        </div>
      </header>

      {/* Summary KPIs */}
      <section className="org-page__kpis">
        <MetricCard label="Total Events" value={events.length} />
        <MetricCard label="High / Critical" value={critCount} accent={critCount > 0} />
        <MetricCard label="Avg Pressure" value={`${avgPressure}%`} />
        <MetricCard label="Predictions" value={predArr.length} />
      </section>

      {/* Create-event form */}
      {showForm && (
        <section className="org-form-section">
          <h2 className="org-form-section__title">Create New Event</h2>
          <form className="org-form" onSubmit={handleCreate}>
            <div className="org-form__row">
              <label className="org-form__field">
                <span>Event Name</span>
                <input value={form.name} onChange={e => update('name', e.target.value)} placeholder="Summer Festival 2026" required />
              </label>
              <label className="org-form__field">
                <span>Venue</span>
                <input value={form.venue} onChange={e => update('venue', e.target.value)} placeholder="Main Arena" />
              </label>
            </div>
            <div className="org-form__row">
              <label className="org-form__field">
                <span>City</span>
                <select value={form.city} onChange={e => update('city', e.target.value)}>
                  {Object.keys(CITY_META).map(c => <option key={c}>{c}</option>)}
                </select>
              </label>
              <label className="org-form__field">
                <span>Category</span>
                <select value={form.category} onChange={e => update('category', e.target.value)}>
                  {['Concert','Festival','EDM','Rock','Jazz','Electronic','Theater','Sports'].map(c => <option key={c}>{c}</option>)}
                </select>
              </label>
              <label className="org-form__field">
                <span>Date</span>
                <input type="date" value={form.dateStr} onChange={e => update('dateStr', e.target.value)} required />
              </label>
              <label className="org-form__field">
                <span>Time</span>
                <input type="time" value={form.timeStr} onChange={e => update('timeStr', e.target.value)} />
              </label>
            </div>

            <h3 className="org-form__subtitle">Ticket Supply & Market Context</h3>
            <div className="org-form__row">
              <label className="org-form__field">
                <span>Tickets Currently Listed</span>
                <span className="org-form__help">Total tickets available for sale right now</span>
                <input type="number" min="0" value={form.listing_count} onChange={e => update('listing_count', e.target.value)} />
              </label>
              <label className="org-form__field">
                <span>Tickets Listed Last Week</span>
                <span className="org-form__help">Used to compute inventory velocity</span>
                <input type="number" min="0" value={form.listing_count_prev} onChange={e => update('listing_count_prev', e.target.value)} />
              </label>
            </div>
            <div className="org-form__row">
              <label className="org-form__field">
                <span>Venue Seating Sections</span>
                <span className="org-form__help">Physical sections containing listings</span>
                <input type="number" min="0" value={form.section_count} onChange={e => update('section_count', e.target.value)} />
              </label>
              <label className="org-form__field">
                <span>Ticket Pricing Tiers</span>
                <span className="org-form__help">Distinct seat categories (e.g. Balcony, Floor)</span>
                <input type="number" min="0" value={form.section_group_count} onChange={e => update('section_group_count', e.target.value)} />
              </label>
            </div>
            <div className="org-form__row">
              <label className="org-form__field">
                <span>Max Purchase Group Size</span>
                <span className="org-form__help">Max tickets purchasable in a single order</span>
                <input type="number" min="0" value={form.max_available_lot} onChange={e => update('max_available_lot', e.target.value)} />
              </label>
              <label className="org-form__field">
                <span>Avg Listing Group Size</span>
                <span className="org-form__help">Average quantity of tickets per listed offer</span>
                <input type="number" min="0" step="0.1" value={form.avg_max_available_lot} onChange={e => update('avg_max_available_lot', e.target.value)} />
              </label>
            </div>
            <div className="org-form__row">
              <label className="org-form__field">
                <span>Great Deals Ratio ({form.deal_rate}%)</span>
                <span className="org-form__help">Percentage of listings priced below typical face value</span>
                <input type="range" min="0" max="100" value={form.deal_rate} onChange={e => update('deal_rate', e.target.value)} />
              </label>
              <label className="org-form__field">
                <span>General Admission (GA) Ratio ({form.ga_listing_rate}%)</span>
                <span className="org-form__help">Percentage of standing room/general admission tickets</span>
                <input type="range" min="0" max="100" value={form.ga_listing_rate} onChange={e => update('ga_listing_rate', e.target.value)} />
              </label>
            </div>

            <div className="org-form__submit-row">
              <button type="submit" className="btn btn--primary btn--lg" disabled={submitting}>
                {submitting ? 'Analysing…' : 'Create & Analyse'}
              </button>
            </div>
          </form>
        </section>
      )}

      {/* Prediction result callout */}
      {createResult && !createResult.error && (
        <section className="org-result-card">
          <div className="org-result-card__left">
            <RiskGauge probability={createResult.demand_probability} level={createResult.risk_level} size={120} />
          </div>
          <div className="org-result-card__right">
            <RiskBadge level={createResult.risk_level} size="lg" />
            <p className="org-result-card__txt">Crowd pressure probability: <strong>{Math.round(createResult.demand_probability * 100)}%</strong></p>
          </div>
        </section>
      )}
      {createResult?.error && (
        <div className="org-result-error">⚠️ {createResult.error}</div>
      )}

      {/* Event grid */}
      <section className="org-page__events">
        <h2 className="org-page__events-title">Your Events</h2>
        <div className="org-page__grid">
          {events.map(evt => (
            <div key={evt.id} className="org-page__card-wrap">
              <EventCard event={evt} prediction={predictions[evt.id]} variant="flat" />
              <div className="org-page__card-actions">
                <button className="org-page__delete-btn btn btn--danger btn--sm" onClick={() => handleDelete(evt.id)}>
                  🗑️ Delete Event
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
