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


# ---- Resource Library schemas (Phase 4A) ----


class ResourceLibraryItem(BaseModel):
    """资源库列表项 — 对应 index.json 中单条资源的元数据（不含正文）"""
    id: str = Field(..., min_length=1, max_length=100)
    title: str
    course: str
    courseCode: str
    topic: str
    topicCode: str
    type: str
    difficulty: Optional[str] = None
    language: Optional[str] = None
    tags: Optional[List[str]] = None
    estimatedTime: Optional[str] = None
    summary: Optional[str] = None
    contentPath: Optional[str] = None
    source: Optional[str] = None
    version: Optional[str] = None
    updatedAt: Optional[str] = None


class ResourceLibraryDetail(BaseModel):
    """资源详情 — 元数据 + 正文内容（按 content_type 区分布局）"""
    id: str
    title: str
    course: str
    courseCode: str
    topic: str
    topicCode: str
    type: str
    difficulty: Optional[str] = None
    language: Optional[str] = None
    tags: Optional[List[str]] = None
    estimatedTime: Optional[str] = None
    summary: Optional[str] = None
    contentPath: Optional[str] = None
    source: Optional[str] = None
    version: Optional[str] = None
    updatedAt: Optional[str] = None
    content_type: str  # "markdown" | "json"
    content: Optional[str] = None        # markdown 正文
    content_json: Optional[Any] = None   # JSON 正文（练习题等）


class ResourceLibraryStats(BaseModel):
    """资源库统计"""
    total_resources: int
    by_course: Dict[str, int]
    by_type: Dict[str, int]
    by_difficulty: Dict[str, int]
    source: str


# ---- User Resource Package schemas (Phase 4B) ----

class UserResourcePackageCreate(BaseModel):
    """添加资源到用户资源包"""
    resource_id: Optional[int] = None
    library_resource_id: Optional[str] = None   # Phase 3 资源库字符串 ID
    custom_title: Optional[str] = None
    topic: Optional[str] = None
    course_name: Optional[str] = None
    resource_type: Optional[str] = None
    estimated_time: Optional[str] = None
    purpose: Optional[str] = None
    priority: Optional[str] = None
    note: Optional[str] = None


class UserResourcePackageUpdate(BaseModel):
    """更新资源包条目 — 所有字段可选"""
    custom_title: Optional[str] = None
    topic: Optional[str] = None
    course_name: Optional[str] = None
    resource_type: Optional[str] = None
    estimated_time: Optional[str] = None
    purpose: Optional[str] = None
    priority: Optional[str] = None
    note: Optional[str] = None
    status: Optional[str] = None


class UserResourcePackageResponse(BaseModel):
    """资源包条目响应"""
    id: int
    user_id: int
    resource_id: Optional[int] = None
    library_resource_id: Optional[str] = None
    custom_title: Optional[str] = None
    topic: Optional[str] = None
    course_name: Optional[str] = None
    resource_type: Optional[str] = None
    estimated_time: Optional[str] = None
    purpose: Optional[str] = None
    priority: Optional[str] = None
    note: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
