from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional

# WHY: Separate schema for password change with validation to ensure security
class PasswordChange(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        WHY: Password strength validation prevents weak passwords
        - Minimum 8 characters enforced at field level
        - Check for at least one digit and one letter for basic security
        """
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v

# WHY: Separate response schema to never expose sensitive data like password hashes
class UserProfile(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# WHY: Statistics schema with computed fields to provide dashboard insights
class UserStatistics(BaseModel):
    total_documents: int = Field(..., description="Total documents uploaded by user")
    total_assignments: int = Field(..., description="Total assignments created by user")
    plagiarism_checks_run: int = Field(..., description="Number of plagiarism checks performed")
    recent_activity_count: int = Field(..., description="Activity in last 7 days")
