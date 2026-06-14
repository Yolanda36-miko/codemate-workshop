"""
评估 API 路由
- GET  /api/assessment/questions    — Mock 题目获取（保留）
- POST /api/assessment/submit       — Mock 提交（保留）
- POST /api/assessment/records      — 保存评估记录 (Phase 4B)
- GET  /api/assessment/growth/{user_id} — 成长值与徽章查询 (Phase 4B)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services import assessment_service, diagnosis_service
from schemas.assessment import AssessmentRecordSaveRequest

router = APIRouter()


# ===================== 保留 Mock 端点 =====================

class SubmitAnswersRequest(BaseModel):
    answers: list[dict]


@router.get("/assessment/questions")
def get_questions(count: int = 3):
    """Return diagnosis questions for the assessment page."""
    return {"questions": diagnosis_service.get_questions(count)}


@router.post("/assessment/submit")
def submit_answers(req: SubmitAnswersRequest):
    return assessment_service.submit_answers(req.answers)


# ===================== Phase 4B: Assessment Record & Growth =====================

@router.post("/assessment/records")
def save_assessment_record(req: AssessmentRecordSaveRequest):
    """保存评估结果（对齐 assessments 表字段）"""
    result = assessment_service.save_assessment_record(req.model_dump())
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to save assessment record")
    return result


@router.get("/assessment/growth/{user_id}")
def get_user_growth(user_id: int):
    """获取用户成长值、等级、徽章与最近变动记录"""
    return assessment_service.get_user_growth(user_id)
