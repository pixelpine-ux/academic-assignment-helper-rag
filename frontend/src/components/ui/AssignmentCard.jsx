import { Calendar, Edit2, Trash2, FileText } from 'lucide-react';
import './AssignmentCard.css';

export default function AssignmentCard({ assignment, onEdit, onDelete }) {
  const { id, title, description, due_date, status, created_at } = assignment;

  const getStatusColor = (status) => {
    const colors = {
      draft: 'gray',
      published: 'blue',
      submitted: 'orange',
      graded: 'green'
    };
    return colors[status] || 'gray';
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'No due date';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const isOverdue = () => {
    if (!due_date) return false;
    return new Date(due_date) < new Date() && status !== 'graded' && status !== 'submitted';
  };

  return (
    <div className="assignment-card">
      <div className="assignment-card-header">
        <span className={`assignment-status status-${getStatusColor(status)}`}>
          {status}
        </span>
        <div className="assignment-actions">
          <button
            className="assignment-action-btn"
            onClick={() => onEdit(assignment)}
            title="Edit assignment"
          >
            <Edit2 size={16} />
          </button>
          <button
            className="assignment-action-btn delete"
            onClick={() => onDelete(id)}
            title="Delete assignment"
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>

      <div className="assignment-card-body">
        <h3 className="assignment-title">{title}</h3>
        {description && (
          <p className="assignment-description">{description}</p>
        )}
      </div>

      <div className="assignment-card-footer">
        <div className={`assignment-due ${isOverdue() ? 'overdue' : ''}`}>
          <Calendar size={14} />
          <span>{formatDate(due_date)}</span>
          {isOverdue() && <span className="overdue-badge">Overdue</span>}
        </div>
      </div>
    </div>
  );
}
