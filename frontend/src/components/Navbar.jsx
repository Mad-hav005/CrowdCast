import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Navbar.css';

export default function Navbar() {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const { auth, isLoggedIn, isOrganizer, logout } = useAuth();
  const isOrg = pathname.startsWith('/organizer');

  function handleLogout() {
    logout();
    navigate('/login');
  }

  return (
    <nav className="navbar">
      <Link to="/" className="navbar__brand">
        <span className="navbar__logo">C</span>
        <span className="navbar__title">CrowdCast</span>
      </Link>

      <div className="navbar__links">
        {isLoggedIn && (
          <Link to="/events" className={`navbar__link ${pathname === '/events' || pathname.startsWith('/events/') ? 'active' : ''}`}>Events</Link>
        )}
        {isLoggedIn && isOrganizer && (
          <Link to="/organizer" className={`navbar__link ${isOrg ? 'active' : ''}`}>Organizer</Link>
        )}

        {isLoggedIn ? (
          <div className="navbar__user">
            <span className="navbar__user-badge" data-role={auth.role}>
              {auth.role === 'organizer' ? '🎯' : '👤'} {auth.name}
            </span>
            <button className="navbar__logout-btn" onClick={handleLogout}>Logout</button>
          </div>
        ) : (
          <Link to="/login" className="navbar__link navbar__link--login">Sign In</Link>
        )}
      </div>
    </nav>
  );
}
