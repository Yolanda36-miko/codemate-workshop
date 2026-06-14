"""
Resource Service
- generate_resources: Mock 资源生成（保留原有行为）
- 资源库索引读取、详情、搜索、统计 (Phase 4A)
"""
import json
import logging
from pathlib import Path
from typing import Optional

from services import profile_service

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
LIBRARY_DIR = DATA_DIR / "resource_library"
INDEX_PATH = LIBRARY_DIR / "index.json"


# ---- Existing Mock generator (unchanged) ----

def generate_resources(
    course_id: str,
    knowledge_point: str,
    difficulty: str = "入门",
    language: str = "Python",
    resource_types: list[str] | None = None,
):
    """Mock resource generation — returns preset resource cards."""
    return profile_service.load_mock("resources")


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
            return "markdown", raw  # 默认按 markdown 处理
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


# ---- Public API ----

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

    # 返回元数据（不含 contentPath 减少响应体积）
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
    """
    资源详情 — 元数据 + 正文内容
    返回 None 表示未找到，返回 dict 含 content_type、content 或 content_json
    """
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
