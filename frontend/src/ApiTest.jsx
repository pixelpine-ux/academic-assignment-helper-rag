import { useState } from 'react';

function ApiTest() {
  const [status, setStatus] = useState('Not tested');
  const [loading, setLoading] = useState(false);

  const testConnection = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/`);
      const data = await response.json();
      setStatus(`✅ Connected! Backend says: ${data.message}`);
    } catch (error) {
      setStatus(`❌ Failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>API Connection Test</h1>
      <p>Backend URL: {import.meta.env.VITE_API_URL}</p>
      <button 
        onClick={testConnection}
        disabled={loading}
        style={{
          padding: '10px 20px',
          fontSize: '16px',
          cursor: loading ? 'not-allowed' : 'pointer',
        }}
      >
        {loading ? 'Testing...' : 'Test Connection'}
      </button>
      <p style={{ marginTop: '20px', fontSize: '18px' }}>
        Status: {status}
      </p>
    </div>
  );
}

export default ApiTest;
