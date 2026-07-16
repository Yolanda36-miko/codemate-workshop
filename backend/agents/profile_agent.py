"""
ProfileAgent — 学习画像采集智能体

Extracts structured profile signals from chat messages or profile drafts.
Wraps the existing profile_service.chat() pipeline.
"""

from typing import Any

from .base_agent import BaseAgent, AgentResult


class ProfileAgent(BaseAgent):
    name = "Profile Agent"
    role = "学习画像采集"
    responsibilities = [
        "通过对话式访谈采集学生的学习基础、困难点、目标和偏好",
        "从画像草稿中提取结构化的 profile_signals",
        "输出可用于后续个性化服务的标准化画像数据",
    ]

    def process(self, **kwargs: Any) -> AgentResult:
        message = kwargs.get("message", "")
        history = kwargs.get("history") or []
        extracted_fields = kwargs.get("extracted_fields") or {}
        missing_fields = kwargs.get("missing_fields") or []
        stage = kwargs.get("stage", "collect_profile")

        from services import profile_service

        result = profile_service.chat(
            message=message,
            history=history,
            extracted_fields=extracted_fields,
            missing_fields=missing_fields,
            stage=stage,
        )

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "reply": result.get("message", ""),
                "extracted_fields": result.get("extracted_fields", {}),
                "missing_fields": result.get("missing_fields", []),
                "stage": result.get("stage", stage),
                "is_complete": result.get("is_complete", False),
            },
            summary=f"画像采集阶段: {result.get('stage', stage)}",
        )

    def extract_signals(self, profile_draft: dict[str, Any] | None = None) -> dict[str, Any]:
        """Extract structured signals from a profile draft without a chat round."""
        if not profile_draft:
            return {"difficulties": [], "goals": [], "preferences": [],
                    "foundation_level": None, "programming_language": None}

        raw_diffs = (profile_draft.get("current_difficulties", []) +
                     profile_draft.get("learning_difficulties", []))
        if isinstance(raw_diffs, str):
            raw_diffs = [t.strip() for t in raw_diffs.split("、") if t.strip()]

        prefs = profile_draft.get("expression_preferences", [])
        if isinstance(prefs, str):
            prefs = [t.strip() for t in prefs.split("、") if t.strip()]

        goals = profile_draft.get("learning_goal", "")
        if isinstance(goals, list):
            goals = "、".join(goals)

        return {
            "difficulties": list({d for d in raw_diffs if d}),
            "goals": [goals] if goals else [],
            "preferences": prefs if isinstance(prefs, list) else [prefs],
            "foundation_level": profile_draft.get("foundation_level"),
            "programming_language": profile_draft.get("programming_language"),
        }
