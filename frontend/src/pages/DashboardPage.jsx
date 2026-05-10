import { useState, useEffect, useCallback, useRef } from 'react';
import { documents, query } from '../services/api';
import Sidebar from '../components/ui/Sidebar';
import ChatMessage from '../components/ui/ChatMessage';
import ChatInput from '../components/ui/ChatInput';
import TypingIndicator from '../components/ui/TypingIndicator';
import './DashboardPage.css';

export default function DashboardPage() {
  const [docs, setDocs] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const loadDocuments = useCallback(async () => {
    try {
      const data = await documents.list();
      setDocs(data);
    } catch {
      setError('Failed to load documents');
    }
  }, []);

  useEffect(() => {
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

  const handleSend = async (question) => {
    const userMsg = { role: 'user', content: question };
    setMessages(prev => [...prev, userMsg]);
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

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
  };

  const handleNewChat = () => {
    setMessages([]);
    setSelectedDoc(null);
  };

  return (
    <div className="dashboard">
      <Sidebar
        documents={docs}
        selectedDoc={selectedDoc}
        onSelectDoc={(doc) => { setSelectedDoc(doc); setMessages([]); }}
        onNewChat={handleNewChat}
        onUpload={handleUpload}
        onDelete={handleDelete}
        uploading={uploading}
      />
      <main className="dashboard-main">
        <div className="dashboard-chat">
          {messages.length === 0 ? (
            <div className="dashboard-empty">
              <div className="dashboard-empty-icon">💬</div>
              <h2>Start a conversation</h2>
              <p>Upload a document or ask a question to get started</p>
            </div>
          ) : (
            messages.map((msg, i) => (
              <ChatMessage
                key={i}
                message={msg}
                onCopy={handleCopy}
              />
            ))
          )}
          {loading && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>
        {error && <div className="dashboard-error">{error}</div>}
        <ChatInput
          onSend={handleSend}
          disabled={loading}
          onFileAttach={() => document.querySelector('input[type="file"]')?.click()}
        />
      </main>
    </div>
  );
}
