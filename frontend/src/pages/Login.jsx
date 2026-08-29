import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Login.css';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from || '/events';

  const [selectedRole, setSelectedRole] = useState(null);
  const [name, setName] = useState('');
  const [step, setStep] = useState('pick'); // 'pick' | 'name'

  function handleRoleSelect(role) {
    setSelectedRole(role);
    setStep('name');
  }

  function handleSubmit(e) {
    e.preventDefault();
    const displayName = name.trim() || (selectedRole === 'organizer' ? 'Organizer' : 'Guest');
    login(selectedRole, displayName);
    navigate(selectedRole === 'organizer' ? '/organizer' : from, { replace: true });
  }

  return (
    <div className="login-page">
      <div className="login-page__glow" />

      <div className="login-card">
        <div className="login-card__brand">
          <span className="login-card__logo">C</span>
          <span className="login-card__title">CrowdCast</span>
        </div>

        {step === 'pick' && (
          <>
            <h1 className="login-card__heading">Welcome</h1>
            <p className="login-card__sub">Choose how you'd like to sign in</p>

            <div className="login-roles">
              <button className="login-role-btn" onClick={() => handleRoleSelect('user')}>
                <div className="login-role-btn__icon">👤</div>
                <div className="login-role-btn__info">
                  <span className="login-role-btn__label">Attendee</span>
                  <span className="login-role-btn__desc">Browse events &amp; view demand forecasts</span>
                </div>
                <span className="login-role-btn__arrow">→</span>
              </button>

              <button className="login-role-btn login-role-btn--accent" onClick={() => handleRoleSelect('organizer')}>
                <div className="login-role-btn__icon">🎯</div>
                <div className="login-role-btn__info">
                  <span className="login-role-btn__label">Organizer</span>
                  <span className="login-role-btn__desc">Create events, manage forecasts &amp; diagnostics</span>
                </div>
                <span className="login-role-btn__arrow">→</span>
              </button>
            </div>
          </>
        )}

        {step === 'name' && (
          <form className="login-name-form" onSubmit={handleSubmit}>
            <button type="button" className="login-name-form__back" onClick={() => setStep('pick')}>← Back</button>
            <h2 className="login-card__heading">
              Sign in as {selectedRole === 'organizer' ? 'Organizer' : 'Attendee'}
            </h2>
            <p className="login-card__sub">Enter your name to continue</p>
            <input
              className="login-name-form__input"
              placeholder="Your name"
              value={name}
              onChange={e => setName(e.target.value)}
              autoFocus
            />
            <button type="submit" className="btn btn--primary btn--lg login-name-form__submit">
              Continue
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
