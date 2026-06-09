"""
数据库初始化脚本
用于创建数据库表和基础结构

使用方法:
    cd backend
    python -m scripts.init_db
"""
import sys
import os

# 添加父目录到路径以便导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base, engine, SessionLocal, StudentProfile
from models import (
    User,
    Course,
    KnowledgePoint,
    Resource,
    ResourcePackage,
    LearningPath,
    PathNode,
    Assessment,
    AssessmentRecord,
    GrowthValue,
    Badge,
    UserBadge,
    ProfileConversation,
    CourseRelation,
    KnowledgePointRelation,
    UserResourcePackage,
    PathNodeResource,
    GrowthRecord,
    AssessmentAnswer,
)
