"""
资源生成、资源库与用户资源包 API 路由
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, model_validator
from typing import Optional, List
from services import resource_service
from schemas.resource import (
    UserResourcePackageCreate,
    UserResourcePackageUpdate,
    UserResourcePackageResponse,
)

router = APIRouter()


# ===================== 资源生成（Mock + LLM） =====================

class ResourceGenerateRequest(BaseModel):
    course_id: str
    knowledge_point: str
    learning_topic: str = ""       # frontend compat alias
    difficulty: str = "入门"
    language: str = "Python"
    resource_types: list[str] | None = None
    quick_profile: dict | None = None  # Phase 3B: quick personalization

    @model_validator(mode='before')
    @classmethod
    def normalize_fields(cls, data):
        if isinstance(data, dict):
            kp = data.get('knowledge_point', '')
            lt = data.get('learning_topic', '')
            if not kp and lt:
                data = {**data, 'knowledge_point': lt}
        return data

    @model_validator(mode='after')
    def check_knowledge_point(self):
        if not self.knowledge_point.strip():
            raise ValueError('knowledge_point 或 learning_topic 至少需要提供一个非空值')
        return self


@router.post("/resources/generate")
def generate_resources(req: ResourceGenerateRequest):
    return resource_service.generate_resources(
        course_id=req.course_id,
        knowledge_point=req.knowledge_point,
        difficulty=req.difficulty,
        language=req.language,
        resource_types=req.resource_types,
        quick_profile=req.quick_profile,
        learning_topic=req.learning_topic,
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


# ===================== 用户资源包（Phase 4B） =====================

@router.get("/resources/packages/{user_id}")
def get_user_packages(user_id: int):
    """获取用户的资源包列表"""
    packages = resource_service.get_user_packages(user_id)
    return {"packages": packages, "user_id": user_id, "total": len(packages)}


@router.post("/resources/packages")
def add_to_package(req: UserResourcePackageCreate, user_id: int = Query(..., description="用户 ID")):
    """添加资源到用户资源包"""
    result = resource_service.add_to_package(user_id, req.model_dump())
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to add to package")
    return result


@router.put("/resources/packages/{package_id}")
def update_package_item(package_id: int, req: UserResourcePackageUpdate, user_id: int = Query(..., description="用户 ID")):
    """更新资源包条目"""
    result = resource_service.update_package_item(package_id, user_id, req.model_dump(exclude_unset=True))
    if result is None:
        raise HTTPException(status_code=404, detail=f"Package #{package_id} not found")
    return result


@router.delete("/resources/packages/{package_id}")
def delete_package_item(package_id: int, user_id: int = Query(..., description="用户 ID")):
    """删除资源包条目"""
    ok = resource_service.delete_package_item(package_id, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Package #{package_id} not found")
    return {"detail": "deleted", "package_id": package_id}
