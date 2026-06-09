"""
课程与知识点相关的 Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class CourseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    cover_image: Optional[str] = None
    difficulty: str = "beginner"
    total_hours: int = 0
    order_index: int = 0
    is_active: bool = True
    extra_data: Optional[Dict[str, Any]] = None


class CourseCreate(CourseBase):
    """创建课程"""
    pass


class CourseUpdate(BaseModel):
    """更新课程"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    cover_image: Optional[str] = None
    difficulty: Optional[str] = None
    total_hours: Optional[int] = None
    order_index: Optional[int] = None
    is_active: Optional[bool] = None
    extra_data: Optional[Dict[str, Any]] = None


class CourseResponse(CourseBase):
    """课程响应"""
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class KnowledgePointBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    content: Optional[str] = None
    order_index: int = 0
    difficulty: str = "beginner"
    estimated_minutes: int = 30
    prerequisites: Optional[List[int]] = None
    learning_objectives: Optional[List[str]] = None
    extra_data: Optional[Dict[str, Any]] = None


class KnowledgePointCreate(KnowledgePointBase):
    """创建知识点"""
    course_id: int


class KnowledgePointUpdate(BaseModel):
    """更新知识点"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    content: Optional[str] = None
    order_index: Optional[int] = None
    difficulty: Optional[str] = None
    estimated_minutes: Optional[int] = None
    prerequisites: Optional[List[int]] = None
    learning_objectives: Optional[List[str]] = None
    extra_data: Optional[Dict[str, Any]] = None


class KnowledgePointResponse(KnowledgePointBase):
    """知识点响应"""
    id: int
    course_id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
