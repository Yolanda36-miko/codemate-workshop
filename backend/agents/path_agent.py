"""
PathAgent — 学习路径规划智能体

Accepts profile signals (difficulties, goals, foundation level, preferences)
and returns a personalised 10-module data-structures learning path with
focus-module reordering and resource preference alignment.

当前实现基于规则排序 + 本地路径模板，不依赖 LLM。
"""

from typing import Any

from .base_agent import BaseAgent, AgentResult


# ---------------------------------------------------------------------------
# Difficulty keyword → DS module mapping (ordered; more-specific first)
# ---------------------------------------------------------------------------
DIFFICULTY_MODULE_MAP: list[tuple[list[str], str, str]] = [
    (["复杂度", "大O", "时间复杂度", "空间复杂度", "渐进分析"],       "ds-1", "复杂度分析与基础概念"),
    (["链表", "顺序表", "线性表", "单链表", "双向链表", "循环链表"],   "ds-2", "线性表"),
    (["递归", "调用栈", "递归调用栈", "栈帧", "尾递归", "终止条件"],   "ds-4", "递归与调用栈"),
    (["栈", "队列", "LIFO", "FIFO", "单调栈", "循环队列"],            "ds-3", "栈与队列"),
    (["树遍历", "树", "二叉树", "BST", "前序", "中序", "后序", "层序", "堆", "优先队列"],
                                                                       "ds-5", "树与二叉树"),
    (["图遍历", "图", "BFS", "DFS", "Dijkstra", "拓扑排序", "最短路径"], "ds-6", "图结构与图算法"),
    (["排序", "快排", "快速排序", "归并排序", "二分查找", "稳定性"],     "ds-7", "排序与查找"),
    (["哈希", "散列", "散列表", "冲突", "链地址", "开放地址"],          "ds-8", "散列表"),
    (["动态规划", "DP", "背包", "状态转移", "记忆化搜索", "最优子结构"], "ds-9", "动态规划入门"),
]

MOCK_NODES: list[dict[str, Any]] = [
    {"id": "ds-1",  "name": "复杂度分析与基础概念", "duration": "1-3 天", "stage": "基础概念", "keywords": ["时间复杂度", "空间复杂度", "大O表示法"], "defaultResources": [], "reason": "复杂度分析是评估和比较算法效率的基本功"},
    {"id": "ds-2",  "name": "线性表",               "duration": "2-4 天", "stage": "核心理解", "keywords": ["顺序表", "链表"],             "defaultResources": [], "reason": "线性表是最基础的动态数据结构"},
    {"id": "ds-3",  "name": "栈与队列",             "duration": "2-3 天", "stage": "核心理解", "keywords": ["栈", "队列"],                 "defaultResources": [], "reason": "栈与队列是最常用的受限线性结构"},
    {"id": "ds-4",  "name": "递归与调用栈",         "duration": "2-4 天", "stage": "核心理解", "keywords": ["递归", "调用栈"],             "defaultResources": [], "reason": "递归是树、图、DP 的思维基础"},
    {"id": "ds-5",  "name": "树与二叉树",           "duration": "4-6 天", "stage": "代码实现", "keywords": ["二叉树", "遍历", "BST", "堆"], "defaultResources": [], "reason": "树是数据结构的核心章节"},
    {"id": "ds-6",  "name": "图结构与图算法",       "duration": "5-7 天", "stage": "代码实现", "keywords": ["图", "DFS", "BFS", "最短路径"], "defaultResources": [], "reason": "图算法是最具挑战性的章节"},
    {"id": "ds-7",  "name": "排序与查找",           "duration": "4-6 天", "stage": "练习巩固", "keywords": ["排序", "二分查找"],           "defaultResources": [], "reason": "排序与查找是面试最高频的算法"},
    {"id": "ds-8",  "name": "散列表",              "duration": "2-4 天", "stage": "练习巩固", "keywords": ["散列表", "哈希"],             "defaultResources": [], "reason": "散列表是开发中使用频率最高的数据结构"},
    {"id": "ds-9",  "name": "动态规划入门",         "duration": "4-7 天", "stage": "练习巩固", "keywords": ["动态规划", "状态转移"],       "defaultResources": [], "reason": "动态规划是算法学习的制高点"},
    {"id": "ds-10", "name": "综合项目实践",         "duration": "1-2 周", "stage": "项目应用", "keywords": ["综合", "项目"],               "defaultResources": [], "reason": "综合实践是检验学习成果的最佳方式"},
]


class PathAgent(BaseAgent):
    name = "Path Agent"
    role = "学习路径规划"
    responsibilities = [
        "基于画像信号（学习困难、目标、基础水平）生成个性化 DS 学习路径",
        "将画像匹配的重点模块提前至复杂度分析之后，非重点模块保持相对顺序",
        "根据资源偏好和 learning_goal 调整推荐资源优先级",
    ]

    def process(self, **kwargs: Any) -> AgentResult:
        profile_signals = kwargs.get("profile_signals") or {}
        difficulties: list[str] = profile_signals.get("difficulties", [])
        goals: list[str] = profile_signals.get("goals", [])
        preferences: list[str] = profile_signals.get("preferences", [])
        foundation_level: str | None = profile_signals.get("foundation_level")

        # 1. Map difficulties to module ids
        focus_ids = self._resolve_focus_modules(difficulties)

        # 2. Determine preferred resource types
        preferred_types = self._resolve_preferred_types(preferences, goals)

        # 3. Build enriched + reordered nodes
        nodes = self._build_nodes(focus_ids, preferred_types, foundation_level)

        focus_names = [n["name"] for n in nodes if n.get("is_focus")]
        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "path_name": "数据结构与算法个性化学习路径",
                "nodes": nodes,
                "focus_modules": focus_names,
                "profile_used": bool(difficulties or goals or preferences),
            },
            summary=(f"生成 {len(nodes)} 个模块的学习路径，"
                     f"重点模块: {focus_names if focus_names else ['(无)']}"),
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_focus_modules(self, difficulties: list[str]) -> set[str]:
        ids: set[str] = set()
        for diff in difficulties:
            for terms, mid, _name in DIFFICULTY_MODULE_MAP:
                if any(t in diff for t in terms):
                    ids.add(mid)
                    break
        return ids

    def _resolve_preferred_types(self, preferences: list[str], goals: list[str]) -> list[str]:
        types: list[str] = []
        for p in preferences:
            if "图解" in p:    self._add(types, "图解讲义")
            if "代码" in p:    self._add(types, "代码示例与注释")
            if "易错" in p:    self._add(types, "个性化讲解文档")
            if "练习" in p or "分层" in p: self._add(types, "分层练习题")
            if "项目" in p or "案例" in p: self._add(types, "项目式学习案例")
            if "思维导图" in p or "知识梳理" in p: self._add(types, "知识点思维导图")
        for g in goals:
            if "刷题" in g:    self._add(types, "分层练习题"); self._add(types, "代码示例与注释")
            if "考试" in g:    self._add(types, "个性化讲解文档"); self._add(types, "知识点思维导图")
            if "项目" in g:    self._add(types, "项目式学习案例"); self._add(types, "代码示例与注释")
            if "概念" in g or "理解" in g: self._add(types, "图解讲义"); self._add(types, "个性化讲解文档")
        return types

    @staticmethod
    def _add(arr: list[str], val: str) -> None:
        if val not in arr:
            arr.append(val)

    def _build_nodes(
        self,
        focus_ids: set[str],
        preferred_types: list[str],
        foundation_level: str | None,
    ) -> list[dict[str, Any]]:
        enriched: list[dict[str, Any]] = []
        for node in MOCK_NODES:
            n = dict(node)
            is_focus = n["id"] in focus_ids
            n["is_focus"] = is_focus

            # Adjust duration
            dur = n["duration"]
            if foundation_level == "基础薄弱":
                if dur == "1-3 天":  n["duration"] = "2-4 天"
                elif dur == "2-3 天": n["duration"] = "3-5 天"
                elif dur == "2-4 天": n["duration"] = "3-5 天"
            elif foundation_level == "较好":
                if dur == "4-6 天":   n["duration"] = "3-4 天"
                elif dur == "5-7 天": n["duration"] = "4-5 天"
                elif dur == "4-7 天": n["duration"] = "3-5 天"
                elif dur == "1-2 周": n["duration"] = "5-7 天"

            # Add supplementary resources for focus nodes
            if is_focus and preferred_types:
                existing = [r.get("type", "") for r in n.get("defaultResources", [])]
                added = 0
                for pt in preferred_types:
                    if added >= 2:
                        break
                    if pt not in existing:
                        n.setdefault("defaultResources", []).append({
                            "resourceId": f'{n["id"]}-sup-{added}',
                            "title": f'{n["name"]}{self._short_label(pt)}',
                            "type": pt,
                            "estimatedTime": "20 分钟",
                            "source": "default",
                        })
                        added += 1

            enriched.append(n)

        # Reorder: ds-1 first → focus modules → rest
        result: list[dict[str, Any]] = []
        ds1 = next((n for n in enriched if n["id"] == "ds-1"), None)
        if ds1:
            result.append(ds1)
        for n in enriched:
            if n["id"] != "ds-1" and n["id"] in focus_ids:
                result.append(n)
        for n in enriched:
            if n["id"] != "ds-1" and n["id"] not in focus_ids:
                result.append(n)
        return result

    @staticmethod
    def _short_label(res_type: str) -> str:
        mapping = {
            "图解讲义": "图解讲义",
            "代码示例与注释": "代码示例",
            "个性化讲解文档": "核心讲解",
            "分层练习题": "分层练习",
            "项目式学习案例": "项目案例",
            "知识点思维导图": "思维导图",
        }
        return mapping.get(res_type, res_type)
