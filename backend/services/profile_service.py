"""
Profile Service
- chat / generate_profile: Mock 画像对话与生成（保留原有行为）
- get_profile / upsert_profile / get_conversations / add_conversation: DB CRUD (Phase 4B)
"""
import json
import logging
import re
from pathlib import Path
from typing import Optional

from database import SessionLocal
from models.profile import StudentProfile, ProfileConversation

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"


def load_mock(name: str):
    with open(DATA_DIR / "mock_responses.json", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(name, {})


# ---- Role normalization for LLM provider compatibility ----

_ROLE_MAP = {
    "buddy": "assistant",
    "agent": "assistant",
    "assistant": "assistant",
    "user": "user",
    "student": "user",
    "system": "system",
}


def _normalize_role(role: str) -> str:
    """Normalize frontend role values to LLM-compatible roles (assistant/user/system)."""
    return _ROLE_MAP.get(role.lower().strip(), "user")


# ---- DS-specific field definitions ----

DS_FIELDS = [
    "learning_difficulties",
    "current_difficulties",
    "programming_language",
    "learned_courses",
    "expression_preferences",
    "learning_goal",
    "error_prone_points",
]

DS_FIELD_QUESTIONS: dict[str, str] = {
    "learning_difficulties": "你在学习数据结构与算法时，感觉最吃力的模块是哪一个？递归调用栈、二叉树遍历、图算法（BFS/DFS）、排序算法，还是动态规划？",
    "current_difficulties": "能具体说说卡在哪里吗？比如递归的终止条件容易写错、二叉树的遍历顺序容易混、还是图的 visited 标记时机搞不清？",
    "programming_language": "你希望代码示例使用 C++、Python、Java 还是 C？",
    "learned_courses": "你之前学过程序设计基础、离散数学这些先修课程吗？",
    "expression_preferences": "你更想看图解讲解、代码示例、易错点、分层练习还是项目案例？",
    "learning_goal": "你现在更偏考试复习、刷题训练、课程作业还是项目实践？",
    "error_prone_points": "你在写算法题时容易在哪些地方出错？比如递归终止条件漏写、遍历顺序搞反、复杂度分析算错、visited 标记时机不对，还是状态转移方程推不出来？",
}

KEY_FIELDS = ["programming_language", "learning_goal", "foundation_level", "current_difficulties", "expression_preferences", "learned_courses", "error_prone_points"]


def _split_tags(val: str) -> set[str]:
    """Split a '、'-joined string into a set of tags, filtering empties."""
    if not val or not val.strip():
        return set()
    return {t.strip() for t in val.split("、") if t.strip()}


def _extract_from_message(message: str, ef: dict, mf: list[str]) -> set[str]:
    """
    Extract & merge DS-specific profile fields from user message.
    Mutates ef (merge) and mf (remove on first fill) in-place.

    Returns the set of field keys that were updated in this message.
    """
    lower = message.lower()
    updated: set[str] = set()

    # ===== single-value: only set if detected in current message =====

    # --- programming_language ---
    lang = None
    if any(w in lower for w in ["c++", "cpp", "cplusplus", "c plus plus"]):
        lang = "C++"
    elif "python" in lower:
        lang = "Python"
    elif "java" in lower and "javascript" not in lower:
        lang = "Java"
    elif "c语言" in lower or (" c " in lower and "c++" not in lower and "cplusplus" not in lower):
        lang = "C"
    if lang:
        ef["programming_language"] = lang
        if "programming_language" in mf:
            mf.remove("programming_language")
        updated.add("programming_language")

    # --- learning_goal ---
    goals = []
    if any(w in lower for w in ["刷题", "题目", "leetcode", "力扣", "牛客"]):
        goals.append("刷题训练")
    if any(w in lower for w in ["考试", "复习", "期末"]):
        goals.append("考试复习")
    if any(w in lower for w in ["课程作业", "作业"]):
        goals.append("课程作业")
    if any(w in lower for w in ["项目实践"]):
        goals.append("项目实践")
    if any(w in lower for w in ["项目", "实践"]) and "项目实践" not in goals:
        goals.append("项目实践")
    if any(w in lower for w in ["理解", "概念", "入门"]):
        goals.append("概念理解")
    if goals:
        ef["learning_goal"] = "、".join(goals)
        if "learning_goal" in mf:
            mf.remove("learning_goal")
        updated.add("learning_goal")

    # --- foundation_level (sniffed from text) ---
    if "基础" in lower:
        if any(w in lower for w in ["薄弱", "差", "不好", "零基础", "基础差"]):
            ef["foundation_level"] = "基础薄弱"
        elif any(w in lower for w in ["一般", "还行", "中等"]):
            ef["foundation_level"] = "一般"
        elif any(w in lower for w in ["较好", "熟悉", "扎实", "好"]):
            ef["foundation_level"] = "较好"
        updated.add("foundation_level")

    # ===== multi-value: always merge with existing =====

    # --- current_difficulties ---
    new_diffs = _extract_difficulty_tags(lower)
    if new_diffs:
        existing = _split_tags(ef.get("current_difficulties", ""))
        merged = existing | new_diffs
        ef["current_difficulties"] = "、".join(sorted(merged))
        if "current_difficulties" in mf:
            mf.remove("current_difficulties")
        updated.add("current_difficulties")

    # --- learning_difficulties ---
    new_diffs2 = _extract_difficulty_tags(lower)
    if new_diffs2:
        existing = _split_tags(ef.get("learning_difficulties", ""))
        merged = existing | new_diffs2
        ef["learning_difficulties"] = "、".join(sorted(merged))
        if "learning_difficulties" in mf:
            mf.remove("learning_difficulties")
        updated.add("learning_difficulties")

    # --- expression_preferences ---
    new_prefs = _extract_preference_tags(lower)
    if new_prefs:
        existing = _split_tags(ef.get("expression_preferences", ""))
        merged = existing | new_prefs
        ef["expression_preferences"] = "、".join(sorted(merged))
        if "expression_preferences" in mf:
            mf.remove("expression_preferences")
        updated.add("expression_preferences")

    # --- error_prone_points ---
    new_errors = _extract_error_tags(lower)
    if new_errors:
        existing = _split_tags(ef.get("error_prone_points", ""))
        merged = existing | new_errors
        ef["error_prone_points"] = "、".join(sorted(merged))
        if "error_prone_points" in mf:
            mf.remove("error_prone_points")
        updated.add("error_prone_points")

    # --- learned_courses ---
    new_courses = _extract_course_tags(lower)
    if new_courses:
        existing = _split_tags(ef.get("learned_courses", ""))
        merged = existing | new_courses
        ef["learned_courses"] = "、".join(sorted(merged))
        if "learned_courses" in mf:
            mf.remove("learned_courses")
        updated.add("learned_courses")

    return updated


# ---- Tag extraction helpers (avoid false positives) ----

def _extract_difficulty_tags(lower: str) -> set[str]:
    """Extract DS difficulty tags. Avoid matching 图解 or 调用栈 context."""
    tags: set[str] = set()
    # Only match 图 if NOT preceded by 解 (to avoid 图解 false positive)
    if any(w in lower for w in ["递归"]): tags.add("递归调用栈")
    if any(w in lower for w in ["二叉树", "前序", "中序", "后序"]): tags.add("树遍历")
    if "树" in lower and "二叉树" not in lower: tags.add("树遍历")
    if any(w in lower for w in ["遍历"]) and "二叉树" not in lower: tags.add("树遍历")
    if any(w in lower for w in ["bfs", "dfs", "最短路", "连通"]): tags.add("图遍历")
    # 图 only if NOT part of 图解 (check for standalone 图)
    if "图" in lower and "图解" not in lower: tags.add("图遍历")
    if any(w in lower for w in ["排序", "快排", "快速排序"]): tags.add("排序算法")
    if any(w in lower for w in ["动态规划", "dp", "背包"]): tags.add("动态规划")
    if any(w in lower for w in ["哈希", "散列", "冲突"]): tags.add("散列表")
    if any(w in lower for w in ["二分"]): tags.add("二分查找")
    return tags


def _extract_preference_tags(lower: str) -> set[str]:
    """Extract expression preference tags."""
    tags: set[str] = set()
    if any(w in lower for w in ["图解", "图示", "可视化"]):
        tags.add("图解讲解")
    if any(w in lower for w in ["代码示例", "示例代码", "模板"]):
        tags.add("代码示例")
    if "代码" in lower and "代码示例" not in lower and "示例代码" not in lower:
        tags.add("代码示例")
    if any(w in lower for w in ["易错", "错题", "坑点"]):
        tags.add("易错点归纳")
    if any(w in lower for w in ["练习", "分层"]):
        tags.add("分层练习题")
    if any(w in lower for w in ["项目案例"]):
        tags.add("项目案例")
    return tags


def _extract_error_tags(lower: str) -> set[str]:
    """Extract error-prone point tags. Require explicit error signals, not just topic mentions."""
    tags: set[str] = set()
    has_error = any(w in lower for w in ["搞混", "搞反", "搞错", "出错", "写错", "漏写", "忘记", "不对", "总是错", "经常错"])
    if any(w in lower for w in ["递归"]) and (has_error or "终止条件" in lower):
        tags.add("递归终止条件")
    if any(w in lower for w in ["遍历", "搞反", "搞混"]) and has_error:
        tags.add("遍历顺序混淆")
    if any(w in lower for w in ["复杂度", "大O"]) and has_error:
        tags.add("复杂度判断")
    if any(w in lower for w in ["visited", "标记"]) and has_error:
        tags.add("visited 标记时机")
    if any(w in lower for w in ["状态转移", "转移方程"]) and has_error:
        tags.add("状态转移方程")
    if any(w in lower for w in ["边界", "越界", "溢出"]) and has_error:
        tags.add("数组边界")
    return tags


def _extract_course_tags(lower: str) -> set[str]:
    """Extract prior course tags. Require past-tense or explicit course name context."""
    tags: set[str] = set()
    if "程序设计" in lower or "c语言" in lower or "c程序设计" in lower:
        tags.add("程序设计基础")
    if "离散数学" in lower or "离散" in lower:
        tags.add("离散数学")
    # Only tag 数据结构 as a PRIOR course when explicitly in past-tense context
    if "数据结构" in lower and any(w in lower for w in ["学过", "修过", "上过", "完成", "之前"]):
        tags.add("数据结构")
    if "计算机导论" in lower:
        tags.add("计算机导论")
    if "编程语言基础" in lower:
        tags.add("编程语言基础")
    return tags


def _generate_next_question(mf: list[str], ef: dict) -> str:
    """Generate the next question based on the first remaining missing field."""
    if not mf:
        return "好的，我已经了解了你的数据结构学习情况。接下来做几道轻量诊断题，帮我更准确地评估你的知识基础和实践能力，好吗？"

    next_field = mf[0]
    question = DS_FIELD_QUESTIONS.get(next_field, "能再跟我多说说你的数据结构学习情况吗？")

    # Contextual preamble based on already-collected fields
    preambles = {
        "learned_courses": lambda: f"好的，{ef.get('programming_language', '')} 是个不错的选择。" if ef.get("programming_language") else "了解了。",
        "expression_preferences": lambda: "了解了你的基础背景。" if ef.get("learned_courses") else "好的。",
        "learning_goal": lambda: "很好，我会优先匹配你偏好的资源形式。" if ef.get("expression_preferences") else "明白了。",
        "error_prone_points": lambda: "目标很清晰！" if ef.get("learning_goal") else "好的。",
    }

    preamble_fn = preambles.get(next_field)
    if preamble_fn:
        preamble = preamble_fn()
        return f"{preamble} {question}"

    if next_field == "programming_language" and ef.get("current_difficulties"):
        return f"了解了你的困难点。换个话题——{question}"

    if next_field == "current_difficulties" and ef.get("learning_difficulties"):
        return f"好的。{question}"

    return question


def _dynamic_mock_chat(message: str, history=None, extracted_fields=None, missing_fields=None, stage: str = "collect_profile") -> dict:
    """State-machine driven mock: collect → prereq → errors → summary."""
    # Rebuild profile from extracted_fields
    profile = {}
    if extracted_fields:
        profile = {k: v for k, v in extracted_fields.items() if isinstance(v, str) and v.strip()}

    # Merge new info from current message
    _merge_profile_from_message(message, profile)

    # Determine next stage
    next_stage = _determine_next_stage(profile, stage)

    # Generate reply
    reply = _generate_reply(next_stage, profile, message)

    # Compute missing
    missing = _compute_missing(profile)
    is_complete = next_stage == "summary"

    return {
        "message": reply,
        "reply": reply,
        "profile": profile,
        "extracted_fields": profile,
        "missing_fields": missing,
        "stage": next_stage,
        "is_complete": is_complete,
    }


def _merge_profile_from_message(message: str, profile: dict) -> None:
    """Extract DS fields from user message and merge into profile dict (mutates in-place)."""
    lower = message.lower()

    # --- programming_language (single-value) ---
    if any(w in lower for w in ["c++", "cpp", "cplusplus", "c plus plus"]):
        profile["programming_language"] = "C++"
    elif "python" in lower:
        profile["programming_language"] = "Python"
    elif "java" in lower and "javascript" not in lower:
        profile["programming_language"] = "Java"
    elif "c语言" in lower or (" c " in lower and "c++" not in lower and "cplusplus" not in lower):
        profile["programming_language"] = "C"

    # --- learning_goal ---
    goals = []
    if any(w in lower for w in ["刷题", "题目", "leetcode", "力扣", "牛客"]):
        goals.append("刷题训练")
    if any(w in lower for w in ["考试", "复习", "期末"]):
        goals.append("考试复习")
    if any(w in lower for w in ["课程作业", "作业"]):
        goals.append("课程作业")
    if any(w in lower for w in ["项目实践"]):
        goals.append("项目实践")
    if any(w in lower for w in ["项目", "实践"]) and "项目实践" not in goals:
        goals.append("项目实践")
    if any(w in lower for w in ["理解", "概念", "入门"]):
        goals.append("概念理解")
    if goals:
        profile["learning_goal"] = "、".join(goals)

    # --- foundation_level ---
    if "基础" in lower:
        if any(w in lower for w in ["薄弱", "差", "不好", "零基础", "基础差", "一般偏弱"]):
            profile["foundation_level"] = "基础薄弱"
        elif any(w in lower for w in ["一般", "还行", "中等"]):
            profile["foundation_level"] = "一般"
        elif any(w in lower for w in ["较好", "熟悉", "扎实", "比较会"]):
            profile["foundation_level"] = "较好"

    # --- multi-value: union-merge ---
    _merge_tags(profile, "current_difficulties", _extract_difficulty_tags(lower))
    _merge_tags(profile, "learning_difficulties", _extract_difficulty_tags(lower))
    _merge_tags(profile, "expression_preferences", _extract_preference_tags(lower))
    _merge_tags(profile, "error_prone_points", _extract_error_tags(lower))
    _merge_tags(profile, "learned_courses", _extract_course_tags(lower))


def _merge_tags(profile: dict, key: str, new_tags: set[str]) -> None:
    if not new_tags:
        return
    existing = _split_tags(profile.get(key, ""))
    merged = existing | new_tags
    profile[key] = "、".join(sorted(merged))


def _determine_next_stage(profile: dict, current_stage: str) -> str:
    has_prereq = any(profile.get(f, "").strip() for f in ["foundation_level", "learned_courses"])
    has_errors = bool(profile.get("error_prone_points", "").strip())
    key_count = sum(1 for f in KEY_FIELDS if profile.get(f, "").strip())
    key_fields_filled = key_count >= 4

    if current_stage == "collect_profile":
        if key_fields_filled and not has_prereq:
            return "ask_prerequisite"
        if key_fields_filled and has_prereq and not has_errors:
            return "ask_error_points"
        if key_fields_filled and has_prereq and has_errors:
            return "summary"
        return "collect_profile"

    if current_stage == "ask_prerequisite":
        now_has_prereq = any(profile.get(f, "").strip() for f in ["foundation_level", "learned_courses"])
        if now_has_prereq and has_errors:
            return "summary"
        if now_has_prereq and not has_errors:
            return "ask_error_points"
        return "ask_prerequisite"

    if current_stage == "ask_error_points":
        return "summary" if (has_errors or key_fields_filled) else "ask_error_points"

    return "summary"


def _generate_reply(stage: str, profile: dict, user_message: str) -> str:
    if stage == "collect_profile":
        diffs = profile.get("current_difficulties", "")
        lang = profile.get("programming_language", "")
        goal = profile.get("learning_goal", "")
        prefs = profile.get("expression_preferences", "")
        if diffs and lang and goal and prefs:
            return f"好的，我记下了：你主要用 {lang}，目标是{goal}，困难点在{diffs}，偏好{prefs}。接下来能跟我说说你之前的先修基础吗？比如学过程序设计基础、离散数学吗？基础水平如何？"
        if diffs and not lang:
            return f"了解了{diffs}这些困难点。你平时写算法题主要用哪种语言？C++、Python、Java 还是 C？"
        if lang and not goal:
            return "你目前学习数据结构与算法的目标是什么？刷题训练、考试复习、课程作业，还是项目实践？"
        if lang and not prefs:
            return "你更喜欢哪种学习资源？图解讲解、代码示例、易错点归纳，还是分层练习？"
        return "能再跟我说说你的学习情况吗？你常用什么语言？有什么学习目标？喜欢什么资源形式？"

    if stage == "ask_prerequisite":
        return "你之前学过哪些先修课程？程序设计基础、离散数学、计算机导论？另外你觉得自己的基础水平如何——基础薄弱、一般，还是比较扎实？"

    if stage == "ask_error_points":
        return "你在写算法题时容易在哪些地方出错？比如递归终止条件漏写、遍历顺序搞混、复杂度分析算错，还是状态转移方程推不出来？"

    if stage == "summary":
        lines = []
        if profile.get("programming_language"):
            lines.append(f"编程语言：{profile['programming_language']}")
        if profile.get("learning_goal"):
            lines.append(f"学习目标：{profile['learning_goal']}")
        if profile.get("foundation_level"):
            lines.append(f"基础水平：{profile['foundation_level']}")
        if profile.get("current_difficulties"):
            lines.append(f"薄弱模块：{profile['current_difficulties']}")
        if profile.get("expression_preferences"):
            lines.append(f"偏好资源：{profile['expression_preferences']}")
        if profile.get("error_prone_points"):
            lines.append(f"易错点：{profile['error_prone_points']}")
        if lines:
            return "你的学习画像已经比较完整了！以下是摘要：\n" + "\n".join(lines) + "\n\n你可以继续补充更多信息，我会实时更新画像。也可以切换到资源生成页面查看个性化资源。"
        return "你的学习画像已经比较完整了！你可以继续补充更多信息，我会实时更新画像。"

    return "还有其他想告诉我的吗？"


def _compute_missing(profile: dict) -> list[str]:
    return [f for f in KEY_FIELDS if not profile.get(f, "").strip()]


# ---- Profile Chat (Phase 5B: LLM-integrated) ----

def chat(message: str, history: list[dict] | None = None, extracted_fields: dict | None = None, missing_fields: list[str] | None = None, stage: str = "collect_profile"):
    """
    Profile chat — state-machine-driven interview.

    Mock mode: state-machine-driven extraction + stage progression.
    Real LLM: renders chat_profile.txt prompt, calls LLM, validates JSON.
    Falls back to dynamic mock on any failure.
    """
    from services.llm_service import get_llm, MockProvider

    llm = get_llm()

    if isinstance(llm, MockProvider):
        return _dynamic_mock_chat(message, history, extracted_fields, missing_fields, stage)

    try:
        result = _chat_via_llm(llm, message, history, extracted_fields, missing_fields, stage)
        if result is not None:
            return result
    except Exception as e:
        logger.warning("LLM chat call failed: %s — falling back to dynamic mock", e)

    return _dynamic_mock_chat(message, history, extracted_fields, missing_fields, stage)


def _chat_via_llm(llm, message: str, history: list[dict] | None, extracted_fields: dict | None = None, missing_fields: list[str] | None = None, stage: str = "collect_profile") -> dict | None:
    from services.prompt_service import render_template

    ef = extracted_fields or {}
    mf = missing_fields or [
        "learning_difficulties",
        "current_difficulties",
        "programming_language",
        "learned_courses",
        "expression_preferences",
        "learning_goal",
        "error_prone_points",
    ]

    rendered = render_template(
        "chat_profile",
        student_name=ef.get("display_name", ""),
        student_background="",
        extracted_fields=ef,
        missing_fields=mf,
        stage=stage,
    )

    if not rendered:
        logger.warning("chat_profile template render returned empty — falling back to mock")
        return None

    # Build message list with role normalization
    messages: list[dict] = [{"role": "system", "content": rendered}]
    if history:
        for h in history:
            role = _normalize_role(h.get("role", ""))
            content = h.get("content", "")
            if role and content:
                messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": message})

    result = llm.chat_json(messages, temperature=0.7)

    if not isinstance(result, dict):
        logger.warning(
            "LLM chat_json returned non-dict (type=%s) — falling back to mock",
            type(result).__name__,
        )
        return None

    # Strict type validation
    msg = result.get("message")
    if not isinstance(msg, str) or not msg.strip():
        logger.warning("LLM response missing or empty 'message' field — falling back to mock")
        return None

    extracted = result.get("extracted_fields", {})
    if not isinstance(extracted, dict):
        logger.warning("LLM response 'extracted_fields' is not a dict — falling back to mock")
        return None

    missing = result.get("missing_fields", [])
    if not isinstance(missing, list):
        logger.warning("LLM response 'missing_fields' is not a list — falling back to mock")
        return None

    stage = result.get("stage", "ready_for_diagnosis" if not missing else "collecting")
    if not isinstance(stage, str):
        stage = "ready_for_diagnosis" if not missing else "collecting"

    return {
        "message": msg.strip(),
        "extracted_fields": extracted,
        "missing_fields": missing,
        "stage": stage,
        "is_complete": not missing,
    }


def generate_profile(profile_data: dict | None = None):
    """Mock profile generation — returns the default student profile."""
    with open(DATA_DIR / "default_profile.json", encoding="utf-8") as f:
        return json.load(f)


# ---- Phase 4B: DB CRUD ----

def get_profile(user_id: int) -> Optional[dict]:
    """获取用户画像，无记录时返回 None"""
    db = None
    try:
        db = SessionLocal()
        profile = db.query(StudentProfile).filter(
            StudentProfile.user_id == user_id
        ).first()
        if profile is None:
            return None
        return {
            "id": profile.id,
            "user_id": profile.user_id,
            "knowledge_base_score": profile.knowledge_base_score,
            "practice_ability_score": profile.practice_ability_score,
            "cognitive_styles": profile.cognitive_styles,
            "error_patterns": profile.error_patterns,
            "learning_goals": profile.learning_goals,
            "resource_preferences": profile.resource_preferences,
            "profile_summary": profile.profile_summary,
            "diagnosis_status": profile.diagnosis_status,
            "created_at": profile.created_at.isoformat() if profile.created_at else None,
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
            "source": "database",
        }
    except Exception as e:
        logger.warning("Failed to get profile for user %d: %s", user_id, e)
        return None
    finally:
        if db:
            db.close()


def upsert_profile(user_id: int, data: dict) -> dict:
    """创建或更新用户画像（upsert）"""
    db = None
    try:
        db = SessionLocal()
        profile = db.query(StudentProfile).filter(
            StudentProfile.user_id == user_id
        ).first()

        if profile is None:
            profile = StudentProfile(user_id=user_id)
            db.add(profile)

        # 仅更新显式传入的字段
        updatable = [
            "knowledge_base_score", "practice_ability_score",
            "cognitive_styles", "error_patterns", "learning_goals",
            "resource_preferences", "profile_summary", "diagnosis_status",
        ]
        for field in updatable:
            if field in data:
                setattr(profile, field, data[field])

        db.commit()
        db.refresh(profile)

        return {
            "id": profile.id,
            "user_id": profile.user_id,
            "knowledge_base_score": profile.knowledge_base_score,
            "practice_ability_score": profile.practice_ability_score,
            "cognitive_styles": profile.cognitive_styles,
            "error_patterns": profile.error_patterns,
            "learning_goals": profile.learning_goals,
            "resource_preferences": profile.resource_preferences,
            "profile_summary": profile.profile_summary,
            "diagnosis_status": profile.diagnosis_status,
            "created_at": profile.created_at.isoformat() if profile.created_at else None,
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
            "source": "database",
        }
    except Exception as e:
        logger.warning("Failed to upsert profile for user %d: %s — falling back to mock", user_id, e)
        if db:
            db.rollback()
        # Fallback: return the input data as-is
        return {**data, "user_id": user_id, "source": "mock_fallback"}
    finally:
        if db:
            db.close()


def get_conversations(user_id: int) -> list[dict]:
    """获取用户画像对话历史"""
    db = None
    try:
        db = SessionLocal()
        conversations = db.query(ProfileConversation).filter(
            ProfileConversation.user_id == user_id
        ).order_by(ProfileConversation.created_at.asc()).all()
        return [
            {
                "id": c.id,
                "user_id": c.user_id,
                "role": c.role,
                "message": c.message,
                "extracted_fields": c.extracted_fields,
                "missing_fields": c.missing_fields,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in conversations
        ]
    except Exception as e:
        logger.warning("Failed to get conversations for user %d: %s", user_id, e)
        return []
    finally:
        if db:
            db.close()


def add_conversation(user_id: int, role: str, message: str,
                     extracted_fields: Optional[str] = None,
                     missing_fields: Optional[str] = None) -> Optional[dict]:
    """追加一条对话消息"""
    db = None
    try:
        db = SessionLocal()
        conv = ProfileConversation(
            user_id=user_id,
            role=role,
            message=message,
            extracted_fields=extracted_fields,
            missing_fields=missing_fields,
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)
        return {
            "id": conv.id,
            "user_id": conv.user_id,
            "role": conv.role,
            "message": conv.message,
            "extracted_fields": conv.extracted_fields,
            "missing_fields": conv.missing_fields,
            "created_at": conv.created_at.isoformat() if conv.created_at else None,
        }
    except Exception as e:
        logger.warning("Failed to add conversation for user %d: %s", user_id, e)
        if db:
            db.rollback()
        return None
    finally:
        if db:
            db.close()
