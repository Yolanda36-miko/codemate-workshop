"""
Path 模型 - 学习路径
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, Boolean
from datetime import datetime
from database import Base


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=False)
    goal = Column(Text, nullable=True)
    source = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LearningPathNode(Base):
    __tablename__ = "learning_path_nodes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False)
    node_order = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=True)
    learning_goal = Column(Text, nullable=True)
    estimated_time = Column(String(50), nullable=True)
    status = Column(String(20), nullable=False)
    growth_targets = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PathNodeResource(Base):
    __tablename__ = "path_node_resources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(Integer, ForeignKey("learning_path_nodes.id"), nullable=False)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=True)
    source = Column(String(50), nullable=False)
    is_from_user_package = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
