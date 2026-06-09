"""
Course 模型 - 课程
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from datetime import datetime
from database import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    stage = Column(String(50), nullable=True)
    positioning = Column(String(100), nullable=True)
    keywords = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CourseRelation(Base):
    __tablename__ = "course_relations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    from_course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    to_course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    relation_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)



