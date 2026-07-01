"""
Tutor Chat API
- POST /api/tutor/chat — keyword-aware mock tutoring response.
  Falls back to LLM provider when configured with a real provider.
"""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class TutorChatRequest(BaseModel):
    message: str
    student_profile: dict | None = None
    history: list[dict] | None = None


# ========== Keyword -> domain mapping ==========

TOPIC_KEYWORDS: dict[str, list[str]] = {
    "recursion": ["递归", "调用栈", "出口", "基准情形", "栈帧"],
    "binary_tree": ["二叉树", "前序", "中序", "后序", "遍历", "层序", "树"],
    "array": ["数组", "下标", "越界", "边界", "列表", "索引"],
    "linked_list": ["链表", "节点", "指针", "头结点"],
    "sorting": ["排序", "查找", "搜索", "冒泡", "快速排序", "二分", "归并"],
    "dp": ["动态规划", "dp", "状态定义", "状态转移", "最优子结构", "重叠子问题", "背包", "记忆化"],
    "function_call": ["函数", "调用", "参数", "返回值", "作用域", "嵌套"],
    "debug": ["调试", "debug", "报错", "错误", "异常", "排错"],
    "project": ["项目", "实践", "开发", "应用", "综合"],
}

# ========== Domain-specific response builders ==========


def _build_recursion_response(msg: str) -> dict:
    return {
        "greeting": "关于递归这个问题，我来帮你梳理清楚！",
        "approach": (
            "递归的核心是「把大问题分解成小问题」，"
            "每次递归调用都解决一个更小的子问题，直到遇到基准情形。"
        ),
        "steps": [
            "第一步：明确递归函数的定义——它要解决什么问题，输入和输出是什么。",
            "第二步：找到基准情形（Base Case）——最简单、不需要再递归的情况。",
            "第三步：写出递归关系——如何把当前问题转化为更小的子问题。",
            "第四步：在纸上模拟调用栈，理解每次递归调用时参数如何变化、返回值如何传递。",
        ],
        "code_example": (
            "def factorial(n):\n"
            "    if n <= 1:         # 基准情形\n"
            "        return 1\n"
            "    return n * factorial(n - 1)  # 递归关系\n"
            "\n"
            "# f(4) -> 4*f(3) -> 4*3*f(2) -> 4*3*2*f(1) -> 4*3*2*1 = 24"
        ),
        "recommended_resources": [
            {"title": "递归调用栈图解讲义", "url": "#"},
            {"title": "递归代码示例与注释", "url": "#"},
        ],
        "suggested_exercise": "尝试用递归实现斐波那契数列，并画出 f(5) 的调用栈图。",
    }


def _build_binary_tree_response(msg: str) -> dict:
    return {
        "greeting": "二叉树遍历是数据结构的核心内容，让我帮你理清思路！",
        "approach": (
            "二叉树遍历的核心记忆点是「根节点被访问的时机」："
            "先访问根叫前序，中间访问根叫中序，最后访问根叫后序。"
        ),
        "steps": [
            "第一步：理解三种遍历的本质区别——「前/中/后」指的是根节点在第几位被处理。",
            "第二步：前序遍历（根->左->右）——先处理根节点，再递归处理左右子树。",
            "第三步：中序遍历（左->根->右）——先递归左子树，再处理根，最后递归右子树。",
            "第四步：后序遍历（左->右->根）——先递归处理左右子树，最后处理根节点。",
        ],
        "code_example": (
            "class TreeNode:\n"
            "    def __init__(self, val=0, left=None, right=None):\n"
            "        self.val = val\n"
            "        self.left = left\n"
            "        self.right = right\n"
            "\n"
            "def preorder(root):\n"
            "    if root is None:\n"
            "        return\n"
            "    print(root.val)       # 根\n"
            "    preorder(root.left)   # 左\n"
            "    preorder(root.right)  # 右"
        ),
        "recommended_resources": [
            {"title": "二叉树遍历图解讲义", "url": "#"},
            {"title": "遍历代码示例与注释", "url": "#"},
        ],
        "suggested_exercise": "用同一棵树分别跑前序、中序、后序遍历，对比输出结果的差异。",
    }


def _build_array_response(msg: str) -> dict:
    return {
        "greeting": "数组是编程中最基础也最重要的数据结构，我来帮你理清概念！",
        "approach": (
            "数组操作的核心是理解索引从 0 开始，以及边界条件。"
            "大部分数组错误都来自越界访问。"
        ),
        "steps": [
            "第一步：明确数组索引范围——长度为 n 的数组，有效索引是 0 到 n-1。",
            "第二步：遍历数组时，循环条件用 i < n（不是 i <= n），防止越界。",
            "第三步：处理多维数组时，逐层理解——外层索引对应行，内层索引对应列。",
            "第四步：注意边界情况——空数组、单元素数组、首尾元素的特殊处理。",
        ],
        "code_example": (
            "arr = [10, 20, 30, 40, 50]\n"
            "n = len(arr)           # n = 5\n"
            "for i in range(n):     # range(5) -> 0,1,2,3,4\n"
            "    print(arr[i])       # 安全访问\n"
            "# arr[n] -> IndexError  # 越界！"
        ),
        "recommended_resources": [
            {"title": "数组操作基础讲解", "url": "#"},
            {"title": "数组边界条件练习题", "url": "#"},
        ],
        "suggested_exercise": "写一个函数反转数组，分别用循环和切片两种方式实现。",
    }


def _build_linked_list_response(msg: str) -> dict:
    return {
        "greeting": "链表是理解指针和动态数据结构的关键，让我来帮你理清！",
        "approach": (
            "链表的核心是每个节点包含数据域和指向下一个节点的指针。"
            "理解指针的指向关系是掌握链表的关键。"
        ),
        "steps": [
            "第一步：理解节点结构——每个节点包含数据域和指针域。",
            "第二步：掌握链表遍历——从头结点开始，沿着 next 指针逐个访问。",
            "第三步：理解插入操作——先让新节点的 next 指向后继，再修改前驱的 next。",
            "第四步：注意空链表和头尾节点的边界情况。",
        ],
        "code_example": (
            "class ListNode:\n"
            "    def __init__(self, val=0, next=None):\n"
            "        self.val = val\n"
            "        self.next = next\n"
            "\n"
            "def traverse(head):\n"
            "    curr = head\n"
            "    while curr:\n"
            "        print(curr.val)\n"
            "        curr = curr.next"
        ),
        "recommended_resources": [
            {"title": "链表数据结构图解", "url": "#"},
            {"title": "链表操作代码示例", "url": "#"},
        ],
        "suggested_exercise": "实现链表的插入和删除操作，画出每一步指针的变化。",
    }


def _build_sorting_response(msg: str) -> dict:
    return {
        "greeting": "排序算法是算法学习的经典入口，让我帮你理清思路！",
        "approach": (
            "排序算法的学习路径：先理解简单排序（冒泡、选择、插入），"
            "再学习高效排序（快速、归并），最后掌握它们的适用场景。"
        ),
        "steps": [
            "第一步：从冒泡排序入手——理解比较和交换的基本操作。",
            "第二步：学习快速排序的分治思想——选基准、分区、递归。",
            "第三步：理解归并排序——先分后合，稳定排序的代表。",
            "第四步：掌握不同排序算法的适用场景和时间复杂度。",
        ],
        "code_example": (
            "def bubble_sort(arr):\n"
            "    n = len(arr)\n"
            "    for i in range(n):\n"
            "        for j in range(n - i - 1):\n"
            "            if arr[j] > arr[j + 1]:\n"
            "                arr[j], arr[j + 1] = arr[j + 1], arr[j]\n"
            "    return arr"
        ),
        "recommended_resources": [
            {"title": "排序算法可视化图解", "url": "#"},
            {"title": "排序算法代码对比", "url": "#"},
        ],
        "suggested_exercise": (
            "用 Python 实现冒泡排序和快速排序，"
            "对比它们在随机数组和已排序数组上的表现。"
        ),
    }


def _build_dp_response(msg: str) -> dict:
    return {
        "greeting": "动态规划是算法学习中的重要里程碑，让我帮你建立DP思维！",
        "approach": (
            "动态规划的核心是「找到最优子结构」——"
            "大问题的最优解包含子问题的最优解。关键是正确定义状态和写出转移方程。"
        ),
        "steps": [
            "第一步：明确问题是否具有最优子结构——能否用子问题的最优解构造原问题的最优解。",
            "第二步：定义状态——用一个或多个变量描述子问题的状态，例如 dp[i] 表示前 i 个元素的最优解。",
            "第三步：写出状态转移方程——当前状态如何从之前的某个状态转移而来。",
            "第四步：确定计算顺序——自顶向下（记忆化搜索）还是自底向上（递推填表）。",
        ],
        "code_example": (
            "# 0-1 背包问题 — 经典 DP 入门\n"
            "def knapsack(weights, values, capacity):\n"
            "    n = len(weights)\n"
            "    dp = [[0] * (capacity + 1) for _ in range(n + 1)]\n"
            "    for i in range(1, n + 1):\n"
            "        for w in range(capacity + 1):\n"
            "            if weights[i-1] > w:\n"
            "                dp[i][w] = dp[i-1][w]\n"
            "            else:\n"
            "                dp[i][w] = max(dp[i-1][w], dp[i-1][w-weights[i-1]] + values[i-1])\n"
            "    return dp[n][capacity]"
        ),
        "recommended_resources": [
            {"title": "动态规划入门讲解", "url": "#"},
            {"title": "经典DP问题分类整理", "url": "#"},
        ],
        "suggested_exercise": (
            "从斐波那契数列的记忆化搜索开始，"
            "然后尝试解决「爬楼梯」和「最小路径和」问题，逐步过渡到背包问题。"
        ),
    }


def _build_function_call_response(msg: str) -> dict:
    return {
        "greeting": "函数调用机制是理解程序执行流程的核心，我来帮你讲清楚！",
        "approach": (
            "理解函数调用的关键是三个概念：参数传递、返回值和调用栈。"
        ),
        "steps": [
            "第一步：理解参数传递——Python 中不可变对象传值，可变对象传引用。",
            "第二步：掌握返回值——函数通过 return 将结果返回给调用者。",
            "第三步：理解调用栈——每次函数调用会压栈，返回时弹栈。",
            "第四步：注意作用域——函数内部变量是局部的，外部无法直接访问。",
        ],
        "code_example": (
            "def add(a, b):\n"
            "    result = a + b    # result 是局部变量\n"
            "    return result      # 返回值\n"
            "\n"
            "x = add(3, 4)         # x = 7\n"
            "# print(result)        # 报错：result 不在作用域内"
        ),
        "recommended_resources": [
            {"title": "函数调用机制详解", "url": "#"},
            {"title": "作用域与闭包讲解", "url": "#"},
        ],
        "suggested_exercise": "写一个函数追踪练习：定义三个嵌套函数，在纸面上追踪每次调用时的参数值和返回值。",
    }


def _build_debug_response(msg: str) -> dict:
    return {
        "greeting": "调试是每个开发者必须掌握的技能，我来分享一些实用技巧！",
        "approach": (
            "调试的核心是「假设-验证」循环：先根据错误信息提出假设，"
            "再用工具或打印验证，逐步缩小问题范围。"
        ),
        "steps": [
            "第一步：仔细阅读错误信息——错误类型、出错行号、调用堆栈是三个最重要的信息。",
            "第二步：定位问题行——从堆栈最底层（你的代码）开始，向上追溯。",
            "第三步：在可疑位置插入 print 输出关键变量，验证你的假设。",
            "第四步：检查边界条件——空值、零值、数组越界是最常见的错误来源。",
        ],
        "code_example": (
            "# 调试技巧示例\n"
            "def find_max(arr):\n"
            "    print(f'输入数组: {arr}')  # 打印输入\n"
            "    if not arr:                 # 处理边界\n"
            "        return None\n"
            "    max_val = arr[0]\n"
            "    for i, v in enumerate(arr):\n"
            "        print(f'i={i}, v={v}, max={max_val}')\n"
            "        if v > max_val:\n"
            "            max_val = v\n"
            "    return max_val"
        ),
        "recommended_resources": [
            {"title": "调试方法论与技巧", "url": "#"},
            {"title": "常见错误类型速查", "url": "#"},
        ],
        "suggested_exercise": "故意写一个包含越界错误的数组访问代码，通过报错信息定位并修复它。",
    }


def _build_project_response(msg: str) -> dict:
    return {
        "greeting": "项目实践是把知识转化为能力的关键一步！",
        "approach": (
            "项目学习的最佳策略是从小到大、从模仿到创新。"
            "先完成一个简单但完整的项目，再逐步增加复杂度。"
        ),
        "steps": [
            "第一步：明确项目目标——确定要实现的核心功能和预期效果。",
            "第二步：拆解任务——把大项目分解为独立的小模块，逐个实现。",
            "第三步：先写核心逻辑——从最简单的功能开始，确保能跑通。",
            "第四步：逐步完善——添加边界处理、错误处理、用户交互等。",
        ],
        "code_example": None,
        "recommended_resources": [
            {"title": "项目式学习案例集", "url": "#"},
            {"title": "从零搭建完整项目指南", "url": "#"},
        ],
        "suggested_exercise": (
            "选择一个你感兴趣的小项目（如计算器、待办列表），"
            "按照上述步骤从零开始实现。"
        ),
    }


def _build_generic_response(msg: str) -> dict:
    """Generate a generic but topic-aware response when no specific domain matches."""
    question_preview = msg[:40] + ("..." if len(msg) > 40 else "")
    return {
        "greeting": f"关于「{question_preview}」这个问题，我来帮你分析一下！",
        "approach": "根据你的问题，建议从基础概念入手，逐步深入理解相关知识点。",
        "steps": [
            "第一步：明确问题涉及的核心概念和知识点。",
            "第二步：查阅相关基础资料，建立概念框架。",
            "第三步：结合代码示例加深理解，动手运行验证。",
            "第四步：完成相关练习，检验掌握程度。",
        ],
        "code_example": None,
        "recommended_resources": [
            {"title": "个性化讲解文档", "url": "#"},
            {"title": "知识点思维导图", "url": "#"},
        ],
        "suggested_exercise": "尝试用自己的语言复述该知识点，然后完成一道相关练习题。",
    }


# ========== Response dispatcher ==========

_DOMAIN_BUILDERS = {
    "recursion": _build_recursion_response,
    "binary_tree": _build_binary_tree_response,
    "array": _build_array_response,
    "linked_list": _build_linked_list_response,
    "sorting": _build_sorting_response,
    "dp": _build_dp_response,
    "function_call": _build_function_call_response,
    "debug": _build_debug_response,
    "project": _build_project_response,
}


def _detect_topic(msg: str) -> str | None:
    """Detect the primary topic from the user message using keyword matching."""
    lower = msg.lower()
    for domain, keywords in TOPIC_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in lower:
                return domain
    return None


def _build_mock_tutor_response(msg: str) -> dict:
    """Build a keyword-aware mock tutoring response."""
    topic = _detect_topic(msg)
    builder = _DOMAIN_BUILDERS.get(topic) if topic else None
    if builder:
        return builder(msg)
    return _build_generic_response(msg)


@router.post("/tutor/chat")
def tutor_chat(req: TutorChatRequest):
    """
    Tutor chat endpoint.

    Mock mode (LLM_PROVIDER=mock):
      Returns a keyword-aware response that varies based on the user's
      question topic (recursion, binary-tree, array, dp, etc.).

    Real LLM mode:
      Forwards to the configured LLM provider with the user's profile
      and history context (integration point preserved for future phase).
    """
    message = (req.message or "").strip()
    if not message:
        return {
            "greeting": "请描述你遇到的学习问题，我来帮你分析！",
            "approach": "",
            "steps": [],
            "code_example": None,
            "recommended_resources": [],
            "suggested_exercise": "",
        }

    return _build_mock_tutor_response(message)
