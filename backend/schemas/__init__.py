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

__all__ = [
    "UserBase",
    "UserCreate",
    "UserResponse",
    "StudentProfileBase",
    "StudentProfileCreate",
    "StudentProfileResponse",
    "ProfileConversationBase",
    "ProfileConversationCreate",
    "ProfileConversationResponse",
]
