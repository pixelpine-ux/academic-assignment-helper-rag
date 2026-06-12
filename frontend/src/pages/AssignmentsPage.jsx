import { useState, useEffect } from 'react';
import { assignments, documents } from '../services/api';
import { useToast } from '../components/ui/Toast';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import AssignmentCard from '../components/ui/AssignmentCard';
import AssignmentModal from '../components/ui/AssignmentModal';
import Button from '../components/ui/Button';
import { Plus, Filter, ArrowLeft } from 'lucide-react';
import './AssignmentsPage.css';

export default function AssignmentsPage() {
  const [assignmentList, setAssignmentList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingAssignment, setEditingAssignment] = useState(null);
  const [statusFilter, setStatusFilter] = useState('all');
  const [saving, setSaving] = useState(false);
  const toast = useToast();
  const { user } = useAuth();
  const navigate = useNavigate();

  const loadAssignments = async () => {
    try {
      setLoading(true);
      const filters = statusFilter !== 'all' ? { status: statusFilter, user_id: user?.id } : { user_id: user?.id };
      const data = await assignments.list(filters);
      setAssignmentList(data);
    } catch (err) {
      toast.error(err.message || 'Failed to load assignments');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user?.id) {
      loadAssignments();
    }
  }, [statusFilter, user?.id]);

  const handleCreate = () => {
    setEditingAssignment(null);
    setShowModal(true);
  };

  const handleEdit = (assignment) => {
    setEditingAssignment(assignment);
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this assignment? Documents will not be deleted.')) return;
    try {
      await assignments.delete(id);
      await loadAssignments();
      toast.success('Assignment deleted');
    } catch (err) {
      toast.error(err.message || 'Delete failed');
    }
  };

  const handleSave = async (assignmentData) => {
    setSaving(true);
    try {
      if (editingAssignment) {
        await assignments.update(editingAssignment.id, assignmentData);
        toast.success('Assignment updated');
      } else {
        await assignments.create({ ...assignmentData, created_by: user.id });
        toast.success('Assignment created');
      }
      setShowModal(false);
      await loadAssignments();
    } catch (err) {
      toast.error(err.message || 'Save failed');
    } finally {
      setSaving(false);
    }
  };

  const getStatusCounts = () => {
    return {
      all: assignmentList.length,
      draft: assignmentList.filter(a => a.status === 'draft').length,
      published: assignmentList.filter(a => a.status === 'published').length,
      submitted: assignmentList.filter(a => a.status === 'submitted').length,
      graded: assignmentList.filter(a => a.status === 'graded').length,
    };
  };

  const counts = getStatusCounts();

  return (
    <div className="assignments-page">
      <div className="assignments-header">
        <div>
          <button className="back-button" onClick={() => navigate('/dashboard')}>
            <ArrowLeft size={20} />
            Back to Dashboard
          </button>
          <h1>My Assignments</h1>
          <p className="assignments-subtitle">Manage your academic assignments</p>
        </div>
        <Button variant="primary" icon={<Plus size={18} />} onClick={handleCreate}>
          New Assignment
        </Button>
      </div>

      <div className="assignments-filters">
        <div className="filter-tabs">
          {['all', 'draft', 'published', 'submitted', 'graded'].map(status => (
            <button
              key={status}
              className={`filter-tab ${statusFilter === status ? 'active' : ''}`}
              onClick={() => setStatusFilter(status)}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
              <span className="filter-count">{counts[status]}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="assignments-grid">
        {loading ? (
          <div className="assignments-loading">Loading assignments...</div>
        ) : assignmentList.length === 0 ? (
          <div className="assignments-empty">
            <div className="assignments-empty-icon">📚</div>
            <h2>No assignments yet</h2>
            <p>Create your first assignment to get started</p>
            <Button variant="primary" icon={<Plus size={18} />} onClick={handleCreate}>
              Create Assignment
            </Button>
          </div>
        ) : (
          assignmentList.map(assignment => (
            <AssignmentCard
              key={assignment.id}
              assignment={assignment}
              onEdit={handleEdit}
              onDelete={handleDelete}
            />
          ))
        )}
      </div>

      {showModal && (
        <AssignmentModal
          assignment={editingAssignment}
          onSave={handleSave}
          onClose={() => setShowModal(false)}
          saving={saving}
        />
      )}
    </div>
  );
}
