"""
Prompt Service (Phase 5A)

Loads and renders Jinja2 prompt templates from the prompts/ directory.
Does NOT call LLMs — that's llm_service.py's job.

Usage:
    from services.prompt_service import load_template, render_template
    raw = load_template("chat_profile")
    rendered = render_template("chat_profile", student_name="李同学", extracted_fields={})
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

_JINJA_ENV: Optional[object] = None


def _get_env():
    """Lazy-load Jinja2 environment."""
    global _JINJA_ENV
    if _JINJA_ENV is not None:
        return _JINJA_ENV
    try:
        from jinja2 import Environment, FileSystemLoader, BaseLoader, TemplateNotFound as JinjaNotFound  # type: ignore
    except ImportError:
        raise ImportError(
            "jinja2 package is not installed. Run: pip install jinja2"
        )
    _JINJA_ENV = Environment(
        loader=FileSystemLoader(str(PROMPTS_DIR)),
        autoescape=False,
    )
    return _JINJA_ENV


def load_template(name: str) -> str:
    """
    Load a raw template from prompts/<name>.

    Automatically appends .txt if the name doesn't have an extension.
    Returns empty string if the file doesn't exist.
    """
    if not name.endswith(".txt"):
        filename = f"{name}.txt"
    else:
        filename = name

    path = PROMPTS_DIR / filename
    if not path.exists():
        logger.warning("Prompt template not found: %s", path)
        return ""

    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        logger.warning("Failed to read prompt template %s: %s", path, e)
        return ""


def render_template(name: str, **kwargs) -> str:
    """
    Load and render a Jinja2 template with the given keyword arguments.

    Falls back to empty string if the template cannot be loaded or rendered.
    """
    if not name.endswith(".txt"):
        template_name = f"{name}.txt"
    else:
        template_name = name

    try:
        env = _get_env()
        tmpl = env.get_template(template_name)
        return tmpl.render(**kwargs)
    except Exception as e:
        logger.warning("Failed to render prompt template %r: %s", name, e)
        return ""
