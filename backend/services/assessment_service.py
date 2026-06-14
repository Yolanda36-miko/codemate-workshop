"""
Assessment Service
- submit_answers: Mock 评估提交（保留原有行为）
- save_assessment_record / get_user_growth: DB CRUD (Phase 4B)
"""
import json
import logging
from typing import Optional

from database import SessionLocal
from models.assessment import Assessment, AssessmentAnswer
from models.growth import GrowthValue, GrowthRecord, Badge, UserBadge

from services import profile_service

logger = logging.getLogger(__name__)


# ---- Existing Mock endpoint (unchanged) ----

def submit_answers(answers: list[dict]):
    """Mock assessment submission — returns preset results."""
    return profile_service.load_mock("assessment")


# ---- Phase 4B: Assessment Record & Growth ----

def save_assessment_record(data: dict) -> Optional[dict]:
    """保存评估记录（对齐 assessments 表字段）"""
    db = None
    try:
        db = SessionLocal()
        assessment = Assessment(
            user_id=data["user_id"],
            topic=data.get("topic"),
            question=data.get("question"),
            score=data.get("score"),
            total_questions=data.get("total_questions"),
            correct_count=data.get("correct_count"),
            wrong_points=data.get("wrong_points"),
            growth_delta=data.get("growth_delta"),
            badge_awarded=data.get("badge_awarded"),
        )
        db.add(assessment)
        db.flush()  # get assessment.id before commit

        # Save individual answers
        answers_data = data.get("answers") or []
        saved_answers = []
        for ans in answers_data:
            answer = AssessmentAnswer(
                assessment_id=assessment.id,
                question_id=ans.get("question_id") if isinstance(ans, dict) else getattr(ans, "question_id", None),
                question_text=ans.get("question_text") if isinstance(ans, dict) else getattr(ans, "question_text", None),
                selected_answer=ans.get("selected_answer") if isinstance(ans, dict) else getattr(ans, "selected_answer", None),
                correct_answer=ans.get("correct_answer") if isinstance(ans, dict) else getattr(ans, "correct_answer", None),
                is_correct=ans.get("is_correct") if isinstance(ans, dict) else getattr(ans, "is_correct", None),
                knowledge_point=ans.get("knowledge_point") if isinstance(ans, dict) else getattr(ans, "knowledge_point", None),
                feedback=ans.get("feedback") if isinstance(ans, dict) else getattr(ans, "feedback", None),
            )
            db.add(answer)
            saved_answers.append(answer)

        db.commit()
        db.refresh(assessment)

        return {
            "id": assessment.id,
            "user_id": assessment.user_id,
            "topic": assessment.topic,
            "score": assessment.score,
            "total_questions": assessment.total_questions,
            "correct_count": assessment.correct_count,
            "wrong_points": assessment.wrong_points,
            "growth_delta": assessment.growth_delta,
            "badge_awarded": assessment.badge_awarded,
            "created_at": assessment.created_at.isoformat() if assessment.created_at else None,
        }
    except Exception as e:
        logger.warning("Failed to save assessment for user %d: %s", data.get("user_id"), e)
        if db:
            db.rollback()
        return None
    finally:
        if db:
            db.close()


def get_user_growth(user_id: int) -> dict:
    """获取用户成长值、等级与徽章"""
    db = None
    try:
        db = SessionLocal()

        # Growth value
        growth = db.query(GrowthValue).filter(
            GrowthValue.user_id == user_id
        ).first()
        growth_data = {
            "total_points": growth.total_points if growth else 0,
            "level": growth.level if growth else 1,
            "last_updated_at": growth.last_updated_at.isoformat() if (growth and growth.last_updated_at) else None,
        }

        # Badges
        user_badges = db.query(UserBadge).filter(
            UserBadge.user_id == user_id
        ).all()
        badges = []
        for ub in user_badges:
            badge = db.query(Badge).filter(Badge.id == ub.badge_id).first()
            if badge:
                badges.append({
                    "badge_id": badge.id,
                    "badge_code": badge.badge_code,
                    "name": badge.name,
                    "description": badge.description,
                    "icon": badge.icon,
                    "earned_at": ub.earned_at.isoformat() if ub.earned_at else None,
                })

        # Recent growth records
        records = db.query(GrowthRecord).filter(
            GrowthRecord.user_id == user_id
        ).order_by(GrowthRecord.created_at.desc()).limit(20).all()
        growth_records = [
            {
                "id": r.id,
                "source_type": r.source_type,
                "source_id": r.source_id,
                "knowledge_base_delta": r.knowledge_base_delta,
                "practice_ability_delta": r.practice_ability_delta,
                "reason": r.reason,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in records
        ]

        return {
            "user_id": user_id,
            "growth": growth_data,
            "badges": badges,
            "recent_records": growth_records,
            "source": "database",
        }
    except Exception as e:
        logger.warning("Failed to get growth for user %d: %s", user_id, e)
        return {
            "user_id": user_id,
            "growth": {"total_points": 0, "level": 1, "last_updated_at": None},
            "badges": [],
            "recent_records": [],
            "source": "mock_fallback",
        }
    finally:
        if db:
            db.close()
