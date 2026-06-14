"""
Profile Service
- chat / generate_profile: Mock 画像对话与生成（保留原有行为）
- get_profile / upsert_profile / get_conversations / add_conversation: DB CRUD (Phase 4B)
"""
import json
import logging
from pathlib import Path
from typing import Optional

from database import SessionLocal
from models.profile import StudentProfile, ProfileConversation

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"


def load_mock(name: str):
    with open(DATA_DIR / "mock_responses.json", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(name, {})


# ---- Existing Mock endpoints (unchanged) ----

def chat(message: str, history: list[dict] | None = None):
    """Mock profile chat — returns next question and extracted/missing fields."""
    return load_mock("profile_chat")


def generate_profile(profile_data: dict | None = None):
    """Mock profile generation — returns the default student profile."""
    with open(DATA_DIR / "default_profile.json", encoding="utf-8") as f:
        return json.load(f)


# ---- Phase 4B: DB CRUD ----

def get_profile(user_id: int) -> Optional[dict]:
    """获取用户画像，无记录时返回 None"""
    db = None
    try:
        db = SessionLocal()
        profile = db.query(StudentProfile).filter(
            StudentProfile.user_id == user_id
        ).first()
        if profile is None:
            return None
        return {
            "id": profile.id,
            "user_id": profile.user_id,
            "knowledge_base_score": profile.knowledge_base_score,
            "practice_ability_score": profile.practice_ability_score,
            "cognitive_styles": profile.cognitive_styles,
            "error_patterns": profile.error_patterns,
            "learning_goals": profile.learning_goals,
            "resource_preferences": profile.resource_preferences,
            "profile_summary": profile.profile_summary,
            "diagnosis_status": profile.diagnosis_status,
            "created_at": profile.created_at.isoformat() if profile.created_at else None,
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
            "source": "database",
        }
    except Exception as e:
        logger.warning("Failed to get profile for user %d: %s", user_id, e)
        return None
    finally:
        if db:
            db.close()


def upsert_profile(user_id: int, data: dict) -> dict:
    """创建或更新用户画像（upsert）"""
    db = None
    try:
        db = SessionLocal()
        profile = db.query(StudentProfile).filter(
            StudentProfile.user_id == user_id
        ).first()

        if profile is None:
            profile = StudentProfile(user_id=user_id)
            db.add(profile)

        # 仅更新显式传入的字段
        updatable = [
            "knowledge_base_score", "practice_ability_score",
            "cognitive_styles", "error_patterns", "learning_goals",
            "resource_preferences", "profile_summary", "diagnosis_status",
        ]
        for field in updatable:
            if field in data:
                setattr(profile, field, data[field])

        db.commit()
        db.refresh(profile)

        return {
            "id": profile.id,
            "user_id": profile.user_id,
            "knowledge_base_score": profile.knowledge_base_score,
            "practice_ability_score": profile.practice_ability_score,
            "cognitive_styles": profile.cognitive_styles,
            "error_patterns": profile.error_patterns,
            "learning_goals": profile.learning_goals,
            "resource_preferences": profile.resource_preferences,
            "profile_summary": profile.profile_summary,
            "diagnosis_status": profile.diagnosis_status,
            "created_at": profile.created_at.isoformat() if profile.created_at else None,
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
            "source": "database",
        }
    except Exception as e:
        logger.warning("Failed to upsert profile for user %d: %s — falling back to mock", user_id, e)
        if db:
            db.rollback()
        # Fallback: return the input data as-is
        return {**data, "user_id": user_id, "source": "mock_fallback"}
    finally:
        if db:
            db.close()


def get_conversations(user_id: int) -> list[dict]:
    """获取用户画像对话历史"""
    db = None
    try:
        db = SessionLocal()
        conversations = db.query(ProfileConversation).filter(
            ProfileConversation.user_id == user_id
        ).order_by(ProfileConversation.created_at.asc()).all()
        return [
            {
                "id": c.id,
                "user_id": c.user_id,
                "role": c.role,
                "message": c.message,
                "extracted_fields": c.extracted_fields,
                "missing_fields": c.missing_fields,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in conversations
        ]
    except Exception as e:
        logger.warning("Failed to get conversations for user %d: %s", user_id, e)
        return []
    finally:
        if db:
            db.close()


def add_conversation(user_id: int, role: str, message: str,
                     extracted_fields: Optional[str] = None,
                     missing_fields: Optional[str] = None) -> Optional[dict]:
    """追加一条对话消息"""
    db = None
    try:
        db = SessionLocal()
        conv = ProfileConversation(
            user_id=user_id,
            role=role,
            message=message,
            extracted_fields=extracted_fields,
            missing_fields=missing_fields,
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)
        return {
            "id": conv.id,
            "user_id": conv.user_id,
            "role": conv.role,
            "message": conv.message,
            "extracted_fields": conv.extracted_fields,
            "missing_fields": conv.missing_fields,
            "created_at": conv.created_at.isoformat() if conv.created_at else None,
        }
    except Exception as e:
        logger.warning("Failed to add conversation for user %d: %s", user_id, e)
        if db:
            db.rollback()
        return None
    finally:
        if db:
            db.close()
