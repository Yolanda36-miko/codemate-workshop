"""
Knowledge 模型 - 知识点
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from datetime import datetime
from database import Base


class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    difficulty = Column(String(20), nullable=True)
    tags = Column(Text, nullable=True)
    common_errors = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class KnowledgePointRelation(Base):
    __tablename__ = "knowledge_point_relations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    from_kp_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=False)
    to_kp_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=False)
    relation_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
