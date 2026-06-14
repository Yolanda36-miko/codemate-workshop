"""
课程与知识点 API 路由
"""
from fastapi import APIRouter, HTTPException, Query
from services import course_service

router = APIRouter()


# ===================== 课程 =====================

@router.get("/courses")
def list_courses():
    """获取所有课程列表（含知识点计数）"""
    return course_service.get_all_courses()


@router.get("/courses/{course_code}")
def get_course(course_code: str):
    """获取课程详情（含知识点、先修关系、关联课程）"""
    result = course_service.get_course_by_code(course_code)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Course '{course_code}' not found",
        )
    return result


# ===================== 知识点 =====================

@router.get("/knowledge-points")
def list_knowledge_points(course_code: str = Query(..., description="课程代码，如 programming_basics")):
    """按课程代码获取知识点列表"""
    return course_service.get_knowledge_points_by_course(course_code)


@router.get("/knowledge-points/{kp_id}")
def get_knowledge_point(kp_id: int):
    """获取知识点详情（含所属课程和前置知识点）"""
    result = course_service.get_knowledge_point_detail(kp_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Knowledge point #{kp_id} not found",
        )
    return result
