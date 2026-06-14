"""
资源生成与资源库 API 路由
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from services import resource_service

router = APIRouter()


# ===================== 资源生成（保留 Mock） =====================

class ResourceGenerateRequest(BaseModel):
    course_id: str
    knowledge_point: str
    difficulty: str = "入门"
    language: str = "Python"
    resource_types: list[str] | None = None


@router.post("/resources/generate")
def generate_resources(req: ResourceGenerateRequest):
    return resource_service.generate_resources(
        req.course_id, req.knowledge_point, req.difficulty, req.language, req.resource_types
    )


# ===================== 资源库（Phase 4A） =====================

@router.get("/resources/library")
def list_library_resources(
    course_code: Optional[str] = Query(None, description="课程代码，如 data_structures"),
    topic_code: Optional[str] = Query(None, description="主题代码，如 binary_tree_traversal"),
    type: Optional[str] = Query(None, description="资源类型，如 分层练习题"),
    difficulty: Optional[str] = Query(None, description="难度：基础/进阶/提高"),
    language: Optional[str] = Query(None, description="编程语言，如 Python"),
    tags: Optional[List[str]] = Query(None, description="标签列表（AND 逻辑）"),
    search: Optional[str] = Query(None, description="在标题和摘要中搜索关键词"),
):
    """资源库列表 — 支持按课程、主题、类型、难度、语言、标签、关键词筛选"""
    return resource_service.list_library_resources(
        course_code=course_code,
        topic_code=topic_code,
        resource_type=type,
        difficulty=difficulty,
        language=language,
        tags=tags,
        search=search,
    )


# ⚠️ /resources/library/stats MUST be defined before /resources/library/{resource_id}
# to prevent "stats" from being captured as a resource_id path parameter.

@router.get("/resources/library/stats")
def get_library_stats():
    """资源库统计 — 按课程、类型、难度分组计数"""
    return resource_service.get_library_stats()


@router.get("/resources/library/{resource_id}")
def get_library_resource(resource_id: str):
    """资源详情 — 含元数据和正文内容（Markdown 或 JSON）"""
    result = resource_service.get_library_resource_detail(resource_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Resource '{resource_id}' not found in library",
        )
    return result
