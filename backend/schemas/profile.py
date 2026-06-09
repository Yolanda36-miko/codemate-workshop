"""
Profile schemas - 用户画像相关的 Pydantic 模型
"""
from datetime import datetime
from pydantic import BaseModel


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
