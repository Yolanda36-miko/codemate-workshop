"""
Growth 模型 - 成长与徽章
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from datetime import datetime
from database import Base


class GrowthValue(Base):
    __tablename__ = "growth_values"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    last_updated_at = Column(DateTime, default=datetime.utcnow)


class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    badge_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)
    condition_type = Column(String(50), nullable=True)
    condition_value = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserBadge(Base):
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    badge_id = Column(Integer, ForeignKey("badges.id"), nullable=False)
    earned_at = Column(DateTime, default=datetime.utcnow)
    source_type = Column(String(50), nullable=True)
    source_id = Column(Integer, nullable=True)


class GrowthRecord(Base):
    __tablename__ = "growth_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    source_type = Column(String(50), nullable=False)
    source_id = Column(Integer, nullable=True)
    knowledge_base_delta = Column(Integer, nullable=True)
    practice_ability_delta = Column(Integer, nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
