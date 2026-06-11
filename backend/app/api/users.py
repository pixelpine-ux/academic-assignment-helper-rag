from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from database import get_db
from models import User, Document, Assignment
from app.schemas.user import UserProfile, UserStatistics, PasswordChange
from app.core.dependencies import get_current_user
from app.core.auth import verify_password, get_password_hash

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserProfile)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    WHY: /me endpoint is REST convention for current authenticated user
    - No user_id parameter needed, uses JWT token from Authorization header
    - Prevents users from accessing other users' profiles
    """
    return current_user

@router.get("/me/statistics", response_model=UserStatistics)
def get_my_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    WHY: Aggregated statistics for user dashboard
    - Single endpoint for all stats reduces API calls
    - Queries are optimized with COUNT() at DB level, not in Python
    - Recent activity uses 7-day window for meaningful engagement metric
    """
    # WHY: Use db.query().count() instead of len() to avoid loading all records
    total_documents = db.query(Document).filter(
        Document.uploaded_by == current_user.id
    ).count()
    
    total_assignments = db.query(Assignment).filter(
        Assignment.created_by == current_user.id
    ).count()
    
    # WHY: Plagiarism checks = documents with content_hash (indicates check was run)
    plagiarism_checks = db.query(Document).filter(
        and_(
            Document.uploaded_by == current_user.id,
            Document.content_hash.isnot(None)
        )
    ).count()
    
    # WHY: Recent activity window = last 7 days, configurable if needed
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_activity = db.query(Document).filter(
        and_(
            Document.uploaded_by == current_user.id,
            Document.created_at >= seven_days_ago
        )
    ).count()
    
    return UserStatistics(
        total_documents=total_documents,
        total_assignments=total_assignments,
        plagiarism_checks_run=plagiarism_checks,
        recent_activity_count=recent_activity
    )

@router.put("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    WHY: Password change requires current password for security
    - Prevents unauthorized password changes if session is compromised
    - Uses 204 No Content for successful updates (REST best practice)
    - Validates current password BEFORE hashing new one (performance)
    """
    # WHY: Verify current password first to prevent unauthorized changes
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # WHY: Check new password is different from current (prevent no-op updates)
    if verify_password(password_data.new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # WHY: Hash password with bcrypt (handled by get_password_hash)
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    # WHY: Return 204 with no body (HTTP standard for successful update with no content)
    return None
