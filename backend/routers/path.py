"""
学习路径 API 路由
- POST /api/path/generate            — Mock 路径生成（保留）
- GET  /api/paths/{user_id}          — 用户路径列表 (Phase 4B)
- POST /api/paths                    — 创建路径 (Phase 4B)
- GET  /api/paths/{path_id}          — 路径详情含节点 (Phase 4B)
- PUT  /api/paths/{path_id}          — 更新路径 (Phase 4B)
- POST /api/paths/{path_id}/nodes    — 添加节点 (Phase 4B)
- PUT  /api/paths/nodes/{node_id}    — 更新节点 (Phase 4B)
- POST /api/paths/nodes/{node_id}/resources — 关联资源 (Phase 4B)
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from services import path_service
from schemas.learning_path import (
    PathCreateRequest,
    PathUpdateRequest,
    PathNodeCreateRequest,
    PathNodeUpdateRequest,
    PathNodeResourceLinkRequest,
)

router = APIRouter()


# ===================== 保留 Mock 端点 =====================

class PathGenerateRequest(BaseModel):
    student_profile: dict | None = None


@router.post("/path/generate")
def generate_path(req: PathGenerateRequest | None = None):
    return path_service.generate_path(req.student_profile if req else None)


# ===================== Phase 4B: Path & Node CRUD =====================

@router.get("/paths/{user_id}")
def list_paths(user_id: int):
    """获取用户的所有学习路径"""
    paths = path_service.get_user_paths(user_id)
    return {"paths": paths, "user_id": user_id, "total": len(paths)}


@router.post("/paths")
def create_path(req: PathCreateRequest, user_id: int = Query(..., description="用户 ID")):
    """创建学习路径，可选附带节点列表"""
    data = req.model_dump()
    result = path_service.create_path(user_id, data)
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to create path")

    # 如果有节点，批量创建
    nodes_data = data.get("nodes") or []
    created_nodes = []
    for nd in nodes_data:
        node = path_service.create_node(result["id"], user_id, nd)
        if node:
            created_nodes.append(node)

    result["nodes"] = created_nodes
    return result


@router.get("/paths/{path_id}")
def get_path_detail(path_id: int, user_id: int = Query(..., description="用户 ID")):
    """获取路径详情（含节点列表与关联资源）"""
    result = path_service.get_path_detail(path_id, user_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Path #{path_id} not found")
    return result


@router.put("/paths/{path_id}")
def update_path(path_id: int, req: PathUpdateRequest, user_id: int = Query(..., description="用户 ID")):
    """更新学习路径"""
    result = path_service.update_path(path_id, user_id, req.model_dump(exclude_unset=True))
    if result is None:
        raise HTTPException(status_code=404, detail=f"Path #{path_id} not found")
    return result


@router.post("/paths/{path_id}/nodes")
def create_node(path_id: int, req: PathNodeCreateRequest, user_id: int = Query(..., description="用户 ID")):
    """向路径添加节点"""
    result = path_service.create_node(path_id, user_id, req.model_dump())
    if result is None:
        raise HTTPException(status_code=404, detail=f"Path #{path_id} not found")
    return result


@router.put("/paths/nodes/{node_id}")
def update_node(node_id: int, req: PathNodeUpdateRequest):
    """更新路径节点（状态、顺序、目标等）"""
    result = path_service.update_node(node_id, req.model_dump(exclude_unset=True))
    if result is None:
        raise HTTPException(status_code=404, detail=f"Node #{node_id} not found")
    return result


@router.post("/paths/nodes/{node_id}/resources")
def link_node_resource(node_id: int, req: PathNodeResourceLinkRequest):
    """关联资源到路径节点"""
    result = path_service.link_node_resource(node_id, req.model_dump())
    if result is None:
        raise HTTPException(status_code=404, detail=f"Node #{node_id} not found")
    return result
