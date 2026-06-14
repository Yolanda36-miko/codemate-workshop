"""
知识点相关的 Pydantic Schemas
（主要 knowledge 类型定义在 schemas/course.py 中以保持关联）
"""
from schemas.course import (
    KnowledgePointListItem,
    KnowledgePointDetail,
    KnowledgePointResponse,
    KnowledgePointRelationItem,
)

__all__ = [
    "KnowledgePointListItem",
    "KnowledgePointDetail",
    "KnowledgePointResponse",
    "KnowledgePointRelationItem",
]
