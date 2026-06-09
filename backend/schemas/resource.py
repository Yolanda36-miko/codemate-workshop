"""
资源相关的 Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ResourceBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    resource_type: str = Field(..., pattern="^(video|article|exercise|project|quiz)$")
    content_url: Optional[str] = None
    content: Optional[str] = None
    difficulty: str = "beginner"
    estimated_minutes: int = 30
    tags: Optional[List[str]] = None
    extra_data: Optional[Dict[str, Any]] = None
    is_active: bool = True


class ResourceCreate(ResourceBase):
    """创建资源"""
    course_id: Optional[int] = None
    knowledge_point_id: Optional[int] = None


class ResourceUpdate(BaseModel):
    """更新资源"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    resource_type: Optional[str] = None
    content_url: Optional[str] = None
    content: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_minutes: Optional[int] = None
    tags: Optional[List[str]] = None
    extra_data: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class ResourceResponse(ResourceBase):
    """资源响应"""
    id: int
    course_id: Optional[int] = None
    knowledge_point_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ResourcePackageBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    package_type: str = "default"
    package_content: Optional[Dict[str, Any]] = None
    order_index: int = 0
    is_completed: bool = False


class ResourcePackageCreate(ResourcePackageBase):
    """创建资源包"""
    resource_id: Optional[int] = None


class ResourcePackageResponse(ResourcePackageBase):
    """资源包响应"""
    id: int
    resource_id: Optional[int] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
