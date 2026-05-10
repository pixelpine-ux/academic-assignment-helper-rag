import { useState, useEffect, useCallback, useRef } from 'react';
import { documents, query } from '../services/api';
import { useToast } from '../components/ui/Toast';
import { useChatHistory } from '../hooks/useChatHistory';
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
  const [currentChatId, setCurrentChatId] = useState(null);
  const messagesEndRef = useRef(null);
  const toast = useToast();
  const { history, createChat, addMessage, deleteChat, clearHistory, getChat } = useChatHistory();

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
      toast.error('Failed to load documents');
    }
  }, [toast]);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    try {
      await documents.upload(file);
      await loadDocuments();
      toast.success(`${file.name} uploaded successfully`);
      e.target.value = '';
    } catch (err) {
      toast.error(err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this document?')) return;
    try {
      await documents.delete(id);
      await loadDocuments();
      toast.success('Document deleted');
      if (selectedDoc?.id === id) {
        setSelectedDoc(null);
        setMessages([]);
      }
    } catch {
      toast.error('Delete failed');
    }
  };

  const handleSend = async (question) => {
    // Create new chat if none exists
    let chatId = currentChatId;
    if (!chatId) {
      const newChat = createChat();
      chatId = newChat.id;
      setCurrentChatId(chatId);
    }

    const userMsg = { role: 'user', content: question };
    setMessages(prev => [...prev, userMsg]);
    addMessage(chatId, userMsg);
    setLoading(true);

    try {
      const response = await query.ask(question);
      const assistantMsg = {
        role: 'assistant',
        content: response.answer,
        sources: response.source_document_ids || [],
        chunks_used: response.chunks_used
      };
      setMessages(prev => [...prev, assistantMsg]);
      addMessage(chatId, assistantMsg);
    } catch (err) {
      toast.error(err.message || 'Query failed');
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };

  const handleNewChat = () => {
    setMessages([]);
    setSelectedDoc(null);
    setCurrentChatId(null);
  };

  const handleSelectChat = (chat) => {
    setCurrentChatId(chat.id);
    setMessages(chat.messages);
    setSelectedDoc(null);
  };

  const handleDeleteChat = (chatId) => {
    deleteChat(chatId);
    if (currentChatId === chatId) {
      handleNewChat();
    }
    toast.success('Chat deleted');
  };

  const handleClearHistory = () => {
    if (clearHistory()) {
      handleNewChat();
      toast.success('Chat history cleared');
    }
  };

  return (
    <div className="dashboard">
      <Sidebar
        documents={docs}
        selectedDoc={selectedDoc}
        onSelectDoc={(doc) => { setSelectedDoc(doc); setMessages([]); setCurrentChatId(null); }}
        onNewChat={handleNewChat}
        onUpload={handleUpload}
        onDelete={handleDelete}
        uploading={uploading}
        chatHistory={history}
        selectedChat={currentChatId ? getChat(currentChatId) : null}
        onSelectChat={handleSelectChat}
        onDeleteChat={handleDeleteChat}
        onClearHistory={handleClearHistory}
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
        <ChatInput
          onSend={handleSend}
          disabled={loading}
          onFileAttach={() => document.querySelector('input[type="file"]')?.click()}
        />
      </main>
    </div>
  );
}
