"""
Resource Service
- generate_resources: Mock 资源生成（保留原有行为）
- 资源库索引读取、详情、搜索、统计 (Phase 4A)
- 用户资源包 CRUD (Phase 4B)
"""
import json
import logging
from pathlib import Path
from typing import Optional

from database import SessionLocal
from models.resource import UserResourcePackage

from services import profile_service

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
LIBRARY_DIR = DATA_DIR / "resource_library"
INDEX_PATH = LIBRARY_DIR / "index.json"


# ---- Resource Generation (Phase 7A: LLM-integrated) ----

def generate_resources(
    course_id: str,
    knowledge_point: str,
    difficulty: str = "入门",
    language: str = "Python",
    resource_types: list[str] | None = None,
):
    """
    Generate personalized learning resources.

    LLM_PROVIDER=mock:
      Returns the original mock response from mock_responses.json directly.

    LLM_PROVIDER=openai | anthropic:
      Renders generate_resources.txt prompt, calls the real LLM,
      validates + enriches the JSON response. Falls back to mock on any failure.
    """
    from services.llm_service import get_llm, MockProvider

    llm = get_llm()

    # Mock mode: keep original behavior unchanged
    if isinstance(llm, MockProvider):
        return profile_service.load_mock("resources")

    # Real provider: render prompt, call LLM, validate + fallback
    try:
        result = _generate_via_llm(llm, course_id, knowledge_point, difficulty, language, resource_types)
        if result is not None:
            return result
    except Exception as e:
        logger.warning("LLM generate_resources failed: %s — falling back to mock", e)

    return profile_service.load_mock("resources")


def _generate_via_llm(
    llm,
    course_id: str,
    knowledge_point: str,
    difficulty: str = "入门",
    language: str = "Python",
    resource_types: list[str] | None = None,
) -> dict | None:
    """
    Render prompt, call LLM, validate response, enrich resource cards.

    Returns {"resource_cards": [...]} on success, or None if anything fails
    (prompt rendering, LLM error, JSON parse failure, structural validation).
    """
    from services.prompt_service import render_template

    effective_types = resource_types if resource_types else ["讲解文档", "代码示例", "练习题"]

    rendered = render_template(
        "generate_resources",
        course_id=course_id,
        knowledge_point=knowledge_point,
        difficulty=difficulty,
        language=language,
        resource_types=effective_types,
    )

    if not rendered:
        logger.warning("generate_resources template render returned empty — falling back to mock")
        return None

    messages: list[dict] = [
        {"role": "system", "content": rendered},
        {
            "role": "user",
            "content": (
                f"请为以下学习需求生成资源推荐：\n"
                f"课程：{course_id}\n"
                f"知识点：{knowledge_point}\n"
                f"难度：{difficulty}\n"
                f"语言：{language}\n"
                f"偏好类型：{', '.join(effective_types)}"
            ),
        },
    ]

    result = llm.chat_json(messages, temperature=0.7)

    if not isinstance(result, dict):
        logger.warning(
            "LLM chat_json returned non-dict (type=%s) — falling back to mock",
            type(result).__name__,
        )
        return None

    cards = result.get("resource_cards")
    if not isinstance(cards, list) or len(cards) == 0:
        logger.warning(
            "LLM response missing or empty 'resource_cards' list — falling back to mock"
        )
        return None

    # Validate, filter, and enrich each card
    enriched_cards: list[dict] = []
    for i, card in enumerate(cards):
        if not isinstance(card, dict):
            continue
        title = card.get("title")
        res_type = card.get("type")
        summary = card.get("summary", "")

        # Skip cards missing required LLM-generated fields
        if not isinstance(title, str) or not title.strip():
            continue
        if not isinstance(res_type, str) or not res_type.strip():
            continue
        if not isinstance(summary, str):
            summary = ""

        enriched_cards.append({
            "id": f"res-llm-{i + 1:03d}",
            "title": title.strip(),
            "type": res_type.strip(),
            "course": course_id,
            "knowledge_point": knowledge_point,
            "difficulty": difficulty,
            "language": language,
            "summary": summary.strip(),
        })

    if not enriched_cards:
        logger.warning("All LLM-generated resource cards were invalid — falling back to mock")
        return None

    return {"resource_cards": enriched_cards}


# ---- Internal helpers ----

def _load_index() -> Optional[dict]:
    """加载 resource_library/index.json"""
    if not INDEX_PATH.exists():
        logger.warning("Resource library index not found: %s", INDEX_PATH)
        return None
    try:
        with open(INDEX_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Failed to read resource library index: %s", e)
        return None


def _read_content_file(content_path: str) -> tuple[Optional[str], Optional[str]]:
    """
    读取资源正文文件
    返回 (content_type, content_str) 或 (content_type, None)
    """
    full_path = LIBRARY_DIR / content_path
    if not full_path.exists():
        logger.warning("Resource content file not found: %s", full_path)
        return None, None

    suffix = full_path.suffix.lower()
    try:
        with open(full_path, encoding="utf-8") as f:
            raw = f.read()
        if suffix == ".json":
            return "json", raw
        elif suffix in (".md", ".txt"):
            return "markdown", raw
        else:
            return "markdown", raw
    except OSError as e:
        logger.warning("Failed to read content file %s: %s", full_path, e)
        return None, None


def _filter_resources(
    resources: list[dict],
    course_code: Optional[str] = None,
    topic_code: Optional[str] = None,
    resource_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    language: Optional[str] = None,
    tags: Optional[list[str]] = None,
    search: Optional[str] = None,
) -> list[dict]:
    """在资源列表中按条件筛选"""
    result = resources
    if course_code:
        result = [r for r in result if r.get("courseCode") == course_code]
    if topic_code:
        result = [r for r in result if r.get("topicCode") == topic_code]
    if resource_type:
        result = [r for r in result if r.get("type") == resource_type]
    if difficulty:
        result = [r for r in result if r.get("difficulty") == difficulty]
    if language:
        result = [r for r in result if r.get("language") == language]
    if tags:
        for tag in tags:
            result = [r for r in result if tag in (r.get("tags") or [])]
    if search:
        search_lower = search.lower()
        result = [
            r for r in result
            if search_lower in (r.get("title") or "").lower()
            or search_lower in (r.get("summary") or "").lower()
        ]
    return result


# ---- Public API: Resource Library (Phase 4A) ----

def list_library_resources(
    course_code: Optional[str] = None,
    topic_code: Optional[str] = None,
    resource_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    language: Optional[str] = None,
    tags: Optional[list[str]] = None,
    search: Optional[str] = None,
) -> dict:
    """
    资源库列表（支持多条件筛选）
    返回元数据列表，不含正文内容
    """
    index = _load_index()
    if index is None:
        return {"resources": [], "total": 0, "source": "resource_library_unavailable"}

    all_resources = index.get("resources", [])
    filtered = _filter_resources(
        all_resources, course_code, topic_code, resource_type,
        difficulty, language, tags, search,
    )

    items = []
    for r in filtered:
        items.append({
            "id": r.get("id"),
            "title": r.get("title"),
            "course": r.get("course"),
            "courseCode": r.get("courseCode"),
            "topic": r.get("topic"),
            "topicCode": r.get("topicCode"),
            "type": r.get("type"),
            "difficulty": r.get("difficulty"),
            "language": r.get("language"),
            "tags": r.get("tags"),
            "estimatedTime": r.get("estimatedTime"),
            "summary": r.get("summary"),
        })

    return {
        "resources": items,
        "total": len(items),
        "source": "resource_library_index",
    }


def get_library_resource_detail(resource_id: str) -> Optional[dict]:
    """资源详情 — 元数据 + 正文内容"""
    index = _load_index()
    if index is None:
        return None

    all_resources = index.get("resources", [])
    match = None
    for r in all_resources:
        if r.get("id") == resource_id:
            match = r
            break

    if not match:
        return None

    detail = {
        "id": match.get("id"),
        "title": match.get("title"),
        "course": match.get("course"),
        "courseCode": match.get("courseCode"),
        "topic": match.get("topic"),
        "topicCode": match.get("topicCode"),
        "type": match.get("type"),
        "difficulty": match.get("difficulty"),
        "language": match.get("language"),
        "tags": match.get("tags"),
        "estimatedTime": match.get("estimatedTime"),
        "summary": match.get("summary"),
        "contentPath": match.get("contentPath"),
        "source": match.get("source"),
        "version": match.get("version"),
        "updatedAt": match.get("updatedAt"),
    }

    content_path = match.get("contentPath")
    if content_path:
        content_type, raw = _read_content_file(content_path)
        detail["content_type"] = content_type or "unknown"
        if content_type == "json" and raw:
            try:
                detail["content_json"] = json.loads(raw)
                detail["content"] = None
            except json.JSONDecodeError:
                detail["content"] = raw
                detail["content_json"] = None
        else:
            detail["content"] = raw
            detail["content_json"] = None
    else:
        detail["content_type"] = "none"
        detail["content"] = None
        detail["content_json"] = None

    return detail


def get_library_stats() -> dict:
    """资源库统计：按课程、类型、难度分组计数"""
    index = _load_index()
    if index is None:
        return {
            "total_resources": 0,
            "by_course": {},
            "by_type": {},
            "by_difficulty": {},
            "source": "resource_library_unavailable",
        }

    all_resources = index.get("resources", [])
    by_course: dict[str, int] = {}
    by_type: dict[str, int] = {}
    by_difficulty: dict[str, int] = {}

    for r in all_resources:
        cc = r.get("courseCode", "unknown")
        rt = r.get("type", "unknown")
        diff = r.get("difficulty", "unknown")
        by_course[cc] = by_course.get(cc, 0) + 1
        by_type[rt] = by_type.get(rt, 0) + 1
        by_difficulty[diff] = by_difficulty.get(diff, 0) + 1

    return {
        "total_resources": len(all_resources),
        "by_course": dict(sorted(by_course.items())),
        "by_type": dict(sorted(by_type.items())),
        "by_difficulty": dict(sorted(by_difficulty.items())),
        "source": "resource_library_index",
    }


# ---- Phase 4B: User Resource Package CRUD ----

def get_user_packages(user_id: int) -> list[dict]:
    """获取用户的资源包列表"""
    db = None
    try:
        db = SessionLocal()
        packages = db.query(UserResourcePackage).filter(
            UserResourcePackage.user_id == user_id
        ).order_by(UserResourcePackage.created_at.desc()).all()
        return [
            {
                "id": p.id,
                "user_id": p.user_id,
                "resource_id": p.resource_id,
                "library_resource_id": None,
                "custom_title": p.custom_title,
                "topic": p.topic,
                "course_name": p.course_name,
                "resource_type": p.resource_type,
                "estimated_time": p.estimated_time,
                "purpose": p.purpose,
                "priority": p.priority,
                "note": p.note,
                "status": p.status,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            }
            for p in packages
        ]
    except Exception as e:
        logger.warning("Failed to get packages for user %d: %s", user_id, e)
        return []
    finally:
        if db:
            db.close()


def add_to_package(user_id: int, data: dict) -> Optional[dict]:
    """添加资源到用户资源包（含去重：user_id + custom_title + topic + course_name）"""
    db = None
    try:
        db = SessionLocal()

        # Dedup: check if the same resource already exists for this user
        title = data.get("custom_title", "")
        topic = data.get("topic", "")
        course = data.get("course_name", "")
        existing = db.query(UserResourcePackage).filter(
            UserResourcePackage.user_id == user_id,
            UserResourcePackage.custom_title == title,
            UserResourcePackage.topic == topic,
            UserResourcePackage.course_name == course,
        ).first()

        if existing:
            return {
                "id": existing.id,
                "user_id": existing.user_id,
                "resource_id": existing.resource_id,
                "library_resource_id": None,
                "custom_title": existing.custom_title,
                "topic": existing.topic,
                "course_name": existing.course_name,
                "resource_type": existing.resource_type,
                "estimated_time": existing.estimated_time,
                "purpose": existing.purpose,
                "priority": existing.priority,
                "note": existing.note,
                "status": existing.status,
                "created_at": existing.created_at.isoformat() if existing.created_at else None,
                "updated_at": existing.updated_at.isoformat() if existing.updated_at else None,
                "detail": "already_saved",
            }

        pkg = UserResourcePackage(
            user_id=user_id,
            resource_id=data.get("resource_id"),
            custom_title=title,
            topic=topic,
            course_name=course,
            resource_type=data.get("resource_type"),
            estimated_time=data.get("estimated_time"),
            purpose=data.get("purpose"),
            priority=data.get("priority"),
            note=data.get("note"),
            status="saved",
        )
        db.add(pkg)
        db.commit()
        db.refresh(pkg)
        return {
            "id": pkg.id,
            "user_id": pkg.user_id,
            "resource_id": pkg.resource_id,
            "library_resource_id": data.get("library_resource_id"),
            "custom_title": pkg.custom_title,
            "topic": pkg.topic,
            "course_name": pkg.course_name,
            "resource_type": pkg.resource_type,
            "estimated_time": pkg.estimated_time,
            "purpose": pkg.purpose,
            "priority": pkg.priority,
            "note": pkg.note,
            "status": pkg.status,
            "created_at": pkg.created_at.isoformat() if pkg.created_at else None,
            "updated_at": pkg.updated_at.isoformat() if pkg.updated_at else None,
        }
    except Exception as e:
        logger.warning("Failed to add package for user %d: %s", user_id, e)
        if db:
            db.rollback()
        return None
    finally:
        if db:
            db.close()


def update_package_item(package_id: int, user_id: int, data: dict) -> Optional[dict]:
    """更新用户资源包条目"""
    db = None
    try:
        db = SessionLocal()
        pkg = db.query(UserResourcePackage).filter(
            UserResourcePackage.id == package_id,
            UserResourcePackage.user_id == user_id,
        ).first()
        if not pkg:
            return None

        updatable = [
            "custom_title", "topic", "course_name", "resource_type",
            "estimated_time", "purpose", "priority", "note", "status",
        ]
        for field in updatable:
            if field in data:
                setattr(pkg, field, data[field])

        db.commit()
        db.refresh(pkg)
        return {
            "id": pkg.id,
            "user_id": pkg.user_id,
            "resource_id": pkg.resource_id,
            "library_resource_id": None,
            "custom_title": pkg.custom_title,
            "topic": pkg.topic,
            "course_name": pkg.course_name,
            "resource_type": pkg.resource_type,
            "estimated_time": pkg.estimated_time,
            "purpose": pkg.purpose,
            "priority": pkg.priority,
            "note": pkg.note,
            "status": pkg.status,
            "created_at": pkg.created_at.isoformat() if pkg.created_at else None,
            "updated_at": pkg.updated_at.isoformat() if pkg.updated_at else None,
        }
    except Exception as e:
        logger.warning("Failed to update package #%d: %s", package_id, e)
        if db:
            db.rollback()
        return None
    finally:
        if db:
            db.close()


def delete_package_item(package_id: int, user_id: int) -> bool:
    """删除用户资源包条目"""
    db = None
    try:
        db = SessionLocal()
        pkg = db.query(UserResourcePackage).filter(
            UserResourcePackage.id == package_id,
            UserResourcePackage.user_id == user_id,
        ).first()
        if not pkg:
            return False
        db.delete(pkg)
        db.commit()
        return True
    except Exception as e:
        logger.warning("Failed to delete package #%d: %s", package_id, e)
        if db:
            db.rollback()
        return False
    finally:
        if db:
            db.close()
