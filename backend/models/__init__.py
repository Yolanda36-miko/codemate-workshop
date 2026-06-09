"""
SQLAlchemy 数据模型模块
"""

from .user import User
from .profile import StudentProfile, ProfileConversation
from .course import Course, CourseRelation
from .knowledge import KnowledgePoint, KnowledgePointRelation
from .resource import Resource, UserResourcePackage
from .path import LearningPath, LearningPathNode, PathNodeResource
from .assessment import Assessment, AssessmentAnswer
from .growth import GrowthRecord, Badge, UserBadge, GrowthValue

__all__ = [
    "User",
    "StudentProfile",
    "ProfileConversation",
    "Course",
    "CourseRelation",
    "KnowledgePoint",
    "KnowledgePointRelation",
    "Resource",
    "UserResourcePackage",
    "LearningPath",
    "LearningPathNode",
    "PathNodeResource",
    "Assessment",
    "AssessmentAnswer",
    "GrowthRecord",
    "Badge",
    "UserBadge",
    "GrowthValue",
]
