"""
CoordinatorAgent — 多智能体协同调度

Orchestrates the four domain agents (Profile, Resource, Path, Assessment)
to deliver a complete learning-support flow.
"""

from typing import Any

from .base_agent import BaseAgent, AgentResult
from .profile_agent import ProfileAgent
from .resource_agent import ResourceAgent
from .path_agent import PathAgent
from .assessment_agent import AssessmentAgent


class CoordinatorAgent(BaseAgent):
    name = "Coordinator Agent"
    role = "多智能体流程协调"
    responsibilities = [
        "统一调度 ProfileAgent、ResourceAgent、PathAgent、AssessmentAgent 四个功能智能体",
        "组织完整的「画像 → 资源 → 路径 → 辅导评估」学习支持流程",
        "提供工作流描述和阶段性协同结果",
    ]

    def __init__(self) -> None:
        self.profile_agent = ProfileAgent()
        self.resource_agent = ResourceAgent()
        self.path_agent = PathAgent()
        self.assessment_agent = AssessmentAgent()

    def process(self, **kwargs: Any) -> AgentResult:
        """
        Run the full learning-support flow.

        Expected kwargs:
            mode: "full" | "describe" | "profile_only" | "resources_only" | "path_only" | "tutor" | "quiz"
            profile_signals, topic, resource_types, language, question, ...
        """
        mode = kwargs.pop("mode", "describe")

        if mode == "describe":
            return self._describe_workflow()
        if mode == "profile_only":
            return self.profile_agent.run(**kwargs)
        if mode == "resources_only":
            return self.resource_agent.run(**kwargs)
        if mode == "path_only":
            return self.path_agent.run(**kwargs)
        if mode == "tutor":
            return self.assessment_agent.run(mode="tutor", **kwargs)
        if mode == "quiz":
            return self.assessment_agent.run(mode="quiz", **kwargs)
        if mode == "full":
            return self._run_full_flow(**kwargs)

        return AgentResult(
            agent_name=self.name,
            success=False,
            summary=f"未知模式: {mode}",
        )

    # ------------------------------------------------------------------
    # Workflow description (documentation-facing)
    # ------------------------------------------------------------------

    def describe_workflow(self) -> AgentResult:
        """Return a structured description of the multi-agent workflow."""
        return self._describe_workflow()

    def _describe_workflow(self) -> AgentResult:
        steps = [
            {
                "step": 1,
                "agent": self.profile_agent.name,
                "role": self.profile_agent.role,
                "action": "接收学生对话或画像草稿，提取学习目标、困难点、基础水平、资源偏好和编程语言，输出结构化 profile_signals。",
            },
            {
                "step": 2,
                "agent": self.resource_agent.name,
                "role": self.resource_agent.role,
                "action": "根据学习主题、资源类型偏好和 profile_signals，检索本地资源库并生成个性化 ResourceCard，经后处理校验后返回。",
            },
            {
                "step": 3,
                "agent": self.path_agent.name,
                "role": self.path_agent.role,
                "action": "基于 profile_signals 中的学习困难映射重点模块，将匹配模块提前至复杂度分析之后，并结合资源偏好调整推荐资源。",
            },
            {
                "step": 4,
                "agent": self.assessment_agent.name,
                "role": self.assessment_agent.role,
                "action": "接收学生问题、当前学习主题和 profile_signals，提供辅导问答（核心解释 + 关键点 + 下一步建议）和闯关练习题。",
            },
        ]

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "workflow_name": "CodeMate 学习支持协同流程",
                "agent_count": 5,  # 4 domain + coordinator
                "steps": steps,
                "agents": [
                    a.describe()
                    for a in (self.profile_agent, self.resource_agent, self.path_agent, self.assessment_agent, self)
                ],
            },
            summary="CodeMate 采用轻量级多智能体协同架构：Coordinator 调度 4 个功能智能体，"
                    "按「画像采集 → 资源生成 → 路径规划 → 辅导评估」顺序组织学习支持流程。",
        )

    # ------------------------------------------------------------------
    # Full flow
    # ------------------------------------------------------------------

    def run_learning_support_flow(
        self,
        profile_signals: dict[str, Any] | None = None,
        topic: str = "",
        resource_types: list[str] | None = None,
        language: str = "Python",
        question: str = "",
    ) -> AgentResult:
        """Convenience method: run the full pipeline."""
        return self._run_full_flow(
            profile_signals=profile_signals or {},
            topic=topic,
            resource_types=resource_types or [],
            language=language,
            question=question,
        )

    def _run_full_flow(self, **kwargs: Any) -> AgentResult:
        profile_signals: dict[str, Any] = kwargs.get("profile_signals", {})
        topic: str = kwargs.get("topic", "")
        resource_types: list[str] = kwargs.get("resource_types", [])
        language: str = kwargs.get("language", "Python")
        question: str = kwargs.get("question", "")

        results: dict[str, Any] = {}

        # Step 1 – Path planning (profile → modules)
        path_result = self.path_agent.run(profile_signals=profile_signals)
        results["path"] = {
            "success": path_result.success,
            "summary": path_result.summary,
            "data": path_result.data,
        }

        # Step 2 – Resource generation (topic + profile → cards)
        if topic:
            res_result = self.resource_agent.run(
                topic=topic,
                resource_types=resource_types,
                profile_signals=profile_signals,
                language=language,
            )
            results["resources"] = {
                "success": res_result.success,
                "summary": res_result.summary,
                "data": res_result.data,
            }

        # Step 3 – Tutoring (question + topic + profile → feedback)
        if question:
            assess_result = self.assessment_agent.run(
                mode="tutor",
                question=question,
                topic=topic,
                profile_signals=profile_signals,
            )
            results["assessment"] = {
                "success": assess_result.success,
                "summary": assess_result.summary,
                "data": assess_result.data,
            }

        # Step 4 – Quiz generation
        if topic:
            quiz_result = self.assessment_agent.run(
                mode="quiz",
                topic=topic,
                profile_signals=profile_signals,
            )
            results["quiz"] = {
                "success": quiz_result.success,
                "summary": quiz_result.summary,
                "data": quiz_result.data,
            }

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "workflow": "画像 → 路径规划 → 资源生成 → 辅导评估",
                "profile_signals_used": profile_signals,
                "results": results,
            },
            summary=f"完成完整学习支持流程：路径({results.get('path', {}).get('success')}) "
                    f"→ 资源({results.get('resources', {}).get('success')}) "
                    f"→ 评估({results.get('assessment', {}).get('success')}) "
                    f"→ 闯关({results.get('quiz', {}).get('success')})",
        )
