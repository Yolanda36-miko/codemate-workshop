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


# ---- Phase 4B: Assessment record save schemas (align with DB models) ----
# 旧 schema 保留不动；以下字段对齐 models/assessment.py


class AssessmentAnswerItem(BaseModel):
    """单条作答记录"""
    question_id: Optional[str] = None
    question_text: Optional[str] = None
    selected_answer: Optional[str] = None
    correct_answer: Optional[str] = None
    is_correct: Optional[bool] = None
    knowledge_point: Optional[str] = None
    feedback: Optional[str] = None


class AssessmentRecordSaveRequest(BaseModel):
    """保存评估结果 — 字段对齐 models/assessment.py Assessment"""
    user_id: int
    topic: Optional[str] = None
    question: Optional[str] = None
    score: Optional[int] = None
    total_questions: Optional[int] = None
    correct_count: Optional[int] = None
    wrong_points: Optional[str] = None
    growth_delta: Optional[str] = None   # JSON string: {"knowledge_base": 5, "practice_ability": 4}
    badge_awarded: Optional[str] = None
    answers: Optional[List[AssessmentAnswerItem]] = None


class AssessmentResultResponse(BaseModel):
    """评估结果响应 — DB model 字段（Phase 4B）"""
    id: int
    user_id: int
    topic: Optional[str] = None
    score: Optional[int] = None
    total_questions: Optional[int] = None
    correct_count: Optional[int] = None
    wrong_points: Optional[str] = None
    growth_delta: Optional[str] = None
    badge_awarded: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
