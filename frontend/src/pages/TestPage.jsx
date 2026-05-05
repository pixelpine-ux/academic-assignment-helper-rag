import { useState } from 'react';
import { auth, documents, query } from '../services/api';

export default function TestPage() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const addResult = (test, success, message) => {
    setResults(prev => [...prev, { test, success, message, time: new Date().toLocaleTimeString() }]);
  };

  const runTests = async () => {
    setResults([]);
    setLoading(true);

    // Test 1: Register
    try {
      const email = `test${Date.now()}@example.com`;
      await auth.register(email, 'password123');
      addResult('Register', true, `User ${email} created`);

      // Test 2: Login
      try {
        const loginData = await auth.login(email, 'password123');
        addResult('Login', true, `Token: ${loginData.access_token.substring(0, 20)}...`);

        // Test 3: Upload Document
        try {
          const testFile = new File(['Test content for RAG'], 'test.txt', { type: 'text/plain' });
          const uploadData = await documents.upload(testFile);
          addResult('Upload', true, `Document ID: ${uploadData.id}`);

          // Test 4: List Documents
          try {
            const docList = await documents.list();
            addResult('List Documents', true, `Found ${docList.length} documents`);

            // Test 5: Query Document
            if (uploadData.id) {
              try {
                const queryData = await query.ask('What is this document about?');
                addResult('Query', true, `Answer: ${queryData.answer.substring(0, 50)}...`);
              } catch (err) {
                addResult('Query', false, err.message);
              }
            }

            // Test 6: Delete Document
            try {
              await documents.delete(uploadData.id);
              addResult('Delete', true, 'Document deleted');
            } catch (err) {
              addResult('Delete', false, err.message);
            }
          } catch (err) {
            addResult('List Documents', false, err.message);
          }
        } catch (err) {
          addResult('Upload', false, err.message);
        }

        // Logout
        auth.logout();
        addResult('Logout', true, 'Token cleared');
      } catch (err) {
        addResult('Login', false, err.message);
      }
    } catch (err) {
      addResult('Register', false, err.message);
    }

    setLoading(false);
  };

  return (
    <div style={{ padding: '40px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>API Functionality Test</h1>
      <button
        onClick={runTests}
        disabled={loading}
        style={{
          padding: '12px 24px',
          fontSize: '16px',
          backgroundColor: loading ? '#ccc' : '#0066cc',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: loading ? 'not-allowed' : 'pointer',
          marginBottom: '20px'
        }}
      >
        {loading ? 'Running Tests...' : 'Run All Tests'}
      </button>

      <div style={{ marginTop: '20px' }}>
        {results.map((result, i) => (
          <div
            key={i}
            style={{
              padding: '15px',
              marginBottom: '10px',
              backgroundColor: result.success ? '#d4edda' : '#f8d7da',
              border: `1px solid ${result.success ? '#c3e6cb' : '#f5c6cb'}`,
              borderRadius: '4px'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
              <strong>{result.test}</strong>
              <span style={{ fontSize: '12px', color: '#666' }}>{result.time}</span>
            </div>
            <div style={{ fontSize: '14px', color: result.success ? '#155724' : '#721c24' }}>
              {result.success ? '✓' : '✗'} {result.message}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
