"""
Path Service
- generate_path: Mock 学习路径生成（保留原有行为）
- Path + Node CRUD (Phase 4B)
"""
import logging
from typing import Optional

from database import SessionLocal
from models.path import LearningPath, LearningPathNode, PathNodeResource
from models.course import Course
from models.knowledge import KnowledgePoint

from services import profile_service

logger = logging.getLogger(__name__)


# ---- Existing Mock generator (unchanged) ----

def generate_path(student_profile: dict | None = None):
    """Mock path generation — returns the default learning path."""
    return profile_service.load_mock("path")


# ---- Phase 4B: Path CRUD ----

def create_path(user_id: int, data: dict) -> Optional[dict]:
    """创建学习路径"""
    db = None
    try:
        db = SessionLocal()
        path = LearningPath(
            user_id=user_id,
            name=data.get("name", "Untitled Path"),
            goal=data.get("goal"),
            source=data.get("source", "manual"),
            status=data.get("status", "active"),
        )
        db.add(path)
        db.commit()
        db.refresh(path)
        return {
            "id": path.id,
            "user_id": path.user_id,
            "name": path.name,
            "goal": path.goal,
            "source": path.source,
            "status": path.status,
            "created_at": path.created_at.isoformat() if path.created_at else None,
            "updated_at": path.updated_at.isoformat() if path.updated_at else None,
        }
    except Exception as e:
        logger.warning("Failed to create path for user %d: %s", user_id, e)
        if db:
            db.rollback()
        return None
    finally:
        if db:
            db.close()


def get_user_paths(user_id: int) -> list[dict]:
    """获取用户的所有学习路径"""
    db = None
    try:
        db = SessionLocal()
        paths = db.query(LearningPath).filter(
            LearningPath.user_id == user_id
        ).order_by(LearningPath.created_at.desc()).all()
        return [
            {
                "id": p.id,
                "user_id": p.user_id,
                "name": p.name,
                "goal": p.goal,
                "source": p.source,
                "status": p.status,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            }
            for p in paths
        ]
    except Exception as e:
        logger.warning("Failed to get paths for user %d: %s", user_id, e)
        return []
    finally:
        if db:
            db.close()


def get_path_detail(path_id: int, user_id: int) -> Optional[dict]:
    """获取学习路径详情（含节点列表与关联资源）"""
    db = None
    try:
        db = SessionLocal()
        path = db.query(LearningPath).filter(
            LearningPath.id == path_id,
            LearningPath.user_id == user_id,
        ).first()
        if not path:
            return None

        nodes = db.query(LearningPathNode).filter(
            LearningPathNode.path_id == path_id
        ).order_by(LearningPathNode.node_order.asc()).all()

        node_list = []
        for node in nodes:
            course_name = None
            kp_name = None
            if node.course_id:
                course = db.query(Course).filter(Course.id == node.course_id).first()
                if course:
                    course_name = course.name
            if node.knowledge_point_id:
                kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == node.knowledge_point_id).first()
                if kp:
                    kp_name = kp.name

            resources = db.query(PathNodeResource).filter(
                PathNodeResource.node_id == node.id
            ).all()
            resource_list = [
                {
                    "id": r.id,
                    "resource_id": r.resource_id,
                    "source": r.source,
                    "is_from_user_package": r.is_from_user_package,
                }
                for r in resources
            ]

            node_list.append({
                "id": node.id,
                "path_id": node.path_id,
                "node_order": node.node_order,
                "title": node.title,
                "course_id": node.course_id,
                "course_name": course_name,
                "knowledge_point_id": node.knowledge_point_id,
                "knowledge_point_name": kp_name,
                "learning_goal": node.learning_goal,
                "estimated_time": node.estimated_time,
                "status": node.status,
                "growth_targets": node.growth_targets,
                "resources": resource_list,
                "created_at": node.created_at.isoformat() if node.created_at else None,
                "updated_at": node.updated_at.isoformat() if node.updated_at else None,
            })

        return {
            "id": path.id,
            "user_id": path.user_id,
            "name": path.name,
            "goal": path.goal,
            "source": path.source,
            "status": path.status,
            "nodes": node_list,
            "created_at": path.created_at.isoformat() if path.created_at else None,
            "updated_at": path.updated_at.isoformat() if path.updated_at else None,
        }
    except Exception as e:
        logger.warning("Failed to get path detail #%d: %s", path_id, e)
        return None
    finally:
        if db:
            db.close()


def update_path(path_id: int, user_id: int, data: dict) -> Optional[dict]:
    """更新学习路径"""
    db = None
    try:
        db = SessionLocal()
        path = db.query(LearningPath).filter(
            LearningPath.id == path_id,
            LearningPath.user_id == user_id,
        ).first()
        if not path:
            return None

        updatable = ["name", "goal", "status"]
        for field in updatable:
            if field in data:
                setattr(path, field, data[field])

        db.commit()
        db.refresh(path)
        return {
            "id": path.id,
            "user_id": path.user_id,
            "name": path.name,
            "goal": path.goal,
            "source": path.source,
            "status": path.status,
            "created_at": path.created_at.isoformat() if path.created_at else None,
            "updated_at": path.updated_at.isoformat() if path.updated_at else None,
        }
    except Exception as e:
        logger.warning("Failed to update path #%d: %s", path_id, e)
        if db:
            db.rollback()
        return None
    finally:
        if db:
            db.close()


def create_node(path_id: int, user_id: int, data: dict) -> Optional[dict]:
    """向学习路径添加节点"""
    db = None
    try:
        db = SessionLocal()
        # Verify path belongs to user
        path = db.query(LearningPath).filter(
            LearningPath.id == path_id,
            LearningPath.user_id == user_id,
        ).first()
        if not path:
            return None

        node = LearningPathNode(
            path_id=path_id,
            node_order=data.get("node_order", 0),
            title=data.get("title", ""),
            course_id=data.get("course_id"),
            knowledge_point_id=data.get("knowledge_point_id"),
            learning_goal=data.get("learning_goal"),
            estimated_time=data.get("estimated_time"),
            status=data.get("status", "not_started"),
            growth_targets=data.get("growth_targets"),
        )
        db.add(node)
        db.commit()
        db.refresh(node)
        return {
            "id": node.id,
            "path_id": node.path_id,
            "node_order": node.node_order,
            "title": node.title,
            "course_id": node.course_id,
            "knowledge_point_id": node.knowledge_point_id,
            "learning_goal": node.learning_goal,
            "estimated_time": node.estimated_time,
            "status": node.status,
            "growth_targets": node.growth_targets,
            "created_at": node.created_at.isoformat() if node.created_at else None,
            "updated_at": node.updated_at.isoformat() if node.updated_at else None,
        }
    except Exception as e:
        logger.warning("Failed to create node for path #%d: %s", path_id, e)
        if db:
            db.rollback()
        return None
    finally:
        if db:
            db.close()


def update_node(node_id: int, data: dict) -> Optional[dict]:
    """更新路径节点（常用于状态变更）"""
    db = None
    try:
        db = SessionLocal()
        node = db.query(LearningPathNode).filter(
            LearningPathNode.id == node_id
        ).first()
        if not node:
            return None

        updatable = [
            "title", "node_order", "learning_goal", "estimated_time",
            "status", "growth_targets",
        ]
        for field in updatable:
            if field in data:
                setattr(node, field, data[field])

        db.commit()
        db.refresh(node)
        return {
            "id": node.id,
            "path_id": node.path_id,
            "node_order": node.node_order,
            "title": node.title,
            "course_id": node.course_id,
            "knowledge_point_id": node.knowledge_point_id,
            "learning_goal": node.learning_goal,
            "estimated_time": node.estimated_time,
            "status": node.status,
            "growth_targets": node.growth_targets,
            "created_at": node.created_at.isoformat() if node.created_at else None,
            "updated_at": node.updated_at.isoformat() if node.updated_at else None,
        }
    except Exception as e:
        logger.warning("Failed to update node #%d: %s", node_id, e)
        if db:
            db.rollback()
        return None
    finally:
        if db:
            db.close()


def link_node_resource(node_id: int, data: dict) -> Optional[dict]:
    """关联资源到路径节点"""
    db = None
    try:
        db = SessionLocal()
        node = db.query(LearningPathNode).filter(
            LearningPathNode.id == node_id
        ).first()
        if not node:
            return None

        link = PathNodeResource(
            node_id=node_id,
            resource_id=data.get("resource_id"),
            source=data.get("source", "resource_library"),
            is_from_user_package=data.get("is_from_user_package", False),
        )
        db.add(link)
        db.commit()
        db.refresh(link)
        return {
            "id": link.id,
            "node_id": link.node_id,
            "resource_id": link.resource_id,
            "source": link.source,
            "is_from_user_package": link.is_from_user_package,
            "created_at": link.created_at.isoformat() if link.created_at else None,
        }
    except Exception as e:
        logger.warning("Failed to link resource to node #%d: %s", node_id, e)
        if db:
            db.rollback()
        return None
    finally:
        if db:
            db.close()
