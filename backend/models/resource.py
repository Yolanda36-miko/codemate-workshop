"""
Resource 模型 - 资源
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, Boolean
from datetime import datetime
from database import Base


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_id = Column(String(100), unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=True)
    resource_type = Column(String(50), nullable=False)
    difficulty = Column(String(20), nullable=True)
    language = Column(String(50), nullable=True)
    tags = Column(Text, nullable=True)
    estimated_time = Column(String(50), nullable=True)
    summary = Column(Text, nullable=True)
    content_path = Column(String(500), nullable=True)
    source_type = Column(String(50), nullable=False)
    source_resource_ids = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ResourcePackage(Base):
    __tablename__ = "resource_packages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    course_id = Column(Integer, ForeignKey("courses.id"))
    tags = Column(Text)
    is_active = Column(Integer, default=1)
    extra_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserResourcePackage(Base):
    __tablename__ = "user_resource_packages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=True)
    custom_title = Column(String(200), nullable=True)
    topic = Column(String(200), nullable=True)
    course_name = Column(String(200), nullable=True)
    resource_type = Column(String(50), nullable=True)
    estimated_time = Column(String(50), nullable=True)
    purpose = Column(String(50), nullable=True)
    priority = Column(String(50), nullable=True)
    note = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="saved")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
