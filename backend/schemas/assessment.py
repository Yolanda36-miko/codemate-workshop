"""
评估相关的 Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AssessmentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    assessment_type: str = "diagnosis"
    difficulty: str = "intermediate"
    total_score: int = 100
    passing_score: int = 60
    time_limit_minutes: Optional[int] = None
    questions: Optional[List[Dict[str, Any]]] = None
    extra_data: Optional[Dict[str, Any]] = None
    is_active: bool = True


class AssessmentCreate(AssessmentBase):
    """创建评估"""
    pass


class AssessmentResponse(AssessmentBase):
    """评估响应"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AssessmentRecordBase(BaseModel):
    score: Optional[int] = None
    percentage: Optional[float] = None
    is_passed: bool = False
    answers: Optional[List[Dict[str, Any]]] = None
    correct_answers: Optional[List[Dict[str, Any]]] = None
    feedback: Optional[str] = None
    time_spent_minutes: Optional[int] = None
    status: str = "completed"
    extra_data: Optional[Dict[str, Any]] = None


class AssessmentRecordCreate(AssessmentRecordBase):
    """创建评估记录"""
    user_id: int
    assessment_id: int


class AssessmentRecordResponse(AssessmentRecordBase):
    """评估记录响应"""
    id: int
    user_id: int
    assessment_id: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
