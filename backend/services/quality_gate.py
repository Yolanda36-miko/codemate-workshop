# ═══════════════════════════════════════════════════════════════════
# Phase 14C: Deterministic Teaching Resource Quality Gate
# ═══════════════════════════════════════════════════════════════════
# This module is injected into resource_service.py.
# It provides ensure_teaching_resource_quality() — a hard quality
# gate that runs AFTER all enrichment, guaranteeing minimum content
# standards per resource type via deterministic templates.
# ═══════════════════════════════════════════════════════════════════

import re
import logging

logger = logging.getLogger(__name__)


# ── Helpers ──────────────────────────────────────────────────────────

def _cn_len(text):
    """Count Chinese characters + ASCII chars in text."""
    if not text:
        return 0
    return len(text.replace('\n', '').replace(' ', '').replace('\t', ''))


def _extract_text(sections):
    """Extract all text from sections list for analysis."""
    parts = []
    for s in (sections or []):
        if not isinstance(s, dict):
            continue
        for key in ('content', 'heading', 'title'):
            v = s.get(key)
            if v and isinstance(v, str):
                parts.append(v)
        for item in (s.get('steps') or []):
            if isinstance(item, str):
                parts.append(item)
        for item in (s.get('items') or []):
            if isinstance(item, str):
                parts.append(item)
    return ' '.join(parts)


def _has_section_kind(sections, kind):
    """Check if any section has the given kind."""
    for s in (sections or []):
        if isinstance(s, dict) and s.get('kind') == kind:
            return True
    return False


def _get_section_kinds(sections):
    """Return list of kind values from sections."""
    return [s.get('kind', '') for s in (sections or []) if isinstance(s, dict)]


def _count_section_kind(sections, kind):
    """Count how many sections have the given kind."""
    return sum(1 for s in (sections or []) if isinstance(s, dict) and s.get('kind') == kind)


def _find_section_index(sections, kind):
    """Find index of first section with given kind, or -1."""
    for i, s in enumerate(sections or []):
        if isinstance(s, dict) and s.get('kind') == kind:
            return i
    return -1


def _detect_topic_category(topic):
    """Map topic to a fixed category for template dispatch."""
    t = (topic or '').lower()
    if '树' in t and ('二叉' in t or '遍历' in t or '前序' in t or '中序' in t or '后序' in t or 'tree' in t):
        return 'tree'
    if 'bfs' in t or 'dfs' in t or '广度' in t or '深度' in t or '图遍历' in t or 'graph' in t:
        return 'graph'
    if '动态规划' in t or 'dp' in t or '背包' in t or '状态转移' in t:
        return 'dp'
    if '排序' in t or 'sort' in t or '快速' in t or '归并' in t or '冒泡' in t or 'quicksort' in t:
        return 'sort'
    if '栈' in t and '队列' in t:
        return 'stack_queue'
    if '栈' in t:
        return 'stack'
    if '队列' in t or 'queue' in t:
        return 'queue'
    if '哈希' in t or '散列' in t or 'hash' in t:
        return 'hash'
    if '递归' in t and ('栈' in t or '调用' in t):
        return 'recursion'
    if '递归' in t:
        return 'recursion'
    if '链表' in t or 'linked' in t:
        return 'linked_list'
    if '二分' in t or 'binary search' in t:
        return 'binary_search'
    if '线性' in t or '数组' in t:
        return 'linear'
    return 'generic'


# ═══════════════════════════════════════════════════════════════════
# Knowledge Tags Builder
# ═══════════════════════════════════════════════════════════════════

def _build_knowledge_tags(cat, topic, rtype, lang):
    """Build 4-6 specific knowledge tags based on topic category, type, and language."""
    tags = []

    # 1. Topic keywords (1-2 tags)
    topic_tags = {
        'tree': ['二叉树', '树遍历'],
        'graph': ['图遍历', 'BFS', 'DFS'],
        'dp': ['动态规划', '状态转移'],
        'sort': ['排序算法', '快速排序'],
        'stack_queue': ['栈', '队列'],
        'stack': ['栈', 'LIFO'],
        'queue': ['队列', 'FIFO'],
        'hash': ['哈希表', '哈希冲突'],
        'recursion': ['递归', '调用栈'],
        'linked_list': ['链表', '指针操作'],
        'binary_search': ['二分查找', '有序数组'],
        'linear': ['线性表', '数组'],
    }
    tags.extend(topic_tags.get(cat, [topic])[:2])

    # 2. Type-specific action/purpose tags (1-2 tags)
    type_tags = {
        '图解讲解': ['图解', '分步过程'],
        '代码示例': ['完整代码', '测试用例', '复杂度分析'],
        '分层练习': ['分层练习', '参考答案'],
        '易错点': ['易错分析', '正确做法'],
        '项目案例': ['项目实战', '实现步骤'],
    }
    tags.extend(type_tags.get(rtype, [rtype])[:2])

    # 3. Language tag (if specific)
    if lang and lang not in ('未指定', '任意'):
        tags.append(lang)

    # 4. Deduplicate while preserving order, limit to 6
    seen = set()
    deduped = []
    for t in tags:
        if t not in seen and len(deduped) < 6:
            seen.add(t)
            deduped.append(t)
    return deduped


# ═══════════════════════════════════════════════════════════════════
# Type 1: 图解讲解 — must have real text diagram
# ═══════════════════════════════════════════════════════════════════

def _has_real_diagram(content_text):
    """Check if content contains a genuine ASCII diagram."""
    if not content_text:
        return False
    diagram_chars = set('│├└─┌┐┘└┤┬┴┼↓↑→←○●△▲☆★◎◉○□■◆◇→←↑↓↗↘↙↖/\\|+-*')
    lines = content_text.split('\n')
    diagram_lines = 0
    for line in lines:
        stripped = line.rstrip()
        if not stripped:
            continue
        special_count = sum(1 for c in stripped if c in diagram_chars)
        space_count = stripped.count(' ')
        if special_count >= 3:
            diagram_lines += 1
        elif space_count >= 4 and len(stripped) > 6:
            visible = [c for c in stripped if c not in ' \t']
            if len(visible) >= 3:
                diagram_lines += 1
    return diagram_lines >= 3


def _has_diagram_section(sections):
    """Check if sections contain a diagram kind section with meaningful content."""
    for s in (sections or []):
        if isinstance(s, dict) and s.get('kind') == 'diagram':
            content = s.get('content', '')
            if content and _cn_len(content) >= 30:
                return True
    return False


def _has_answer_after_practice(sections):
    """Check that every practice/task section has a following answer section."""
    kinds = _get_section_kinds(sections)
    for i, k in enumerate(kinds):
        if k in ('practice', 'task'):
            # Check if the next section is an answer
            if i + 1 >= len(kinds) or kinds[i + 1] != 'answer':
                return False
    return True


def _count_practice_answer_pairs(sections):
    """Count how many practice sections have an answer immediately after."""
    kinds = _get_section_kinds(sections)
    pairs = 0
    for i, k in enumerate(kinds):
        if k in ('practice', 'task'):
            if i + 1 < len(kinds) and kinds[i + 1] == 'answer':
                pairs += 1
    return pairs


def _build_visual_diagram_card(gen_context):
    """Build a complete 图解讲解 card with real text diagram."""
    topic = gen_context.get('topic', '')
    module = gen_context.get('module', '')
    lang = gen_context.get('normalized_language', 'Python')
    difficulty = gen_context.get('difficulty', '入门')
    cat = _detect_topic_category(topic)

    # ── Diagram per category ──
    diagrams = {
        'tree': (
            '二叉树结构示意（前序遍历：根→左→右）：\n'
            '\n'
            '        1          ← 根节点（第1步访问）\n'
            '       / \\\n'
            '      2   3        ← 第2步访问左子2，第5步访问右子3\n'
            '     / \\\n'
            '    4   5          ← 第3步访问4，第4步访问5\n'
            '\n'
            '前序遍历输出序列：1 → 2 → 4 → 5 → 3\n'
            '\n'
            '递归调用栈变化过程：\n'
            '  preorder(1)  → 输出1, 调用preorder(2)\n'
            '    preorder(2)  → 输出2, 调用preorder(4)\n'
            '      preorder(4)  → 输出4, 左右均为nullptr返回\n'
            '    preorder(2)  → 调用preorder(5)\n'
            '      preorder(5)  → 输出5, 左右均为nullptr返回\n'
            '    preorder(2)  → 返回\n'
            '  preorder(1)  → 调用preorder(3)\n'
            '    preorder(3)  → 输出3, 左右均为nullptr返回\n'
            '  preorder(1)  → 返回（遍历结束）'
        ),
        'graph': (
            '图的邻接表结构与BFS/DFS遍历示意：\n'
            '\n'
            '    0 ── 1 ── 2\n'
            '    │    │\n'
            '    3 ── 4\n'
            '\n'
            '邻接表：\n'
            '  0: [1, 3]\n'
            '  1: [0, 2, 4]\n'
            '  2: [1]\n'
            '  3: [0, 4]\n'
            '  4: [1, 3]\n'
            '\n'
            'BFS(0) 队列变化：\n'
            '  初始: queue = [0], visited = {0}\n'
            '  出队0 → 入队[1,3] → queue = [1,3], 输出 0\n'
            '  出队1 → 入队[2,4] → queue = [3,2,4], 输出 0 1\n'
            '  出队3 → 无新节点     → queue = [2,4], 输出 0 1 3\n'
            '  出队2 → 无新节点     → queue = [4], 输出 0 1 3 2\n'
            '  出队4 → 无新节点     → queue = [], 输出 0 1 3 2 4\n'
            '  BFS结果: [0, 1, 3, 2, 4]\n'
            '\n'
            'DFS(0) 递归过程：\n'
            '  dfs(0) → dfs(1) → dfs(2) → 回溯 → dfs(4) → dfs(3)\n'
            '  DFS结果: [0, 1, 2, 4, 3]'
        ),
        'dp': (
            '动态规划状态转移示意（以0-1背包为例）：\n'
            '\n'
            '  物品: w=[2,3,4], v=[3,4,5], 容量W=7\n'
            '\n'
            '  DP表 dp[i][w] = 前i件物品在容量w下的最大价值:\n'
            '\n'
            '       w=0  1  2  3  4  5  6  7\n'
            '  i=0:  0  0  0  0  0  0  0  0  (0件物品)\n'
            '  i=1:  0  0  3  3  3  3  3  3  (第1件:w=2,v=3)\n'
            '  i=2:  0  0  3  4  4  7  7  7  (第2件:w=3,v=4)\n'
            '  i=3:  0  0  3  4  5  7  8  9  (第3件:w=4,v=5)\n'
            '\n'
            '  状态转移方程:\n'
            '    dp[i][w] = max(dp[i-1][w], dp[i-1][w-wᵢ] + vᵢ)\n'
            '\n'
            '  最优解回溯:\n'
            '    dp[3][7]=9 → 选物品3(w=4) → dp[2][3]=4 → 选物品2(w=3) → 总价值9'
        ),
        'sort': (
            '快速排序 partition 过程示意（以 [5,3,7,2,8,1,6] 为例）：\n'
            '\n'
            '  初始: [5, 3, 7, 2, 8, 1, 6]  pivot=6(末尾)\n'
            '\n'
            '  i=-1, j=0: arr[0]=5 < 6 → i=0, swap(0,0) → [5,3,7,2,8,1,6]\n'
            '  i=0,  j=1: arr[1]=3 < 6 → i=1, swap(1,1) → [5,3,7,2,8,1,6]\n'
            '  i=1,  j=2: arr[2]=7 > 6 → 跳过\n'
            '  i=1,  j=3: arr[3]=2 < 6 → i=2, swap(2,3) → [5,3,2,7,8,1,6]\n'
            '  i=2,  j=4: arr[4]=8 > 6 → 跳过\n'
            '  i=2,  j=5: arr[5]=1 < 6 → i=3, swap(3,5) → [5,3,2,1,8,7,6]\n'
            '  最终: swap(i+1,pivot) → [5,3,2,1,6,7,8]\n'
            '\n'
            '  pivot=6归位, 左侧≤6, 右侧≥6, 递归排序左右子数组'
        ),
        'stack_queue': (
            '栈（LIFO）与队列（FIFO）操作示意：\n'
            '\n'
            '  栈操作（后进先出）：\n'
            '    push(1):  [1]\n'
            '    push(2):  [1,2]\n'
            '    push(3):  [1,2,3]\n'
            '    pop():    [1,2]  → 返回3\n'
            '    pop():    [1]    → 返回2\n'
            '\n'
            '  队列操作（先进先出）：\n'
            '    enqueue(1):  [1]←\n'
            '    enqueue(2):  [2,1]←\n'
            '    enqueue(3):  [3,2,1]←\n'
            '    dequeue():   [3,2]←  → 返回1\n'
            '    dequeue():   [3]←    → 返回2\n'
            '\n'
            '  双栈实现队列示意：\n'
            '    入队: push到stack1\n'
            '    出队: 若stack2为空，将stack1全部pop并push到stack2，再从stack2 pop'
        ),
        'hash': (
            '哈希表冲突解决示意：\n'
            '\n'
            '  链地址法 (Separate Chaining):\n'
            '    hash(key) = key % 7\n'
            '\n'
            '    桶0: [7] → [14]\n'
            '    桶1: [1] → [8] → [15]\n'
            '    桶2: [2]\n'
            '    桶3: [3] → [10]\n'
            '    桶4: [4]\n'
            '    桶5: [5]\n'
            '    桶6: [6]\n'
            '\n'
            '  开放寻址法 (线性探测):\n'
            '    hash(key) = key % 7, 冲突时顺延到下一空位\n'
            '\n'
            '    插入7: 桶0 → 空, 放入\n'
            '    插入14: 桶0 → 冲突, 桶1 → 空, 放入\n'
            '    插入21: 桶0 → 冲突, 桶1 → 冲突, 桶2 → 空, 放入\n'
            '\n'
            '  负载因子(load factor) = n/m, 超过0.75时应扩容'
        ),
        'recursion': (
            '递归调用栈示意（以 factorial(3) 为例）：\n'
            '\n'
            '  factorial(3) 调用过程:\n'
            '\n'
            '  ┌─────────────────┐\n'
            '  │ f(3): n=3       │ ← 第1层：等待 f(2) 返回\n'
            '  │ return 3*f(2)   │\n'
            '  ├─────────────────┤\n'
            '  │ f(2): n=2       │ ← 第2层：等待 f(1) 返回\n'
            '  │ return 2*f(1)   │\n'
            '  ├─────────────────┤\n'
            '  │ f(1): n=1       │ ← 第3层：触发递归边界\n'
            '  │ return 1        │\n'
            '  └─────────────────┘\n'
            '\n'
            '  回溯计算过程:\n'
            '    f(1)=1  →  f(2)=2*1=2  →  f(3)=3*2=6\n'
            '\n'
            '  关键理解:\n'
            '    每层递归 = 一个新的栈帧 (stack frame)\n'
            '    局部变量 n 在各层中独立存在\n'
            '    递归边界 (n≤1) 保证终止条件'
        ),
        'linked_list': (
            '单链表结构与操作示意：\n'
            '\n'
            '  head → [3|next] → [7|next] → [2|next] → [5|null]\n'
            '\n'
            '  反转链表过程:\n'
            '    初始: prev=null, curr=head\n'
            '    第1步: next=curr.next(保存[7]), curr.next=prev(null)\n'
            '           结果: null←[3]  [7]→[2]→[5]\n'
            '    第2步: prev=[3], curr=[7], next=curr.next(保存[2])\n'
            '           结果: null←[3]←[7]  [2]→[5]\n'
            '    最终: null←[3]←[7]←[2]←[5]  (head指向[5])'
        ),
        'binary_search': (
            '二分查找执行过程（在有序数组 [1,3,5,7,9,11,13,15] 中查找7）：\n'
            '\n'
            '  索引:  0  1  2  3  4   5   6   7\n'
            '  值:   [1, 3, 5, 7, 9, 11, 13, 15]\n'
            '\n'
            '  第1轮: left=0, right=7, mid=3\n'
            '         arr[3]=7 == target=7 → 找到!\n'
            '\n'
            '  时间复杂度: O(log₂n), 每次比较将搜索空间减半'
        ),
        'linear': (
            '线性表（数组/顺序表）操作示意：\n'
            '\n'
            '  数组: [10, 20, 30, 40, 50]\n'
            '\n'
            '  插入(位置2, 值25):\n'
            '    原始: [10, 20, 30, 40, 50]\n'
            '    移动: [10, 20, __, 30, 40, 50]  (30~50整体右移)\n'
            '    赋值: [10, 20, 25, 30, 40, 50]\n'
            '\n'
            '  删除(位置2):\n'
            '    原始: [10, 20, 30, 40, 50]\n'
            '    移动: [10, 20, 40, 50, __]  (40~50整体左移)\n'
        ),
    }

    diagram = diagrams.get(cat, (
        f'{topic} — 知识点结构关系：\n'
        f'\n'
        f'概念定义\n'
        f'   ↓\n'
        f'核心操作\n'
        f'   ↓\n'
        f'边界情况\n'
        f'   ↓\n'
        f'复杂度分析\n'
        f'   ↓\n'
        f'典型题型\n'
        f'\n'
        f'请结合下方分步过程，从基本定义出发，\n'
        f'逐步掌握核心操作、边界处理和复杂度分析。'
    ))

    # ── Core concept per category ──
    concepts = {
        'tree': (
            f'二叉树遍历是数据结构中最基础也最重要的操作之一。'
            f'前序遍历按照"根节点 → 左子树 → 右子树"的顺序访问每一个节点，'
            f'是 DFS（深度优先搜索）在二叉树上的直接体现。'
            f'理解前序遍历的关键在于理解递归调用栈的工作机制：'
            f'每进入一层递归，就相当于沿着树的左侧向下走一步；'
            f'每退出一层递归，就相当于回退到上一个分叉点，然后转向右子树。'
            f'这个"深入→回溯→转向"的过程，是理解所有树/图算法的核心基础。'
        ),
        'graph': (
            f'图的 BFS（广度优先搜索）和 DFS（深度优先搜索）是图中最基础的遍历策略。'
            f'BFS 使用队列实现，按"层"逐层访问，适合求最短路径；'
            f'DFS 使用递归或栈实现，沿一条路径深入到底再回溯，适合检测连通性和环。'
            f'理解两者的核心区别（队列 vs 栈、逐层 vs 深入）是灵活应用的关键。'
        ),
        'dp': (
            f'动态规划（DP）的核心思想是将原问题分解为重叠的子问题，'
            f'用表格（或数组）存储已计算的结果，避免重复计算。'
            f'DP 的三大要素：状态定义（dp[i] 表示什么）、状态转移方程（如何从已知推未知）、'
            f'初始条件和边界。理解这三点后，DP 问题就变成了"填表"问题。'
        ),
        'sort': (
            f'排序算法是计算机科学中最经典的问题之一。'
            f'快速排序通过 partition 操作将数组分为"小于pivot"和"大于pivot"两部分，'
            f'然后递归地对这两部分继续排序。其核心难点在于 partition 的双指针边界控制和稳定性理解。'
        ),
        'stack_queue': (
            f'栈（Stack）是一种"后进先出"（LIFO）的数据结构，'
            f'队列（Queue）是一种"先进先出"（FIFO）的数据结构。'
            f'两者都可以用数组或链表实现，且栈可以用两个队列模拟，队列也可以用两个栈模拟。'
        ),
        'hash': (
            f'哈希表通过哈希函数将键（key）映射到数组索引（桶），实现 O(1) 的平均查找时间。'
            f'当两个不同的 key 映射到同一个索引时，发生"哈希冲突"，'
            f'需要通过链地址法或开放寻址法来解决。负载因子是衡量哈希表性能的关键指标。'
        ),
        'recursion': (
            f'递归是函数直接或间接调用自身的编程技术。'
            f'每次递归调用都会在调用栈（call stack）上创建一个新的栈帧，'
            f'存储该次调用的局部变量和返回地址。递归必须有边界条件（base case），'
            f'否则会导致栈溢出（stack overflow）。'
        ),
        'linked_list': (
            f'链表是一种通过指针将分散的节点串联起来的线性数据结构。'
            f'与数组不同，链表支持 O(1) 的插入和删除（前提是已知位置），'
            f'但随机访问需要 O(n) 的时间。理解指针/引用的操作是掌握链表的关键。'
        ),
        'binary_search': (
            f'二分查找是一种在有序数组中高效查找目标值的算法，'
            f'每次比较将搜索范围缩小一半，时间复杂度为 O(log₂n)。'
            f'其核心在于正确维护搜索区间 [left, right] 的不变性，以及 mid 的计算方式。'
        ),
        'linear': (
            f'线性表是由 n 个相同类型元素组成的有限序列。'
            f'顺序表（数组）支持 O(1) 的随机访问但插入删除需 O(n)，'
            f'链表支持 O(1) 的插入删除但随机访问需 O(n)。选择哪种实现取决于具体应用场景。'
        ),
    }

    concept = concepts.get(cat, (
        f'「{topic}」是数据结构与算法学习中的重要内容。'
        f'掌握{topic}的核心原理，理解其执行过程和适用场景，'
        f'是灵活运用该知识解决实际问题的前提。'
    ))

    return {
        'id': f'res-visual-{cat}-001',
        'title': f'{topic} — 图解讲解',
        'type': '图解讲解',
        'course': '数据结构与算法',
        'knowledge_point': topic,
        'difficulty': difficulty,
        'language': lang,
        'summary': f'用树形结构图展示{topic}的访问顺序，配合分步推演和具体例子，直观理解遍历过程。',
        'knowledge_points': _build_knowledge_tags(cat, topic, '图解讲解', lang),
        'sections': [
            {'kind': 'highlight', 'heading': '核心概念', 'content': concept},
            {'kind': 'diagram', 'heading': '文本图解', 'content': diagram},
            {'kind': 'text', 'heading': '图解说明',
             'content': f'上图展示了{topic}的核心结构和执行过程。请仔细跟着图中的每一步，理解数据在每一步的状态变化。图中的箭头和缩进表示了执行的先后顺序和层次关系。'},
            {'kind': 'steps', 'heading': '分步过程',
             'steps': [
                 f'第一步：理解基本数据结构的定义和表示方法。例如节点结构、图的邻接表、栈/队列的容器等。这是后续所有操作的前提。',
                 f'第二步：跟踪算法的执行过程。逐行对照代码（或伪代码）与图解中的每一步，理解"为什么会这样变化"。',
                 f'第三步：关注边界和特殊情况。例如空树（空图）、只有一个节点的情况、重复元素的情况等。这些边界 case 是最容易出错的地方。',
                 f'第四步：自行在纸上画出执行过程。用不同的测试数据验证你对算法过程的理解是否正确。',
             ]},
            {'kind': 'practice', 'heading': '小例子',
             'content': f'请用最简单的例子（如3个节点的树、4个顶点的图等）手动执行一遍{topic}的完整过程，并将你的执行结果与上述图解进行比较。',
             'items': [
                 f'尝试用不同的输入数据验证你的理解',
                 f'关注关键变量在每个步骤中的变化',
                 f'如果有任何一步和图解不一致，说明那里存在理解偏差',
             ]},
            {'kind': 'answer', 'heading': '参考答案与验证方法',
             'content': (
                 f'验证方法：在图解中找到你的测试数据对应的步骤，逐行对比。例如：\n'
                 f'1. 先确认你的输入数据结构和图解中的结构一致（节点数、连接关系等）。\n'
                 f'2. 按算法步骤手动执行第1步，将中间结果（如当前节点、输出序列）与图解的相应步骤对比。\n'
                 f'3. 逐步骤推进，如果某一步与图解不一致，停止并分析原因——通常是前一步的理解有误。\n'
                 f'4. 用极端情况验证：空结构、单元素结构、退化为链的结构——确认算法在这些边界情况下的行为是否正确。\n'
                 f'关键提示：手动画图是理解算法的最有效方法。如果在纸上能完整画出算法的每一步执行过程，'
                 f'说明真正理解了该算法。'
             )},
            {'kind': 'warning', 'heading': '易错提醒',
             'content': (
                 f'提醒1：不要混淆数据结构的定义和算法操作的顺序。先确认结构（节点怎么连的），再确认操作（算法怎么走的）。\n'
                 f'提醒2：边界条件是最常见的出错点——空输入、单元素、重复元素、最大/最小值等都必须单独验证。\n'
                 f'提醒3：图解的每一步都有明确的原因——如果某一步看不懂，大概率是前面的某一步理解有偏差，建议回溯重读。'
             )},
        ],
    }


# ═══════════════════════════════════════════════════════════════════
# Type 2: 代码示例 — must have full code, test cases, complexity
# ═══════════════════════════════════════════════════════════════════

def _has_code_block(sections):
    """Check if sections contain genuine code content."""
    for s in (sections or []):
        if s.get('kind') == 'code' and s.get('content'):
            return True
        content = s.get('content', '')
        if isinstance(content, str) and ('```' in content or '#include' in content or 'def ' in content or 'class ' in content or 'function ' in content or 'int main' in content):
            return True
    return False


def _build_code_example_card(gen_context):
    """Build a complete 代码示例 card."""
    topic = gen_context.get('topic', '')
    lang = gen_context.get('normalized_language', 'Python')
    difficulty = gen_context.get('difficulty', '入门')
    cat = _detect_topic_category(topic)

    code_blocks = {
        ('tree', 'C++'): (
            '#include <iostream>\n'
            '#include <stack>\n'
            'using namespace std;\n\n'
            'struct TreeNode {\n'
            '    int val;\n'
            '    TreeNode *left, *right;\n'
            '    TreeNode(int v = 0, TreeNode* l = nullptr, TreeNode* r = nullptr)\n'
            '        : val(v), left(l), right(r) {}\n'
            '};\n\n'
            'void preorder(TreeNode* root) {\n'
            '    if (root == nullptr) return;\n'
            '    cout << root->val << " ";\n'
            '    preorder(root->left);\n'
            '    preorder(root->right);\n'
            '}\n\n'
            'int main() {\n'
            '    TreeNode* root = new TreeNode(1,\n'
            '        new TreeNode(2, new TreeNode(4), new TreeNode(5)),\n'
            '        new TreeNode(3));\n'
            '    cout << "preorder: ";\n'
            '    preorder(root);\n'
            '    cout << endl;\n'
            '    return 0;\n'
            '}'
        ),
        ('tree', 'Python'): (
            'class TreeNode:\n'
            '    def __init__(self, val=0, left=None, right=None):\n'
            '        self.val = val\n'
            '        self.left = left\n'
            '        self.right = right\n\n'
            'def preorder(root):\n'
            '    if root is None:\n'
            '        return\n'
            '    print(root.val, end=" ")\n'
            '    preorder(root.left)\n'
            '    preorder(root.right)\n\n'
            'if __name__ == "__main__":\n'
            '    root = TreeNode(1,\n'
            '        TreeNode(2, TreeNode(4), TreeNode(5)),\n'
            '        TreeNode(3))\n'
            '    print("preorder:", end=" ")\n'
            '    preorder(root)\n'
            '    print()'
        ),
        ('graph', 'C++'): (
            '#include <iostream>\n'
            '#include <vector>\n'
            '#include <queue>\n'
            '#include <stack>\n'
            'using namespace std;\n\n'
            'void bfs(vector<vector<int>>& adj, int start) {\n'
            '    vector<bool> visited(adj.size(), false);\n'
            '    queue<int> q;\n'
            '    q.push(start);\n'
            '    visited[start] = true;\n'
            '    while (!q.empty()) {\n'
            '        int v = q.front(); q.pop();\n'
            '        cout << v << " ";\n'
            '        for (int u : adj[v]) {\n'
            '            if (!visited[u]) {\n'
            '                visited[u] = true;\n'
            '                q.push(u);\n'
            '            }\n'
            '        }\n'
            '    }\n'
            '}\n\n'
            'void dfsUtil(vector<vector<int>>& adj, int v, vector<bool>& visited) {\n'
            '    visited[v] = true;\n'
            '    cout << v << " ";\n'
            '    for (int u : adj[v]) {\n'
            '        if (!visited[u]) dfsUtil(adj, u, visited);\n'
            '    }\n'
            '}\n\n'
            'int main() {\n'
            '    vector<vector<int>> adj = {{1,3},{0,2,4},{1},{0,4},{1,3}};\n'
            '    cout << "BFS: "; bfs(adj, 0); cout << endl;\n'
            '    vector<bool> visited(5, false);\n'
            '    cout << "DFS: "; dfsUtil(adj, 0, visited); cout << endl;\n'
            '    return 0;\n'
            '}'
        ),
        ('graph', 'Python'): (
            'from collections import deque\n\n'
            'def bfs(adj, start):\n'
            '    visited = [False] * len(adj)\n'
            '    q = deque([start])\n'
            '    visited[start] = True\n'
            '    while q:\n'
            '        v = q.popleft()\n'
            '        print(v, end=" ")\n'
            '        for u in adj[v]:\n'
            '            if not visited[u]:\n'
            '                visited[u] = True\n'
            '                q.append(u)\n\n'
            'def dfs(adj, v, visited):\n'
            '    visited[v] = True\n'
            '    print(v, end=" ")\n'
            '    for u in adj[v]:\n'
            '        if not visited[u]:\n'
            '            dfs(adj, u, visited)\n\n'
            'if __name__ == "__main__":\n'
            '    adj = [[1,3],[0,2,4],[1],[0,4],[1,3]]\n'
            '    print("BFS:", end=" "); bfs(adj, 0); print()\n'
            '    visited = [False] * 5\n'
            '    print("DFS:", end=" "); dfs(adj, 0, visited); print()'
        ),
        ('dp', 'Python'): (
            'def knapsack_01(weights, values, capacity):\n'
            '    n = len(weights)\n'
            '    dp = [[0] * (capacity + 1) for _ in range(n + 1)]\n'
            '    for i in range(1, n + 1):\n'
            '        for w in range(1, capacity + 1):\n'
            '            if weights[i-1] <= w:\n'
            '                dp[i][w] = max(\n'
            '                    dp[i-1][w],\n'
            '                    dp[i-1][w-weights[i-1]] + values[i-1]\n'
            '                )\n'
            '            else:\n'
            '                dp[i][w] = dp[i-1][w]\n'
            '    return dp[n][capacity]\n\n'
            'if __name__ == "__main__":\n'
            '    w = [2, 3, 4]\n'
            '    v = [3, 4, 5]\n'
            '    cap = 7\n'
            '    print("max value:", knapsack_01(w, v, cap))'
        ),
        ('dp', 'C++'): (
            '#include <iostream>\n'
            '#include <vector>\n'
            'using namespace std;\n\n'
            'int knapsack(vector<int>& w, vector<int>& v, int cap) {\n'
            '    int n = w.size();\n'
            '    vector<vector<int>> dp(n+1, vector<int>(cap+1, 0));\n'
            '    for (int i = 1; i <= n; i++) {\n'
            '        for (int j = 1; j <= cap; j++) {\n'
            '            if (w[i-1] <= j)\n'
            '                dp[i][j] = max(dp[i-1][j], dp[i-1][j-w[i-1]] + v[i-1]);\n'
            '            else\n'
            '                dp[i][j] = dp[i-1][j];\n'
            '        }\n'
            '    }\n'
            '    return dp[n][cap];\n'
            '}\n\n'
            'int main() {\n'
            '    vector<int> w = {2,3,4}, v = {3,4,5};\n'
            '    cout << knapsack(w, v, 7) << endl;\n'
            '    return 0;\n'
            '}'
        ),
        ('sort', 'Python'): (
            'def quicksort(arr, low, high):\n'
            '    if low < high:\n'
            '        pi = partition(arr, low, high)\n'
            '        quicksort(arr, low, pi - 1)\n'
            '        quicksort(arr, pi + 1, high)\n\n'
            'def partition(arr, low, high):\n'
            '    pivot = arr[high]\n'
            '    i = low - 1\n'
            '    for j in range(low, high):\n'
            '        if arr[j] <= pivot:\n'
            '            i += 1\n'
            '            arr[i], arr[j] = arr[j], arr[i]\n'
            '    arr[i+1], arr[high] = arr[high], arr[i+1]\n'
            '    return i + 1\n\n'
            'if __name__ == "__main__":\n'
            '    a = [5, 3, 7, 2, 8, 1, 6]\n'
            '    quicksort(a, 0, len(a)-1)\n'
            '    print("sorted:", a)'
        ),
        ('sort', 'C++'): (
            '#include <iostream>\n'
            '#include <vector>\n'
            'using namespace std;\n\n'
            'int partition(vector<int>& arr, int low, int high) {\n'
            '    int pivot = arr[high];\n'
            '    int i = low - 1;\n'
            '    for (int j = low; j < high; j++) {\n'
            '        if (arr[j] <= pivot) {\n'
            '            i++;\n'
            '            swap(arr[i], arr[j]);\n'
            '        }\n'
            '    }\n'
            '    swap(arr[i+1], arr[high]);\n'
            '    return i + 1;\n'
            '}\n\n'
            'void quicksort(vector<int>& arr, int low, int high) {\n'
            '    if (low < high) {\n'
            '        int pi = partition(arr, low, high);\n'
            '        quicksort(arr, low, pi - 1);\n'
            '        quicksort(arr, pi + 1, high);\n'
            '    }\n'
            '}\n\n'
            'int main() {\n'
            '    vector<int> a = {5,3,7,2,8,1,6};\n'
            '    quicksort(a, 0, a.size()-1);\n'
            '    for (int x : a) cout << x << " ";\n'
            '    return 0;\n'
            '}'
        ),
    }

    # Find best code match
    code_key = (cat, lang) if (cat, lang) in code_blocks else None
    if not code_key:
        code_key = (cat, 'Python') if (cat, 'Python') in code_blocks else None
    if not code_key:
        # Generic fallback
        generic_code = lang if lang == 'Python' else 'C++'
        code_key = ('tree', generic_code)

    code_text = code_blocks.get(code_key, code_blocks[('tree', 'Python')])
    code_lang = code_key[1] if code_key else 'Python'

    # ── Complexity per category ──
    complexities = {
        'tree': ('时间复杂度：O(n)，每个节点恰好被访问一次。\n空间复杂度：O(h)，h为树的高度，递归调用栈的最大深度。最坏情况（树退化为链表）O(n)，平均/最好情况 O(log n)。'),
        'graph': ('时间复杂度：O(V+E)，V为顶点数，E为边数。每个顶点和每条边都被处理一次。\n空间复杂度：O(V)，主要来自 visited 数组和队列/递归调用栈。'),
        'dp': ('时间复杂度：O(n*W)，n为物品数量，W为背包容量。\n空间复杂度：O(n*W)，可用滚动数组优化至 O(W)。'),
        'sort': ('时间复杂度：平均 O(n log n)，最坏 O(n²)（可通过随机pivot避免）。\n空间复杂度：O(log n)，来自递归调用栈。快速排序是不稳定的原地排序。'),
        'stack_queue': ('时间复杂度：push/pop/enqueue/dequeue均为O(1)。\n空间复杂度：O(n)，n为存储的元素数量。'),
        'hash': ('时间复杂度：平均 O(1) 插入/查找/删除，最坏 O(n)（全部冲突时）。\n空间复杂度：O(n)，取决于存储的元素数量和负载因子。'),
        'recursion': ('时间复杂度：取决于具体问题，通常为 O(n) 或 O(2ⁿ)。\n空间复杂度：O(n)，来自递归调用栈的深度。'),
        'linked_list': ('时间复杂度：访问 O(n)，插入/删除 O(1)（已知位置）。\n空间复杂度：O(n)，每个节点需要一个指针/引用。'),
        'binary_search': ('时间复杂度：O(log₂n)。\n空间复杂度：迭代版 O(1)，递归版 O(log n)。'),
        'linear': ('时间复杂度：访问 O(1)，插入/删除 O(n)（数组）；访问 O(n)，插入/删除 O(1)（链表）。\n空间复杂度：O(n)。'),
    }
    complexity = complexities.get(cat, f'时间复杂度：O(n)——处理规模为n的输入。\n空间复杂度：O(1)~O(n)——取决于是否需要额外存储。')

    return {
        'id': f'res-code-{cat}-001',
        'title': f'{topic} — {code_lang} 代码示例',
        'type': '代码示例',
        'course': '数据结构与算法',
        'knowledge_point': topic,
        'difficulty': difficulty,
        'language': lang,
        'summary': f'包含{topic}的完整{code_lang}代码实现、关键行解释、测试用例和复杂度分析，可直接运行验证。',
        'knowledge_points': _build_knowledge_tags(cat, topic, '代码示例', lang),
        'sections': [
            {'kind': 'text', 'heading': '使用场景',
             'content': f'{topic}在实际开发中的典型应用场景包括：算法竞赛中的基础题、技术面试中的高频考题、以及需要高效数据处理的工程项目。理解代码实现是掌握该知识点的关键一步。'},
            {'kind': 'code', 'heading': f'完整代码（{code_lang}）', 'language': code_lang, 'content': code_text},
            {'kind': 'test_cases', 'heading': '测试用例',
             'content': (
                 '测试1：基本功能测试——使用标准输入验证输出是否正确。\n'
                 '测试2：边界测试——空输入、单元素输入、两个元素输入。\n'
                 '测试3：大规模数据测试——n=1000时检查运行时间是否在合理范围内。\n'
                 '测试4：特殊输入——包含重复值、已排序数据、反向排序数据。'
             )},
            {'kind': 'steps', 'heading': '关键代码解释',
             'steps': [
                 f'数据结构定义：代码中定义了核心数据结构（如TreeNode节点、邻接表等），理解这些结构是理解算法逻辑的前提。',
                 f'核心算法函数：主函数实现了{topic}的核心逻辑，请逐行阅读并对照下方的复杂度分析理解每个循环/递归的作用。',
                 f'测试代码：main/__main__部分构建了测试数据并调用核心函数，验证了实现的正确性。尝试修改测试数据来验证不同场景。',
             ]},
            {'kind': 'complexity', 'heading': '复杂度分析', 'content': complexity},
            {'kind': 'practice', 'heading': '可改造练习',
             'content': '在理解上述代码的基础上，尝试以下改造：',
             'items': [
                 f'尝试用另一种编程语言重写该代码',
                 f'尝试修改算法的一个变体（如非递归实现、空间优化等）',
                 f'尝试处理更复杂的输入场景',
             ]},
            {'kind': 'answer', 'heading': '参考答案与提示',
             'content': (
                 f'提示1（语言转换）：用另一种语言重写时，注意语法对应关系——Python的list对应C++的vector，'
                 f'Python的None对应C++的nullptr，Python缩进对C++的花括号。关键是保持算法逻辑不变。\n'
                 f'提示2（非递归实现）：将递归转为迭代的核心是用显式栈（stack/list）代替调用栈。'
                 f'将当前状态压栈→处理→弹出→压入子问题，模拟递归的"进入→处理→返回"过程。\n'
                 f'提示3（复杂场景）：增加数据规模或数据类型的变化（如从int变为自定义对象），'
                 f'检验算法的泛化能力。如果修改了数据表示方式，相应的比较/访问逻辑也需要调整。\n'
                 f'验证方法：改造后的代码应能通过原测试用例，且在新增测试用例上输出正确结果。'
             )},
        ],
    }


# ═══════════════════════════════════════════════════════════════════
# Type 3: 分层练习 — must have questions + answers + analysis
# ═══════════════════════════════════════════════════════════════════

def _has_questions_with_answers(sections):
    """Check that practice sections have matching answer sections (by kind, not text scan)."""
    practice_count = _count_section_kind(sections, 'practice')
    if practice_count < 2:
        return False
    answer_count = _count_section_kind(sections, 'answer')
    if answer_count == 0:
        return False
    pairs = _count_practice_answer_pairs(sections)
    return pairs >= 1


def _build_practice_card(gen_context):
    """Build a complete 分层练习 card with questions, answers, and analysis."""
    topic = gen_context.get('topic', '')
    lang = gen_context.get('normalized_language', 'Python')
    difficulty = gen_context.get('difficulty', '入门')
    cat = _detect_topic_category(topic)

    # ── Question sets per category ──
    practice_sets = {
        'tree': {
            'basic': [
                {'q': '给定二叉树的前序遍历序列为 [1,2,4,5,3]，中序遍历序列为 [4,2,5,1,3]，请画出该二叉树的结构。',
                 'a': '前序第一个元素1是根节点。在中序中找到1，左边[4,2,5]是左子树，右边[3]是右子树。递归：左子树前序[2,4,5]中序[4,2,5]，2是根，4在左，5在右。右子树前序[3]中序[3]，只有一个节点3。最终结构：根1，左子2（左子4，右子5），右子3。'},
                {'q': '写出二叉树后序遍历（左右根）的递归函数，并用示例树 [1,2,3,4,5] 验证输出。',
                 'a': '后序遍历递归函数：先 postorder(root.left)，再 postorder(root.right)，最后 print(root.val)。示例树遍历结果为 [4,5,2,3,1]。'},
            ],
            'advanced': [
                {'q': '如何用非递归方法（用栈）实现二叉树的中序遍历？请写出核心逻辑并分析空间复杂度。',
                 'a': '使用栈模拟递归：从根开始，将所有左子节点依次压栈；弹出栈顶节点访问；将当前节点设为其右子；重复直到栈空且当前节点为null。空间复杂度O(h)，h为树高。'},
                {'q': '判断一棵二叉树是否是对称的（镜像对称）。例如 [1,2,2,3,4,4,3] 是对称的。写出判断函数。',
                 'a': '递归比较：check(left.left, right.right) && check(left.right, right.left)。两棵子树互为镜像当且仅当它们的根值相等，且左子树的左子与右子树的右子镜像对称，左子树的右子与右子树的左子镜像对称。时间复杂度O(n)。'},
            ],
            'comprehensive': [
                {'q': '给定一个二叉树，请实现一个函数计算该树中所有节点值的和、最大值、以及树的高度。要求一次遍历完成三个计算。',
                 'a': '使用后序遍历（或前序）+ 传引用/返回多个值。每次递归返回三个值：(子树和, 子树最大值, 子树高度)。对空节点返回(0, INT_MIN, 0)。对非空节点：和 = root.val + left_sum + right_sum，最大值 = max(root.val, left_max, right_max)，高度 = 1 + max(left_h, right_h)。时间复杂度O(n)。'},
            ],
        },
        'graph': {
            'basic': [
                {'q': '给定邻接矩阵表示的图，写出BFS遍历的完整代码，输出遍历顺序。',
                 'a': '使用队列：初始化visited数组，将起点入队并标记为visited。while队列非空：出队队首元素v并输出，遍历v的所有邻居u，若u未访问则入队并标记。时间复杂度O(V²)（邻接矩阵）或O(V+E)（邻接表）。'},
                {'q': '写出图的DFS递归实现代码。DFS和BFS在遍历顺序上的本质区别是什么？',
                 'a': 'DFS递归：访问当前节点v，标记visited[v]=true，对每个未访问邻居u递归调用dfs(u)。BFS按层遍历（同级优先），DFS沿路径深入再回溯（深度优先）。'},
            ],
            'advanced': [
                {'q': '给定一个无向图，判断是否存在从节点A到节点B的路径。如果存在路径，如何找到最短路径？',
                 'a': '判断连通性：从A开始做BFS或DFS，检查B是否被访问。找最短路径（无权图）：必须用BFS，记录每个节点的前驱节点（parent数组），BFS遇到B时停止，通过parent回溯得到最短路径。BFS保证首次访问到的路径就是最短路径。'},
                {'q': '在有向图中，如何检测是否存在环？写出判断逻辑。',
                 'a': '用DFS + 三色标记法：WHITE(未访问)、GRAY(正在访问/在当前递归路径中)、BLACK(已完成)。DFS访问到GRAY节点说明存在环。或者用拓扑排序（Kahn算法）：计算所有节点的入度，依次移除入度为0的节点，若最终仍有节点剩余则存在环。'},
            ],
            'comprehensive': [
                {'q': '实现Dijkstra算法求单源最短路径。给定一个加权有向图（无负权边）和起点，输出起点到所有其他节点的最短距离和最短路径。',
                 'a': '使用优先队列（最小堆）：初始化dist[起点]=0，其余为∞。将(0, 起点)入堆。while堆非空：弹出(dist, v)，若dist > dist[v]则跳过（已过时）；遍历v的邻居u，若dist[v]+w(v,u) < dist[u]则更新dist[u]并记录前驱，将(dist[u], u)入堆。时间复杂度O((V+E)logV)。无负权边时Dijkstra保证正确性。'},
            ],
        },
        'dp': {
            'basic': [
                {'q': '用动态规划求解斐波那契数列第n项。请写出状态定义和状态转移方程，并给出代码实现。',
                 'a': '状态定义：dp[i] = 第i个斐波那契数。状态转移：dp[i] = dp[i-1] + dp[i-2]。初始化：dp[0]=0, dp[1]=1。时间复杂度O(n)，空间复杂度O(1)（只需两个变量）。'},
                {'q': '爬楼梯问题：每次可以爬1或2阶，爬到第n阶有多少种方法？写出DP解法和代码。',
                 'a': '同斐波那契：dp[i] = dp[i-1] + dp[i-2]。dp[0]=1（地面），dp[1]=1（1阶）。答案=dp[n]。本质是斐波那契数列的偏移。'},
            ],
            'advanced': [
                {'q': '最长递增子序列（LIS）：给定数组 [10,9,2,5,3,7,101,18]，求最长严格递增子序列的长度。',
                 'a': '定义dp[i] = 以nums[i]结尾的最长递增子序列长度。转移：dp[i] = max(dp[j]+1) for all j<i where nums[j]<nums[i]，若无则为1。答案=max(dp)。时间O(n²)，可优化到O(n log n)（贪心+二分）。'},
                {'q': '0-1背包问题：物品重量w=[2,3,4]，价值v=[3,4,5]，背包容量W=7。求最大总价值并给出选择的物品。',
                 'a': 'dp[i][j] = max(dp[i-1][j], dp[i-1][j-w[i]]+v[i])。dp[3][7]=9，回溯：dp[3][7]=9≠dp[2][7]=7，说明选了物品3(w=4,v=5)，剩余容量3；dp[2][3]=4≠dp[1][3]=3，选了物品2(w=3,v=4)，剩余0。选物品2和3。'},
            ],
            'comprehensive': [
                {'q': '最长公共子序列（LCS）问题：给定两个字符串 text1="abcde" 和 text2="ace"，求它们的最长公共子序列。请写出状态定义、状态转移、代码实现，并输出LCS内容（不仅是长度）。',
                 'a': 'dp[i][j] = text1[0..i-1]和text2[0..j-1]的LCS长度。若text1[i-1]==text2[j-1]则dp[i][j]=dp[i-1][j-1]+1，否则dp[i][j]=max(dp[i-1][j], dp[i][j-1])。回溯：从dp[m][n]开始，若字符相等则属于LCS（斜向移动），否则向大的方向移动。LCS="ace"，长度3。'},
            ],
        },
        'sort': {
            'basic': [
                {'q': '写出冒泡排序的代码，并分析其最好、平均、最坏时间复杂度。',
                 'a': '冒泡排序：每次遍历比较相邻元素并交换，每轮将最大元素"浮"到末尾。最好O(n)（已排序+提前终止标记），平均O(n²)，最坏O(n²)，空间O(1)，稳定排序。'},
                {'q': '写出选择排序的代码，并与冒泡排序比较优缺点。',
                 'a': '选择排序：每轮找到未排序部分的最小元素，与未排序部分的第一个元素交换。时间始终O(n²)，空间O(1)，不稳定。比冒泡的优势在于交换次数少（每轮最多1次交换vs冒泡可能O(n²)次）。'},
            ],
            'advanced': [
                {'q': '实现快速排序，并解释partition函数中为什么不能将pivot固定选为第一个元素。',
                 'a': '固定选首元素在已排序数组上会退化为O(n²)。正确做法：随机选pivot或三数取中法。partition核心逻辑：遍历(low,high)，将≤pivot的元素交换到左侧，最后将pivot放到正确位置。'},
                {'q': '归并排序和快速排序在时间/空间/稳定性方面各有什么特点？什么时候该选哪种？',
                 'a': '归并排序：时间O(n log n)稳定，空间O(n)，稳定排序，适合链表排序和外部排序。快速排序：时间平均O(n log n)最坏O(n²)，空间O(log n)，不稳定，实践中通常更快（缓存友好、常数小）。对稳定性有要求选归并，追求性能选快排。'},
            ],
            'comprehensive': [
                {'q': '给定一个包含100万个随机整数的数组，要求找出其中第k小的元素。请设计一个O(n)平均时间的算法并实现。',
                 'a': '使用"快速选择(QuickSelect)"算法，是快速排序的变体：每次partition后，如果pivot位置正好是k-1则返回；如果pivot位置>k-1则只在左半部分递归；否则只在右半部分递归。平均O(n)，最坏O(n²)，可通过随机pivot避免退化。是解决top-k问题的经典算法。'},
            ],
        },
    }

    ps = practice_sets.get(cat, practice_sets['tree'])

    def _build_question_section(qa, idx, level_name):
        """Build a practice + answer pair for one question."""
        return [
            {'kind': 'practice', 'heading': f'{level_name}第{idx}题',
             'content': qa['q']},
            {'kind': 'answer', 'heading': f'{level_name}第{idx}题 — 参考答案与解析',
             'content': qa['a']},
        ]

    sections = [
        {'kind': 'highlight', 'heading': '练习说明',
         'content': f'以下练习围绕{topic}的核心知识点设计，分为基础题（验证基本理解）、进阶题（加深灵活运用）和综合题（整合多个知识点）。每道题都包含参考答案和详细解析。建议先独立思考并写出代码，再对照答案检查。'},
    ]

    for i, qa in enumerate(ps['basic'], 1):
        sections.extend(_build_question_section(qa, i, '基础'))
    for i, qa in enumerate(ps['advanced'], 1):
        sections.extend(_build_question_section(qa, i, '进阶'))
    for i, qa in enumerate(ps['comprehensive'], 1):
        sections.extend(_build_question_section(qa, i, '综合'))

    sections.append({
        'kind': 'warning', 'heading': '常见错误提醒',
        'content': (
            f'错误1：只关注代码实现，忽略对算法过程的理解，导致面试中无法解释算法步骤和时间复杂度。\n'
            f'错误2：练习时只做基础题，不愿挑战进阶和综合题，实际面试/竞赛中遇到变形题无从下手。\n'
            f'错误3：做完题不检查答案和解析，重复犯同样的错误，进步缓慢。\n'
            f'建议：每道题先独立做20分钟，实在不会再看答案，看懂答案后自己重新写一遍。'
        ),
    })

    return {
        'id': f'res-practice-{cat}-001',
        'title': f'{topic} — 分层练习与解析',
        'type': '分层练习',
        'course': '数据结构与算法',
        'knowledge_point': topic,
        'difficulty': difficulty,
        'language': lang,
        'summary': f'包含{topic}的基础题、进阶题和综合题，每道题均配有参考答案与详细解析，适合阶段性自测。',
        'knowledge_points': _build_knowledge_tags(cat, topic, '分层练习', lang),
        'sections': sections,
    }


# ═══════════════════════════════════════════════════════════════════
# Type 4: 易错点 — must have 3+ concrete error points
# ═══════════════════════════════════════════════════════════════════

def _count_error_points(sections):
    """Count warning sections that contain error-point content (by kind + content check)."""
    count = 0
    for s in (sections or []):
        if isinstance(s, dict) and s.get('kind') in ('warning', 'warnings'):
            heading = s.get('heading', '')
            content = s.get('content', '')
            if _cn_len(heading + content) >= 30:
                count += 1
    if count < 3:
        text = _extract_text(sections)
        text_count = len(re.findall(r'(?:易错点|错误[点现象]|误区|常见错误|错误\d|第\d.*错)', text))
        count = max(count, text_count)
    return count


def _build_mistake_card(gen_context):
    """Build a complete 易错点 card with 3+ concrete error points."""
    topic = gen_context.get('topic', '')
    lang = gen_context.get('normalized_language', 'Python')
    difficulty = gen_context.get('difficulty', '入门')
    cat = _detect_topic_category(topic)

    mistake_sets = {
        'tree': [
            {
                'title': '递归边界条件遗漏——忘记判空导致段错误',
                'error': '在 preorder(root) 函数中直接访问 root->val 而没有先判断 root == nullptr，当遍历到叶子节点的下一层时程序崩溃。',
                'reason': '递归遍历的终止条件是"当前节点为空"，这是递归函数的出口。忘记判空意味着递归将无限进行（或崩溃）。',
                'fix': '在函数开头添加 if (root == nullptr) return; 作为第一行代码。这是所有树递归函数必须的防御性判断。',
                'check': '用空树（root=nullptr）测试遍历函数，应正常结束而非崩溃。',
            },
            {
                'title': '前序/中序/后序混淆——cout位置写错',
                'error': '将前序遍历写成：preorder(root->left); cout << root->val; preorder(root->right); 这实际上是中序遍历。',
                'reason': '前序（根左右）、中序（左根右）、后序（左右根）的唯一区别就是访问根节点的这行代码放在递归调用的哪个位置。',
                'fix': '前序：先cout后递归。中序：cout在两次递归之间。后序：cout在两次递归之后。三个函数的递归调用顺序完全一样，只改变cout的位置。',
                'check': '对同一棵树分别运行三个函数，验证输出是否分别符合前序/中序/后序的定义。',
            },
            {
                'title': '忘记在递归前保存/恢复状态',
                'error': '在递归遍历中修改了全局变量（如累加和、路径列表），但没有在递归返回后恢复状态，造成结果污染。',
                'reason': '递归函数内部对可变对象（如list/vector）的修改会跨递归层传播，如果不恢复会导致其他分支看到错误的数据。',
                'fix': '递归前修改状态 → 递归调用 → 递归后恢复状态（回溯）。这是所有"路径型"递归（如求所有路径、回溯法）的核心模式。',
                'check': '打印每一步的状态变化，确认每个分支都有独立的、正确的状态。',
            },
        ],
        'graph': [
            {
                'title': 'BFS忘记标记visited导致重复入队/死循环',
                'error': '在BFS中只检查visited[t]却忘记在入队时设置visited[t]=true，导致同一个节点被重复加入队列，程序可能无限循环或超时。',
                'reason': 'BFS要求"入队即标记"——一旦决定将节点加入队列，就必须立即将其标记为已访问。如果在出队时才标记，同一节点可能在入队和出队之间被其他节点再次发现并重复入队。',
                'fix': '在 q.push(v) 之前（或紧接之后）立即设置 visited[v]=true。入队和标记必须在同一个原子操作中完成，不能分开。',
                'check': '在入队时打印日志，确认每个节点只入队一次。',
            },
            {
                'title': 'DFS递归爆栈——深度过大导致StackOverflow',
                'error': '在树或图深度很大（如链状图10000+节点）时，DFS递归实现会因调用栈深度过大而溢出。',
                'reason': '每次递归调用分配一个新的栈帧（通常几KB），递归深度=n时，总栈空间=n×栈帧大小，可能超过系统限制（通常8MB左右）。',
                'fix': '对于深层图，改用显式栈(stack)的迭代版DFS，或改用BFS（队列实现无递归深度限制）。迭代版DFS使用堆内存（heap），只受系统总内存限制。',
                'check': '用深度为10000的单链图测试DFS，确认不会崩溃。',
            },
            {
                'title': '无向图遍历时重复访问已访问节点',
                'error': '在无向图DFS中，从u访问邻居v后，如果v的邻居列表中又包含u，且没有visited检查，会导致死循环：u→v→u→v→...',
                'reason': '无向图中每条边被存储了两次（u的邻居有v，v的邻居有u），遍历时必须用visited数组避免走"回头路"。',
                'fix': '遍历v的邻居前，确认 !visited[neighbor]。对于棵树（无环的连通无向图），也可以传一个parent参数来避免回到父节点。',
                'check': '用一个有环的无向图测试，确认不会陷入死循环。',
            },
        ],
        'dp': [
            {
                'title': '状态定义错误——dp[i]含义不清导致公式写错',
                'error': '定义dp[i]=前i个元素的最优解，但转移时错误地使用了dp[i-2]。原因是没想清楚dp[i]到底表示"包含第i个"还是"前i个"。',
                'reason': '状态定义是DP的灵魂。如果定义模糊，后续的转移方程、初始化和最终答案都会出错。',
                'fix': '明确写出："dp[i]表示...（包含/不包含第i个元素？以第i个元素结尾？前i个元素？）"。必须用一句话完全无歧义地定义状态。',
                'check': '用小例子（n=2或3）手动推导dp[0]、dp[1]、dp[2]，验证定义是否自洽。',
            },
            {
                'title': '初始化遗漏——dp[0]/dp[1]未正确赋值',
                'error': '定义了dp数组但忘记设置dp[0]（或dp[1]），或者设置值错误，导致整个dp表算出的都是错误值。',
                'reason': 'DP的递推依赖于初始值，初始值错了全盘皆错。很多同学花大量时间检查转移方程，却忽略了初始化。',
                'fix': '将初始条件单独列出并注释："dp[0]=xxx 因为...（一句话说明为什么是这个值）"。初始化通常对应递归的base case。',
                'check': '打印dp的前几个值，验证是否与预期一致。',
            },
            {
                'title': '遍历顺序错误——循环嵌套方向或顺序反了',
                'error': '0-1背包中写成 for w in range(weights[i-1], W+1)（正序），这在空间优化（一维）中会导致同一物品被重复使用，变成完全背包。',
                'reason': '正序遍历容量时，dp[w-weight[i]]可能已经是"已经考虑了第i件物品"的状态，导致第i件物品被多次使用。逆序遍历保证每个物品只用一次。',
                'fix': '0-1背包一维优化必须逆序遍历容量：for w in range(W, weights[i-1]-1, -1)。完全背包才用正序。',
                'check': '用简单例子（所有物品重量和价值相同）验证——0-1背包的总价值应≤capacity，完全背包可以超过。',
            },
        ],
        'sort': [
            {
                'title': '快排pivot固定端点导致O(n²)退化',
                'error': '固定选首或尾元素作为pivot，在已排序数组上退化为O(n²)，递归深度=n，n=10000时可能超时或栈溢出。',
                'reason': '理想pivot应使左右子数组尽量均匀。固定端点pivot在有序数据上每次只排除一个元素。',
                'fix': '随机选一个元素与末尾交换作为pivot，或用三数取中法（比较arr[low], arr[mid], arr[high]选中间值）。',
                'check': '用已排序数组[1,2,...,1000]测试，确认运行时间在合理范围内。',
            },
            {
                'title': 'partition双指针的循环条件写错',
                'error': '内层while写成arr[i] <= pivot（含等号），导致全等数组[5,5,5,5]上指针无法移动，死循环。',
                'reason': 'partition的不变量是"严格小于的在左边，严格大于的在右边"，等于的可放任意一侧。含等号破坏了这一不变量。',
                'fix': '内层while使用<和>（不含等号）。外层while条件用i<=j（含等号）保证指针交错时正确退出。',
                'check': '用全等数组测试，确保不会无限循环。',
            },
            {
                'title': '排序稳定性误解——以为写了稳定代码就稳定',
                'error': '认为快速排序通过在partition中把相等的元素放在同侧就可以变稳定，实际上做不到——partition中的交换操作依然可能打乱相等元素的相对顺序。',
                'reason': '稳定性是指"相等元素的相对顺序在排序后保持不变"。涉及跨元素交换（swap两个不相邻的元素）的排序算法通常无法保持稳定性。',
                'fix': '快速排序本质上是基于"交换"的，无法保证稳定性。如果需要稳定且高效的排序，使用归并排序或TimSort（Python内置sorted的实现）。',
                'check': '用带标记的测试数据如[(5,"a"),(3,"b"),(5,"c")]验证：稳定的排序应保留两个5的先后顺序(a在c前)。',
            },
        ],
    }

    mistakes = mistake_sets.get(cat, [
        {
            'title': f'{topic} — 概念理解偏差',
            'error': f'对{topic}的核心定义理解不准确，导致实际应用时选错数据结构或算法。',
            'reason': '很多同学只记住了名词和大概思路，但没有真正理解底层原理和适用条件。',
            'fix': f'重新阅读{topic}的定义和经典应用场景，用手写方式推导一个完整的执行过程。',
            'check': f'能用一句话说清楚{topic}的适用条件和限制。',
        },
        {
            'title': f'{topic} — 边界条件处理不当',
            'error': '代码在正常输入下运行正确，但在空输入、单元素、重复元素等边界情况出错。',
            'reason': '写代码时只关注了"一般情况"，没有系统验证所有边界。',
            'fix': '列出所有边界情况清单（空、单、双、重复、最大、最小），逐一测试。',
            'check': '每个边界case都有对应的测试用例且全部通过。',
        },
        {
            'title': f'{topic} — 时间和空间代价估计不准',
            'error': f'使用{topic}时没有考虑数据规模，在小数据上正常的算法在大数据上严重超时或超内存。',
            'reason': '习惯在小数据集上测试，没有建立"数据规模→时间/空间需求"的直觉。',
            'fix': f'对每个使用{topic}的场景，预估n的范围并计算时间/空间需求。例如n=10⁵时O(n²)=10¹⁰≈100秒（不可接受），O(n log n)≈1.7×10⁶≈可接受。',
            'check': '在大数据集（n≥10000）上验证性能。',
        },
    ])

    sections = [
        {'kind': 'highlight', 'heading': f'{topic} — 高频易错点总结',
         'content': f'以下总结了{topic}在实际编程和面试中最常见的易错点。每个易错点包含：错误表现（现象）、错误原因（根因）、正确做法（修复方案）、检查方法（如何自测）。建议逐条对照检查自己的代码。'},
    ]

    for i, m in enumerate(mistakes, 1):
        sections.append({
            'kind': 'warning',
            'heading': f'易错点{i}：{m["title"]}',
            'content': (
                f'错误表现：{m["error"]}\n'
                f'错误原因：{m["reason"]}\n'
                f'正确做法：{m["fix"]}\n'
                f'检查方法：{m["check"]}'
            ),
        })

    sections.append({
        'kind': 'practice', 'heading': '自检练习',
        'content': '请对照以上易错点，检查你自己写的代码：',
        'items': [
            f'你的代码是否包含了上述易错点中的任何一项？',
            f'如果有，请按照"正确做法"修改代码并重新测试',
            f'如果全部避免了，尝试向同学解释"为什么这样写是对的"',
        ],
    })

    sections.append({
        'kind': 'answer', 'heading': '参考答案与自检指南',
        'content': (
            f'自检指南（按易错点逐项核对）：\n'
            f'1. 递归边界条件：检查每个递归函数的第一行是否有空指针/空列表的提前返回判断。如有，√。\n'
            f'2. 遍历顺序：确认前序/中序/后序的cout/print位置正确——前序在先，中序在中，后序在后。如有注释标注，更佳。\n'
            f'3. 状态恢复：检查所有修改可变对象（list/dict）的递归函数，在递归调用后是否有对应的撤销/恢复操作。如有，√。\n'
            f'4. BFS入队标记：检查BFS代码中visited标记是否在入队时（而非出队时）设置。如有，√。\n'
            f'5. DFS爆栈预防：如果数据规模可能很大，是否考虑了迭代版DFS或BFS作为替代方案。\n'
            f'6. DP状态定义：能否用一句话清晰描述dp[i]的含义？如果能，√。\n'
            f'7. DP初始化：是否明确设置了dp[0]/dp[1]等初始值，并理解为什么是这个值。如有，√。\n'
            f'8. 排序pivot选择：快排实现中是否使用了随机pivot或三数取中法，而非固定端点。如有，√。\n'
            f'自检结果：全部打√说明你对{topic}的理解已经比较扎实。有任何一项未通过，建议重点回顾对应的易错点并修改代码。'
        ),
    })

    return {
        'id': f'res-mistakes-{cat}-001',
        'title': f'{topic} — 易错点总结',
        'type': '易错点',
        'course': '数据结构与算法',
        'knowledge_point': topic,
        'difficulty': difficulty,
        'language': lang,
        'summary': f'总结{topic}的{len(mistakes)}个高频易错点，逐一分析错误原因并给出正确做法和自检方法，避免重复踩坑。',
        'knowledge_points': _build_knowledge_tags(cat, topic, '易错点', lang),
        'sections': sections,
    }


# ═══════════════════════════════════════════════════════════════════
# Type 5: 项目案例 — must have steps, code, evaluation
# ═══════════════════════════════════════════════════════════════════

def _has_project_steps(sections):
    """Check if project card has steps/task section and evaluation section by kind."""
    has_steps = _has_section_kind(sections, 'steps') or _has_section_kind(sections, 'task')
    has_eval = _has_section_kind(sections, 'evaluation')
    return has_steps and has_eval


def _build_project_card(gen_context):
    """Build a complete 项目案例 card."""
    topic = gen_context.get('topic', '')
    lang = gen_context.get('normalized_language', 'Python')
    difficulty = gen_context.get('difficulty', '入门')
    cat = _detect_topic_category(topic)

    projects = {
        'tree': {
            'background': '在编译器设计和表达式求值中，二叉树（特别是语法树/表达式树）是核心数据结构。例如计算器需要将中缀表达式"3+4*5"转换为表达式树并求值。本项目实现一个简单的表达式树求值器。',
            'ds': '二叉树（表达式树）：叶子节点存储操作数（数字），内部节点存储运算符（+, -, *, /）。通过后序遍历自底向上求值。',
            'goals': ['解析后缀表达式构建表达式树', '实现后序遍历递归求值', '支持 +, -, *, / 四种基本运算'],
            'steps': [
                '步骤1：定义表达式树节点结构——TreeNode包含val(操作数或运算符)、left和right指针。操作数是叶子节点（左右子为空），运算符是内部节点。',
                '步骤2：从后缀表达式构建树——读入后缀表达式（如"3 4 5 * +"），遇到操作数就创建叶子节点并入栈，遇到运算符就弹出两个节点作为右左子节点，创建新的运算符节点并入栈。最终栈顶节点即为表达式树的根。',
                '步骤3：实现后序遍历求值——如果节点是操作数（叶子），直接返回其数值；如果是运算符，先递归求值左子树，再递归求值右子树，然后根据运算符计算结果。',
                '步骤4：测试验证——用多组后缀表达式测试，验证求值结果的正确性，并对比中缀表达式的手动计算结果。',
            ],
            'code': (
                f'class TreeNode:\n'
                f'    def __init__(self, val, left=None, right=None):\n'
                f'        self.val = val\n'
                f'        self.left = left\n'
                f'        self.right = right\n\n'
                f'def build_tree(postfix):\n'
                f'    stack = []\n'
                f'    for token in postfix.split():\n'
                f'        if token in "+-*/":\n'
                f'            right = stack.pop()\n'
                f'            left = stack.pop()\n'
                f'            stack.append(TreeNode(token, left, right))\n'
                f'        else:\n'
                f'            stack.append(TreeNode(int(token)))\n'
                f'    return stack[0]\n\n'
                f'def evaluate(root):\n'
                f'    if root.left is None and root.right is None:\n'
                f'        return root.val\n'
                f'    l = evaluate(root.left)\n'
                f'    r = evaluate(root.right)\n'
                f'    if root.val == "+": return l + r\n'
                f'    if root.val == "-": return l - r\n'
                f'    if root.val == "*": return l * r\n'
                f'    if root.val == "/": return l / r\n'
                f'    return 0'
            ),
            'extensions': ['扩展1：支持中缀表达式输入（需要先转换为后缀表达式，即"中缀→后缀→建树→求值"完整流水线）', '扩展2：支持括号和运算优先级', '扩展3：支持更多运算符（如幂运算^、取模%）', '扩展4：增加图形化展示表达式树结构'],
            'evaluation': '评分标准：1.代码能否正确运行（40分）—所有测试用例通过；2.表达式树的构建逻辑是否正确（25分）—建树函数的正确性；3.后序遍历求值的实现是否正确（20分）—递归逻辑无误；4.边界处理（10分）—能处理除零、空表达式等异常情况；5.代码清晰度（5分）—合理命名和注释。',
        },
        'graph': {
            'background': '社交网络分析是现代应用的核心功能之一。"你可能认识的人"（朋友推荐）功能本质上是图上的二度邻居发现。本项目基于BFS实现一个简单的朋友推荐系统。',
            'ds': '图（邻接表）：每个用户是一个顶点，好友关系是无向边。二度邻居（朋友的朋友）是潜在的推荐对象。',
            'goals': ['构建用户-好友关系图（邻接表）', '用BFS发现某用户的二度邻居', '按共同好友数量排序推荐'],
            'steps': [
                '步骤1：定义图的数据结构——使用邻接表（dict of set）存储无向图，每个用户对应一个好友集合。',
                '步骤2：实现二度邻居发现——对目标用户做BFS两层：第一层是直接好友（距离1），第二层是好友的好友（距离2），排除自己和直接好友。',
                '步骤3：按共同好友数排序——对每个二度邻居，统计它与目标用户的共同好友数，按降序排列。共同好友越多，推荐优先级越高。',
                '步骤4：测试验证——构建一个包含10+用户的社交网络，验证推荐结果是否合理（人工判断推荐的相关性）。',
            ],
            'code': (
                f'from collections import deque, defaultdict\n\n'
                f'def recommend_friends(graph, user):\n'
                f'    """返回user的二度邻居推荐列表,按共同好友数降序"""\n'
                f'    # BFS层序遍历\n'
                f'    visited = {{user: 0}}  # user→distance\n'
                f'    q = deque([user])\n'
                f'    second_degree = []\n'
                f'    while q:\n'
                f'        v = q.popleft()\n'
                f'        for u in graph.get(v, set()):\n'
                f'            if u not in visited:\n'
                f'                visited[u] = visited[v] + 1\n'
                f'                if visited[u] == 2:\n'
                f'                    second_degree.append(u)\n'
                f'                elif visited[u] < 2:\n'
                f'                    q.append(u)\n'
                f'    # 按共同好友数排序\n'
                f'    uf = graph.get(user, set())\n'
                f'    scored = [(len(uf & graph.get(u, set())), u) for u in second_degree]\n'
                f'    scored.sort(reverse=True)\n'
                f'    return [u for _, u in scored]'
            ),
            'extensions': ['扩展1：支持双向推荐（A推荐B的同时，B也推荐A）', '扩展2：加入"已屏蔽"或"不是好友"功能', '扩展3：考虑好友关系的权重（如互动频率）', '扩展4：用图数据库（如Neo4j）实现大规模社交网络推荐'],
            'evaluation': '评分标准：1.代码正确性（40分）—BFS两层正确，不包含自己和直接好友；2.推荐排序合理性（25分）—共同好友多的优先推荐；3.算法效率（20分）—使用BFS而非DFS，时间复杂度O(V+E)；4.代码清晰度（10分）；5.扩展任务完成度（5分）。',
        },
        'dp': {
            'background': '在物流配送和路径规划中，"最短路径"或"最小成本"是核心问题。本项目使用动态规划实现一个简单的配送路径优化系统，在多个配送点之间规划最优路线。',
            'ds': '动态规划状态表（二维数组dp[i][mask]）：表示从第i个点出发、已访问集合为mask时的最小成本。本质是旅行商问题(TSP)的DP解法。',
            'goals': ['理解TSP问题的DP状态定义', '实现基于DP的路径优化算法', '输出最优路径和最小成本'],
            'steps': [
                '步骤1：问题建模——将配送点编号为0~n-1（0为起点/仓库），成本矩阵cost[i][j]表示从点i到点j的距离或时间。目标是找到从0出发、访问所有点恰好一次、回到0的最短路径。',
                '步骤2：状态定义——dp[mask][i] = 从起点0出发，已经访问了mask表示的集合（包含i），当前在点i时的最小成本。mask的第j位为1表示已经访问过点j。',
                '步骤3：状态转移——dp[mask][i] = min(dp[mask_without_i][j] + cost[j][i])，其中j是mask中除i外的某个点（前驱节点）。需要遍历所有可能的mask和最后访问节点i。',
                '步骤4：最终答案——min(dp[full_mask][i] + cost[i][0])，即访问完所有点后回到起点0的最小成本。',
            ],
            'code': (
                f'def tsp_dp(cost):\n'
                f'    n = len(cost)\n'
                f'    INF = float("inf")\n'
                f'    # dp[mask][i] = 从0出发, 访问mask中的点, 最后在i的最短路径\n'
                f'    SIZE = 1 << n\n'
                f'    dp = [[INF] * n for _ in range(SIZE)]\n'
                f'    dp[1][0] = 0  # 只访问起点0\n'
                f'    for mask in range(SIZE):\n'
                f'        for i in range(n):\n'
                f'            if not (mask >> i) & 1:\n'
                f'                continue\n'
                f'            if dp[mask][i] == INF:\n'
                f'                continue\n'
                f'            for j in range(n):\n'
                f'                if (mask >> j) & 1:\n'
                f'                    continue  # 已经访问过\n'
                f'                new_mask = mask | (1 << j)\n'
                f'                dp[new_mask][j] = min(\n'
                f'                    dp[new_mask][j],\n'
                f'                    dp[mask][i] + cost[i][j]\n'
                f'                )\n'
                f'    full = (1 << n) - 1\n'
                f'    ans = min(dp[full][i] + cost[i][0] for i in range(n))\n'
                f'    return ans'
            ),
            'extensions': ['扩展1：实现路径回溯——不仅输出最小成本，还输出具体访问顺序', '扩展2：支持时间窗口约束（某些点在特定时间后才能访问）', '扩展3：用启发式算法（如遗传算法/模拟退火）解决大规模TSP问题', '扩展4：可视化路径结果，在地图上展示配送路线'],
            'evaluation': '评分标准：1.DP状态定义正确（30分）—mask和最终节点的含义清晰；2.状态转移正确（30分）—min操作和cost累加无误；3.初始化和边界处理正确（20分）—dp[1][0]=0，INF处理；4.最终答案计算正确（15分）—包含回到起点的成本；5.代码可读性（5分）。',
        },
        'sort': {
            'background': '在大数据处理中，当数据量超过内存容量时需要使用外部排序（External Sort）。本项目实现一个基于归并排序思想的外部排序系统，理解"分治+归并"在处理大规模数据中的应用。',
            'ds': '多路归并（K-way Merge）使用最小堆（优先队列）高效合并多个有序子文件。核心数据结构：MinHeap。',
            'goals': ['理解外部排序的核心思想', '实现分块排序和多路归并', '分析外部排序的I/O复杂度'],
            'steps': [
                '步骤1：分块（Split Phase）——将大文件切分为多个能完全载入内存的小块（chunk），对每个chunk在内存中排序（使用快速排序或归并排序），将排序结果写回磁盘，形成多个有序子文件。',
                '步骤2：多路归并（Merge Phase）——使用最小堆（优先队列）同时从K个有序子文件中读取数据。堆中维护(当前最小值, 来源文件编号)，每次取堆顶（全局最小值）输出到最终文件，然后从该来源文件读取下一个元素补充入堆。',
                '步骤3：优化——增大chunk大小（减少文件数量）或增加归并路数K（减少归并趟数）来优化I/O性能。理想情况下只需要一趟归并。',
                '步骤4：测试验证——生成一个包含100万随机数的文件，分别用内存排序和外部排序处理，验证结果一致且外部排序在内存受限情况下仍能正常工作。',
            ],
            'code': (
                f'import heapq\n\n'
                f'def external_sort(input_file, output_file, chunk_size):\n'
                f'    # Phase 1: Split into sorted chunks\n'
                f'    chunk_files = []\n'
                f'    with open(input_file) as f:\n'
                f'        chunk = []\n'
                f'        for line in f:\n'
                f'            chunk.append(int(line))\n'
                f'            if len(chunk) >= chunk_size:\n'
                f'                chunk.sort()\n'
                f'                cf = f"chunk_{{len(chunk_files)}}.txt"\n'
                f'                with open(cf, "w") as cf_out:\n'
                f'                    for num in chunk:\n'
                f'                        cf_out.write(f"{{num}}\\n")\n'
                f'                chunk_files.append(cf)\n'
                f'                chunk = []\n'
                f'    # Phase 2: K-way merge\n'
                f'    files = [open(cf) for cf in chunk_files]\n'
                f'    heap = []\n'
                f'    for i, fh in enumerate(files):\n'
                f'        line = fh.readline()\n'
                f'        if line:\n'
                f'            heapq.heappush(heap, (int(line), i))\n'
                f'    with open(output_file, "w") as out:\n'
                f'        while heap:\n'
                f'            val, i = heapq.heappop(heap)\n'
                f'            out.write(f"{{val}}\\n")\n'
                f'            line = files[i].readline()\n'
                f'            if line:\n'
                f'                heapq.heappush(heap, (int(line), i))\n'
                f'    for fh in files:\n'
                f'        fh.close()'
            ),
            'extensions': ['扩展1：实现多趟归并——当chunk数量超过可用文件描述符时，需要多趟归并', '扩展2：支持对不同数据类型（字符串、浮点数）的外部排序', '扩展3：计算并对比不同chunk_size对I/O性能的影响', '扩展4：实现带缓冲的I/O以减少磁盘操作次数'],
            'evaluation': '评分标准：1.分块排序正确（30分）—每个chunk内部有序；2.多路归并正确（35分）—最终输出完全有序；3.内存控制（20分）—任何时候内存使用不超过chunk_size+堆大小；4.边界处理（10分）—处理文件末尾、空文件等；5.性能分析（5分）—I/O复杂度分析正确。',
        },
    }

    proj = projects.get(cat, {
        'background': f'本项目围绕{topic}设计一个完整的实战案例，将理论知识应用到具体的编程任务中。通过动手实现，加深对{topic}核心原理的理解。',
        'ds': f'{topic}相关的核心数据结构或算法。',
        'goals': ['理解需求和设计解决方案', '实现核心功能代码', '测试和验证结果', '完成扩展任务'],
        'steps': [
            f'步骤1：需求分析——明确项目的输入、输出和约束条件。确定使用{topic}的哪个具体知识点来解决。',
            f'步骤2：数据结构/算法设计——根据需求设计合适的数据结构和算法流程。画出流程图或伪代码。',
            f'步骤3：代码实现——用{lang}编写完整实现，确保代码可以编译/运行。',
            f'步骤4：测试验证——设计测试用例验证正确性，处理边界情况。',
        ],
        'code': f'# {topic} 项目核心代码框架\n# 请根据需求分析完成函数实现\n\ndef solve(input_data):\n    # TODO: 实现{topic}的核心逻辑\n    pass\n\nif __name__ == "__main__":\n    # TODO: 构建测试数据并调用solve\n    pass',
        'extensions': [f'扩展1：增加{topic}的一个变体实现', f'扩展2：优化时间或空间复杂度', f'扩展3：增加图形化或可视化展示', f'扩展4：写一份项目总结文档'],
        'evaluation': '评分标准：1.功能正确性（40分）—代码能正常运行且输出正确；2.数据结构/算法选择合理（25分）—选择最优方案并解释原因；3.代码质量（20分）—结构清晰、命名规范、有适当注释；4.扩展任务完成度（10分）；5.文档质量（5分）。',
    })

    return {
        'id': f'res-project-{cat}-001',
        'title': f'{topic} — 项目案例实战',
        'type': '项目案例',
        'course': '数据结构与算法',
        'knowledge_point': topic,
        'difficulty': difficulty,
        'language': lang,
        'summary': f'围绕{topic}设计完整项目案例，包含需求分析、实现步骤、核心代码和扩展任务，适合动手实践。',
        'knowledge_points': _build_knowledge_tags(cat, topic, '项目案例', lang),
        'sections': [
            {'kind': 'text', 'heading': '项目背景', 'content': proj['background']},
            {'kind': 'highlight', 'heading': '使用的数据结构或算法', 'content': proj['ds']},
            {'kind': 'task', 'heading': '功能目标', 'items': proj['goals']},
            {'kind': 'steps', 'heading': '实现步骤', 'steps': proj['steps']},
            {'kind': 'code', 'heading': '核心代码', 'language': lang, 'content': proj['code']},
            {'kind': 'design', 'heading': '扩展任务', 'content': '\n'.join(proj['extensions'])},
            {'kind': 'evaluation', 'heading': '评价标准', 'content': proj['evaluation']},
        ],
    }


# ═══════════════════════════════════════════════════════════════════
# Section Structure Enforcer — runs on EVERY card after gate
# ═══════════════════════════════════════════════════════════════════

def _enforce_section_structure(card, gen_context):
    """
    Ensure card sections contain all required kind types for its resource type.
    This runs on EVERY card (whether it passed the gate or was template-replaced)
    and fills in any missing section kinds.

    Unlike the gate check (which uses a binary pass/fail), this function
    surgically adds missing sections without replacing the entire card.
    """
    rtype = card.get('type', '')
    sections = card.get('sections', [])
    if not isinstance(sections, list):
        sections = []
    topic = gen_context.get('topic', '')
    lang = gen_context.get('normalized_language', 'Python')
    kinds = _get_section_kinds(sections)

    logger.info("Section enforcer: type=%r kinds=%s", rtype, kinds)

    # ── 图解讲解: ensure diagram, steps, example ──
    if rtype == '图解讲解':
        if not _has_section_kind(sections, 'diagram'):
            diagram_text = _build_diagram_for_topic(topic, gen_context)
            # Insert diagram after the first highlight/text section, or at position 1
            insert_at = 1
            for i, s in enumerate(sections):
                if s.get('kind') in ('highlight', 'text', 'heading'):
                    insert_at = i + 1
                    break
            sections.insert(insert_at, {
                'kind': 'diagram', 'heading': f'{topic} — 结构图解',
                'content': diagram_text
            })
            logger.info("Section enforcer: added missing 'diagram' section for 图解讲解")

        if not _has_section_kind(sections, 'steps') and not _has_section_kind(sections, 'example'):
            sections.append({
                'kind': 'steps', 'heading': '分步理解',
                'steps': [
                    f'步骤1：理解{topic}的核心数据结构和定义。',
                    f'步骤2：跟踪算法的执行流程，对照上述图解逐行理解。',
                    f'步骤3：关注边界条件——空输入、单元素、重复元素等情况。',
                    f'步骤4：在纸上手动画出执行过程，验证你的理解。',
                ]
            })
            logger.info("Section enforcer: added missing 'steps' section for 图解讲解")

        # Ensure every practice/task has a substantive answer
        ensure_practice_answer_pairs(sections, topic, gen_context)

    # ── 代码示例: ensure code, test_cases, complexity ──
    elif rtype == '代码示例':
        if not _has_section_kind(sections, 'test_cases'):
            sections.append({
                'kind': 'test_cases', 'heading': '测试用例',
                'content': (
                    f'测试1：基本功能测试——使用标准输入验证{topic}的输出是否正确。\n'
                    f'测试2：边界测试——空输入、单元素输入、两个元素输入。\n'
                    f'测试3：大规模数据测试——n=1000时检查运行时间和内存使用。\n'
                    f'测试4：特殊输入——包含重复值、已排序数据、反向排序数据。'
                )
            })
            logger.info("Section enforcer: added missing 'test_cases' section for 代码示例")

        if not _has_section_kind(sections, 'complexity'):
            sections.append({
                'kind': 'complexity', 'heading': '复杂度分析',
                'content': f'时间复杂度：O(n)（n为输入规模）。\n空间复杂度：O(1) 或 O(n)（取决于是否需要额外存储）。\n具体复杂度取决于算法的实现方式和数据特征，请在理解代码的基础上自行推导。'
            })
            logger.info("Section enforcer: added missing 'complexity' section for 代码示例")

        # Ensure every practice/task has a substantive answer
        ensure_practice_answer_pairs(sections, topic, gen_context)

    # ── 分层练习: ensure practice-answer pairing ──
    elif rtype == '分层练习':
        # Fix ALL practice-answer pairing (+ ensures minimum 5 practices)
        ensure_practice_answer_pairs(sections, topic, gen_context)
        logger.info("Section enforcer: ensured practice-answer pairs for 分层练习")

        if not _has_section_kind(sections, 'warnings') and not _has_section_kind(sections, 'checklist'):
            sections.append({
                'kind': 'warnings', 'heading': '自检清单',
                'content': (
                    f'1. 基础题全部通过了吗？如有不会的，回顾{topic}的基本定义。\n'
                    f'2. 进阶题是否独立完成？如果没有，建议重做一遍。\n'
                    f'3. 综合题能否清晰解释每一步的推导过程？\n'
                    f'4. 是否尝试过修改输入数据来测试算法的健壮性？'
                )
            })

    # ── 易错点: ensure practice has answer ──
    elif rtype == '易错点':
        ensure_practice_answer_pairs(sections, topic, gen_context)
        logger.info("Section enforcer: ensured practice-answer pairs for 易错点")

    # ── 项目案例: ensure evaluation + task answers ──
    elif rtype == '项目案例':
        ensure_practice_answer_pairs(sections, topic, gen_context)
        if not _has_section_kind(sections, 'evaluation'):
            sections.append({
                'kind': 'evaluation', 'heading': '评价标准',
                'content': (
                    f'评分标准：\n'
                    f'1. 功能正确性（40分）——代码能正常运行且输出正确。\n'
                    f'2. 数据结构/算法选择合理（25分）——选择最优方案并解释原因。\n'
                    f'3. 代码质量（20分）——结构清晰、命名规范、有适当注释。\n'
                    f'4. 扩展任务完成度（10分）。\n'
                    f'5. 文档质量（5分）。'
                )
            })
            logger.info("Section enforcer: added missing 'evaluation' section for 项目案例")

    card['sections'] = sections
    return card


def _build_diagram_for_topic(topic, gen_context):
    """Build a topic-specific, detailed ASCII text diagram.

    Keyword matching within each category produces truly relevant diagrams —
    no generic "输入→处理步骤1→处理步骤2→输出" templates.
    """
    t = (topic or '').lower()
    module = (gen_context.get('normalized_module', '') or '').lower()

    # ═══════════════════════════════════════════════════════════
    # 1. 递归调用栈 — call stack frame diagram
    # ═══════════════════════════════════════════════════════════
    if any(kw in t for kw in ['递归调用栈', '调用栈']) or ('递归' in t and '栈' in t):
        return (
            f'{topic} — 递归调用栈帧示意：\n'
            f'\n'
            f'栈顶 ↑\n'
            f'┌──────────────────────────────┐\n'
            f'│ preorder(node=D)             │\n'
            f'│ 输出 D，左右子树均为空        │\n'
            f'│ 执行完毕，即将弹出            │\n'
            f'├──────────────────────────────┤\n'
            f'│ preorder(node=B)             │\n'
            f'│ 已访问 B，已进入左子树 D      │\n'
            f'│ 等待 D 返回后处理右子树 E     │\n'
            f'├──────────────────────────────┤\n'
            f'│ preorder(node=A)             │\n'
            f'│ 已访问 A，已进入左子树 B      │\n'
            f'│ 等待 B 完全返回后处理右子树 C │\n'
            f'└──────────────────────────────┘\n'
            f'栈底 ↓\n'
            f'\n'
            f'调用与返回顺序：\n'
            f'  A 调用 B → B 调用 D → D 返回 B\n'
            f'  → B 调用 E → E 返回 B → B 返回 A\n'
            f'  → A 调用 C → C 返回 A → 遍历结束\n'
            f'\n'
            f'关键理解：\n'
            f'  每一次递归调用都在栈上创建一个新的栈帧，\n'
            f'  保存该层函数的局部变量和返回地址。\n'
            f'  当递归到达终止条件（如叶子节点），\n'
            f'  栈帧依次弹出，逐层返回结果。'
        )

    # ═══════════════════════════════════════════════════════════
    # 2. 二叉树 + 具体遍历方式
    # ═══════════════════════════════════════════════════════════
    if any(kw in t for kw in ['二叉树', '树遍历', '前序', '中序', '后序', '层序', 'bst', '二叉搜索树']):
        # Determine which traversal to highlight
        if '前序' in t or 'preorder' in t:
            traversal_highlight = (
                f'\n前序遍历（根→左→右）：A → B → D → E → C\n'
                f'\n'
                f'遍历过程拆解：\n'
                f'  ① 访问根节点 A\n'
                f'       ↓\n'
                f'  ② 递归遍历左子树 B → D → E\n'
                f'       ↓\n'
                f'  ③ 递归遍历右子树 C\n'
                f'\n'
                f'递归栈帧变化：\n'
                f'  push(A) → 输出A → push(B) → 输出B → push(D)\n'
                f'  → 输出D → pop(D) → push(E) → 输出E → pop(E)\n'
                f'  → pop(B) → push(C) → 输出C → pop(C) → pop(A)'
            )
        elif '中序' in t or 'inorder' in t:
            traversal_highlight = (
                f'\n中序遍历（左→根→右）：D → B → E → A → C\n'
                f'\n'
                f'遍历过程拆解：\n'
                f'  ① 递归遍历左子树到底，访问 D\n'
                f'       ↓\n'
                f'  ② 回溯到 B，访问 B，然后递归右子树访问 E\n'
                f'       ↓\n'
                f'  ③ 回溯到 A，访问 A，然后递归右子树访问 C\n'
                f'\n'
                f'重要性质：对二叉搜索树（BST）做中序遍历，\n'
                f'得到的结果是严格升序序列！这是 BST 最核心的性质。'
            )
        elif '后序' in t or 'postorder' in t:
            traversal_highlight = (
                f'\n后序遍历（左→右→根）：D → E → B → C → A\n'
                f'\n'
                f'遍历过程拆解：\n'
                f'  ① 递归遍历左子树到底，访问 D、E\n'
                f'       ↓\n'
                f'  ② 访问 B（左右子树均已访问完）\n'
                f'       ↓\n'
                f'  ③ 递归遍历右子树，访问 C\n'
                f'       ↓\n'
                f'  ④ 最后访问根节点 A\n'
                f'\n'
                f'典型应用：删除整棵树（先删子节点再删根节点），\n'
                f'计算目录大小（先算子目录大小再算父目录）。'
            )
        elif '层序' in t or 'levelorder' in t or '层' in t:
            traversal_highlight = (
                f'\n层序遍历（逐层从左到右）：A → B → C → D → E\n'
                f'\n'
                f'使用队列辅助：\n'
                f'  初始队列：[A]\n'
                f'  出队A，入队B、C → 队列：[B, C]\n'
                f'  出队B，入队D、E → 队列：[C, D, E]\n'
                f'  出队C → 队列：[D, E]\n'
                f'  出队D → 队列：[E]\n'
                f'  出队E → 队列：[ ] → 结束'
            )
        else:
            traversal_highlight = (
                f'\n前序遍历：A → B → D → E → C\n'
                f'中序遍历：D → B → E → A → C\n'
                f'后序遍历：D → E → B → C → A\n'
                f'层序遍历：A → B → C → D → E'
            )

        return (
            f'{topic} — 二叉树结构图与遍历顺序：\n'
            f'\n'
            f'示例二叉树：\n'
            f'\n'
            f'            A\n'
            f'          /   \\\n'
            f'         B     C\n'
            f'        / \\\n'
            f'       D   E\n'
            f'\n'
            f'节点信息：\n'
            f'  A：根节点，度为 2（拥有左右孩子 B、C）\n'
            f'  B：内部节点，度为 2（拥有左右孩子 D、E）\n'
            f'  C：内部节点，度为 0（叶子节点）\n'
            f'  D：叶子节点，度为 0\n'
            f'  E：叶子节点，度为 0\n'
            f'{traversal_highlight}'
        )

    # ═══════════════════════════════════════════════════════════
    # 3. Dijkstra / 最短路径
    # ═══════════════════════════════════════════════════════════
    if any(kw in t for kw in ['dijkstra', '最短路径', '最短距离', '最短路']):
        return (
            f'{topic} — Dijkstra 最短路径求解过程：\n'
            f'\n'
            f'带权图：\n'
            f'\n'
            f'         A ──2── B\n'
            f'         │        │\\\n'
            f'         4        1  3\n'
            f'         │        │   \\\n'
            f'         C ──2── E    D\n'
            f'          \\        \\  /\n'
            f'           5        3/\n'
            f'            \\      /\n'
            f'             F ───\n'
            f'\n'
            f'以 A 为起点，求 A 到各节点的最短路径：\n'
            f'\n'
            f'初始距离表：\n'
            f'  A=0, B=∞, C=∞, D=∞, E=∞, F=∞\n'
            f'\n'
            f'第1步 — 访问 A（当前最短=0）：\n'
            f'  松弛 A→B：min(∞, 0+2)=2  → 更新 B=2\n'
            f'  松弛 A→C：min(∞, 0+4)=4  → 更新 C=4\n'
            f'  距离表：A=0✓, B=2, C=4, D=∞, E=∞, F=∞\n'
            f'\n'
            f'第2步 — 访问 B（当前最短=2）：\n'
            f'  松弛 B→E：min(∞, 2+1)=3  → 更新 E=3\n'
            f'  松弛 B→D：min(∞, 2+3)=5  → 更新 D=5\n'
            f'  距离表：A=0✓, B=2✓, C=4, D=5, E=3, F=∞\n'
            f'\n'
            f'第3步 — 访问 E（当前最短=3）：\n'
            f'  松弛 E→C：min(4, 3+2)=4  → C 不变\n'
            f'  松弛 E→D：min(5, 3+3)=5  → D 不变\n'
            f'  距离表：A=0✓, B=2✓, C=4, D=5, E=3✓, F=∞\n'
            f'\n'
            f'第4步 — 访问 C（当前最短=4）：\n'
            f'  松弛 C→F：min(∞, 4+5)=9  → 更新 F=9\n'
            f'  距离表：A=0✓, B=2✓, C=4✓, D=5, E=3✓, F=9\n'
            f'\n'
            f'最终结果：\n'
            f'  A→A = 0    A→B = 2 (A→B)\n'
            f'  A→C = 4 (A→C)    A→D = 5 (A→B→D)\n'
            f'  A→E = 3 (A→B→E)    A→F = 9 (A→C→F)\n'
            f'\n'
            f'核心思想总结：\n'
            f'  1. 每次选择距离起点最近的未访问节点\n'
            f'  2. 通过该节点松弛其所有邻居的距离\n'
            f'  3. 使用优先队列（最小堆）优化选择过程\n'
            f'  4. 时间复杂度：O((V+E)·logV)（堆优化版）'
        )

    # ═══════════════════════════════════════════════════════════
    # 4. BFS / DFS / 图遍历
    # ═══════════════════════════════════════════════════════════
    if any(kw in t for kw in ['bfs', 'dfs', '广度', '深度', '图遍历']):
        is_bfs = 'bfs' in t or '广度' in t
        return (
            f'{topic} — {"BFS（广度优先搜索）" if is_bfs else "DFS（深度优先搜索）"}遍历过程：\n'
            f'\n'
            f'图结构：\n'
            f'\n'
            f'    A ──── B ──── D\n'
            f'    │      │\n'
            f'    │      │\n'
            f'    C ──── E\n'
            f'\n'
            f'邻接关系：\n'
            f'  A: [B, C]    B: [A, D, E]\n'
            f'  C: [A, E]    D: [B]\n'
            f'  E: [B, C]\n'
            f'\n'
            f'{_bfs_diagram_detail() if is_bfs else _dfs_diagram_detail()}'
        )

    # ═══════════════════════════════════════════════════════════
    # 5. 动态规划 / 背包问题
    # ═══════════════════════════════════════════════════════════
    if any(kw in t for kw in ['动态规划', 'dp', '背包', '0-1', '状态转移']):
        return _build_dp_knapsack_diagram(topic)

    # ═══════════════════════════════════════════════════════════
    # 6. 队列
    # ═══════════════════════════════════════════════════════════
    if any(kw in t for kw in ['队列', 'queue']):
        if '循环' in t:
            return (
                f'{topic} — 循环队列操作示意：\n'
                f'\n'
                f'循环队列（capacity=5）：\n'
                f'\n'
                f'下标：   0      1      2      3      4\n'
                f'      ┌──────┬──────┬──────┬──────┬──────┐\n'
                f'元素： │  10  │  20  │  30  │      │      │\n'
                f'      └──────┴──────┴──────┴──────┴──────┘\n'
                f'         ↑                    ↑\n'
                f'       front                rear\n'
                f'\n'
                f'当前状态：\n'
                f'  front = 0（指向队首元素 10）\n'
                f'  rear  = 3（指向下一个可插入位置）\n'
                f'  元素个数 = (rear - front + capacity) % capacity = 3\n'
                f'\n'
                f'入队(enqueue)操作：\n'
                f'  arr[rear] = 新元素\n'
                f'  rear = (rear + 1) % capacity\n'
                f'\n'
                f'出队(dequeue)操作：\n'
                f'  取出元素 = arr[front]\n'
                f'  front = (front + 1) % capacity\n'
                f'\n'
                f'判空：front == rear\n'
                f'判满：(rear + 1) % capacity == front\n'
                f'（为区分空/满，实际容量只用了 capacity-1 个位置）'
            )
        return (
            f'{topic} — 队列操作示意（FIFO 先进先出）：\n'
            f'\n'
            f'队尾(rear) ←─────── 队首(front)\n'
            f'   入队方向             出队方向\n'
            f'\n'
            f'操作序列：\n'
            f'  初始状态：[]\n'
            f'  enqueue(10)： 入队 ← [10]              (front=0, rear=1)\n'
            f'  enqueue(20)： 入队 ← [10, 20]          (front=0, rear=2)\n'
            f'  enqueue(30)： 入队 ← [10, 20, 30]      (front=0, rear=3)\n'
            f'  dequeue()：   [20, 30] → 返回 10        (front=1, rear=3)\n'
            f'  enqueue(40)： 入队 ← [20, 30, 40]      (front=1, rear=4)\n'
            f'  dequeue()：   [30, 40] → 返回 20        (front=2, rear=4)\n'
            f'\n'
            f'关键特性：\n'
            f'  - 先进入队列的元素先被取出（FIFO）\n'
            f'  - 入队发生在队尾，出队发生在队首\n'
            f'  - 时间复杂度：入队 O(1)、出队 O(1)'
        )

    # ═══════════════════════════════════════════════════════════
    # 7. 栈
    # ═══════════════════════════════════════════════════════════
    if any(kw in t for kw in ['栈', 'stack']):
        return (
            f'{topic} — 栈操作示意（LIFO 后进先出）：\n'
            f'\n'
            f'栈顶 ↑（入栈/出栈均在此端）\n'
            f'┌──────┐\n'
            f'│  30  │ ← top（最后入栈，最先出栈）\n'
            f'├──────┤\n'
            f'│  20  │\n'
            f'├──────┤\n'
            f'│  10  │ ← bottom（最先入栈，最后出栈）\n'
            f'└──────┘\n'
            f'栈底 ↓\n'
            f'\n'
            f'操作序列演示：\n'
            f'  push(10)：栈=[10]，top 指向 10\n'
            f'  push(20)：栈=[10, 20]，top 指向 20\n'
            f'  push(30)：栈=[10, 20, 30]，top 指向 30\n'
            f'  pop()：   返回 30，top 回退到 20\n'
            f'  pop()：   返回 20，top 回退到 10\n'
            f'\n'
            f'典型应用场景：\n'
            f'  - 函数调用栈：保存返回地址和局部变量\n'
            f'  - 括号匹配：( [ {{ 依次入栈，遇到 ) ] }} 时出栈比对\n'
            f'  - 表达式求值：操作数入栈，遇到运算符时弹出计算\n'
            f'  - DFS 非递归实现：用栈替代系统调用栈\n'
            f'\n'
            f'时间复杂度：push O(1)、pop O(1)、peek O(1)'
        )

    # ═══════════════════════════════════════════════════════════
    # 8. 排序
    # ═══════════════════════════════════════════════════════════
    if any(kw in t for kw in ['排序', 'sort', '快速', '归并', '冒泡']):
        return _build_sort_diagram(topic)

    # ═══════════════════════════════════════════════════════════
    # 9. 哈希
    # ═══════════════════════════════════════════════════════════
    if any(kw in t for kw in ['哈希', '散列', 'hash']):
        return (
            f'{topic} — 哈希表结构与冲突处理：\n'
            f'\n'
            f'哈希表（size=7，使用除留余数法 hash(key) = key % 7）：\n'
            f'\n'
            f'索引      存储内容\n'
            f'┌─────┬──────────────────────┐\n'
            f'│  0  │ (空)                  │\n'
            f'│  1  │ key=8  → key=15        │  ← 冲突！链地址法连接\n'
            f'│  2  │ key=9                  │\n'
            f'│  3  │ key=10                 │\n'
            f'│  4  │ (空)                  │\n'
            f'│  5  │ key=12                 │\n'
            f'│  6  │ (空)                  │\n'
            f'└─────┴──────────────────────┘\n'
            f'\n'
            f'插入过程说明：\n'
            f'  插入 key=8  → hash(8)=1，桶 [1] 为空，直接放入\n'
            f'  插入 key=15 → hash(15)=1，桶 [1] 已被 key=8 占用！\n'
            f'                 采用链地址法：key=15 链接到 key=8 之后\n'
            f'\n'
            f'查找过程：\n'
            f'  key → hash(key) → 定位桶索引 → 遍历链表 → 比较 key → 返回值\n'
            f'\n'
            f'冲突处理方法对比：\n'
            f'  链地址法：每个桶存链表，冲突元素挂在链表尾部\n'
            f'  开放定址法：冲突时找下一个空桶（线性探测/平方探测）\n'
            f'  再哈希法：使用第二个哈希函数重新计算位置\n'
            f'\n'
            f'时间复杂度（平均）：查询 O(1)、插入 O(1)、删除 O(1)'
        )

    # ═══════════════════════════════════════════════════════════
    # 10. 链表
    # ═══════════════════════════════════════════════════════════
    if any(kw in t for kw in ['链表', 'linked']):
        return (
            f'{topic} — 链表结构与基本操作：\n'
            f'\n'
            f'单链表结构：\n'
            f'\n'
            f'  head → [3|next] → [7|next] → [2|next] → [5|null]\n'
            f'          节点1        节点2        节点3        节点4\n'
            f'\n'
            f'节点定义：\n'
            f'  每个节点包含两个部分：\n'
            f'    data：存储的实际数据（如 3, 7, 2, 5）\n'
            f'    next：指向下一个节点的指针（最后一个指向 null）\n'
            f'\n'
            f'插入操作（在节点2之后插入值9）：\n'
            f'  ① 创建新节点 newNode(9)\n'
            f'  ② newNode.next = 节点2.next（即节点3）\n'
            f'  ③ 节点2.next = newNode\n'
            f'  结果：[3]→[7]→[9]→[2]→[5]\n'
            f'\n'
            f'删除操作（删除值为2的节点）：\n'
            f'  ① 找到值为2的节点的前驱节点（值为7的节点）\n'
            f'  ② 前驱.next = 被删节点.next（即值为5的节点）\n'
            f'  结果：[3]→[7]→[5]\n'
            f'\n'
            f'时间复杂度：查找 O(n)、插入 O(1)*、删除 O(1)*\n'
            f'  *假设已定位到操作位置'
        )

    # ═══════════════════════════════════════════════════════════
    # 11. 二分查找
    # ═══════════════════════════════════════════════════════════
    if any(kw in t for kw in ['二分', 'binary search']):
        return (
            f'{topic} — 二分查找执行过程（在有序数组中查找 7）：\n'
            f'\n'
            f'有序数组：\n'
            f'  索引:  0   1   2   3   4   5   6   7\n'
            f'  值：  [1,  3,  5,  7,  9, 11, 13, 15]\n'
            f'\n'
            f'第1轮：\n'
            f'  left=0, right=7, mid=⌊(0+7)/2⌋=3\n'
            f'  arr[3]=7 == target=7 → 找到了！返回索引 3\n'
            f'\n'
            f'若查找 target=4（不存在的值）：\n'
            f'第1轮：left=0, right=7, mid=3, arr[3]=7 > 4 → right=2\n'
            f'第2轮：left=0, right=2, mid=1, arr[1]=3 < 4 → left=2\n'
            f'第3轮：left=2, right=2, mid=2, arr[2]=5 > 4 → right=1\n'
            f'终止：left=2 > right=1 → 查找失败，target 不存在\n'
            f'\n'
            f'核心要点：\n'
            f'  - 前提条件：数组必须有序（升序或降序）\n'
            f'  - 每次比较将搜索范围减半\n'
            f'  - 时间复杂度：O(log₂ n)\n'
            f'  - 空间复杂度：迭代版 O(1)，递归版 O(log n)（调用栈）'
        )

    # ═══════════════════════════════════════════════════════════
    # 12. 线性表 / 数组
    # ═══════════════════════════════════════════════════════════
    if any(kw in t for kw in ['线性', '数组']):
        return (
            f'{topic} — 线性表（顺序表）结构与操作：\n'
            f'\n'
            f'存储示意（内存中连续存放）：\n'
            f'\n'
            f'  地址：  0x100  0x104  0x108  0x10C  0x110\n'
            f'        ┌──────┬──────┬──────┬──────┬──────┐\n'
            f'  值：  │  10  │  20  │  30  │  40  │  50  │\n'
            f'        └──────┴──────┴──────┴──────┴──────┘\n'
            f'  索引：    0      1      2      3      4\n'
            f'\n'
            f'随机访问：arr[2] → 30（O(1) 时间直接定位）\n'
            f'\n'
            f'插入操作（在索引2位置插入值25）：\n'
            f'  原始：[10, 20, 30, 40, 50]\n'
            f'  步骤1：从尾部开始，30~50 整体右移一位\n'
            f'         [10, 20, __, 30, 40, 50]\n'
            f'  步骤2：在空位赋值\n'
            f'         [10, 20, 25, 30, 40, 50]\n'
            f'  时间复杂度：O(n)（最坏情况需要移动n个元素）\n'
            f'\n'
            f'删除操作（删除索引2的元素）：\n'
            f'  原始：[10, 20, 30, 40, 50]\n'
            f'  步骤1：40~50 整体左移一位\n'
            f'         [10, 20, 40, 50, __]\n'
            f'  时间复杂度：O(n)\n'
            f'\n'
            f'对比链表的优势与劣势：\n'
            f'  优势：随机访问 O(1)、缓存友好\n'
            f'  劣势：插入/删除 O(n)、需要连续内存'
        )

    # ═══════════════════════════════════════════════════════════
    # 13. 通用兜底 — 知识点结构关系图（不是输入→处理步骤！）
    # ═══════════════════════════════════════════════════════════
    return (
        f'{topic} — 知识点结构关系：\n'
        f'\n'
        f'概念定义\n'
        f'   ↓\n'
        f'核心操作\n'
        f'   ↓\n'
        f'边界情况\n'
        f'   ↓\n'
        f'复杂度分析\n'
        f'   ↓\n'
        f'典型题型\n'
        f'\n'
        f'学习建议：\n'
        f'  1. 先理解数据结构或算法的定义和核心思想\n'
        f'  2. 通过简单的示例数据手动画出执行过程\n'
        f'  3. 关注边界条件——空输入、单元素、重复元素\n'
        f'  4. 分析时间复杂度和空间复杂度\n'
        f'  5. 通过典型题目巩固理解'
    )


# ── Diagram detail helpers ──

def _bfs_diagram_detail():
    return (
        f'BFS 遍历过程（使用队列，从 A 出发）：\n'
        f'\n'
        f'初始队列：[A]（标记A已访问）\n'
        f'\n'
        f'队列变化过程：\n'
        f'  出队 A，访问 A：\n'
        f'    A 的邻居 B、C 未访问 → 入队 B、C\n'
        f'    队列：[B, C]\n'
        f'    \n'
        f'  出队 B，访问 B：\n'
        f'    B 的邻居 A（已访问跳过）D、E 未访问 → 入队 D、E\n'
        f'    队列：[C, D, E]\n'
        f'    \n'
        f'  出队 C，访问 C：\n'
        f'    C 的邻居 A（已访问跳过）E（已访问跳过）\n'
        f'    队列：[D, E]\n'
        f'    \n'
        f'  出队 D，访问 D：\n'
        f'    D 的邻居 B（已访问跳过）\n'
        f'    队列：[E]\n'
        f'    \n'
        f'  出队 E，访问 E：\n'
        f'    E 的邻居 B、C（均已访问跳过）\n'
        f'    队列：[] → 遍历结束\n'
        f'\n'
        f'BFS 遍历顺序：A → B → C → D → E\n'
        f'\n'
        f'关键特性：\n'
        f'  - 按"层"逐层遍历，先访问距离起点近的节点\n'
        f'  - 使用队列（FIFO）保证先入队的先被处理\n'
        f'  - 适合求无权图的最短路径\n'
        f'  - 时间复杂度：O(V+E)，空间复杂度：O(V)'
    )

def _dfs_diagram_detail():
    return (
        f'DFS 遍历过程（使用递归/栈，从 A 出发）：\n'
        f'\n'
        f'递归调用栈变化：\n'
        f'\n'
        f'  push A → 访问 A：\n'
        f'    A 的邻居 B 未访问 → 递归进入 B\n'
        f'    栈：[A]\n'
        f'    \n'
        f'  push B → 访问 B：\n'
        f'    B 的邻居 A（已访问）D 未访问 → 递归进入 D\n'
        f'    栈：[A, B]\n'
        f'    \n'
        f'  push D → 访问 D：\n'
        f'    D 的邻居 B（已访问），无其他未访问邻居\n'
        f'    → 回溯，pop D\n'
        f'    栈：[A, B]\n'
        f'    \n'
        f'  B 继续检查邻居 E 未访问 → 递归进入 E：\n'
        f'  push E → 访问 E：\n'
        f'    E 的邻居 B（已访问）C 未访问 → 递归进入 C\n'
        f'    栈：[A, B, E]\n'
        f'    \n'
        f'  push C → 访问 C：\n'
        f'    C 的邻居 A、E（均已访问）→ 回溯，pop C\n'
        f'    栈：[A, B, E]\n'
        f'    \n'
        f'  E 无更多未访问邻居 → pop E\n'
        f'  B 无更多未访问邻居 → pop B\n'
        f'  A 无更多未访问邻居 → pop A → 遍历结束\n'
        f'\n'
        f'DFS 遍历顺序：A → B → D → E → C\n'
        f'\n'
        f'关键特性：\n'
        f'  - 沿一条路径深入到底，再回溯探索其他分支\n'
        f'  - 使用栈（LIFO）：递归隐式栈 或 显式Stack\n'
        f'  - 适合检测连通分量、拓扑排序、找桥/割点\n'
        f'  - 时间复杂度：O(V+E)，空间复杂度：O(V)'
    )

def _build_dp_knapsack_diagram(topic):
    """Build a detailed 0-1 knapsack DP table diagram."""
    return (
        f'{topic} — 0-1 背包问题动态规划求解：\n'
        f'\n'
        f'问题描述：\n'
        f'  背包容量 W = 5\n'
        f'  物品列表：\n'
        f'    物品1：重量=2, 价值=3\n'
        f'    物品2：重量=3, 价值=4\n'
        f'    物品3：重量=4, 价值=5\n'
        f'\n'
        f'DP 状态定义：\n'
        f'  dp[i][w] = 考虑前 i 个物品，背包容量为 w 时的最大价值\n'
        f'\n'
        f'DP 表格（行=物品编号，列=容量）：\n'
        f'\n'
        f'           w=0   1    2    3    4    5\n'
        f'        ┌────┬────┬────┬────┬────┬────┐\n'
        f'  无物品│  0 │  0 │  0 │  0 │  0 │  0 │\n'
        f'        ├────┼────┼────┼────┼────┼────┤\n'
        f'  物品1 │  0 │  0 │  3 │  3 │  3 │  3 │  (wt=2,val=3)\n'
        f'        ├────┼────┼────┼────┼────┼────┤\n'
        f'  物品2 │  0 │  0 │  3 │  4 │  4 │  7 │  (wt=3,val=4)\n'
        f'        ├────┼────┼────┼────┼────┼────┤\n'
        f'  物品3 │  0 │  0 │  3 │  4 │  5 │  7 │  (wt=4,val=5)\n'
        f'        └────┴────┴────┴────┴────┴────┘\n'
        f'\n'
        f'状态转移方程：\n'
        f'  dp[i][w] = max(\n'
        f'      dp[i-1][w],                        // 不选第i个物品\n'
        f'      dp[i-1][w-wt[i]] + val[i]          // 选择第i个物品\n'
        f'  )   ↑ 前提：w >= wt[i]\n'
        f'\n'
        f'关键推导（以 dp[2][5] = 7 为例）：\n'
        f'  不选物品2：dp[1][5] = 3\n'
        f'  选择物品2：dp[1][5-3] + 4 = dp[1][2] + 4 = 3 + 4 = 7 ← 更大！\n'
        f'  所以 dp[2][5] = max(3, 7) = 7\n'
        f'\n'
        f'回溯得到最优方案：\n'
        f'  dp[3][5]=7, dp[2][5]=7 → 物品3未选\n'
        f'  dp[2][5]=7, dp[1][5]=3 → 物品2选了\n'
        f'  dp[1][2]=3, dp[0][2]=0 → 物品1选了\n'
        f'  最优方案：选物品1 + 物品2，总价值=7，总重量=5\n'
        f'\n'
        f'时间复杂度：O(nW)，空间复杂度：O(nW) 可优化为 O(W)'
    )

def _build_sort_diagram(topic):
    """Build a detailed sorting process diagram."""
    t = (topic or '').lower()
    if '快速' in t or 'quick' in t:
        return (
            f'{topic} — 快速排序划分过程：\n'
            f'\n'
            f'原始数组：[6, 3, 8, 2, 5]\n'
            f'\n'
            f'选择 pivot = 5（以最右元素为基准）\n'
            f'\n'
            f'划分过程（Lomuto 分区方案）：\n'
            f'  i = -1（指向小于 pivot 的区域末尾）\n'
            f'  j = 0: arr[0]=6 > 5 → 不交换\n'
            f'  j = 1: arr[1]=3 < 5 → i=0, swap(arr[0], arr[1])\n'
            f'          数组变为 [3, 6, 8, 2, 5]\n'
            f'  j = 2: arr[2]=8 > 5 → 不交换\n'
            f'  j = 3: arr[3]=2 < 5 → i=1, swap(arr[1], arr[3])\n'
            f'          数组变为 [3, 2, 8, 6, 5]\n'
            f'  最后：swap(arr[i+1]=arr[2], pivot)\n'
            f'          数组变为 [3, 2, 5, 8, 6]\n'
            f'\n'
            f'划分结果：\n'
            f'  小于 pivot：[3, 2]\n'
            f'  pivot：      [5]  ← 位于最终正确位置（索引2）\n'
            f'  大于 pivot：[8, 6]\n'
            f'\n'
            f'递归处理：\n'
            f'  左半 [3, 2] → 排序得 [2, 3]\n'
            f'  右半 [8, 6] → 排序得 [6, 8]\n'
            f'  合并：  [2, 3] + [5] + [6, 8] = [2, 3, 5, 6, 8]\n'
            f'\n'
            f'时间复杂度：平均 O(n·log n)，最坏 O(n²)（已有序时）\n'
            f'空间复杂度：O(log n)（递归调用栈深度）'
        )
    if '归并' in t or 'merge' in t:
        return (
            f'{topic} — 归并排序分治过程：\n'
            f'\n'
            f'原始数组：[6, 3, 8, 2, 5, 1, 7, 4]\n'
            f'\n'
            f'拆分阶段（divide）：\n'
            f'  [6,3,8,2,5,1,7,4]\n'
            f'  → [6,3,8,2]  +  [5,1,7,4]\n'
            f'  → [6,3] [8,2]  +  [5,1] [7,4]\n'
            f'  → [6] [3] [8] [2] [5] [1] [7] [4]  ← 全部拆到单元素\n'
            f'\n'
            f'合并阶段（merge）：\n'
            f'  [6] + [3] → [3, 6]\n'
            f'  [8] + [2] → [2, 8]\n'
            f'  [3,6] + [2,8] → [2, 3, 6, 8]  ← 双指针归并\n'
            f'  [5] + [1] → [1, 5]\n'
            f'  [7] + [4] → [4, 7]\n'
            f'  [1,5] + [4,7] → [1, 4, 5, 7]\n'
            f'  [2,3,6,8] + [1,4,5,7] → [1, 2, 3, 4, 5, 6, 7, 8] ✓\n'
            f'\n'
            f'时间复杂度：始终 O(n·log n)\n'
            f'空间复杂度：O(n)（需要临时数组存放合并结果）\n'
            f'特点：稳定排序，适合链表等非连续存储结构'
        )
    if '冒泡' in t or 'bubble' in t:
        return (
            f'{topic} — 冒泡排序过程：\n'
            f'\n'
            f'原始数组：[5, 3, 8, 2, 1]\n'
            f'\n'
            f'第1轮（比较4次）：\n'
            f'  5>3 → swap → [3, 5, 8, 2, 1]\n'
            f'  5<8 → 不动 → [3, 5, 8, 2, 1]\n'
            f'  8>2 → swap → [3, 5, 2, 8, 1]\n'
            f'  8>1 → swap → [3, 5, 2, 1, 8]  ← 最大值8就位\n'
            f'\n'
            f'第2轮（比较3次）：\n'
            f'  3<5 → 不动 → [3, 5, 2, 1, 8]\n'
            f'  5>2 → swap → [3, 2, 5, 1, 8]\n'
            f'  5>1 → swap → [3, 2, 1, 5, 8]  ← 5就位\n'
            f'\n'
            f'最终结果：[1, 2, 3, 5, 8]\n'
            f'\n'
            f'时间复杂度：O(n²)，空间复杂度：O(1)\n'
            f'特点：稳定排序，每轮将当前最大元素"浮"到末尾'
        )
    # generic sort
    return (
        f'{topic} — 排序算法执行过程：\n'
        f'\n'
        f'原始数组：[6, 3, 8, 2, 5]\n'
        f'\n'
        f'排序过程：\n'
        f'  [6, 3, 8, 2, 5]  原始无序序列\n'
        f'       ↓ 比较与交换\n'
        f'  [3, 6, 8, 2, 5]  第1步：前两个元素有序\n'
        f'       ↓ 继续处理\n'
        f'  [3, 6, 2, 8, 5]  第2步：较大元素后移\n'
        f'       ↓ 继续处理\n'
        f'  [3, 2, 6, 5, 8]  第3步：最大值归位\n'
        f'       ↓ 继续处理\n'
        f'  [2, 3, 5, 6, 8]  第4步：全部有序 ✓\n'
        f'\n'
        f'核心思想：\n'
        f'  通过多次比较和交换，将无序序列变成有序序列。\n'
        f'  不同的排序算法在比较策略和交换方式上各有特点，\n'
        f'  适用于不同的数据规模和分布特征。'
    )


def _insert_answer_after_practice(sections, topic):
    """Insert answer sections after any practice section that lacks one.

    DEPRECATED: use ensure_practice_answer_pairs() instead.
    This function retained for backward compatibility — delegates to the new one.
    """
    gen_context = {'topic': topic}
    return ensure_practice_answer_pairs(sections, topic, gen_context)


def ensure_practice_answer_pairs(sections, topic, gen_context=None):
    """Ensure every practice/task section is followed by a MATCHED answer section.

    KEY CHANGE: No longer inserts generic answers. If a practice has no matching
    answer, or if the practice-answer pair fails alignment validation, BOTH the
    practice AND answer are replaced with a matched pair from the deterministic
    exercise builder (same data in question and answer).

    For 分层练习 with mismatched pairs, ALL practice-answer sections are
    completely rebuilt from deterministic paired templates.

    Returns the modified sections list (mutates in place).
    """
    if gen_context is None:
        gen_context = {}
    rtype = gen_context.get('resource_type', '')
    lang = gen_context.get('normalized_language', 'C++')
    cat = _detect_topic_category(topic)

    # ── Step 1: Scan for unpaired or misaligned practices ──
    practices_without_answers = []
    misaligned_pairs = []
    for i, s in enumerate(sections):
        if s.get('kind') in ('practice', 'task'):
            has_answer = (i + 1 < len(sections) and sections[i + 1].get('kind') == 'answer')
            if not has_answer:
                practices_without_answers.append(i)
            else:
                # Check alignment
                p_content = s.get('content', '') or ''
                a_content = sections[i + 1].get('content', '') or ''
                # Simple alignment check — skip if called from resource_service (no circular import)
                try:
                    from services.resource_service import validate_layered_practice_sections
                    result = validate_layered_practice_sections(sections, topic)
                    if not result['valid']:
                        # Find which specific pairs are misaligned
                        for err in result['errors']:
                            # Extract index from error messages like 'Practice "..." (idx N)'
                            import re as _re
                            m = _re.search(r'\(idx (\d+)\)', err)
                            if m:
                                idx = int(m.group(1))
                                if idx not in misaligned_pairs and idx in [pi for pi, _ in enumerate(sections) if sections[pi].get('kind') in ('practice', 'task')]:
                                    misaligned_pairs.append(idx)
                except Exception:
                    pass

    needs_patching = practices_without_answers or misaligned_pairs

    if not needs_patching:
        return sections

    # ── Step 2: For 分层练习 with mismatches, rebuild entirely ──
    if rtype == '分层练习' and misaligned_pairs:
        try:
            from services.resource_service import build_layered_exercise_pairs
            pairs = build_layered_exercise_pairs(topic, '', lang, rtype)
            # Remove all existing practice/answer sections, keep non-practice sections
            keep_sections = [s for s in sections if s.get('kind') not in ('practice', 'task', 'answer')]
            new_sections = []
            for s in keep_sections:
                new_sections.append(s)
                # Insert paired Q&A right after the highlight/warnings etc
            # Better: rebuild with highlight first, then pairs, then warnings/check_criteria
            result = []
            # Separate metadata from practice/answer
            before = []
            after = []
            seen_first_practice = False
            for s in keep_sections:
                if not seen_first_practice:
                    before.append(s)
                else:
                    after.append(s)
            # Reconstruct
            result.extend(before)
            for pair in pairs:
                result.append({
                    'kind': 'practice',
                    'heading': pair['level'] + '题',
                    'content': pair['question'],
                })
                result.append({
                    'kind': 'answer',
                    'heading': pair['level'] + '题 — 参考答案与解析',
                    'content': pair['answer'],
                })
            result.extend(after)
            sections.clear()
            sections.extend(result)
            return sections
        except Exception:
            pass

    # ── Step 3: For individual unpaired practices (non-分层练习), use matched pairs ──
    if practices_without_answers:
        try:
            from services.resource_service import build_layered_exercise_pairs
            pairs = build_layered_exercise_pairs(topic, '', lang, rtype)
            new_sections = []
            pair_idx = 0
            for i, s in enumerate(sections):
                new_sections.append(s)
                if s.get('kind') in ('practice', 'task') and i in practices_without_answers:
                    if pair_idx < len(pairs):
                        pair = pairs[pair_idx]
                        pair_idx += 1
                        new_sections.append({
                            'kind': 'answer',
                            'heading': f'{s.get("heading", "练习")} — 参考答案与解析',
                            'content': pair['answer'],
                        })
            sections.clear()
            sections.extend(new_sections)
            return sections
        except Exception:
            pass

    # ── Step 4: Legacy fallback (should rarely be reached) ──
    # If deferred import failed, use KB-based answers as last resort
    new_sections = []
    for i, s in enumerate(sections):
        new_sections.append(s)
        if s.get('kind') in ('practice', 'task'):
            if i + 1 < len(sections) and sections[i + 1].get('kind') == 'answer':
                continue
            practice_heading = s.get('heading', '')
            practice_content = s.get('content', '')
            answer = _build_topic_specific_answer(topic, cat, lang, practice_heading, practice_content)
            answer = _validate_answer_quality(answer, topic, cat)
            new_sections.append(answer)

    # Validate existing answers
    for i, s in enumerate(new_sections):
        if s.get('kind') == 'answer':
            new_sections[i] = _validate_answer_quality(s, topic, cat)

    # For 分层练习, fill missing practices from templates
    if rtype == '分层练习':
        current_practices = _extract_practice_sections(new_sections)
        if len(current_practices) < 5:
            new_sections = _fill_missing_practices(new_sections, topic, cat, lang, current_practices)
            for i, s in enumerate(new_sections):
                if s.get('kind') == 'answer':
                    new_sections[i] = _validate_answer_quality(s, topic, cat)

    sections.clear()
    sections.extend(new_sections)
    return sections


# ═══════════════════════════════════════════════════════════════════
# Topic-specific answer builder
# ═══════════════════════════════════════════════════════════════════

# Knowledge base: category → [practice_heading_snippet, answer_content]
# Every answer must contain these 4 sections with concrete, verifiable content.
# "最终答案" is the mandatory quality marker — no answer is valid without it.
_ANSWER_KB = {
    'tree': {
        '遍历': (
            f'最终答案：\n'
            f'前序遍历：A → B → D → E → C\n'
            f'中序遍历：D → B → E → A → C\n'
            f'后序遍历：D → E → B → C → A\n'
            f'层序遍历：A → B → C → D → E\n\n'
            f'解题步骤：\n'
            f'1. 画出给定的二叉树结构（根A，左子B、右子C，B的左子D、右子E）。\n'
            f'2. 前序（根左右）：先写A→递归左子树B→D→E→递归右子树C → 得到 A B D E C。\n'
            f'3. 中序（左根右）：递归左子树到底(D)→B→E→根A→右子树C → 得到 D B E A C。\n'
            f'4. 后序（左右根）：递归左子树(D→E→B)→右子树(C)→根A → 得到 D E B C A。\n'
            f'5. 层序（队列）：A入队→出A入BC→出B入DE→出C→出D→出E → 得到 A B C D E。\n\n'
            f'解析：\n'
            f'二叉树遍历的本质是"何时访问根节点"。前序是先根后子，中序是左子→根→右子，后序是先子后根，层序是逐层从左到右。递归实现用系统调用栈，非递归前/中/后序需要显式栈，层序需要队列。\n\n'
            f'易错提醒：\n'
            f'- 不要把中序和排序混为一谈（只有BST的中序才是升序）\n'
            f'- 非递归前序入栈顺序是"先右后左"（因为栈是LIFO）\n'
            f'- 层序必须用队列，不能用栈（顺序会不同）\n'
            f'- 递归终止条件是 root==nullptr，忘记会导致无限递归'
        ),
        '结构': (
            f'最终答案：\n'
            f'重建的二叉树：\n'
            f'        1\n'
            f'      /   \\\n'
            f'     2     3\n'
            f'    / \\\n'
            f'   4   5\n\n'
            f'解题步骤：\n'
            f'1. 前序[1,2,4,5,3]的第一个元素1是根节点。\n'
            f'2. 在中序[4,2,5,1,3]中找到1，左边[4,2,5]是左子树（3个节点），右边[3]是右子树（1个节点）。\n'
            f'3. 左子树：前序取接下来的3个[2,4,5]，中序取[4,2,5]→根为2，中序中2左边[4]是左子，右边[5]是右子。\n'
            f'4. 右子树：前序取[3]，中序取[3]→只有一个节点3。\n\n'
            f'解析：\n'
            f'前序+中序可以唯一确定一棵二叉树（前提：没有重复值）。核心是"前序定根，中序分左右"。用哈希表存储中序中每个值的索引可将查找时间从O(n)降到O(1)。\n\n'
            f'易错提醒：\n'
            f'- 仅前序和后序无法唯一确定二叉树\n'
            f'- 递归时左右子树的切分长度必须一致\n'
            f'- BST的中序遍历是升序序列，前序+后序可唯一确定BST结构'
        ),
        '实现': (
            f'最终答案（C++ 前序遍历代码）：\n'
            f'void preorder(TreeNode* root) {{\n'
            f'    if (root == nullptr) return;\n'
            f'    cout << root->val << " ";  // 访问根\n'
            f'    preorder(root->left);       // 左子树\n'
            f'    preorder(root->right);      // 右子树\n'
            f'}}\n\n'
            f'非递归实现（显式栈）：\n'
            f'void preorderIter(TreeNode* root) {{\n'
            f'    if (!root) return;\n'
            f'    stack<TreeNode*> st;\n'
            f'    st.push(root);\n'
            f'    while (!st.empty()) {{\n'
            f'        TreeNode* node = st.top(); st.pop();\n'
            f'        cout << node->val << " ";\n'
            f'        if (node->right) st.push(node->right);  // 先右\n'
            f'        if (node->left) st.push(node->left);     // 后左\n'
            f'    }}\n'
            f'}}\n\n'
            f'解题步骤：\n'
            f'1. 判断根是否为空，为空则直接返回。\n'
            f'2. 先访问当前节点（打印或存储值）。\n'
            f'3. 递归遍历左子树。\n'
            f'4. 递归遍历右子树。\n\n'
            f'解析：\n'
            f'递归版核心是理解"递"和"归"：递是沿着左子树向下深入，归是到达叶子后回溯。非递归版用栈模拟系统调用栈——先压右子再压左子，保证左子先出栈（栈是LIFO）。\n\n'
            f'易错提醒：\n'
            f'- 非递归版入栈顺序是"先右后左"，不是先左后右！\n'
            f'- 忘记判空会导致空指针访问\n'
            f'- 递归深度过大可能栈溢出（最坏O(n)），可改用迭代+栈'
        ),
    },
    'graph': {
        'BFS': (
            f'最终答案：\n'
            f'BFS遍历顺序：A → B → C → D → E → F\n\n'
            f'解题步骤：\n'
            f'1. 初始化：visited数组全为false，队列为空。\n'
            f'2. 起点A入队，标记visited[A]=true。\n'
            f'3. 出队A并输出，将A的邻居B、C入队并标记visited。队列=[B, C]\n'
            f'4. 出队B并输出，将B的邻居D、E入队并标记。队列=[C, D, E]\n'
            f'5. 出队C并输出，将C的邻居F入队并标记。队列=[D, E, F]\n'
            f'6. 出队D、E、F并输出，队列为空，遍历结束。\n\n'
            f'解析：\n'
            f'BFS使用队列(FIFO)保证"先访问距离起点近的节点"。同层节点在更深层节点之前被访问，因此BFS天然适合求无权图的最短路径。入队时标记visited，而非出队时标记，可避免重复入队。\n\n'
            f'易错提醒：\n'
            f'- visited必须在入队时标记，否则同一节点可能被重复入队\n'
            f'- 无权图最短路径用BFS；加权图最短路径用Dijkstra\n'
            f'- BFS的队列不能用栈替代（会变成DFS）'
        ),
        'DFS': (
            f'最终答案：\n'
            f'DFS遍历顺序：A → B → D → E → C → F\n\n'
            f'解题步骤：\n'
            f'1. 从A出发，标记visited[A]=true，输出A。\n'
            f'2. A的邻居B未访问，递归进入B，输出B。\n'
            f'3. B的邻居D未访问，递归进入D，输出D。\n'
            f'4. D无未访问邻居，回溯到B。B的邻居E未访问，递归进入E，输出E。\n'
            f'5. E无未访问邻居，回溯到B，B无更多邻居，回溯到A。\n'
            f'6. A的邻居C未访问，递归进入C，输出C。\n'
            f'7. C的邻居F未访问，递归进入F，输出F。遍历结束。\n\n'
            f'解析：\n'
            f'DFS沿一条路径"深入到底"再回溯。递归实现利用函数调用栈自动保存回溯点；非递归实现需显式栈。DFS适合检测连通分量、拓扑排序、寻找割点和桥。\n\n'
            f'易错提醒：\n'
            f'- 递归版DFS注意终止条件，否则可能栈溢出\n'
            f'- 非递归版入栈后要在出栈时标记visited（与BFS不同！）\n'
            f'- DFS不保证找到的是最短路径（BFS才保证）\n'
            f'- 有向图检测环用DFS三色标记法'
        ),
        '最短路径': (
            f'最终答案：\n'
            f'无权图从A到F的最短距离=2，最短路径=A→C→F（或A→B→E，取决于实现）。\n\n'
            f'解题步骤：\n'
            f'1. BFS从起点A开始，dist[A]=0。\n'
            f'2. 处理A：邻居B的dist=1，邻居C的dist=1，parent[B]=A, parent[C]=A。\n'
            f'3. 处理B：邻居D的dist=2, E的dist=2。\n'
            f'4. 处理C：邻居F的dist=2，parent[F]=C。\n'
            f'5. 首次访问F时dist=2就是最短距离。回溯parent：F←C←A。\n\n'
            f'解析：\n'
            f'无权图的最短路径=最少边数，BFS按层遍历保证首次访问的距离就是最短距离。加权图+Dijkstra：每次选dist最小节点松弛邻居。\n\n'
            f'易错提醒：\n'
            f'- BFS只能求无权图最短路径（边权相等）\n'
            f'- Dijkstra要求所有边权非负\n'
            f'- 记录parent数组才能回溯出具体路径，不只是距离'
        ),
    },
    'dp': {
        '背包': (
            f'最终答案：\n'
            f'最大总价值 = 7\n'
            f'选择的物品：1号物品（重量2，价值3）+ 2号物品（重量3，价值4）\n'
            f'总重量 = 5（未超过容量5）\n\n'
            f'解题步骤：\n'
            f'1. 定义dp[i][w] = 考虑前i个物品、容量为w时的最大价值。\n'
            f'2. 初始化：dp[0][all w]=0（没有物品时价值为0）。\n'
            f'3. 物品1(wt=2,val=3)：dp[1][2..5]=3。\n'
            f'4. 物品2(wt=3,val=4)：对w≥3，比较不选(dp[1][w])和选(dp[1][w-3]+4)。w=5时dp[1][5]=3 vs dp[1][2]+4=3+4=7→取7。\n'
            f'5. 物品3(wt=4,val=5)：w=5时dp[2][5]=7 vs dp[2][1]+5=5→7更大。不选物品3。\n'
            f'6. 回溯：dp[3][5]=7, dp[2][5]=7→物品3未选；dp[2][5]≠dp[1][5]→物品2选了(剩余容量2)；dp[1][2]=3≠0→物品1选了。\n\n'
            f'解析：\n'
            f'"0-1"表示每个物品只能选0次或1次。状态转移的核心决策是：第i个物品选还是不选。选的前提是剩余容量 ≥ 物品重量。\n\n'
            f'易错提醒：\n'
            f'- 一维DP优化时必须从后向前遍历(防止物品被重复使用)\n'
            f'- 初始化的dp[0][0..W]应全为0（不是-∞）\n'
            f'- 与完全背包的区别：0-1背包每个物品只能选一次\n'
            f'- 回溯时从右下角开始，比较dp[i][w]与dp[i-1][w]判断是否选了物品i'
        ),
        'LIS': (
            f'最终答案：\n'
            f'给定数组 [10, 9, 2, 5, 3, 7, 101, 18]\n'
            f'最长严格递增子序列 = [2, 3, 7, 101] 或 [2, 5, 7, 101]，长度 = 4\n\n'
            f'解题步骤：\n'
            f'1. dp[i] = 以nums[i]结尾的最长递增子序列长度，初始全为1。\n'
            f'2. i=0(10): dp[0]=1。\n'
            f'3. i=1(9): j=0, 9<10跳过, dp[1]=1。\n'
            f'4. i=2(2): 均大于, dp[2]=1。\n'
            f'5. i=3(5): j=2, nums[2]=2<5, dp[3]=dp[2]+1=2。\n'
            f'6. i=4(3): j=2, 2<3, dp[4]=dp[2]+1=2。\n'
            f'7. i=5(7): j=3, 5<7, dp[5]=dp[3]+1=3; j=4, 3<7, dp[5]=max(3,dp[4]+1)=3。\n'
            f'8. i=6(101): dp[6]=max(dp[j]+1)=4。\n'
            f'9. i=7(18): dp[7]=4。答案 = max(dp) = 4。\n\n'
            f'解析：\n'
            f'O(n²)解法：对每个位置i，扫描前面所有位置j，若nums[j]<nums[i]则可接在dp[j]之后。O(n log n)优化：贪心+二分查找维护tails数组。\n\n'
            f'易错提醒：\n'
            f'- dp[i]表示"以nums[i]结尾"，不是"前i个的LIS"，最终答案是max(dp)，不是dp[n-1]\n'
            f'- 严递增要求nums[j]<nums[i]（不能等于）\n'
            f'- 输出子序列内容需要额外记录predecessor数组'
        ),
        'LCS': (
            f'最终答案：\n'
            f'给定 text1="abcde", text2="ace"\n'
            f'LCS = "ace"，长度 = 3\n\n'
            f'解题步骤：\n'
            f'1. 构建dp[m+1][n+1]表格。m=5, n=3。\n'
            f'2. dp[1][1]: a==a → dp[1][1]=dp[0][0]+1=1。\n'
            f'3. dp[2][1]: b≠a → max(dp[1][1]=1, dp[2][0]=0)=1。\n'
            f'4. dp[3][1]: c≠a → max(dp[2][1]=1, dp[3][0]=0)=1。\n'
            f'5. dp[3][2]: c==c → dp[2][1]+1=2。\n'
            f'6. dp[5][3]: e==e → dp[4][2]+1=3。\n'
            f'7. 回溯：dp[5][3]=3←dp[4][2]+1(字符e), dp[4][2]=2←dp[3][1]+1(字符c), dp[3][1]=1←dp[0][0]+1(字符a) → LCS="ace"。\n\n'
            f'解析：\n'
            f'LCS是经典的二维DP。dp[i][j]表示text1前i个字符和text2前j个字符的LCS长度。当两个字符相等时，可以从dp[i-1][j-1]+1转移；不相等时取max(dp[i-1][j], dp[i][j-1])。\n\n'
            f'易错提醒：\n'
            f'- dp下标从1开始，字符比较时用i-1和j-1\n'
            f'- 回溯时"斜向移动"表示该字符属于LCS\n'
            f'- LCS不同于"最长公共子串"（子串要求连续）'
        ),
    },
    'sort': {
        '排序': (
            f'最终答案：\n'
            f'给定数组 [6, 3, 8, 2, 5]\n'
            f'冒泡排序后：[2, 3, 5, 6, 8]\n'
            f'快速排序后：[2, 3, 5, 6, 8]\n'
            f'归并排序后：[2, 3, 5, 6, 8]\n\n'
            f'解题步骤（以快速排序为例，pivot=5）：\n'
            f'1. 原始数组：[6, 3, 8, 2, 5]。选最右元素5为pivot。\n'
            f'2. 划分：≤5的放左边 → [3, 2]；5放中间；>5的放右边 → [6, 8]。\n'
            f'3. 当前数组：[3, 2, 5, 6, 8]，5已在正确位置(索引2)。\n'
            f'4. 递归排序左半[3, 2]（选2为pivot→[2, 3]）。\n'
            f'5. 递归排序右半[6, 8]（选8为pivot→[6, 8]）。\n'
            f'6. 合并结果：[2, 3, 5, 6, 8]。\n\n'
            f'解析：\n'
            f'不同排序算法各有适用场景。快速排序平均O(n log n)且常数因子小，实践中通常最快；归并排序稳定且最坏也是O(n log n)，适合链表和外部排序；冒泡/选择/插入O(n²)仅适合小数据或特定场景。\n\n'
            f'易错提醒：\n'
            f'- 快排最坏情况O(n²)出现在"每次选到最小/最大元素作为pivot"\n'
            f'- 归并排序需要O(n)额外空间\n'
            f'- 稳定性：相等元素的相对顺序是否保持不变'
        ),
        '快排': (
            f'最终答案：\n'
            f'输入数组：[6, 3, 8, 2, 5]，pivot=5\n'
            f'一次划分后：[3, 2, 5, 6, 8]\n'
            f'pivot最终位置：索引2\n'
            f'完成排序后：[2, 3, 5, 6, 8]\n\n'
            f'解题步骤：\n'
            f'1. 选最右元素5为pivot。设i=-1（小于pivot区域的末尾）。\n'
            f'2. j=0: arr[0]=6>5 → 不交换。\n'
            f'3. j=1: arr[1]=3≤5 → i=0, swap(arr[0],arr[1]) → [3,6,8,2,5]。\n'
            f'4. j=2: arr[2]=8>5 → 不交换。\n'
            f'5. j=3: arr[3]=2≤5 → i=1, swap(arr[1],arr[3]) → [3,2,8,6,5]。\n'
            f'6. 循环结束，swap(arr[i+1]=arr[2], pivot) → [3,2,5,6,8]。\n'
            f'7. 返回i+1=2（pivot的最终索引）。\n'
            f'8. 递归排序arr[0..1]和arr[3..4]。\n\n'
            f'解析：\n'
            f'Lomuto划分的核心是维护一个"小于等于pivot"的区域，用指针i标记该区域的末尾。每遇到一个≤pivot的元素，就扩大该区域并把新元素交换进来。\n\n'
            f'易错提醒：\n'
            f'- 固定选最右元素为pivot在已排序数组上退化为O(n²)，推荐随机选pivot\n'
            f'- 划分时i从-1开始，不是0\n'
            f'- 最终swap不能忘记，否则pivot不在正确位置'
        ),
        '归并': (
            f'最终答案：\n'
            f'输入数组：[6, 3, 8, 2, 5]\n'
            f'归并排序后：[2, 3, 5, 6, 8]\n'
            f'合并过程：\n'
            f'  [6]与[3]→[3,6]；[8]与[2]→[2,8]；[5]保持不变\n'
            f'  [3,6]与[2,8]→[2,3,6,8]；与[5]→[2,3,5,6,8]\n\n'
            f'解题步骤：\n'
            f'1. 拆分：[6,3,8,2,5]→[6,3][8,2,5]→[6][3][8][2,5]→[6][3][8][2][5]。\n'
            f'2. 合并[6][3]→比较：3<6，结果=[3,6]。\n'
            f'3. 合并[8][2]→比较：2<8，结果=[2,8]。\n'
            f'4. 合并[3,6][2,8]→双指针：p1=0(3),p2=0(2)→2<3取2→p2=1(8)→3<8取3→p1=1(6)→6<8取6→取8→[2,3,6,8]。\n'
            f'5. 合并[2,3,6,8][5]→[2,3,5,6,8]。\n\n'
            f'解析：\n'
            f'归并排序=分治法。divide：O(log n)层递归拆分。merge：每层O(n)合并。总O(n log n)。需要O(n)临时数组。\n\n'
            f'易错提醒：\n'
            f'- 合并时需要临时数组，不能原地完成\n'
            f'- 双指针合并时要处理剩余元素（一侧耗尽后直接复制另一侧剩余）\n'
            f'- 归并排序是稳定的（相等时优先取左半元素）'
        ),
    },
    'stack': {
        '栈': (
            f'最终答案：\n'
            f'操作序列：push(10), push(20), push(30), pop(), pop()\n'
            f'pop()输出：30, 20（后进先出）\n'
            f'最终栈内元素：[10]（仅剩最早入栈的元素）\n\n'
            f'解题步骤：\n'
            f'1. push(10)：栈=[10]，栈顶=10。\n'
            f'2. push(20)：栈=[10,20]，栈顶=20。\n'
            f'3. push(30)：栈=[10,20,30]，栈顶=30。\n'
            f'4. pop()：弹出栈顶30并返回，栈=[10,20]，栈顶=20。\n'
            f'5. pop()：弹出栈顶20并返回，栈=[10]，栈顶=10。\n\n'
            f'解析：\n'
            f'栈遵循LIFO（后进先出）原则。最后压入的元素最先被弹出。栈可以用数组（维护top指针）或链表（头插法）实现，所有操作O(1)。\n\n'
            f'易错提醒：\n'
            f'- pop前必须检查栈是否为空（否则下溢）\n'
            f'- 数组实现的栈需要处理容量不足的情况\n'
            f'- C++ STL中stack::pop()不返回值，需要先top()再pop()'
        ),
    },
    'queue': {
        '队列': (
            f'最终答案：\n'
            f'操作序列：enqueue(10), enqueue(20), enqueue(30), dequeue(), dequeue()\n'
            f'dequeue()输出：10, 20（先进先出）\n'
            f'最终队列内元素：[30]（仅剩最后入队的元素）\n\n'
            f'解题步骤：\n'
            f'1. enqueue(10)：队首=10，队尾=10，队列=[10]。\n'
            f'2. enqueue(20)：队首=10，队尾=20，队列=[10,20]。\n'
            f'3. enqueue(30)：队首=10，队尾=30，队列=[10,20,30]。\n'
            f'4. dequeue()：取出队首10并返回，队首移到20，队列=[20,30]。\n'
            f'5. dequeue()：取出队首20并返回，队首移到30，队列=[30]。\n\n'
            f'解析：\n'
            f'队列遵循FIFO（先进先出）原则。最早入队的元素最先被取出。循环队列用数组+取模实现，需牺牲一个位置区分空和满。\n\n'
            f'易错提醒：\n'
            f'- dequeue前需检查队列是否为空\n'
            f'- 循环队列判空：front==rear；判满：(rear+1)%capacity==front\n'
            f'- 不要混淆队列(FIFO)和栈(LIFO)的操作顺序'
        ),
    },
    'hash': {
        '哈希': (
            f'最终答案：\n'
            f'哈希函数 hash(key) = key % 5\n'
            f'插入序列：10, 15, 7, 12\n'
            f'最终桶分布：\n'
            f'  index 0: 10 → 15（冲突！15%5=0，链地址法解决）\n'
            f'  index 1: 空\n'
            f'  index 2: 7 → 12（冲突！12%5=2）\n'
            f'  index 3: 空\n'
            f'  index 4: 空\n\n'
            f'解题步骤：\n'
            f'1. 插入10：hash(10)=10%5=0，桶[0]为空→直接放入。\n'
            f'2. 插入15：hash(15)=15%5=0，桶[0]已被10占用→冲突！使用链地址法，15挂在10之后。\n'
            f'3. 插入7：hash(7)=7%5=2，桶[2]为空→直接放入。\n'
            f'4. 插入12：hash(12)=12%5=2，桶[2]已被7占用→冲突！12挂在7之后。\n\n'
            f'解析：\n'
            f'哈希冲突是不可避免的（鸽巢原理），关键是冲突后的处理策略。链地址法最直观（桶变链表）；开放定址法找下一个空桶（线性探测/平方探测）。负载因子>0.75时建议扩容。\n\n'
            f'易错提醒：\n'
            f'- 两个不同key的hash值相同一定冲突\n'
            f'- 查找时也要处理冲突：先定位桶再沿链表比较key\n'
            f'- 扩容(rehashing)时所有key需重新计算位置'
        ),
    },
    'recursion': {
        '递归': (
            f'最终答案：\n'
            f'以计算阶乘 factorial(5) 为例：\n'
            f'factorial(5) = 5 × 4 × 3 × 2 × 1 = 120\n\n'
            f'解题步骤（递归调用展开）：\n'
            f'1. factorial(5) = 5 × factorial(4)，等待factorial(4)返回。\n'
            f'2. factorial(4) = 4 × factorial(3)，等待factorial(3)返回。\n'
            f'3. factorial(3) = 3 × factorial(2)，等待factorial(2)返回。\n'
            f'4. factorial(2) = 2 × factorial(1)，等待factorial(1)返回。\n'
            f'5. factorial(1) = 1（终止条件/base case），开始返回。\n'
            f'6. 回溯：factorial(2)=2×1=2, factorial(3)=3×2=6, factorial(4)=4×6=24, factorial(5)=5×24=120。\n\n'
            f'解析：\n'
            f'递归=函数调用自身。三要素：①终止条件(base case)防止无限递归；②递推关系缩小问题规模；③合并子问题结果。每次递归调用在栈上分配新栈帧。\n\n'
            f'易错提醒：\n'
            f'- 终止条件必不可少，且必须可达（否则栈溢出）\n'
            f'- 递归深度过大时考虑改用迭代或尾递归优化\n'
            f'- 递归的时间复杂度分析使用递推公式T(n)=aT(n/b)+f(n)'
        ),
    },
    'linked_list': {
        '链表': (
            f'最终答案：\n'
            f'给定单链表 head→[3]→[7]→[2]→[5]→null\n'
            f'在节点7后插入值9：head→[3]→[7]→[9]→[2]→[5]→null\n'
            f'删除值为2的节点：head→[3]→[7]→[9]→[5]→null\n\n'
            f'解题步骤：\n'
            f'1. 遍历找到值为7的节点（curr指向它）。\n'
            f'2. 插入9：newNode.next = curr.next（指向[2]）；curr.next = newNode（指向[9]）。\n'
            f'3. 删除2：找到2的前驱节点（值为9）。前驱.next = 被删节点.next（即[5]）。\n\n'
            f'解析：\n'
            f'链表的插入和删除只需修改指针，O(1)时间（已知位置）。查找需要O(n)。链表不需要连续内存，可动态扩展。哑节点(dummy node)简化对头节点的操作。\n\n'
            f'易错提醒：\n'
            f'- 插入时先设newNode.next再设curr.next，顺序不能反\n'
            f'- 删除时需找到前驱节点，不是当前节点本身\n'
            f'- 头节点操作需特殊处理（或用哑节点统一）\n'
            f'- 链表的递归操作可能导致栈溢出（长链表）'
        ),
    },
    'binary_search': {
        '二分': (
            f'最终答案：\n'
            f'在有序数组 [1, 3, 5, 7, 9, 11, 13, 15] 中查找 target=7：\n'
            f'找到！索引 = 3，比较次数 = 1\n'
            f'查找 target=4：未找到（-1），比较次数 = 3\n\n'
            f'解题步骤（查找4）：\n'
            f'1. left=0, right=7, mid=3, arr[3]=7 > 4 → right=mid-1=2。\n'
            f'2. left=0, right=2, mid=1, arr[1]=3 < 4 → left=mid+1=2。\n'
            f'3. left=2, right=2, mid=2, arr[2]=5 > 4 → right=mid-1=1。\n'
            f'4. left=2 > right=1 → 循环结束，返回-1（未找到）。\n\n'
            f'解析：\n'
            f'二分查找每次将搜索范围减半，时间复杂度O(log n)。前提：数组必须有序。mid用left+(right-left)/2防止整数溢出。\n\n'
            f'易错提醒：\n'
            f'- 循环条件是 left <= right（有等号），否则单元素数组可能漏检\n'
            f'- mid用(left+right)/2可能溢出，推荐left+(right-left)/2\n'
            f'- 变体：找第一个/最后一个等于target的位置需特判'
        ),
    },
    'linear': {
        '线性': (
            f'最终答案：\n'
            f'数组 [10, 20, 30, 40, 50]\n'
            f'在索引2处插入25：[10, 20, 25, 30, 40, 50]，移动了3个元素\n'
            f'删除索引2的元素：[10, 20, 40, 50]，移动了2个元素\n\n'
            f'解题步骤：\n'
            f'插入：①从最后一个元素开始，将索引2及之后的元素全部右移一位；②在索引2位置写入25；③长度+1。\n'
            f'删除：①将索引3及之后的元素全部左移一位；②长度-1。\n'
            f'随机访问arr[2]：直接通过基地址+2×元素大小得到地址，O(1)。\n\n'
            f'解析：\n'
            f'线性表(顺序表)用连续内存存储。优势：随机访问O(1)、缓存友好。劣势：插入删除O(n)、需预留空间。动态数组在容量不足时按2倍扩容，均摊时间O(1)。\n\n'
            f'易错提醒：\n'
            f'- 插入时从后向前移动（否则会覆盖未移动的数据）\n'
            f'- 删除时从前向后移动\n'
            f'- 扩容后旧数组需要释放内存（C/C++需手动free/delete）'
        ),
    },
}


def _make_fallback_answer(topic, cat, lang):
    """Build a fallback answer with the 4-section structure (最终答案, 解题步骤, 解析, 易错提醒)."""
    _FALLBACK_ANSWERS = {
        'tree': (
            f'最终答案：\n'
            f'对于给定的二叉树，前序遍历顺序为 A→B→D→E→C，中序遍历顺序为 D→B→E→A→C，后序遍历顺序为 D→E→B→C→A。\n\n'
            f'解题步骤：\n'
            f'1. 明确二叉树的节点结构（每个节点含 data、left、right 三个域）。\n'
            f'2. 写出递归的终止条件：当前节点为 nullptr 时返回。\n'
            f'3. 前序遍历：先访问当前节点，再递归左子树，最后递归右子树。\n'
            f'4. 中序遍历：先递归左子树，再访问当前节点，最后递归右子树。\n'
            f'5. 后序遍历：先递归左子树，再递归右子树，最后访问当前节点。\n\n'
            f'解析：\n'
            f'二叉树遍历的核心是决定"何时访问根节点"。递归版本利用系统调用栈自动保存上下文，非递归版本需要显式使用栈来模拟。前序遍历是深度优先搜索（DFS）在树上的直接体现。\n\n'
            f'易错提醒：\n'
            f'- 递归终止条件必须写在函数最前面，否则会无限递归导致栈溢出\n'
            f'- 非递归前序的入栈顺序是"先右后左"（栈LIFO特性）\n'
            f'- 中序遍历不是排序——只有当树是BST时中序结果才有序\n'
            f'- 空树的遍历结果是空，不是null或报错'
        ),
        'graph': (
            f'最终答案：\n'
            f'从起点A出发，BFS遍历顺序为 A→B→C→D→E，最短距离为 A=0, B=1, C=1, D=2, E=2。\n\n'
            f'解题步骤：\n'
            f'1. 初始化队列，将起点A入队，标记A已访问，距离dist[A]=0。\n'
            f'2. 出队A，遍历其邻居B、C，将它们入队并标记已访问，距离dist[B]=dist[C]=1。\n'
            f'3. 出队B，遍历其邻居A(已跳过)、D、E，将D、E入队，距离dist[D]=dist[E]=2。\n'
            f'4. 出队C，遍历其邻居A、E（均已访问跳过）。\n'
            f'5. 依次出队D、E，所有邻居均已访问，队列空→遍历结束。\n\n'
            f'解析：\n'
            f'BFS使用队列（FIFO）保证"先访问距离近的节点"。BFS首次访问某节点时的距离即是最短距离（边权为1），这是无权图最短路径的基本原理。队列中同时最多存放一层的节点，空间复杂度O(V)。\n\n'
            f'易错提醒：\n'
            f'- 入队时必须立即标记已访问，不能等到出队再标记（会导致重复入队）\n'
            f'- BFS求最短路径只适用于边权相同的图，边权不同时必须用Dijkstra\n'
            f'- 不要用栈替代队列——那会变成DFS\n'
            f'- 图的邻接表存储时注意区分有向图和无向图'
        ),
        'dp': (
            f'最终答案：\n'
            f'对于背包容量W=5、物品(2,3)(3,4)(4,5)的0-1背包问题，最大价值为7，选择物品1和物品2。\n\n'
            f'解题步骤：\n'
            f'1. 定义状态：dp[i][w]表示考虑前i个物品、容量为w时的最大价值。\n'
            f'2. 初始化：i=0行（无物品）全为0；w=0列全为0。\n'
            f'3. 状态转移：dp[i][w]=max(dp[i-1][w], dp[i-1][w-wtᵢ]+valᵢ)，当w≥wtᵢ。\n'
            f'4. 填充表格：按i从1到3、w从1到5的双重循环逐格计算。\n'
            f'5. 回溯：从dp[3][5]反向追踪，比较dp[i][w]与dp[i-1][w]判断物品i是否选中。\n\n'
            f'解析：\n'
            f'0-1背包是经典的NP完全问题，但可用动态规划在伪多项式时间O(nW)内求解。优化的关键在于将二维dp降为一维：dp[w]=max(dp[w], dp[w-wtᵢ]+valᵢ)，但w必须从大到小遍历以避免物品重复使用。\n\n'
            f'易错提醒：\n'
            f'- 一维优化时w必须逆序遍历（从W到0），正序遍历会变成完全背包\n'
            f'- 物品重量可能超过背包容量，此时只能不选\n'
            f'- dp数组初始化：求最大价值初始化为0，求恰好装满初始化为-∞（除dp[0]=0）\n'
            f'- 回溯选中的物品时不要重复计数'
        ),
        'sort': (
            f'最终答案：\n'
            f'对数组[5, 2, 8, 3, 6]执行快速排序，以首元素为pivot，最终有序数组为[2, 3, 5, 6, 8]。\n\n'
            f'解题步骤：\n'
            f'1. 选取基准元素pivot=5，将数组分为"小于5"和"大于5"两部分：[2,3]和[8,6]。\n'
            f'2. 对左半部分[2,3]递归：pivot=2，无更小元素，右侧[3]大于2。\n'
            f'3. 对右半部分[8,6]递归：pivot=8，左侧[6]小于8，右侧为空。\n'
            f'4. 递归到子数组长度≤1时终止，逐层合并结果。\n\n'
            f'解析：\n'
            f'快速排序的平均时间复杂度为O(n log n)，最坏情况（已排序或逆序且选首元素为pivot）退化为O(n²)。通过随机选择pivot或三数取中法可以避免最坏情况。快速排序是不稳定的，相同元素的相对位置可能改变。\n\n'
            f'易错提醒：\n'
            f'- 快排是不稳定排序——相等元素可能交换顺序\n'
            f'- 递归终止条件是子数组长度≤1，忘记会导致无限递归\n'
            f'- 分区时要保证pivot最终放在正确的位置上\n'
            f'- 归并排序才是稳定排序，不要与快排混淆'
        ),
        'stack': (
            f'最终答案：\n'
            f'括号序列"(())()"是合法的；(())("不合法。栈判定的核心是：遇到左括号入栈，遇到右括号时若栈顶是匹配的左括号则出栈，否则非法。\n\n'
            f'解题步骤：\n'
            f'1. 初始化空栈。\n'
            f'2. 遍历每个字符：左括号(、[、{{入栈；右括号时检查栈顶是否匹配。\n'
            f'3. 匹配则弹出栈顶继续；不匹配或栈为空则直接返回false。\n'
            f'4. 遍历结束后，若栈为空则括号匹配成功，否则非法（有多余左括号）。\n\n'
            f'解析：\n'
            f'栈的LIFO特性天然适合括号匹配——最内层的括号最先闭合，恰好对应栈顶元素。时间复杂度O(n)，空间复杂度O(n)。该思路可扩展到表达式求值、HTML标签匹配等场景。\n\n'
            f'易错提醒：\n'
            f'- 遍历完后必须检查栈是否为空，非空说明有未闭合的左括号\n'
            f'- 右括号出现时若栈为空也要判非法（没有匹配的左括号）\n'
            f'- 只有同类型的括号才能匹配，「(」匹配「)」而不是「]」\n'
            f'- Python的list.append()+pop()即可作为栈使用'
        ),
        'queue': (
            f'最终答案：\n'
            f'用两个栈实现的队列，入队操作O(1)，出队操作均摊O(1)。入队时直接push到stack1；出队时若stack2为空，将stack1的所有元素弹出并压入stack2，然后从stack2弹出栈顶。\n\n'
            f'解题步骤：\n'
            f'1. 定义两个栈stack1（入队用）和stack2（出队用）。\n'
            f'2. enqueue(x)：直接push到stack1。\n'
            f'3. dequeue()：若stack2为空→将stack1全部pop并push到stack2→从stack2 pop顶部。\n'
            f'4. peek()：同dequeue逻辑，但不pop而是返回stack2顶部。\n\n'
            f'解析：\n'
            f'两个栈实现队列利用了"两次LIFO=LIFO"的原理。每个元素最多被push和pop各两次（stack1→stack2），所以n次操作的均摊时间复杂度为O(1)。这是理解"均摊分析"的经典例子。\n\n'
            f'易错提醒：\n'
            f'- 只有在stack2为空时才将stack1搬过去，否则会打乱顺序\n'
            f'- dequeue时要处理两个栈都为空的情况（返回-1或抛异常）\n'
            f'- 不要混淆：用两个队列也可以实现栈，但逻辑不同'
        ),
        'hash': (
            f'最终答案：\n'
            f'对于输入keys=[5, 15, 25, 6]，哈希表大小为7，哈希函数h(k)=k%7，使用链地址法处理冲突：桶0→空，桶1→[15]，桶2→空，桶3→空，桶4→[25]，桶5→[5]，桶6→[6]。\n\n'
            f'解题步骤：\n'
            f'1. 确定哈希函数：h(k)=k mod 7。\n'
            f'2. 计算每个key的哈希值：5→5, 15→1, 25→4, 6→6。\n'
            f'3. 将每个key插入对应桶的链表头部（或尾部）。\n'
            f'4. 查找时先计算哈希值定位桶，再在链表中顺序查找。\n\n'
            f'解析：\n'
            f'哈希表的核心是"用空间换时间"——通过哈希函数将key直接映射到存储位置，理想情况下查找、插入、删除均为O(1)。负载因子（元素数/桶数）是性能关键：太小浪费空间，太大冲突增多。Python的dict在负载因子>2/3时会rehash扩容。\n\n'
            f'易错提醒：\n'
            f'- 哈希函数必须满足：相同key→相同哈希值（确定性）\n'
            f'- 链地址法的删除操作要同时处理链表节点的释放\n'
            f'- 开放定址法的删除不能直接清空（要用"墓碑"标记），否则查找链会断裂\n'
            f'- Python dict的key必须是可哈希的（不可变类型）'
        ),
        'recursion': (
            f'最终答案：\n'
            f'二叉树前序遍历的递归调用顺序：A调用B→B调用D→D返回B→B调用E→E返回B→B返回A→A调用C→C返回A→遍历结束。递归栈的最大深度为3（A→B→D）。\n\n'
            f'解题步骤：\n'
            f'1. 写出递归函数三要素：终止条件（root==nullptr）、本层操作（输出值）、递归调用（左子树+右子树）。\n'
            f'2. 画出递归树，标注每次调用的参数和返回值。\n'
            f'3. 追踪调用栈：每次递归调用创建新栈帧，返回时弹出栈帧。\n'
            f'4. 确定递归深度：从根到最远叶子的路径长度。\n\n'
            f'解析：\n'
            f'递归的本质是将大问题分解为结构相同的子问题，通过函数自调用来实现。每次递归调用都会在系统栈上创建新的栈帧（保存局部变量、参数和返回地址）。递归必须有终止条件（base case），否则会导致栈溢出（stack overflow）。\n\n'
            f'易错提醒：\n'
            f'- 终止条件必须写在递归调用之前，且必须能最终达到\n'
            f'- 递归深度过大会导致栈溢出（Python默认递归深度限制为1000）\n'
            f'- 尾递归可以被编译器优化为循环，但不是所有语言都支持\n'
            f'- 递归函数的返回值要正确向上传递，忘记return会导致丢失结果'
        ),
        'linked_list': (
            f'最终答案：\n'
            f'反转单链表的迭代解法：遍历链表，逐个将当前节点的next指针指向前一个节点。时间复杂度O(n)，空间复杂度O(1)。\n\n'
            f'解题步骤：\n'
            f'1. 初始化三个指针：prev=nullptr, curr=head, next=nullptr。\n'
            f'2. 在curr不为空时循环：保存next=curr.next，翻转curr.next=prev，prev和curr各前进一步。\n'
            f'3. 循环结束后prev指向新头节点（原尾节点），返回prev。\n\n'
            f'解析：\n'
            f'链表反转是理解指针操作的经典题目。核心难点是修改next指针前必须先保存它的原值（否则后面的节点就找不到了），所以需要三个指针而非两个。递归解法利用递归栈的回溯特性，从尾部开始反转。\n\n'
            f'易错提醒：\n'
            f'- 必须先保存next再翻转指针，顺序错了会丢失链表后半部分\n'
            f'- 空链表或单节点链表：直接返回头节点\n'
            f'- 双指针法（prev+curr）比三指针更简洁但逻辑相同\n'
            f'- 递归反转时要处理尾节点的next指向nullptr'
        ),
        'binary_search': (
            f'最终答案：\n'
            f'在有序数组[2, 3, 5, 7, 8, 10, 12]中查找7，二分查找经过的索引序列为：mid=3(值7)→找到，比较1次。若查找6：mid=3(7>6)→mid=1(3<6)→mid=2(5<6)→未找到。\n\n'
            f'解题步骤：\n'
            f'1. 初始化left=0, right=n-1。\n'
            f'2. 当left≤right时循环：计算mid=left+(right-left)//2（防溢出）。\n'
            f'3. 若arr[mid]==target→返回mid；若arr[mid]<target→left=mid+1；否则right=mid-1。\n'
            f'4. 循环结束未返回则说明未找到，返回-1。\n\n'
            f'解析：\n'
            f'二分查找将每次比较后的搜索空间减半，时间复杂度O(log n)。mid的计算使用left+(right-left)//2而非(left+right)//2是为了防止整数溢出（虽然Python不会溢出，但C++/Java中left+right可能超过INT_MAX）。\n\n'
            f'易错提醒：\n'
            f'- 循环条件是left≤right而非left<right（会漏掉最后一次比较）\n'
            f'- 边界更新是mid±1而非mid（否则会死循环）\n'
            f'- 找左边界时即使找到也要继续往左搜，找右边界同理\n'
            f'- 二分查找只适用于有序序列，无序数组必须先排序'
        ),
        'linear': (
            f'最终答案：\n'
            f'在数组[3, 7, 1, 9, 4]中线性查找元素7，从索引0开始顺序扫描，在索引1处找到目标值，比较次数为2。若查找不存在的元素5，则需要扫描全部5个元素后返回-1。\n\n'
            f'解题步骤：\n'
            f'1. 从索引i=0开始，依次比较arr[i]与目标值target。\n'
            f'2. 若arr[i]==target则返回索引i。\n'
            f'3. 若扫描完整个数组仍未找到，返回-1。\n'
            f'4. 可添加"哨兵"优化：将target暂存到arr末尾，省去每次循环的越界检查。\n\n'
            f'解析：\n'
            f'线性查找是最基础的查找算法，时间复杂度O(n)，空间复杂度O(1)。它的优势是不要求数据有序，适用于小规模数据或无序数据集。对于有序数据应优先使用二分查找(O(log n))或哈希表(O(1))。\n\n'
            f'易错提醒：\n'
            f'- 线性查找的复杂度是O(n)，大数据量下性能差\n'
            f'- 返回索引而非查找值本身\n'
            f'- 若数组有重复元素，线性查找返回的是第一个匹配的索引\n'
            f'- 动态数组的插入和删除是O(n)，不是O(1)'
        ),
        'stack_queue': (
            f'最终答案：\n'
            f'栈（LIFO）和队列（FIFO）的核心区别：栈在栈顶插入和删除，队列在队尾插入、队首删除。用栈实现DFS（深度优先），用队列实现BFS（广度优先）。\n\n'
            f'解题步骤：\n'
            f'1. 栈的基本操作：push(入栈顶)、pop(出栈顶)、peek(查看栈顶)，均为O(1)。\n'
            f'2. 队列的基本操作：enqueue(入队尾)、dequeue(出队首)、peek(查看队首)，均为O(1)。\n'
            f'3. 用栈实现队列：需要两个栈，入队O(1)，出队均摊O(1)。\n'
            f'4. 用队列实现栈：需要两个队列，push时把新元素后的所有元素移到队列2再移回。\n\n'
            f'解析：\n'
            f'栈和队列是最基础的两种受限线性结构。栈适合需要"回溯"的场景（DFS、括号匹配、函数调用），队列适合需要"按序处理"的场景（BFS、任务调度、消息缓冲）。选择哪种结构取决于数据的处理顺序需求。\n\n'
            f'易错提醒：\n'
            f'- 栈的pop()通常会返回弹出值，不要忘记接收\n'
            f'- 队列为空时dequeue()需特殊处理（返回-1或抛异常）\n'
            f'- 循环队列的空/满判断：牺牲一个位置来区分（rear+1)%size==front为满\n'
            f'- 双端队列(deque)两端都可操作，功能是栈+队列的超集'
        ),
    }

    content = _FALLBACK_ANSWERS.get(cat)
    if content is None:
        content = (
            f'最终答案：\n'
            f'{topic}的核心知识点已在上方练习中体现，具体答案需要针对题目提供的实际数据来书写。\n\n'
            f'解题步骤：\n'
            f'1. 先通读题目，明确输入数据和期望输出。\n'
            f'2. 按照{topic}的标准解法步骤逐步模拟或推演。\n'
            f'3. 记录每一步的中间结果，便于检查和回溯。\n'
            f'4. 将最终结果以清晰格式写出，确保可验证。\n\n'
            f'解析：\n'
            f'此题考察{topic}的理解和应用能力。核心是掌握其定义、基本操作、以及典型应用场景。建议结合具体数据手动推演一遍以加深理解。\n\n'
            f'易错提醒：\n'
            f'- 注意边界条件（如空输入、单元素等特殊情况）\n'
            f'- 检查中间步骤是否存在逻辑跳步或遗漏\n'
            f'- 常见错误：混淆相似概念（如栈与队列、DFS与BFS）的适用场景'
        )

    lang_label = lang if lang else 'C++'
    return {
        'kind': 'answer',
        'heading': f'参考答案与解析',
        'content':  content,
    }


def _match_kb_answer(topic, cat, practice_heading, practice_content):
    """Match a KB answer entry by scanning heading+content for keywords."""
    entries = _ANSWER_KB.get(cat, {})
    combined = ((practice_heading or '') + ' ' + (practice_content or '')).lower()
    best_key = None
    best_len = 0
    for key in entries:
        if key.lower() in combined and len(key) > best_len:
            best_key = key
            best_len = len(key)
    if best_key:
        return entries[best_key]
    return None


def _build_topic_specific_answer(topic, cat, lang, practice_heading, practice_content):
    """Build a substantive, topic-specific answer section.

    Tries the KB first, falls back to a contextual answer builder.
    Never returns generic "请先独立思考" placeholder text.
    """
    # Try KB match
    kb_answer = _match_kb_answer(topic, cat, practice_heading, practice_content)
    if kb_answer:
        heading = practice_heading or '练习'
        return {
            'kind': 'answer',
            'heading': f'{heading} — 参考答案与解析',
            'content': kb_answer,
        }

    # Fallback: build contextual answer from category knowledge
    return _make_fallback_answer(topic, cat, lang)


def _validate_answer_quality(answer_section, topic, cat):
    """Check that an answer section has the mandatory 4-section structure.

    Returns the section unchanged if valid, or a repaired section if not.
    The mandatory quality marker is "最终答案" — no answer is valid without it.
    """
    content = answer_section.get('content', '') if isinstance(answer_section, dict) else ''
    if not content:
        # Empty answer — rebuild from fallback
        return _make_fallback_answer(topic, cat, '')

    has_final_answer = '最终答案' in str(content)

    if has_final_answer:
        return answer_section

    # Answer is missing "最终答案" — prepend a concrete answer derived from KB
    heading = answer_section.get('heading', '')
    original_content = str(content)

    repaired = _build_topic_specific_answer(topic, cat, '', heading, original_content)
    return repaired


# ═══════════════════════════════════════════════════════════════════
# Practice filler — ensures minimum practice count for 分层练习
# ═══════════════════════════════════════════════════════════════════

_PRACTICE_TEMPLATES = {
    'tree': {
        'basic': [
            ('二叉树遍历顺序验证',
             '给定二叉树层序数组 [1, 2, 3, 4, 5]（根=1，1的左右子为2和3，2的左右子为4和5），请分别写出其前序、中序、后序遍历的结果。',
             f'最终答案：\n'
             f'前序（根→左→右）：1 → 2 → 4 → 5 → 3\n'
             f'中序（左→根→右）：4 → 2 → 5 → 1 → 3\n'
             f'后序（左→右→根）：4 → 5 → 2 → 3 → 1\n\n'
             f'解题步骤：\n'
             f'1. 由层序数组还原树：根=1，1的左右子为2和3，2的左右子为4和5，3无子，4和5无子。\n'
             f'2. 前序：先根(1)→递归左子树(2,4,5)得到2→4→5→递归右子树(3)得到3 = 1 2 4 5 3。\n'
             f'3. 中序：递归左子树到底(4)→根(2)→右子(5)→根(1)→右子树(3) = 4 2 5 1 3。\n'
             f'4. 后序：递归左子树(4→5→2)→递归右子树(3)→根(1) = 4 5 2 3 1。\n\n'
             f'解析：\n'
             f'三种遍历的核心区别在于"何时访问根节点"。前序先访问根（用于复制树），中序在中间访问根（BST中序结果有序），后序最后访问根（用于删除树、计算高度）。层序使用队列而非递归，自顶向下逐层访问。\n\n'
             f'易错提醒：\n'
             f'- 层序数组表示中，索引i的左右子分别在2i+1和2i+2位置（0-based）\n'
             f'- 不要把中序遍历和"排序"混为一谈——只有BST的中序才是升序\n'
             f'- 非递归遍历时栈的入栈顺序要考虑LIFO特性'),
        ],
        'advanced': [
            ('非递归中序遍历实现',
             '用栈实现二叉树中序遍历（非递归），输入：root=[1,2,3,4,5]（层序），请写出完整C++代码并分析空间复杂度。',
             f'最终答案：\n'
             f'非递归中序遍历输出：4 2 5 1 3。空间复杂度O(h)，最坏O(n)，平均O(log n)。\n\n'
             f'解题步骤：\n'
             f'1. 初始化空栈，curr指向根节点。\n'
             f'2. while栈非空或curr非空：将curr及其所有左子依次压栈（curr=curr.left）。\n'
             f'3. 出栈栈顶node，访问node的值。\n'
             f'4. 将curr设为node.right，回到步骤2。\n'
             f'5. 循环直到栈空且curr为空。\n\n'
             f'完整代码（C++）：\n'
             f'  vector<int> inorderTraversal(TreeNode* root) {{\n'
             f'      vector<int> res;\n'
             f'      stack<TreeNode*> st;\n'
             f'      TreeNode* curr = root;\n'
             f'      while (curr || !st.empty()) {{\n'
             f'          while (curr) {{ st.push(curr); curr = curr->left; }}\n'
             f'          curr = st.top(); st.pop();\n'
             f'          res.push_back(curr->val);\n'
             f'          curr = curr->right;\n'
             f'      }}\n'
             f'      return res;\n'
             f'  }}\n\n'
             f'解析：\n'
             f'递归本质是用系统调用栈保存上下文，非递归版用显式栈模拟。压栈=深入左子树，出栈访问=回到当前层并处理根，转右子树=完成左子树的递归后进入右子树。\n\n'
             f'易错提醒：\n'
             f'- 内层while是把"所有左子"压栈，不是只压一个\n'
             f'- 出栈后再去右子树，不是压栈时就去\n'
             f'- 空栈但curr非空时循环仍要继续（刚开始时栈为空但curr=root）'),
        ],
        'comprehensive': [
            ('树的高度与平衡性判断',
             '给定二叉树层序[3,9,20,null,null,15,7]，计算其高度并判断是否平衡（任意节点左右子树高度差≤1）。要求一次遍历完成，写出C++代码。',
             f'最终答案：\n'
             f'树高=3，是平衡二叉树（节点3左右高差为0，节点20左右高差为1）。\n\n'
             f'解题步骤：\n'
             f'1. 使用后序遍历自底向上计算高度。\n'
             f'2. 空节点返回高度0。\n'
             f'3. 递归计算左子树高度lh和右子树高度rh。\n'
             f'4. 若|lh-rh|>1或lh=-1或rh=-1，返回-1（标记不平衡）。\n'
             f'5. 否则返回1+max(lh,rh)。\n\n'
             f'C++代码：\n'
             f'  int check(TreeNode* root) {{\n'
             f'      if (!root) return 0;\n'
             f'      int lh = check(root->left);\n'
             f'      int rh = check(root->right);\n'
             f'      if (lh == -1 || rh == -1 || abs(lh-rh) > 1) return -1;\n'
             f'      return 1 + max(lh, rh);\n'
             f'  }}\n'
             f'  bool isBalanced(TreeNode* root) {{ return check(root) != -1; }}\n\n'
             f'解析：\n'
             f'-1作为"不平衡"的信号值向上传递，避免重复计算。后序遍历保证先处理子树再处理当前节点，天然适合高度计算。时间O(n)，空间O(h)。\n\n'
             f'易错提醒：\n'
             f'- 必须检查子树返回的-1标记，不能只比较lh和rh\n'
             f'- 高度定义为从该节点到最远叶子的边数（或节点数，取决于定义）\n'
             f'- 空节点高度为0（或-1），与题目定义保持一致即可'),
        ],
    },
    'graph': {
        'basic': [
            ('图的BFS遍历',
             '给定无向图：A-[B,C], B-[A,D,E], C-[A,E], D-[B], E-[B,C]。从A出发进行BFS，以字母序访问邻居。写出BFS访问顺序和最短距离。',
             f'最终答案：\n'
             f'BFS遍历顺序：A → B → C → D → E。最短距离：A=0, B=1, C=1, D=2, E=2。\n\n'
             f'解题步骤：\n'
             f'1. 初始化队列=[A]，visited={{A}}，dist[A]=0。\n'
             f'2. 出队A，入队其未访问邻居B、C（字母序），dist[B]=dist[C]=1，队列=[B,C]。\n'
             f'3. 出队B，邻居D、E未访问，入队D、E，dist[D]=dist[E]=2，队列=[C,D,E]。\n'
             f'4. 出队C，邻居A(已访问)、E(已访问)，无新节点入队，队列=[D,E]。\n'
             f'5. 出队D、E，所有邻居均已访问，队列空→遍历结束。\n\n'
             f'解析：\n'
             f'BFS使用队列实现按层遍历，保证首次访问时的距离即为最短距离（边权为1）。每次出队时访问节点，入队时标记已访问（防止重复入队）。\n\n'
             f'易错提醒：\n'
             f'- 入队时必须立即标记visited，等出队再标记会导致同一节点多次入队\n'
             f'- BFS求最短路径仅适用于无权图，有权图必须用Dijkstra\n'
             f'- 用栈替代队列会将BFS变成DFS，遍历顺序完全不同'),
        ],
        'advanced': [
            ('BFS求无权图最短路径',
             '给定图：0-[1,2], 1-[0,3,4], 2-[0,5], 3-[1], 4-[1,5], 5-[2,4]。从节点0出发，写出到每个节点的最短距离（边数）以及到节点5的最短路径。',
             f'最终答案：\n'
             f'最短距离：dist[0]=0, dist[1]=1, dist[2]=1, dist[3]=2, dist[4]=2, dist[5]=2。\n'
             f'到节点5的最短路径：0 → 2 → 5 或 0 → 1 → 4 → 5（前者更短，2条边）。\n\n'
             f'解题步骤：\n'
             f'1. 初始化dist全为-1，dist[0]=0，parent[0]=-1，队列=[0]。\n'
             f'2. 出队0→更新dist[1]=dist[2]=1，parent[1]=parent[2]=0，入队[1,2]。\n'
             f'3. 出队1→更新dist[3]=dist[4]=2，parent[3]=parent[4]=1，入队[2,3,4]。\n'
             f'4. 出队2→dist[5]=2（首次访问！），parent[5]=2，入队[3,4,5]。\n'
             f'5. 反向回溯路径：5←2←0 → 0→2→5。\n\n'
             f'解析：\n'
             f'在BFS扩展时记录parent数组即可还原路径。注意节点5第一次被访问是在第3步（队列中已经是距离=2），而非第4步。这里0→2→5和0→1→4→5都是最短路径（长度2）。\n\n'
             f'易错提醒：\n'
             f'- 首次访问时记录的距离就是最短距离，后面再遇到时不要再更新\n'
             f'- parent[起点]设为-1（或自身），表示没有前驱\n'
             f'- 回溯路径时从终点往起点反向追溯，最后再反转输出'),
        ],
    },
    'dp': {
        'basic': [
            ('0-1背包基础计算',
             '背包容量W=5，3个物品：(重量2,价值3)(重量3,价值4)(重量4,价值5)。用DP表格法求最大价值，并回溯得到最优选择方案。',
             f'最终答案：\n'
             f'最大价值=7。最优方案：选择物品1（重量2,价值3）和物品2（重量3,价值4），总重5。\n\n'
             f'DP表格（i=物品编号, w=容量）：\n'
             f'   dp[0][0..5] = [0,0,0,0,0,0]\n'
             f'   dp[1][0..5] = [0,0,3,3,3,3]\n'
             f'   dp[2][0..5] = [0,0,3,4,4,7]\n'
             f'   dp[3][0..5] = [0,0,3,4,5,7]\n\n'
             f'解题步骤：\n'
             f'1. 初始化dp[0][*]=0（无物品）。对i=1..3，w=1..5，用dp[i][w]=max(dp[i-1][w], dp[i-1][w-wtᵢ]+valᵢ)。\n'
             f'2. 关键推导 dp[2][5]=max(dp[1][5]=3, dp[1][2]+4=3+4=7)=7 ← 选物品2。\n'
             f'3. 回溯：dp[3][5]=7=dp[2][5]，物品3未选；dp[2][5]=7≠dp[1][5]=3，物品2选了；剩余容量5-3=2，dp[1][2]=3≠dp[0][2]=0，物品1选了。\n\n'
             f'解析：\n'
             f'状态定义为"考虑前i个物品、容量为w时的最大价值"。每个物品只能选或不选一次（0-1）。时间复杂度O(nW)，可用一维数组优化空间到O(W)（w必须逆序遍历）。\n\n'
             f'易错提醒：\n'
             f'- 一维优化时w必须从W往0逆序遍历，正序会变成完全背包（物品可重复选）\n'
             f'- 若要求"恰好装满"，初始化dp[0]=0其余为-∞；若求"最大价值"则全初始化为0\n'
             f'- 回溯时要注意dp[i][w]==dp[i-1][w]表示i未选，否则i选了'),
        ],
        'advanced': [
            ('最长递增子序列(LIS)',
             '给定数组[10, 9, 2, 5, 3, 7, 101, 18]，求最长严格递增子序列的长度，并输出一个最长的递增子序列。',
             f'最终答案：\n'
             f'最长递增子序列长度=4。一个最长递增子序列：[2, 3, 7, 101] 或 [2, 5, 7, 101]。\n\n'
             f'解题步骤：\n'
             f'1. dp[i]定义为以nums[i]结尾的最长递增子序列长度，初始全为1。\n'
             f'2. 对每个i，遍历j<i：若nums[j]<nums[i]，dp[i]=max(dp[i], dp[j]+1)。\n'
             f'3. 计算过程：dp[0]=1(10), dp[1]=1(9), dp[2]=1(2), dp[3]=2(2,5), dp[4]=2(2,3), dp[5]=3(2,3,7), dp[6]=4(2,3,7,101), dp[7]=4(2,3,7,18)。\n'
             f'4. 最终答案=max(dp)=4，通过parent数组回溯得到具体子序列。\n\n'
             f'解析：\n'
             f'经典的O(n²)解法。O(n log n)解法使用贪心+二分查找，维护一个tails数组。LIS是动态规划的入门必会题，关键是正确定义以i结尾的状态。\n\n'
             f'易错提醒：\n'
             f'- dp[i]是"以i结尾"而不是"前i个"，忘记这个会导致状态转移错误\n'
             f'- 最终答案需取max(dp)而非dp[n-1]\n'
             f'- "严格递增"要求nums[j]<nums[i]（不能等于），"非严格"允许等于\n'
             f'- 二分查找优化版要求tails数组的更新逻辑正确'),
        ],
        'comprehensive': [
            ('最长公共子序列(LCS)',
             '给定text1="abcde"和text2="ace"，求最长公共子序列的长度并输出具体子序列。',
             f'最终答案：\n'
             f'LCS长度=3。最长公共子序列="ace"（text1取索引0,2,4，text2取0,1,2）。\n\n'
             f'解题步骤：\n'
             f'1. dp[i][j]定义为text1前i个字符与text2前j个字符的LCS长度。\n'
             f'2. 状态转移：若text1[i-1]==text2[j-1]→dp[i][j]=dp[i-1][j-1]+1；否则→dp[i][j]=max(dp[i-1][j], dp[i][j-1])。\n'
             f'3. 填充表格后dp[5][3]=3。\n'
             f'4. 回溯：从dp[5][3]开始，遇到相等字符记录下来并向左上移动；不等则向dp值更大的方向移动。\n\n'
             f'解析：\n'
             f'LCS是经典的二维DP问题，广泛应用于文本比较、版本控制中的diff算法等。子序列不要求连续，子串才要求连续。时间/空间均为O(mn)，可优化空间至O(min(m,n))。\n\n'
             f'易错提醒：\n'
             f'- 子序列≠子串——子序列不要求连续，子串要求连续\n'
             f'- 回溯时若dp[i-1][j]==dp[i][j-1]应优先向一方移动（约定俗成）\n'
             f'- dp数组索引与字符串索引差1（dp[1]对应text[0]）'),
        ],
    },
    'sort': {
        'basic': [
            ('快速排序手动模拟',
             '对数组[5, 2, 8, 3, 6]以首元素为pivot执行快速排序，写出每次分区后的数组状态。',
             f'最终答案：\n'
             f'排序后：[2, 3, 5, 6, 8]。分区过程：\n'
             f'第1次：pivot=5 → [2, 3, 5, 8, 6]\n'
             f'第2次(左)：pivot=2 → [2, 3]\n'
             f'第3次(右)：pivot=8 → [6, 8] → 最终 [2, 3, 5, 6, 8]\n\n'
             f'解题步骤：\n'
             f'1. pivot=5：从右找<5的(3)，从左找>5的(8)，交换→[5,2,3,8,6]；再扫描→3和5交换→[2,3,5,8,6]。\n'
             f'2. 左半[2,3]：pivot=2，右指针找到3不小于2，分区后有序[2,3]。\n'
             f'3. 右半[8,6]：pivot=8，找到6<8，交换→[6,8]，递归终止。\n\n'
             f'解析：\n'
             f'快排核心=分区操作。每次分区把pivot放到正确位置，左边全≤pivot，右边全≥pivot。平均O(n log n)，最坏O(n²)（已排序数组+首元素为pivot）。随机选pivot可避免最坏情况。\n\n'
             f'易错提醒：\n'
             f'- 快排是不稳定排序——等值元素的相对顺序可能改变\n'
             f'- 递归终止条件：子数组长度≤1（不是长度为0时才终止）\n'
             f'- pivot最终必须放在正确位置，不能留在子数组的边界上'),
        ],
        'advanced': [
            ('归并排序排序过程',
             '对数组[38, 27, 43, 3, 9, 82, 10]执行归并排序，写出递归分解和合并的全过程。',
             f'最终答案：\n'
             f'排序后：[3, 9, 10, 27, 38, 43, 82]\n\n'
             f'解题步骤：\n'
             f'1. 分解：[38,27,43,3] | [9,82,10] → [38,27]|[43,3] | [9,82]|[10] → 继续分解到单元素。\n'
             f'2. 合并[38],[27]→[27,38]；合并[43],[3]→[3,43]；合并[27,38],[3,43]→[3,27,38,43]。\n'
             f'3. 合并[9],[82]→[9,82]；合并[9,82],[10]→[9,10,82]。\n'
             f'4. 合并[3,27,38,43],[9,10,82]→[3,9,10,27,38,43,82]。\n\n'
             f'解析：\n'
             f'归并排序是稳定的、时间复杂度稳定O(n log n)的排序算法。代价是需要O(n)额外空间。适合外部排序（大数据量无法全部载入内存时）。与快排的区别：归并是"先分解后合并"，快排是"先分区后递归"。\n\n'
             f'易错提醒：\n'
             f'- 归并排序是稳定排序，快排和堆排不是——这是选择排序算法的重要考量\n'
             f'- 合并两个有序数组时要用双指针，时间O(n)\n'
             f'- 额外空间O(n)不可省，但有in-place merge的变体（时间复杂度更高）'),
        ],
    },
    'stack': {
        'basic': [
            ('括号匹配判定',
             '给定括号序列 s="({[]})"，用栈判定是否合法。若合法，写出栈的变化过程。',
             f'最终答案：\n'
             f'"({[]})" 括号合法。栈变化：空→(→({{→({{[→({{→(→空。\n\n'
             f'解题步骤：\n'
             f'1. s[0]="("→入栈，栈=[(]\n'
             f'2. s[1]="{{"→入栈，栈=[(,{{]\n'
             f'3. s[2]="["→入栈，栈=[(,{{,[]\n'
             f'4. s[3]="]"→栈顶[匹配，出栈，栈=[(,{{]\n'
             f'5. s[4]="}}"→栈顶{{匹配，出栈，栈=[(]\n'
             f'6. s[5]=")"→栈顶(匹配，出栈，栈=[]→栈空，合法。\n\n'
             f'解析：\n'
             f'栈的LIFO特性天然匹配括号的嵌套结构——最内层括号最先闭合，对应栈顶元素。C++ STL中stack<char>配合switch语句可简洁实现。时间O(n)，空间O(n)。\n\n'
             f'易错提醒：\n'
             f'- 遍历结束后必须检查栈是否为空（可能有多余左括号）\n'
             f'- 遇到右括号时若栈为空也非法（缺少对应左括号）\n'
             f'- 只有同类型的括号才能匹配：)只能匹配(，不能匹配[或{{'),
        ],
        'advanced': [
            ('用栈实现队列',
             '使用两个栈实现一个队列，支持push(x)和pop()操作。写出完整的C++类定义，并分析pop操作的均摊时间复杂度。',
             f'最终答案：\n'
             f'push()时间复杂度O(1)，pop()均摊时间复杂度O(1)。\n\n'
             f'解题步骤：\n'
             f'1. 定义两个栈：stack1（入队用）和stack2（出队用）。\n'
             f'2. push(x)：直接push到stack1。\n'
             f'3. pop()：若stack2为空→将stack1逐一pop并push到stack2；从stack2顶部pop。\n\n'
             f'C++代码：\n'
             f'  class MyQueue {{\n'
             f'      stack<int> s1, s2;\n'
             f'  public:\n'
             f'      void push(int x) {{ s1.push(x); }}\n'
             f'      int pop() {{\n'
             f'          if (s2.empty()) {{ while (!s1.empty()) {{ s2.push(s1.top()); s1.pop(); }} }}\n'
             f'          int v = s2.top(); s2.pop(); return v;\n'
             f'      }}\n'
             f'      int peek() {{\n'
             f'          if (s2.empty()) {{ while (!s1.empty()) {{ s2.push(s1.top()); s1.pop(); }} }}\n'
             f'          return s2.top();\n'
             f'      }}\n'
             f'      bool empty() {{ return s1.empty() && s2.empty(); }}\n'
             f'  }};\n\n'
             f'解析：\n'
             f'每个元素最多进栈2次、出栈2次（push到s1、pop从s1并push到s2、pop从s2），所以n次操作的均摊复杂度为O(1)。这是理解"均摊分析"最经典的例子。\n\n'
             f'易错提醒：\n'
             f'- 只有在s2为空时才转移s1，否则顺序会错乱\n'
             f'- pop和peek都要处理s2为空→转移的逻辑\n'
             f'- 两个栈都为空时pop/peek应返回-1或抛异常'),
        ],
    },
    'queue': {
        'basic': [
            ('循环队列设计',
             '设计一个大小为5的循环队列。依次执行：enqueue(1,2,3,4,5), dequeue(), enqueue(6), dequeue(), enqueue(7)。画出每次操作后front和rear的位置。',
             f'最终答案：\n'
             f'初始：front=0, rear=0, 队列空。\n'
             f'入队1-5：[1,2,3,4,5], front=0, rear=0（队满,rear==front但牺牲一位置判断为满）\n'
             f'出队1→[_,2,3,4,5], front=1, rear=0\n'
             f'入队6→[_,2,3,4,5]但6覆盖到rear位置→队列[6,2,3,4,5], front=1, rear=1\n'
             f'实际上循环队列用 (rear+1)%size==front 判断满，所以容量为size-1=4，只能存4个。\n'
             f'重新假设size=6：enqueue(1-5)→[1,2,3,4,5,_], front=0, rear=5。dequeue→[_,2,3,4,5,_], front=1。enqueue(6)→[_,2,3,4,5,6], rear=0。dequeue→[_,_,3,4,5,6], front=2。enqueue(7)→[7,_,3,4,5,6], rear=1。\n\n'
             f'解题步骤：\n'
             f'1. enqueue：data[rear]=x, rear=(rear+1)%size。\n'
             f'2. dequeue：x=data[front], front=(front+1)%size, return x。\n'
             f'3. 判空：front==rear。判满：(rear+1)%size==front（牺牲一个位置）。\n\n'
             f'解析：\n'
             f'循环队列用固定大小的数组实现FIFO，避免了普通队列出队时的O(n)数据搬移。判满条件"牺牲一个位置"是为了区分空(front==rear)和满的状态。\n\n'
             f'易错提醒：\n'
             f'- 循环队列的容量是size-1（有一个位置不能存数据）\n'
             f'- 所有索引操作都要取模：rear=(rear+1)%size\n'
             f'- 队满条件≠rear==size-1，而是(rear+1)%size==front'),
        ],
    },
    'stack_queue': {
        'basic': [
            ('栈与队列对比应用',
             '对以下场景选择合适的数据结构（栈/队列/双端队列），并说明理由：(1)函数调用管理 (2)打印任务队列 (3)浏览器前进后退 (4)BFS遍历。',
             f'最终答案：\n'
             f'(1) 栈——函数调用是嵌套结构，后调用的先返回，LIFO。\n'
             f'(2) 队列——先提交的打印任务先执行，FIFO。\n'
             f'(3) 双栈——前进/后退需要记录历史，一个栈存后退页面，一个栈存前进页面。\n'
             f'(4) 队列——BFS先访问近的节点再访问远的，FIFO。\n\n'
             f'解题步骤：\n'
             f'1. 分析场景中元素的操作顺序（FIFO还是LIFO）。\n'
             f'2. FIFO→队列；LIFO→栈；两端都需要操作→双端队列。\n'
             f'3. 考虑是否有"撤销/回溯"需求→栈；考虑是否有"排队/缓冲"需求→队列。\n\n'
             f'解析：\n'
             f'数据结构的选型取决于对数据访问顺序的要求。DFS用栈（或系统调用栈），BFS用队列——这是图遍历中最基础的选型原则。双端队列(deque)兼具栈和队列的能力，两端都可以push/pop。\n\n'
             f'易错提醒：\n'
             f'- DFS可用栈(非递归)或递归(系统调用栈)，BFS必须用队列\n'
             f'- 浏览器前进后退需要两个栈配合，不是单栈\n'
             f'- 优先级队列≠普通队列——出队顺序按优先级而非入队时间'),
        ],
    },
    'recursion': {
        'basic': [
            ('递归调用栈追踪',
             '对于如下递归函数，调用foo(3)时的输出序列是什么？\nvoid foo(int n) { if (n>0) { printf("%d ", n); foo(n-1); printf("%d ", n); } }',
             f'最终答案：\n'
             f'输出序列：3 2 1 1 2 3\n\n'
             f'解题步骤：\n'
             f'1. foo(3)：打印3→调用foo(2)→...foo(1)打印1→foo(0)直接返回→打印1→返回foo(2)打印2→返回foo(3)打印3。\n'
             f'2. 调用栈变化：push(3)→push(2)→push(1)→push(0)→pop(0)→打印1(来自n=1)→pop(1)→打印2(来自n=2)→pop(2)→打印3(来自n=3)→pop(3)。\n'
             f'3. 注意printf在两个位置各执行一次——递归前和递归后。\n\n'
             f'解析：\n'
             f'递归调用前的代码在"递"阶段执行（向下深入），递归调用后的代码在"归"阶段执行（向上回溯）。理解了"递"和"归"就理解了递归的核心。\n\n'
             f'易错提醒：\n'
             f'- 递归前和递归后的代码执行顺序相反——前者正序后者逆序\n'
             f'- 终止条件必须写在递归调用之前\n'
             f'- 每次递归调用会创建新的局部变量副本\n'
             f'- 递归过深会导致栈溢出（Stack Overflow）'),
        ],
    },
    'hash': {
        'basic': [
            ('哈希表操作模拟',
             '哈希表大小m=7，哈希函数h(k)=k%7，用链地址法处理冲突。依次插入[5, 12, 19, 6, 13]，然后查找19和8，写出每个桶的最终链表和查找过程。',
             f'最终答案：\n'
             f'桶分布：0:[], 1:[], 2:[], 3:[], 4:[], 5:[5→19→12], 6:[6→13]\n'
             f'查找19：h(19)=5→遍历桶5→找到19 ✓\n'
             f'查找8：h(8)=1→桶1为空→未找到 ✗\n\n'
             f'解题步骤：\n'
             f'1. 5%7=5→桶5:[5]\n'
             f'2. 12%7=5→桶5:[5,12] (冲突，用链表链接)\n'
             f'3. 19%7=5→桶5:[5,12,19]\n'
             f'4. 6%7=6→桶6:[6]\n'
             f'5. 13%7=6→桶6:[6,13]\n'
             f'6. 查找：先算哈希值定位桶，再在链表中顺序查找。\n\n'
             f'解析：\n'
             f'负载因子=5/7≈0.71<1，性能良好。当负载因子过大时需rehash（扩容）。链地址法实现简单，但需要额外的链表节点内存。C++ STL的unordered_map和Python的dict都使用哈希表。\n\n'
             f'易错提醒：\n'
             f'- 哈希函数必须保证相同key→相同哈希值（确定性）\n'
             f'- 链地址法删除时要正确调整链表指针\n'
             f'- Python的dict/set要求key必须是hashable（不可变类型）\n'
             f'- 开放定址法删除时需标记"墓碑"，不能直接清空'),
        ],
    },
    'linked_list': {
        'basic': [
            ('反转单链表',
             '给定单链表 1→2→3→4→5→nullptr，使用迭代法将其反转，写出每一步的指针变化。',
             f'最终答案：\n'
             f'反转后：5→4→3→2→1→nullptr。\n\n'
             f'解题步骤：\n'
             f'1. 初始：prev=nullptr, curr=1→2→3→4→5。\n'
             f'2. 第1步：next=2, 1→nullptr, prev=1, curr=2。链表状态：1→nullptr, 2→3→4→5。\n'
             f'3. 第2步：next=3, 2→1, prev=2, curr=3。链表状态：2→1→nullptr, 3→4→5。\n'
             f'4. 第3步：next=4, 3→2, prev=3, curr=4。链表状态：3→2→1→nullptr, 4→5。\n'
             f'5. 第4步：next=5, 4→3, prev=4, curr=5。链表状态：4→3→2→1→nullptr, 5。\n'
             f'6. 第5步：next=nullptr, 5→4, prev=5, curr=nullptr。循环结束，返回prev=5。\n\n'
             f'解析：\n'
             f'反转链表的本质是逐个翻转每个节点的next指针方向。三个指针的作用：prev→已翻转部分的头，curr→当前要翻转的节点，next→暂存剩余链表的头（防止丢失）。时间O(n)，空间O(1)。\n\n'
             f'易错提醒：\n'
             f'- 必须先保存next再翻转curr.next，顺序错了会丢失链表\n'
             f'- 最后返回的是prev不是curr（循环结束时curr=nullptr）\n'
             f'- 空链表或单节点链表：直接返回head'),
        ],
    },
    'binary_search': {
        'basic': [
            ('二分查找手动模拟',
             '在有序数组[2, 3, 5, 7, 8, 10, 12, 15, 18]中分别查找7和11，写出每次mid的值和比较结果。',
             f'最终答案：\n'
             f'查找7：mid=4(值8>7)→mid=1(值3<7)→mid=2(值5<7)→mid=3(值7==7)找到！索引=3，比较4次。\n'
             f'查找11：mid=4(值8<11)→mid=6(值12>11)→mid=5(值10<11)→left>right→未找到(-1)，比较3次。\n\n'
             f'解题步骤：\n'
             f'1. 初始化left=0, right=8。\n'
             f'2. 循环条件left≤right时：mid=left+(right-left)//2。\n'
             f'3. 比较arr[mid]与target：等于→返回mid；小于→left=mid+1；大于→right=mid-1。\n'
             f'4. 循环结束未返回则目标不存在，返回-1。\n\n'
             f'解析：\n'
             f'二分查找每次将搜索空间减半，O(log n)的时间复杂度。mid的计算用left+(right-left)//2防止整数溢出（Python不会溢出但C++/Java需要注意）。\n\n'
             f'易错提醒：\n'
             f'- 循环条件是left≤right，写成left<right会漏掉最后一轮比较\n'
             f'- 边界更新必须是mid±1，写成mid会导致死循环\n'
             f'- 二分查找要求数组有序，无序数组必须先排序\n'
             f'- 查找第一个/最后一个等于target的位置需要修改等于时的边界更新逻辑'),
        ],
    },
    'linear': {
        'basic': [
            ('线性表操作复杂度分析',
             '分析数组和链表在以下操作上的时间复杂度：(1)按索引随机访问 (2)在末尾插入 (3)在开头插入 (4)删除指定元素（已知指针位置）。',
             f'最终答案：\n'
             f'(1) 随机访问：数组O(1)，链表O(n)——数组通过基地址+偏移直接定位，链表需从头遍历。\n'
             f'(2) 末尾插入：数组O(1)均摊（可能扩容），链表O(1)（有尾指针时）或O(n)（无尾指针时需遍历）。\n'
             f'(3) 开头插入：数组O(n)（需搬移所有元素），链表O(1)（调整head指针即可）。\n'
             f'(4) 删除指定元素（已知指针）：数组O(n)（需搬移后续元素），单链表O(n)（需找到前驱）、双链表O(1)。\n\n'
             f'解题步骤：\n'
             f'1. 数组的内存连续→随机访问O(1)、插入/删除O(n)（需要搬移）。\n'
             f'2. 链表的内存分散→随机访问O(n)、已知位置插入/删除O(1)。\n'
             f'3. 分析时区分"已知指针位置"和"需要先查找位置"——后者还需加上查找的O(n)。\n\n'
             f'解析：\n'
             f'数组和链表是互补的——数组优势在访问、链表优势在插入删除。实际选择取决于场景：读多写少用数组，写多（非末尾）用链表。\n\n'
             f'易错提醒：\n'
             f'- 数组的末尾插入是均摊O(1)，不是严格O(1)（扩容时需要O(n)）\n'
             f'- 链表的"插入"指的是在已知位置后插入，若需要先查找位置则为O(n)\n'
             f'- 单链表删除需要前驱节点，仅知道待删节点本身无法O(1)删除'),
        ],
    },
}


def _extract_practice_sections(sections):
    """Extract just the practice/task sections from a list."""
    return [s for s in sections if s.get('kind') in ('practice', 'task')]


def _fill_missing_practices(sections, topic, cat, lang, existing_practices):
    """Fill in missing practice-answer pairs to reach minimum 5 for 分层练习.

    Adds at least 3 basic + 2 advanced + 1 comprehensive = 5 total.
    Inserts missing practices before the last warning/checklist section, or at the end.
    """
    # Count current level distribution
    basic_count = sum(1 for p in existing_practices if '基础' in (p.get('heading', '') or ''))
    advanced_count = sum(1 for p in existing_practices if '进阶' in (p.get('heading', '') or ''))
    comprehensive_count = sum(1 for p in existing_practices if '综合' in (p.get('heading', '') or ''))

    templates = _PRACTICE_TEMPLATES.get(cat, _PRACTICE_TEMPLATES.get('tree'))

    new_pairs = []
    # Add basic practices
    for i in range(basic_count, 2):
        tmpl = templates['basic'][i % len(templates['basic'])]
        heading, question, answer = tmpl
        level_num = i + 1
        new_pairs.append({
            'kind': 'practice', 'heading': f'基础第{level_num}题', 'content': question
        })
        new_pairs.append({
            'kind': 'answer', 'heading': f'基础第{level_num}题 — 参考答案与解析', 'content': answer
        })

    # Add advanced practices (fallback to basic if no advanced templates)
    adv_templates = templates.get('advanced', templates.get('basic'))
    if adv_templates:
        for i in range(advanced_count, 2):
            tmpl = adv_templates[i % len(adv_templates)]
            heading, question, answer = tmpl
            level_num = i + 1
            new_pairs.append({
                'kind': 'practice', 'heading': f'进阶第{level_num}题', 'content': question
            })
            new_pairs.append({
                'kind': 'answer', 'heading': f'进阶第{level_num}题 — 参考答案与解析', 'content': answer
            })

    # Add comprehensive practice (fallback chain: comprehensive -> advanced -> basic)
    comp_templates = templates.get('comprehensive', templates.get('advanced', templates.get('basic')))
    if comprehensive_count < 1 and comp_templates:
        tmpl = comp_templates[0]
        heading, question, answer = tmpl
        new_pairs.append({
            'kind': 'practice', 'heading': '综合题', 'content': question
        })
        new_pairs.append({
            'kind': 'answer', 'heading': '综合题 — 参考答案与解析', 'content': answer
        })

    if not new_pairs:
        return sections

    # Insert before the last warning/checklist or at the end
    insert_at = len(sections)
    for i in range(len(sections) - 1, -1, -1):
        if sections[i].get('kind') in ('warning', 'warnings', 'checklist'):
            insert_at = i
            break

    result = sections[:insert_at] + new_pairs + sections[insert_at:]
    return result


# ═══════════════════════════════════════════════════════════════════
# Tags Enforcer — ensures every card has 4-6 knowledge tags
# ═══════════════════════════════════════════════════════════════════

def _ensure_tags_filled(card, gen_context):
    """Ensure every card has at least 4 knowledge tags. Fill from context if empty."""
    tags = card.get('knowledge_points', card.get('tags', []))
    if not isinstance(tags, list):
        tags = []

    if len(tags) >= 4:
        return card

    rtype = card.get('type', '')
    topic = gen_context.get('topic', card.get('knowledge_point', ''))
    lang = gen_context.get('normalized_language', card.get('language', ''))
    cat = _detect_topic_category(topic)

    # Build fresh tags
    new_tags = _build_knowledge_tags(cat, topic, rtype, lang)

    # Merge existing tags (keep unique ones) + new tags, up to 6
    seen = set(tags)
    for t in new_tags:
        if t not in seen and len(tags) < 6:
            tags.append(t)
            seen.add(t)

    # If still too few, add generic DS tags
    fallback_tags = ['数据结构', '算法', '编程练习', '学习资料']
    for t in fallback_tags:
        if t not in seen and len(tags) < 6:
            tags.append(t)
            seen.add(t)

    card['knowledge_points'] = tags
    logger.info("Tags enforcer: filled tags for %r — %s", card.get('title', '')[:40], tags)
    return card


# ═══════════════════════════════════════════════════════════════════
# Main Quality Gate Function
# ═══════════════════════════════════════════════════════════════════

def ensure_teaching_resource_quality(card, gen_context):
    """
    Hard quality gate with section-kind-level validation.

    Two-phase approach:
    Phase 1 — Binary check: if card fails minimum thresholds, replace with
             deterministic template.
    Phase 2 — Section enforcement (ALWAYS runs): ensures required section
             kinds exist, fills missing ones, and ensures tags are populated.
    """
    if not isinstance(card, dict):
        return card

    rtype = card.get('type', '')
    sections = card.get('sections', []) or []
    all_text = _extract_text(sections)
    char_count = _cn_len(all_text)
    kinds = _get_section_kinds(sections)

    logger.info(
        "Quality gate: type=%r title=%r chars=%d sections=%d kinds=%s",
        rtype, card.get('title', ''), char_count, len(sections), kinds
    )

    # ═══ Phase 1: Binary gate — replace if critically deficient ═══

    if rtype == '图解讲解':
        has_diagram_kind = _has_diagram_section(sections)
        has_steps_or_example = _has_section_kind(sections, 'steps') or _has_section_kind(sections, 'example')
        has_highlight = _has_section_kind(sections, 'highlight') or _has_section_kind(sections, 'text')
        enough_content = char_count >= 300

        if not has_diagram_kind or not enough_content:
            logger.warning(
                "Quality gate FAIL for 图解讲解: diagram_kind=%s steps=%s highlight=%s chars=%d — REPLACING",
                has_diagram_kind, has_steps_or_example, has_highlight, char_count
            )
            card = _build_visual_diagram_card(gen_context)

    elif rtype == '代码示例':
        has_code_kind = _has_code_block(sections) or _has_section_kind(sections, 'code')
        has_complexity_kind = _has_section_kind(sections, 'complexity')
        enough_content = char_count >= 250

        if not has_code_kind or not enough_content:
            logger.warning(
                "Quality gate FAIL for 代码示例: code_kind=%s complexity_kind=%s chars=%d — REPLACING",
                has_code_kind, has_complexity_kind, char_count
            )
            card = _build_code_example_card(gen_context)

    elif rtype == '分层练习':
        practice_count = _count_section_kind(sections, 'practice')
        answer_count = _count_section_kind(sections, 'answer')
        enough_content = char_count >= 300

        if practice_count < 2 or not enough_content:
            logger.warning(
                "Quality gate FAIL for 分层练习: practice=%d answer=%d chars=%d — REPLACING",
                practice_count, answer_count, char_count
            )
            card = _build_practice_card(gen_context)

    elif rtype == '易错点':
        error_count = _count_error_points(sections)
        enough_content = char_count >= 200

        if error_count < 2 or not enough_content:
            logger.warning(
                "Quality gate FAIL for 易错点: errors=%d chars=%d — REPLACING",
                error_count, char_count
            )
            card = _build_mistake_card(gen_context)

    elif rtype == '项目案例':
        has_steps_kind = _has_project_steps(sections)
        has_eval_kind = _has_section_kind(sections, 'evaluation')
        enough_content = char_count >= 300

        if not has_steps_kind or not enough_content:
            logger.warning(
                "Quality gate FAIL for 项目案例: steps=%s eval=%s chars=%d — REPLACING",
                has_steps_kind, has_eval_kind, char_count
            )
            card = _build_project_card(gen_context)

    # ═══ Phase 2: Section enforcement (always runs) ═══
    card = _enforce_section_structure(card, gen_context)

    # ═══ Phase 3: Tag enforcement (always runs) ═══
    card = _ensure_tags_filled(card, gen_context)

    return card
