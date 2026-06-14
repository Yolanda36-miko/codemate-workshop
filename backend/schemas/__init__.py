"""
Pydantic Schemas 模块
为 API 请求/响应提供数据验证和序列化
"""

from .user import UserBase, UserCreate, UserResponse
from .profile import (
    StudentProfileBase,
    StudentProfileCreate,
    StudentProfileResponse,
    ProfileConversationBase,
    ProfileConversationCreate,
    ProfileConversationResponse,
)
from .course import (
    CourseBase,
    CourseListItem,
    CourseResponse,
    KnowledgePointListItem,
    KnowledgePointDetail,
    KnowledgePointResponse,
    KnowledgePointRelationItem,
    CourseRelationItem,
)
from .knowledge import (
    KnowledgePointListItem,
    KnowledgePointDetail,
    KnowledgePointResponse,
    KnowledgePointRelationItem,
)
from .resource import (
    ResourceBase,
    ResourceCreate,
    ResourceUpdate,
    ResourceResponse,
    ResourcePackageBase,
    ResourcePackageCreate,
    ResourcePackageResponse,
    ResourceLibraryItem,
    ResourceLibraryDetail,
    ResourceLibraryStats,
)

__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserResponse",
    # Profile
    "StudentProfileBase",
    "StudentProfileCreate",
    "StudentProfileResponse",
    "ProfileConversationBase",
    "ProfileConversationCreate",
    "ProfileConversationResponse",
    # Course & Knowledge
    "CourseBase",
    "CourseListItem",
    "CourseResponse",
    "KnowledgePointListItem",
    "KnowledgePointDetail",
    "KnowledgePointResponse",
    "KnowledgePointRelationItem",
    "CourseRelationItem",
    # Resource
    "ResourceBase",
    "ResourceCreate",
    "ResourceUpdate",
    "ResourceResponse",
    "ResourcePackageBase",
    "ResourcePackageCreate",
    "ResourcePackageResponse",
    "ResourceLibraryItem",
    "ResourceLibraryDetail",
    "ResourceLibraryStats",
]
