import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/**
 * Wraps a route that requires authentication.
 * @param {string} requiredRole - 'any' (just logged in), 'organizer' (organizer only)
 */
export default function ProtectedRoute({ children, requiredRole = 'any' }) {
  const { isLoggedIn, isOrganizer } = useAuth();
  const location = useLocation();

  if (!isLoggedIn) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }

  if (requiredRole === 'organizer' && !isOrganizer) {
    return (
      <div style={{ maxWidth: 600, margin: '80px auto', textAlign: 'center', padding: '0 24px' }}>
        <h2 style={{ marginBottom: 8 }}>🔒 Organizer Access Only</h2>
        <p style={{ color: 'var(--clr-muted)', marginBottom: 20 }}>
          You need to sign in as an <strong>Organizer</strong> to access this page.
        </p>
        <a href="/login" style={{ color: 'var(--clr-accent)' }}>Switch account →</a>
      </div>
    );
  }

  return children;
}
