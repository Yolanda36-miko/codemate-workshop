from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship
from database import Base


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    knowledge_base_score = Column(Integer, nullable=True)
    practice_ability_score = Column(Integer, nullable=True)
    cognitive_styles = Column(Text, nullable=True)
    error_patterns = Column(Text, nullable=True)
    learning_goals = Column(Text, nullable=True)
    resource_preferences = Column(Text, nullable=True)
    profile_summary = Column(Text, nullable=True)
    diagnosis_status = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User")


class ProfileConversation(Base):
    __tablename__ = "profile_conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    extracted_fields = Column(Text, nullable=True)
    missing_fields = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")
