import { useState, useEffect } from 'react';
import DEMO_EVENTS, { eventToPayload } from '../data/demoEvents';
import { predictDemand } from '../services/api';
import EventCard from '../components/EventCard';
import './Events.css';

export default function Events() {
  const [predictions, setPredictions] = useState({});
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('ALL');
  const [apiOk, setApiOk] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function fetchAll() {
      const results = {};
      for (const evt of DEMO_EVENTS) {
        try {
          const pred = await predictDemand(eventToPayload(evt));
          if (!cancelled) results[evt.id] = pred;
        } catch {
          if (!cancelled) setApiOk(false);
        }
      }
      if (!cancelled) setPredictions(results);
    }
    fetchAll();
    return () => { cancelled = true; };
  }, []);

  const cats = ['ALL', ...new Set(DEMO_EVENTS.map(e => e.category))];

  const filtered = DEMO_EVENTS.filter(e => {
    if (filter !== 'ALL' && e.category !== filter) return false;
    if (search && !e.name.toLowerCase().includes(search.toLowerCase()) &&
        !e.venue.toLowerCase().includes(search.toLowerCase()) &&
        !e.city.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="events-page">
      <header className="events-page__header">
        <div>
          <h1 className="events-page__title">Event Intelligence</h1>
          <p className="events-page__sub">Live demand forecasts powered by the CrowdCast ML engine</p>
        </div>
        {!apiOk && (
          <div className="events-page__api-warn">
            ⚠️ Backend unavailable — ensure the API is running on port 8000
          </div>
        )}
      </header>

      <div className="events-page__controls">
        <input
          className="events-page__search"
          placeholder="Search events, venues, cities…"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <div className="events-page__filters">
          {cats.map(c => (
            <button key={c}
              className={`events-page__filter-btn ${filter === c ? 'active' : ''}`}
              onClick={() => setFilter(c)}>{c}</button>
          ))}
        </div>
      </div>

      <div className="events-page__grid">
        {filtered.map(evt => (
          <EventCard key={evt.id} event={evt} prediction={predictions[evt.id]} />
        ))}
        {filtered.length === 0 && (
          <p className="events-page__empty">No events match your search.</p>
        )}
      </div>
    </div>
  );
}
