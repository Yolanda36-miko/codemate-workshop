"""
CodeMate 轻量级多智能体协同层

提供 4 个功能智能体 + 1 个协调智能体，封装现有服务模块：

    ProfileAgent     — 学习画像采集
    ResourceAgent    — 个性化资源生成
    PathAgent        — 学习路径规划
    AssessmentAgent  — 智能辅导与闯关评估
    CoordinatorAgent — 多智能体流程协调

使用示例::

    from agents import CoordinatorAgent

    coordinator = CoordinatorAgent()

    # 查看工作流描述
    result = coordinator.describe_workflow()

    # 运行完整学习支持流程
    result = coordinator.run_learning_support_flow(
        profile_signals={
            "difficulties": ["递归调用栈", "树遍历"],
            "goals": ["刷题训练"],
            "preferences": ["代码示例", "分层练习"],
            "foundation_level": "基础",
            "programming_language": "C++",
        },
        topic="二叉树前序遍历",
        resource_types=["代码示例与注释", "图解讲义"],
        language="C++",
        question="二叉树的前序和中序遍历有什么区别？",
    )
"""

from .base_agent import BaseAgent, AgentResult
from .profile_agent import ProfileAgent
from .resource_agent import ResourceAgent
from .path_agent import PathAgent
from .assessment_agent import AssessmentAgent
from .coordinator_agent import CoordinatorAgent

__all__ = [
    "BaseAgent",
    "AgentResult",
    "ProfileAgent",
    "ResourceAgent",
    "PathAgent",
    "AssessmentAgent",
    "CoordinatorAgent",
]
