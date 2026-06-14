"""
Course & Knowledge Point Service
优先从数据库读取，异常时 fallback 到 Mock JSON 数据
"""
import json
import logging
from pathlib import Path
from typing import Optional

from database import SessionLocal
from models.course import Course, CourseRelation
from models.knowledge import KnowledgePoint, KnowledgePointRelation
from sqlalchemy import func

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"


# ---- Internal helpers ----

def _parse_keywords(keywords_str: Optional[str]) -> list[str]:
    """将数据库中 JSON 字符串格式的 keywords 解析为 list"""
    if not keywords_str:
        return []
    try:
        parsed = json.loads(keywords_str)
        if isinstance(parsed, list):
            return parsed
    except (json.JSONDecodeError, TypeError):
        pass
    return [keywords_str]


def _parse_tags(tags_str: Optional[str]) -> list[str]:
    """将数据库中 JSON 字符串格式的 tags/common_errors 解析为 list"""
    return _parse_keywords(tags_str)


def _load_mock_courses():
    """Fallback: 从 data/courses.json 读取旧 Mock 数据"""
    try:
        with open(DATA_DIR / "courses.json", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"courses": []}


# ---- Public API ----

def get_all_courses():
    """获取所有课程列表（含知识点计数）"""
    db = None
    try:
        db = SessionLocal()
        courses = db.query(Course).all()
        if courses:
            result = []
            for c in courses:
                kp_count = db.query(func.count(KnowledgePoint.id)).filter(
                    KnowledgePoint.course_id == c.id
                ).scalar()
                result.append({
                    "id": c.id,
                    "course_code": c.course_code,
                    "name": c.name,
                    "description": c.description,
                    "stage": c.stage,
                    "positioning": c.positioning,
                    "keywords": _parse_keywords(c.keywords),
                    "knowledge_point_count": kp_count or 0,
                })
            return {"courses": result, "source": "database"}
    except Exception as e:
        logger.warning("Failed to query courses from database: %s — falling back to mock", e)
    finally:
        if db:
            db.close()

    # Fallback to mock
    mock_data = _load_mock_courses()
    return {
        "courses": mock_data.get("courses", []),
        "source": "mock_fallback",
    }


def get_course_by_code(course_code: str):
    """根据 course_code 获取课程详情（含知识点、先修关系）"""
    if not course_code:
        return None

    db = None
    try:
        db = SessionLocal()
        course = db.query(Course).filter(Course.course_code == course_code).first()
        if not course:
            # Try mock fallback
            return _mock_course_detail(course_code)

        # Knowledge points for this course
        kps = db.query(KnowledgePoint).filter(
            KnowledgePoint.course_id == course.id
        ).all()
        kp_list = []
        for kp in kps:
            kp_list.append({
                "id": kp.id,
                "name": kp.name,
                "description": kp.description,
                "difficulty": kp.difficulty,
                "tags": _parse_tags(kp.tags),
                "common_errors": _parse_tags(kp.common_errors),
            })

        # Prerequisites: courses that this course depends on
        prereq_relations = db.query(CourseRelation).filter(
            CourseRelation.to_course_id == course.id,
            CourseRelation.relation_type == "prerequisite",
        ).all()
        prerequisites = []
        for rel in prereq_relations:
            prereq_course = db.query(Course).filter(Course.id == rel.from_course_id).first()
            if prereq_course:
                prerequisites.append({
                    "course_code": prereq_course.course_code,
                    "name": prereq_course.name,
                    "relation": "prerequisite",
                })

        # Related courses: courses that depend on this course
        related_relations = db.query(CourseRelation).filter(
            CourseRelation.from_course_id == course.id,
        ).all()
        related_courses = []
        for rel in related_relations:
            related_course = db.query(Course).filter(Course.id == rel.to_course_id).first()
            if related_course:
                related_courses.append({
                    "course_code": related_course.course_code,
                    "name": related_course.name,
                    "relation": "prerequisite_for",
                })

        return {
            "course": {
                "id": course.id,
                "course_code": course.course_code,
                "name": course.name,
                "description": course.description,
                "stage": course.stage,
                "positioning": course.positioning,
                "keywords": _parse_keywords(course.keywords),
            },
            "knowledge_points": kp_list,
            "prerequisites": prerequisites,
            "related_courses": related_courses,
            "source": "database",
        }
    except Exception as e:
        logger.warning("Failed to query course '%s' from database: %s — falling back to mock", course_code, e)
        return _mock_course_detail(course_code)
    finally:
        if db:
            db.close()


def _mock_course_detail(course_code: str):
    """Mock fallback for course detail"""
    mock_data = _load_mock_courses()
    for c in mock_data.get("courses", []):
        if c.get("id") == course_code or c.get("course_code") == course_code:
            return {
                "course": c,
                "knowledge_points": [],
                "prerequisites": [],
                "related_courses": [],
                "source": "mock_fallback",
            }
    return None


def get_knowledge_points_by_course(course_code: str):
    """按课程 code 获取知识点列表"""
    db = None
    try:
        db = SessionLocal()
        course = db.query(Course).filter(Course.course_code == course_code).first()
        if not course:
            return {"knowledge_points": [], "source": "mock_fallback"}

        kps = db.query(KnowledgePoint).filter(
            KnowledgePoint.course_id == course.id
        ).all()
        result = []
        for kp in kps:
            result.append({
                "id": kp.id,
                "name": kp.name,
                "description": kp.description,
                "difficulty": kp.difficulty,
                "tags": _parse_tags(kp.tags),
                "common_errors": _parse_tags(kp.common_errors),
            })
        return {"knowledge_points": result, "source": "database"}
    except Exception as e:
        logger.warning("Failed to query knowledge points for '%s': %s", course_code, e)
        return {"knowledge_points": [], "source": "mock_fallback"}
    finally:
        if db:
            db.close()


def get_knowledge_point_detail(kp_id: int):
    """获取知识点详情（含所属课程和前置知识点）"""
    db = None
    try:
        db = SessionLocal()
        kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == kp_id).first()
        if not kp:
            return None

        course = db.query(Course).filter(Course.id == kp.course_id).first()

        # Prerequisite knowledge points
        prereq_rels = db.query(KnowledgePointRelation).filter(
            KnowledgePointRelation.to_kp_id == kp.id
        ).all()
        prerequisites = []
        for rel in prereq_rels:
            prereq_kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == rel.from_kp_id).first()
            if prereq_kp:
                prerequisites.append({
                    "id": prereq_kp.id,
                    "name": prereq_kp.name,
                    "relation_type": rel.relation_type,
                })

        return {
            "knowledge_point": {
                "id": kp.id,
                "name": kp.name,
                "description": kp.description,
                "difficulty": kp.difficulty,
                "tags": _parse_tags(kp.tags),
                "common_errors": _parse_tags(kp.common_errors),
                "course": {
                    "course_code": course.course_code if course else None,
                    "name": course.name if course else None,
                } if course else None,
            },
            "prerequisites": prerequisites,
            "source": "database",
        }
    except Exception as e:
        logger.warning("Failed to query knowledge point #%d: %s", kp_id, e)
        return None
    finally:
        if db:
            db.close()
