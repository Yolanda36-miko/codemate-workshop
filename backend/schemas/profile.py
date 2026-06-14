"""
Profile schemas - 用户画像相关的 Pydantic 模型
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class StudentProfileBase(BaseModel):
    user_id: int
    knowledge_base_score: int | None = None
    practice_ability_score: int | None = None
    cognitive_styles: str | None = None
    error_patterns: str | None = None
    learning_goals: str | None = None
    resource_preferences: str | None = None
    profile_summary: str | None = None
    diagnosis_status: str | None = None


class StudentProfileCreate(StudentProfileBase):
    pass


class StudentProfileResponse(StudentProfileBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProfileConversationBase(BaseModel):
    user_id: int
    role: str
    message: str
    extracted_fields: str | None = None
    missing_fields: str | None = None


class ProfileConversationCreate(ProfileConversationBase):
    pass


class ProfileConversationResponse(ProfileConversationBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ---- Phase 4B: Profile CRUD schemas ----

class ProfileUpdate(BaseModel):
    """更新画像 — 所有字段可选，不做必填校验"""
    knowledge_base_score: Optional[int] = None
    practice_ability_score: Optional[int] = None
    cognitive_styles: Optional[str] = None
    error_patterns: Optional[str] = None
    learning_goals: Optional[str] = None
    resource_preferences: Optional[str] = None
    profile_summary: Optional[str] = None
    diagnosis_status: Optional[str] = None


class ConversationCreateRequest(BaseModel):
    """追加对话消息"""
    role: str = Field(..., pattern="^(buddy|user)$")
    message: str = Field(..., min_length=1)
    extracted_fields: Optional[str] = None
    missing_fields: Optional[str] = None


class ConversationItem(BaseModel):
    """对话消息返回项"""
    id: int
    user_id: int
    role: str
    message: str
    extracted_fields: Optional[str] = None
    missing_fields: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
