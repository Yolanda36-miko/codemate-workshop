"""
User schemas - 用户相关的 Pydantic 模型
"""
from datetime import datetime
from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    display_name: str | None = None
    major: str | None = None
    grade: str | None = None
    avatar_text: str | None = None
    mode: str = "demo"


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
