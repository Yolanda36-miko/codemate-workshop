"""
AssessmentAgent — 智能辅导与闯关评估智能体

Accepts a student question, current topic, and profile signals; returns
a concise tutoring reply and (optionally) quiz/challenge questions.

当前实现基于关键词匹配的规则回复 + mock 评估，LLM 集成点为未来扩展预留。
"""

from typing import Any

from .base_agent import BaseAgent, AgentResult


# ---------------------------------------------------------------------------
# Lightweight keyword → response dispatch (mirrors tutor.py logic)
# ---------------------------------------------------------------------------
TOPIC_KEYWORDS: dict[str, list[str]] = {
    "递归":       ["递归", "调用栈", "汉诺塔", "尾递归", "终止条件"],
    "二叉树":     ["二叉树", "前序", "中序", "后序", "层序", "BST", "二叉搜索树", "遍历"],
    "链表":       ["链表", "单链表", "双向链表", "循环链表", "顺序表", "线性表"],
    "排序":       ["排序", "快排", "快速排序", "归并排序", "堆排序", "冒泡", "二分查找"],
    "动态规划":   ["动态规划", "DP", "背包", "状态转移", "记忆化搜索"],
    "图":         ["图", "BFS", "DFS", "Dijkstra", "拓扑排序", "最短路径", "邻接表"],
    "栈与队列":   ["栈", "队列", "单调栈", "循环队列", "括号匹配", "表达式求值"],
    "散列表":     ["哈希", "散列", "散列表", "冲突", "链地址", "开放地址"],
    "复杂度":     ["复杂度", "大O", "时间复杂度", "空间复杂度", "渐进分析"],
}


class AssessmentAgent(BaseAgent):
    name = "Assessment Agent"
    role = "辅导与闯关评估"
    responsibilities = [
        "围绕数据结构主题提供智能辅导问答（核心解释 + 关键点 + 下一步建议）",
        "生成主题相关的闯关练习题并评估答题结果",
        "基于画像信号调整辅导深度和推荐方向",
    ]

    def process(self, **kwargs: Any) -> AgentResult:
        mode = kwargs.get("mode", "tutor")  # "tutor" | "quiz"
        question = kwargs.get("question", "")
        topic = kwargs.get("topic", "")
        profile_signals = kwargs.get("profile_signals") or {}

        if mode == "quiz":
            return self._handle_quiz(question, topic, profile_signals)
        return self._handle_tutor(question, topic, profile_signals)

    # ------------------------------------------------------------------
    # Tutor mode
    # ------------------------------------------------------------------

    def _handle_tutor(self, question: str, topic: str, _signals: dict[str, Any]) -> AgentResult:
        matched_topic = self._match_topic(question, topic)
        response = self._build_tutor_response(matched_topic, question)

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "mode": "tutor",
                "matched_topic": matched_topic,
                "core_explanation": response["core_explanation"],
                "key_points": response["key_points"],
                "next_step": response["next_step"],
                "code_example": response.get("code_example"),
            },
            summary=f"辅导回复，匹配主题: {matched_topic or '(通用)'}",
        )

    def _match_topic(self, question: str, fallback_topic: str) -> str | None:
        q = question.lower()
        for topic_name, keywords in TOPIC_KEYWORDS.items():
            if any(kw.lower() in q for kw in keywords):
                return topic_name
        return fallback_topic or None

    def _build_tutor_response(self, topic: str | None, _question: str) -> dict[str, Any]:
        templates: dict[str, dict[str, Any]] = {
            "递归": {
                "core_explanation": "递归的核心是函数调用自身，每次调用都会在调用栈上创建新的栈帧。理解递归的关键在于明确终止条件（base case）和递推关系（recursive case）。",
                "key_points": ["递归 = 终止条件 + 递推关系", "每次调用产生新栈帧，注意栈溢出", "先写终止条件，再写递推逻辑"],
                "next_step": "建议从「爬楼梯」或「斐波那契」入手，手动画出递归树跟踪调用过程。",
            },
            "二叉树": {
                "core_explanation": "二叉树遍历有前序（根-左-右）、中序（左-根-右）、后序（左-右-根）和层序（BFS）四种方式。前三种可用递归或迭代实现，层序需要队列辅助。",
                "key_points": ["前/中/后序遍历对应不同的根节点访问时机", "BST 的中序遍历结果有序", "层序遍历 = BFS，需用队列"],
                "next_step": "建议手写四种遍历的递归和非递归版本，并练习「验证 BST」「层序遍历输出」等经典题。",
            },
            "链表": {
                "core_explanation": "链表由节点和指针构成，每个节点包含数据域和指向下一节点的指针。链表的插入/删除效率高（O(1)），但随机访问慢（O(n)）。",
                "key_points": ["头节点操作需特殊处理（哨兵节点简化）", "反转链表是经典必会题", "快慢指针可解环检测、中点查找"],
                "next_step": "建议从「反转单链表」开始，然后练习「环形链表检测」「合并有序链表」。",
            },
            "排序": {
                "core_explanation": "经典排序算法的核心对比维度是时间复杂度、空间复杂度和稳定性。快速排序平均 O(n log n) 但最坏 O(n²)，归并排序稳定 O(n log n) 但需要额外空间。",
                "key_points": ["快排：分治 + 基准选择影响性能", "归并：分治 + 合并，稳定但需 O(n) 空间", "二分查找的边界条件是最常见易错点"],
                "next_step": "建议手写快排和归并排序，并在 LeetCode 上练习二分查找的 3 种变体。",
            },
            "动态规划": {
                "core_explanation": "动态规划的核心是将原问题分解为重叠子问题，通过状态定义和状态转移方程自底向上求解。最优子结构和重叠子问题是 DP 的两个必要条件。",
                "key_points": ["明确状态定义（dp[i] 表示什么）", "推导状态转移方程", "确定初始条件和遍历顺序"],
                "next_step": "建议从「爬楼梯」「打家劫舍」入门，再挑战「背包问题」「最长递增子序列」。",
            },
            "图": {
                "core_explanation": "图的遍历是解决图问题的基础。DFS 适合路径搜索和连通性判断，BFS 适合最短路径（无权图）和层序遍历。",
                "key_points": ["DFS = 递归/栈，适合路径搜索", "BFS = 队列，适合最短路径", "Dijkstra 解决带权最短路径"],
                "next_step": "建议从「岛屿数量」开始，练习 DFS/BFS 的图遍历模板，再学习拓扑排序和 Dijkstra。",
            },
        }

        if topic and topic in templates:
            return templates[topic]

        return {
            "core_explanation": "这是一个很好的数据结构问题。理解数据结构的内部机制和适用场景，比死记硬背代码更重要。",
            "key_points": ["先理解数据结构的定义和特性", "掌握基本操作的时间复杂度", "多写代码、多画图加深理解"],
            "next_step": "建议结合具体的代码示例和练习题巩固理解，遇到困难时可以继续提问。",
        }

    # ------------------------------------------------------------------
    # Quiz mode
    # ------------------------------------------------------------------

    def _handle_quiz(self, _question: str, topic: str, _signals: dict[str, Any]) -> AgentResult:
        quiz_questions = self._generate_quiz(topic)
        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "mode": "quiz",
                "topic": topic,
                "questions": quiz_questions,
            },
            summary=f"为「{topic or '通用主题'}」生成 {len(quiz_questions)} 道闯关题",
        )

    def _generate_quiz(self, topic: str | None) -> list[dict[str, Any]]:
        base_questions: list[dict[str, Any]] = [
            {
                "id": "q1",
                "question": f"请简述{'「' + topic + '」' if topic else '该数据结构'}的核心概念和典型应用场景。",
                "options": [],
                "correct": "",
                "knowledge_point": topic or "数据结构基础",
                "explanation": "概念理解是应用的基础。",
            },
            {
                "id": "q2",
                "question": f"写出{'「' + topic + '」' if topic else '该数据结构'}基本操作的时间复杂度分析。",
                "options": [],
                "correct": "",
                "knowledge_point": topic or "复杂度分析",
                "explanation": "复杂度分析是评估算法效率的关键。",
            },
        ]
        return base_questions
