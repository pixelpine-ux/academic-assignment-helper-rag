import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import UploadPage from './pages/UploadPage'
import ApiTest from './ApiTest'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <div style={{ fontFamily: 'sans-serif' }}>
        {/* Navigation Bar */}
        <nav style={{
          padding: '20px',
          backgroundColor: '#f0f0f0',
          borderBottom: '2px solid #ddd'
        }}>
          <h2 style={{ margin: '0 0 10px 0' }}>Academic Assignment Helper</h2>
          <div style={{ display: 'flex', gap: '15px' }}>
            <Link to="/" style={{ textDecoration: 'none', color: '#0066cc' }}>API Test</Link>
            <Link to="/login" style={{ textDecoration: 'none', color: '#0066cc' }}>Login</Link>
            <Link to="/register" style={{ textDecoration: 'none', color: '#0066cc' }}>Register</Link>
            <Link to="/dashboard" style={{ textDecoration: 'none', color: '#0066cc' }}>Dashboard</Link>
            <Link to="/upload" style={{ textDecoration: 'none', color: '#0066cc' }}>Upload</Link>
          </div>
        </nav>

        {/* Routes */}
        <Routes>
          <Route path="/" element={<ApiTest />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/upload" element={<UploadPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App
