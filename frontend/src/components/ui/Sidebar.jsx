import { Plus, FileText, Settings, User, Trash2, MessageSquare, History } from 'lucide-react';
import Button from './Button';
import './Sidebar.css';

export default function Sidebar({ 
  documents, 
  selectedDoc, 
  onSelectDoc, 
  onNewChat, 
  onUpload, 
  onDelete,
  uploading,
  chatHistory = [],
  selectedChat,
  onSelectChat,
  onDeleteChat,
  onClearHistory
}) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <Button 
          variant="primary" 
          icon={<Plus size={18} />}
          onClick={onNewChat}
          className="sidebar-new-btn"
        >
          New Chat
        </Button>
      </div>

      <div className="sidebar-section">
        <div className="sidebar-section-title">
          <MessageSquare size={16} />
          <span>Recent Chats</span>
          {chatHistory.length > 0 && (
            <button 
              className="sidebar-clear-btn"
              onClick={onClearHistory}
              title="Clear all history"
            >
              <Trash2 size={14} />
            </button>
          )}
        </div>
        <div className="sidebar-chats">
          {chatHistory.length === 0 ? (
            <div className="sidebar-empty">No chat history yet</div>
          ) : (
            chatHistory.slice(0, 10).map(chat => (
              <div
                key={chat.id}
                className={`sidebar-chat-item ${selectedChat?.id === chat.id ? 'active' : ''}`}
                onClick={() => onSelectChat(chat)}
              >
                <div className="sidebar-chat-info">
                  <div className="sidebar-chat-title">{chat.title}</div>
                  <div className="sidebar-chat-date">
                    {new Date(chat.updatedAt).toLocaleDateString()}
                  </div>
                </div>
                <button
                  className="sidebar-chat-delete"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteChat(chat.id);
                  }}
                  title="Delete chat"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="sidebar-section">
        <div className="sidebar-section-title">
          <FileText size={16} />
          <span>My Documents ({documents.length})</span>
        </div>
        <label className="sidebar-upload-btn">
          <input 
            type="file" 
            onChange={onUpload} 
            disabled={uploading}
            accept=".pdf,.docx,.txt"
            style={{ display: 'none' }}
          />
          {uploading ? 'Uploading...' : '+ Upload Document'}
        </label>
        <div className="sidebar-documents">
          {documents.map(doc => (
            <div
              key={doc.id}
              className={`sidebar-doc-item ${selectedDoc?.id === doc.id ? 'active' : ''}`}
              onClick={() => onSelectDoc(doc)}
            >
              <div className="sidebar-doc-info">
                <div className="sidebar-doc-name">{doc.filename}</div>
                <div className="sidebar-doc-date">
                  {new Date(doc.created_at).toLocaleDateString()}
                </div>
              </div>
              <button
                className="sidebar-doc-delete"
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(doc.id);
                }}
                title="Delete document"
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="sidebar-footer">
        <button className="sidebar-footer-btn">
          <Settings size={18} />
          <span>Settings</span>
        </button>
        <button className="sidebar-footer-btn">
          <User size={18} />
          <span>Profile</span>
        </button>
      </div>
    </aside>
  );
}
