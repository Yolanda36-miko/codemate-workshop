"""
学习路径相关的 Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List as ListType
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


# ---- Phase 4B: Learning Path & Node CRUD schemas (align with DB models) ----
# 旧 schema 保留不动；以下为 Phase 4B 新增，字段名对齐 models/path.py


class PathCreateRequest(BaseModel):
    """创建学习路径"""
    name: str = Field(..., min_length=1, max_length=200)
    goal: Optional[str] = None
    source: str = "manual"
    status: str = "active"
    nodes: Optional[ListType[dict]] = None   # 可选的节点列表


class PathUpdateRequest(BaseModel):
    """更新学习路径"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    goal: Optional[str] = None
    status: Optional[str] = None


class PathDetailResponse(BaseModel):
    """学习路径详情 — 含节点列表"""
    id: int
    user_id: int
    name: str
    goal: Optional[str] = None
    source: str
    status: str
    nodes: Optional[ListType[dict]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PathNodeCreateRequest(BaseModel):
    """创建路径节点"""
    node_order: int
    title: str = Field(..., min_length=1, max_length=200)
    course_id: Optional[int] = None
    knowledge_point_id: Optional[int] = None
    learning_goal: Optional[str] = None
    estimated_time: Optional[str] = None
    status: str = "not_started"
    growth_targets: Optional[str] = None


class PathNodeUpdateRequest(BaseModel):
    """更新路径节点（常用于状态变更）"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    node_order: Optional[int] = None
    learning_goal: Optional[str] = None
    estimated_time: Optional[str] = None
    status: Optional[str] = None
    growth_targets: Optional[str] = None


class PathNodeDetailResponse(BaseModel):
    """路径节点详情 — 含关联资源"""
    id: int
    path_id: int
    node_order: int
    title: str
    course_id: Optional[int] = None
    course_name: Optional[str] = None
    knowledge_point_id: Optional[int] = None
    knowledge_point_name: Optional[str] = None
    learning_goal: Optional[str] = None
    estimated_time: Optional[str] = None
    status: str
    growth_targets: Optional[str] = None
    resources: Optional[ListType[dict]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PathNodeResourceLinkRequest(BaseModel):
    """关联资源到节点"""
    resource_id: Optional[int] = None
    library_resource_id: Optional[str] = None
    source: str = "resource_library"
    is_from_user_package: bool = False
