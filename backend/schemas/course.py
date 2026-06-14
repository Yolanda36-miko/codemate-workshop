"""
课程与知识点相关的 Pydantic Schemas
字段与 models/course.py 和 models/knowledge.py 对齐
"""
from pydantic import BaseModel, Field
from typing import Optional, List


# ---- Course ----

class CourseBase(BaseModel):
    course_code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    stage: Optional[str] = None
    positioning: Optional[str] = None
    keywords: Optional[str] = None


class CourseListItem(BaseModel):
    """课程列表项（含知识点计数）"""
    id: int
    course_code: str
    name: str
    description: Optional[str] = None
    stage: Optional[str] = None
    positioning: Optional[str] = None
    keywords: Optional[List[str]] = None
    knowledge_point_count: int = 0

    class Config:
        from_attributes = True


class CourseResponse(BaseModel):
    """课程详情"""
    id: int
    course_code: str
    name: str
    description: Optional[str] = None
    stage: Optional[str] = None
    positioning: Optional[str] = None
    keywords: Optional[str] = None

    class Config:
        from_attributes = True


# ---- Knowledge Point ----

class KnowledgePointListItem(BaseModel):
    """知识点列表项"""
    id: int
    name: str
    description: Optional[str] = None
    difficulty: Optional[str] = None
    tags: Optional[List[str]] = None
    common_errors: Optional[List[str]] = None

    class Config:
        from_attributes = True


class KnowledgePointDetail(BaseModel):
    """知识点详情（含所属课程和前置知识点）"""
    id: int
    name: str
    description: Optional[str] = None
    difficulty: Optional[str] = None
    tags: Optional[List[str]] = None
    common_errors: Optional[List[str]] = None
    course: Optional[dict] = None
    prerequisites: List[dict] = []

    class Config:
        from_attributes = True


class KnowledgePointResponse(BaseModel):
    """知识点 API 响应"""
    id: int
    course_id: int
    name: str
    description: Optional[str] = None
    difficulty: Optional[str] = None
    tags: Optional[str] = None
    common_errors: Optional[str] = None

    class Config:
        from_attributes = True


# ---- Relation helpers ----

class CourseRelationItem(BaseModel):
    course_code: str
    name: str
    relation: str


class KnowledgePointRelationItem(BaseModel):
    id: int
    name: str
    relation_type: str
