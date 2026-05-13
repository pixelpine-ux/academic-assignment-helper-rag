import './PlagiarismModal.css';

export default function PlagiarismModal({ result, onClose }) {
  if (!result) return null;

  const { filename, hash_check, vector_check } = result;
  const hasIssues = hash_check.is_duplicate || vector_check.is_flagged;

  const getRiskLevel = () => {
    if (hash_check.is_duplicate) return 'critical';
    if (vector_check.is_flagged && vector_check.similarity_score > 0.8) return 'high';
    if (vector_check.is_flagged) return 'medium';
    return 'safe';
  };

  const riskLevel = getRiskLevel();
  const riskLabels = {
    critical: '🔴 Critical Risk',
    high: '🟠 High Risk',
    medium: '🟡 Medium Risk',
    safe: '✅ No Issues Found'
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Plagiarism Check Results</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-body">
          <div className="plagiarism-filename">{filename}</div>
          
          <div className={`plagiarism-risk plagiarism-risk-${riskLevel}`}>
            {riskLabels[riskLevel]}
          </div>

          <div className="plagiarism-section">
            <h3>🔍 Exact Match Check</h3>
            <div className="plagiarism-result">
              {hash_check.is_duplicate ? (
                <>
                  <span className="status-badge status-fail">Duplicate Found</span>
                  <p>This document is an exact copy of document #{hash_check.matched_document_id}</p>
                </>
              ) : (
                <>
                  <span className="status-badge status-pass">No Duplicates</span>
                  <p>No exact matches found in the database</p>
                </>
              )}
            </div>
          </div>

          <div className="plagiarism-section">
            <h3>🧠 Semantic Similarity Check</h3>
            <div className="plagiarism-result">
              {vector_check.is_flagged ? (
                <>
                  <span className="status-badge status-fail">Similar Content Detected</span>
                  <p>
                    Similarity: <strong>{(vector_check.similarity_score * 100).toFixed(1)}%</strong>
                    {vector_check.matched_document_id && (
                      <> with document #{vector_check.matched_document_id}</>
                    )}
                  </p>
                </>
              ) : (
                <>
                  <span className="status-badge status-pass">Unique Content</span>
                  <p>Similarity: {(vector_check.similarity_score * 100).toFixed(1)}%</p>
                </>
              )}
            </div>
          </div>

          {hasIssues && (
            <div className="plagiarism-warning">
              ⚠️ This document may contain plagiarized content. Review carefully before submission.
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn btn-primary" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
}
