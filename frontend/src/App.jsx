import { BrowserRouter, Routes, Route, Link, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import UploadPage from './pages/UploadPage'
import TestPage from './pages/TestPage'
import './App.css'

function PublicOnlyRoute({ children }) {
  const { user } = useAuth();

  if (user) return <Navigate to="/dashboard" replace />;

  return children;
}

function Navigation() {
  const { user, logout } = useAuth();

  return (
    <nav style={{
      padding: '20px',
      backgroundColor: '#f0f0f0',
      borderBottom: '2px solid #ddd',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center'
    }}>
      <h2 style={{ margin: 0 }}>Academic Assignment Helper</h2>
      <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
        <Link to="/test" style={{ textDecoration: 'none', color: '#666' }}>Test</Link>
        {user ? (
          <>
            <Link to="/dashboard" style={{ textDecoration: 'none', color: '#0066cc' }}>Dashboard</Link>
            <Link to="/upload" style={{ textDecoration: 'none', color: '#0066cc' }}>Upload</Link>
            <button
              onClick={logout}
              style={{
                padding: '8px 16px',
                backgroundColor: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login" style={{ textDecoration: 'none', color: '#0066cc' }}>Login</Link>
            <Link to="/register" style={{ textDecoration: 'none', color: '#0066cc' }}>Register</Link>
          </>
        )}
      </div>
    </nav>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div style={{ fontFamily: 'sans-serif', height: '100vh', display: 'flex', flexDirection: 'column' }}>
          <Navigation />
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/test" element={<TestPage />} />
            <Route path="/login" element={
              <PublicOnlyRoute>
                <LoginPage />
              </PublicOnlyRoute>
            } />
            <Route path="/register" element={
              <PublicOnlyRoute>
                <RegisterPage />
              </PublicOnlyRoute>
            } />
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            } />
            <Route path="/upload" element={
              <ProtectedRoute>
                <UploadPage />
              </ProtectedRoute>
            } />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
