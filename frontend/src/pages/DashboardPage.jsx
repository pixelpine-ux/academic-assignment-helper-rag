import { useState, useEffect, useCallback } from 'react';
import { documents, query } from '../services/api';

export default function DashboardPage() {
  const [docs, setDocs] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  const loadDocuments = useCallback(async () => {
    try {
      const data = await documents.list();
      setDocs(data);
    } catch {
      setError('Failed to load documents');
    }
  }, []);

  useEffect(() => {
    // Initial remote data load for the dashboard.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadDocuments();
  }, [loadDocuments]);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setError('');
    try {
      await documents.upload(file);
      await loadDocuments();
      e.target.value = '';
    } catch (err) {
      setError(err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this document?')) return;
    try {
      await documents.delete(id);
      await loadDocuments();
      if (selectedDoc?.id === id) {
        setSelectedDoc(null);
        setMessages([]);
      }
    } catch {
      setError('Delete failed');
    }
  };

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    const userMsg = { role: 'user', content: question };
    setMessages(prev => [...prev, userMsg]);
    setQuestion('');
    setLoading(true);
    setError('');

    try {
      const response = await query.ask(question);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.answer,
        sources: response.source_document_ids || [],
        chunks_used: response.chunks_used
      }]);
    } catch (err) {
      setError(err.message || 'Query failed');
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', height: 'calc(100vh - 100px)' }}>
      {/* Sidebar */}
      <div style={{ width: '300px', borderRight: '1px solid #ddd', padding: '20px', overflowY: 'auto' }}>
        <h2 style={{ marginTop: 0 }}>Documents</h2>
        <label style={{
          display: 'block',
          padding: '10px',
          backgroundColor: uploading ? '#ccc' : '#0066cc',
          color: 'white',
          textAlign: 'center',
          borderRadius: '4px',
          cursor: uploading ? 'not-allowed' : 'pointer',
          marginBottom: '20px'
        }}>
          {uploading ? 'Uploading...' : '+ Upload'}
          <input type="file" onChange={handleUpload} disabled={uploading} style={{ display: 'none' }} accept=".pdf,.docx,.txt" />
        </label>
        {docs.map(doc => (
          <div
            key={doc.id}
            onClick={() => { setSelectedDoc(doc); setMessages([]); }}
            style={{
              padding: '10px',
              marginBottom: '10px',
              backgroundColor: selectedDoc?.id === doc.id ? '#e6f2ff' : '#f9f9f9',
              borderRadius: '4px',
              cursor: 'pointer',
              border: '1px solid #ddd'
            }}
          >
            <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>{doc.filename}</div>
            <div style={{ fontSize: '12px', color: '#666' }}>{new Date(doc.created_at).toLocaleDateString()}</div>
            <button
              onClick={(e) => { e.stopPropagation(); handleDelete(doc.id); }}
              style={{
                marginTop: '5px',
                padding: '5px 10px',
                fontSize: '12px',
                backgroundColor: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '3px',
                cursor: 'pointer'
              }}
            >
              Delete
            </button>
          </div>
        ))}
      </div>

      {/* Chat Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: '20px', borderBottom: '1px solid #ddd' }}>
          <h2 style={{ margin: 0 }}>Ask Questions</h2>
          <p style={{ margin: '5px 0 0 0', fontSize: '14px', color: '#666' }}>Questions search across all your documents</p>
        </div>
        <div style={{ flex: 1, overflowY: 'auto', padding: '20px' }}>
          {messages.map((msg, i) => (
            <div key={i} style={{
              marginBottom: '20px',
              padding: '15px',
              backgroundColor: msg.role === 'user' ? '#e6f2ff' : '#f9f9f9',
              borderRadius: '8px',
              maxWidth: '80%',
              marginLeft: msg.role === 'user' ? 'auto' : '0'
            }}>
              <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                {msg.role === 'user' ? 'You' : 'Assistant'}
              </div>
              <div>{msg.content}</div>
              {msg.sources && msg.sources.length > 0 && (
                <div style={{ marginTop: '10px', fontSize: '12px', color: '#666' }}>
                  Sources: Document IDs {msg.sources.join(', ')} ({msg.chunks_used} chunks)
                </div>
              )}
            </div>
          ))}
          {loading && <div style={{ color: '#666' }}>Thinking...</div>}
        </div>
        {error && <div style={{ padding: '10px 20px', color: 'red', backgroundColor: '#ffe6e6' }}>{error}</div>}
        <form onSubmit={handleAsk} style={{ padding: '20px', borderTop: '1px solid #ddd', display: 'flex', gap: '10px' }}>
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about this document..."
            disabled={loading}
            style={{
              flex: 1,
              padding: '12px',
              fontSize: '16px',
              border: '1px solid #ddd',
              borderRadius: '4px'
            }}
          />
          <button
            type="submit"
            disabled={loading || !question.trim()}
            style={{
              padding: '12px 24px',
              fontSize: '16px',
              backgroundColor: loading || !question.trim() ? '#ccc' : '#0066cc',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: loading || !question.trim() ? 'not-allowed' : 'pointer'
            }}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
