"""
用户画像 API 路由
- POST /api/profile/chat       — Mock 对话（保留）
- POST /api/profile/generate   — Mock 画像生成（保留）
- GET  /api/profile/{user_id}  — 获取画像 (Phase 4B)
- PUT  /api/profile/{user_id}  — 创建/更新画像 (Phase 4B)
- GET  /api/profile/{user_id}/conversations — 对话历史 (Phase 4B)
- POST /api/profile/{user_id}/conversations — 追加对话 (Phase 4B)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from services import profile_service
from schemas.profile import (
    StudentProfileResponse,
    ProfileUpdate,
    ConversationCreateRequest,
    ConversationItem,
)

router = APIRouter()


# ===================== 保留 Mock 端点 =====================

class ChatRequest(BaseModel):
    message: str
    history: list[dict] | None = None


class GenerateProfileRequest(BaseModel):
    profile_data: dict | None = None


@router.post("/profile/chat")
def profile_chat(req: ChatRequest):
    return profile_service.chat(req.message, req.history)


@router.post("/profile/generate")
def profile_generate(req: GenerateProfileRequest | None = None):
    return profile_service.generate_profile(req.profile_data if req else None)


# ===================== Phase 4B: Profile CRUD =====================

@router.get("/profile/{user_id}")
def get_profile(user_id: int):
    """获取用户画像，若无记录返回 null 字段"""
    result = profile_service.get_profile(user_id)
    if result is None:
        return {
            "id": None,
            "user_id": user_id,
            "knowledge_base_score": None,
            "practice_ability_score": None,
            "cognitive_styles": None,
            "error_patterns": None,
            "learning_goals": None,
            "resource_preferences": None,
            "profile_summary": None,
            "diagnosis_status": None,
            "created_at": None,
            "updated_at": None,
            "source": "not_found",
        }
    return result


@router.put("/profile/{user_id}")
def upsert_profile(user_id: int, data: ProfileUpdate):
    """创建或更新用户画像"""
    update_dict = data.model_dump(exclude_unset=True)
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = profile_service.upsert_profile(user_id, update_dict)
    return result


@router.get("/profile/{user_id}/conversations")
def get_conversations(user_id: int):
    """获取用户画像对话历史"""
    conversations = profile_service.get_conversations(user_id)
    return {"conversations": conversations, "user_id": user_id}


@router.post("/profile/{user_id}/conversations")
def add_conversation(user_id: int, req: ConversationCreateRequest):
    """追加一条画像对话消息"""
    result = profile_service.add_conversation(
        user_id=user_id,
        role=req.role,
        message=req.message,
        extracted_fields=req.extracted_fields,
        missing_fields=req.missing_fields,
    )
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to save conversation")
    return result
