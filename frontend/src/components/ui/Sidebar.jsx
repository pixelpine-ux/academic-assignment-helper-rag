import { Plus, FileText, Settings, User, Trash2 } from 'lucide-react';
import Button from './Button';
import './Sidebar.css';

export default function Sidebar({ 
  documents, 
  selectedDoc, 
  onSelectDoc, 
  onNewChat, 
  onUpload, 
  onDelete,
  uploading 
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
