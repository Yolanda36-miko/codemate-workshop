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
    ProfileUpdate,
    ConversationCreateRequest,
    ConversationItem,
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
    UserResourcePackageCreate,
    UserResourcePackageUpdate,
    UserResourcePackageResponse,
)
from .learning_path import (
    LearningPathBase,
    LearningPathCreate,
    LearningPathResponse,
    PathNodeBase,
    PathNodeCreate,
    PathNodeResponse,
    PathCreateRequest,
    PathUpdateRequest,
    PathDetailResponse,
    PathNodeCreateRequest,
    PathNodeUpdateRequest,
    PathNodeDetailResponse,
    PathNodeResourceLinkRequest,
)
from .assessment import (
    AssessmentBase,
    AssessmentCreate,
    AssessmentResponse,
    AssessmentRecordBase,
    AssessmentRecordCreate,
    AssessmentRecordResponse,
    AssessmentAnswerItem,
    AssessmentRecordSaveRequest,
    AssessmentResultResponse,
)

__all__ = [
    # User
    "UserBase", "UserCreate", "UserResponse",
    # Profile
    "StudentProfileBase", "StudentProfileCreate", "StudentProfileResponse",
    "ProfileConversationBase", "ProfileConversationCreate", "ProfileConversationResponse",
    "ProfileUpdate", "ConversationCreateRequest", "ConversationItem",
    # Course & Knowledge
    "CourseBase", "CourseListItem", "CourseResponse",
    "KnowledgePointListItem", "KnowledgePointDetail", "KnowledgePointResponse",
    "KnowledgePointRelationItem", "CourseRelationItem",
    # Resource
    "ResourceBase", "ResourceCreate", "ResourceUpdate", "ResourceResponse",
    "ResourcePackageBase", "ResourcePackageCreate", "ResourcePackageResponse",
    "ResourceLibraryItem", "ResourceLibraryDetail", "ResourceLibraryStats",
    "UserResourcePackageCreate", "UserResourcePackageUpdate", "UserResourcePackageResponse",
    # Learning Path
    "LearningPathBase", "LearningPathCreate", "LearningPathResponse",
    "PathNodeBase", "PathNodeCreate", "PathNodeResponse",
    "PathCreateRequest", "PathUpdateRequest", "PathDetailResponse",
    "PathNodeCreateRequest", "PathNodeUpdateRequest", "PathNodeDetailResponse",
    "PathNodeResourceLinkRequest",
    # Assessment
    "AssessmentBase", "AssessmentCreate", "AssessmentResponse",
    "AssessmentRecordBase", "AssessmentRecordCreate", "AssessmentRecordResponse",
    "AssessmentAnswerItem", "AssessmentRecordSaveRequest", "AssessmentResultResponse",
]
