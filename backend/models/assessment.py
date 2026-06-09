"""
Assessment 模型 - 评估
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, Boolean
from datetime import datetime
from database import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic = Column(String(200), nullable=True)
    question = Column(Text, nullable=True)
    score = Column(Integer, nullable=True)
    total_questions = Column(Integer, nullable=True)
    correct_count = Column(Integer, nullable=True)
    wrong_points = Column(Text, nullable=True)
    growth_delta = Column(Text, nullable=True)
    badge_awarded = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AssessmentRecord(Base):
    __tablename__ = "assessment_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    score = Column(Integer, default=0)
    status = Column(String(20), default="pending")
    completed_at = Column(DateTime, nullable=True)
    extra_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)


class AssessmentAnswer(Base):
    __tablename__ = "assessment_answers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    question_id = Column(String(50), nullable=True)
    question_text = Column(Text, nullable=True)
    selected_answer = Column(String(500), nullable=True)
    correct_answer = Column(String(500), nullable=True)
    is_correct = Column(Boolean, nullable=True)
    knowledge_point = Column(String(200), nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
