import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Events from './pages/Events';
import EventDetail from './pages/EventDetail';
import Organizer from './pages/Organizer';
import AdvancedDiag from './pages/AdvancedDiag';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Navbar />
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />

          {/* Any logged-in user */}
          <Route path="/events" element={
            <ProtectedRoute><Events /></ProtectedRoute>
          } />
          <Route path="/events/:id" element={
            <ProtectedRoute><EventDetail /></ProtectedRoute>
          } />

          {/* Organizer only */}
          <Route path="/organizer" element={
            <ProtectedRoute requiredRole="organizer"><Organizer /></ProtectedRoute>
          } />
          <Route path="/organizer/advanced" element={
            <ProtectedRoute requiredRole="organizer"><AdvancedDiag /></ProtectedRoute>
          } />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
