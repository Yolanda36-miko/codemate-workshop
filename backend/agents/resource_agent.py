"""
ResourceAgent — 个性化资源生成智能体

Accepts a topic, resource types, and profile signals; delegates to
resource_service.generate_resources() and returns structured resource cards.
"""

from typing import Any

from .base_agent import BaseAgent, AgentResult


class ResourceAgent(BaseAgent):
    name = "Resource Agent"
    role = "个性化资源生成"
    responsibilities = [
        "根据学习主题、资源类型偏好和画像信号生成个性化学习资源",
        "结合本地资源库检索、LLM/Mock 生成和动态 Fallback 提供资源卡片",
        "通过后处理校验（相关性、深度、内容正确性）保证资源质量",
    ]

    def process(self, **kwargs: Any) -> AgentResult:
        topic = kwargs.get("topic", "")
        resource_types = kwargs.get("resource_types") or []
        profile_signals = kwargs.get("profile_signals") or {}
        language = kwargs.get("language", "Python")
        course_id = kwargs.get("course_id", "data_structures")
        difficulty = kwargs.get("difficulty", "入门")

        from services import resource_service

        quick_profile = self._build_quick_profile(profile_signals)

        result = resource_service.generate_resources(
            course_id=course_id,
            knowledge_point=topic,
            difficulty=difficulty,
            language=language,
            resource_types=resource_types if resource_types else None,
            quick_profile=quick_profile,
            learning_topic=topic,
        )

        cards = result.get("resource_cards", [])
        return AgentResult(
            agent_name=self.name,
            success=len(cards) > 0,
            data={
                "resource_cards": cards,
                "topic": result.get("topic", topic),
                "normalized_module": result.get("normalized_module", ""),
                "programming_language_used": result.get("programming_language_used", language),
                "fallback": result.get("fallback", False),
                "generation_signature": result.get("generation_signature", ""),
            },
            summary=f"为「{result.get('topic', topic)}」生成 {len(cards)} 张资源卡片"
                     f"{'（Fallback 模式）' if result.get('fallback') else ''}",
        )

    @staticmethod
    def _build_quick_profile(signals: dict[str, Any]) -> dict[str, Any]:
        """Convert agent profile_signals to the quick_profile format expected by resource_service."""
        if not signals:
            return {}
        qp: dict[str, Any] = {}
        if signals.get("foundation_level"):
            qp["foundation_level"] = signals["foundation_level"]
        if signals.get("goals"):
            qp["learning_goal"] = signals["goals"][0] if signals["goals"] else ""
        if signals.get("programming_language"):
            qp["programming_language"] = signals["programming_language"]
        if signals.get("difficulties"):
            qp["current_difficulties"] = signals["difficulties"]
        if signals.get("preferences"):
            qp["expression_preferences"] = signals["preferences"]
        return qp
