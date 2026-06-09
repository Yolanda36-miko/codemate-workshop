"""
成长值与徽章相关的 Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class GrowthValueBase(BaseModel):
    knowledge_base: int = 0
    practice_ability: int = 0
    thinking_depth: int = 0
    learning_efficiency: int = 0
    total_points: int = 0
    level: int = 1
    title: str = "初学者"
    extra_data: Optional[Dict[str, Any]] = None


class GrowthValueCreate(GrowthValueBase):
    """创建成长值"""
    user_id: int


class GrowthValueResponse(GrowthValueBase):
    """成长值响应"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BadgeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    icon_url: Optional[str] = None
    badge_type: str = "achievement"
    requirement: Optional[Dict[str, Any]] = None
    is_active: bool = True
    order_index: int = 0


class BadgeCreate(BadgeBase):
    """创建徽章"""
    pass


class BadgeResponse(BadgeBase):
    """徽章响应"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserBadgeResponse(BaseModel):
    """用户徽章响应"""
    id: int
    user_id: int
    badge_id: int
    earned_at: datetime
    reason: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True
