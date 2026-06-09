"""
学习路径相关的 Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class LearningPathBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    path_type: str = "personalized"
    status: str = "active"
    progress: int = Field(default=0, ge=0, le=100)
    extra_data: Optional[Dict[str, Any]] = None


class LearningPathCreate(LearningPathBase):
    """创建学习路径"""
    user_id: int
    start_date: Optional[datetime] = None
    estimated_end_date: Optional[datetime] = None


class LearningPathResponse(LearningPathBase):
    """学习路径响应"""
    id: int
    user_id: int
    start_date: Optional[datetime] = None
    estimated_end_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PathNodeBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    node_type: str = "learning"
    order_index: int = 0
    status: str = "pending"
    is_unlocked: bool = False
    extra_data: Optional[Dict[str, Any]] = None


class PathNodeCreate(PathNodeBase):
    """创建路径节点"""
    learning_path_id: int
    knowledge_point_id: Optional[int] = None
    resource_package_id: Optional[int] = None


class PathNodeResponse(PathNodeBase):
    """路径节点响应"""
    id: int
    learning_path_id: int
    knowledge_point_id: Optional[int] = None
    resource_package_id: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
