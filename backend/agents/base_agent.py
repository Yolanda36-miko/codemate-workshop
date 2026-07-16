"""
Lightweight Agent base class.

Each Agent wraps a specific domain capability (profile, resource generation,
path planning, assessment) and exposes a uniform interface for the Coordinator.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentResult:
    """Standardised result envelope returned by every Agent."""

    agent_name: str
    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    summary: str = ""


class BaseAgent(ABC):
    """
    Abstract base for all CodeMate agents.

    Subclasses must define ``name``, ``role``, ``responsibilities`` and
    implement ``process()``.  The ``run()`` convenience method wraps
    ``process()`` so callers always get an ``AgentResult``.
    """

    name: str
    role: str
    responsibilities: list[str] = []

    @abstractmethod
    def process(self, **kwargs: Any) -> AgentResult:
        """Execute the agent's core logic and return a structured result."""
        ...

    def run(self, **kwargs: Any) -> AgentResult:
        """Convenience wrapper that guarantees an AgentResult on failure."""
        try:
            return self.process(**kwargs)
        except Exception as exc:
            return AgentResult(
                agent_name=self.name,
                success=False,
                summary=f"{self.name} 执行失败：{exc}",
            )

    def describe(self) -> dict[str, Any]:
        """Return a human-readable description of this agent."""
        return {
            "name": self.name,
            "role": self.role,
            "responsibilities": self.responsibilities,
        }
