import type { ResourceCard, ResourceGenerateResponse, ResourceGenerateParams, ResourceSection } from '../types'

// ========== Topic normalization ==========

const TOPIC_ALIASES: Record<string, string> = {
  '二叉树遍历': 'binary-tree', '二叉树': 'binary-tree', '二叉树中序遍历': 'binary-tree',
  '二叉树前序遍历': 'binary-tree', '二叉树后序遍历': 'binary-tree', '二叉树层序遍历': 'binary-tree',
  '树遍历': 'binary-tree', 'tree traversal': 'binary-tree',
  '递归': 'recursion', '递归调用栈': 'recursion', '递归调用': 'recursion',
  '递归函数': 'recursion', '递归思想': 'recursion', 'recursion': 'recursion',
  '数组': 'array', '数组边界': 'array', '数组操作': 'array', 'array': 'array',
  '函数调用': 'function-call', '函数调用栈': 'function-call',
  '排序算法': 'sorting', '排序': 'sorting',
  '进程调度': 'process-scheduling', '调度算法': 'process-scheduling',
}

const TOPIC_DISPLAY_NAMES: Record<string, string> = {
  'recursion': '递归调用栈', 'binary-tree': '二叉树遍历', 'array': '数组操作',
  'sorting': '排序算法', 'function-call': '函数调用', 'process-scheduling': '进程调度',
  'generic': '',
}

// LLM_REPLACE: normalizeKnowledgePointWithLLM(input: string) => string
export function normalizeKnowledgePointMock(input: string): string {
  const trimmed = input.trim()
  if (TOPIC_ALIASES[trimmed]) return TOPIC_ALIASES[trimmed]
  const lower = trimmed.toLowerCase()
  for (const [key, value] of Object.entries(TOPIC_ALIASES)) {
    if (lower.includes(key.toLowerCase()) || key.toLowerCase().includes(lower)) return value
  }
  return 'generic'
}

// LLM_REPLACE: inferRelatedCourseWithLLM(input: string, selectedCourse: string) => string
export function inferRelatedCourseMock(input: string, selectedCourse: string): string {
  const topic = normalizeKnowledgePointMock(input)
  if (topic === 'binary-tree' || topic === 'recursion' || topic === 'sorting') return '数据结构与算法'
  if (topic === 'array' || topic === 'function-call') return '数据结构与算法'
  if (topic === 'process-scheduling') return '数据结构与算法'
  return selectedCourse
}

// ========== Resource type metadata ==========

const TYPE_META: { key: string; difficulty: string; language: string; estimated_time: string; teaching_style: string }[] = [
  { key: '个性化讲解文档', difficulty: '基础', language: 'Python', estimated_time: '20 分钟', teaching_style: '图示优先 + 分步骤解释' },
  { key: '知识点思维导图', difficulty: '基础', language: '无', estimated_time: '10 分钟', teaching_style: '图示优先' },
  { key: '代码示例与注释', difficulty: '基础', language: 'Python', estimated_time: '25 分钟', teaching_style: '示例驱动 + 代码案例' },
  { key: '分层练习题', difficulty: '入门→进阶', language: 'Python', estimated_time: '45 分钟', teaching_style: '分步骤解释' },
  { key: '拓展阅读资料', difficulty: '进阶', language: '无', estimated_time: '20 分钟', teaching_style: '示例驱动' },
  { key: '项目式学习案例', difficulty: '综合', language: 'Python', estimated_time: '60 分钟', teaching_style: '项目案例 + 分步骤解释' },
]

// ========== Type-specific detail content builder ==========

interface DetailContent {
  learning_objectives: string
  sections: ResourceSection[]
  key_concepts: string[]
  learning_tips: string[]
  recommended_usage: string
  profile_dimension: string
  next_steps: string
}

function buildBinaryTreeDetail(type: string): DetailContent {
  switch (type) {
    case '个性化讲解文档':
      return {
        learning_objectives: '理解前序、中序、后序遍历的访问顺序，掌握递归遍历的基本思想和调用过程。',
        sections: [
          {
            heading: '前序遍历：根 → 左 → 右',
            content: '先访问根节点，再递归遍历左子树，最后递归遍历右子树。记忆口诀："根左右"。每次遇到一个节点，先处理它，再处理它的子节点。',
            codeBlock: 'def preorder(root):\n    if root is None:\n        return\n    print(root.val, end=\' \')  # 先访问根\n    preorder(root.left)        # 再遍历左子树\n    preorder(root.right)       # 最后遍历右子树',
            language: 'python',
          },
          {
            heading: '中序遍历：左 → 根 → 右',
            content: '先递归遍历左子树，再访问根节点，最后递归遍历右子树。对于二叉搜索树（BST），中序遍历结果是从小到大有序的。记忆口诀："左根右"。',
            codeBlock: 'def inorder(root):\n    if root is None:\n        return\n    inorder(root.left)         # 先遍历左子树\n    print(root.val, end=\' \')  # 再访问根\n    inorder(root.right)        # 最后遍历右子树',
            language: 'python',
          },
          {
            heading: '后序遍历：左 → 右 → 根',
            content: '先递归遍历左右子树，最后访问根节点。应用于删除树（先删子节点再删父节点）、表达式树求值。记忆口诀："左右根"。',
            codeBlock: 'def postorder(root):\n    if root is None:\n        return\n    postorder(root.left)       # 先遍历左子树\n    postorder(root.right)      # 再遍历右子树\n    print(root.val, end=\' \')  # 最后访问根',
            language: 'python',
          },
          {
            heading: '层序遍历：逐层从左到右',
            content: '使用队列实现广度优先搜索（BFS），从上到下、从左到右逐层访问每个节点。',
            codeBlock: 'from collections import deque\ndef levelorder(root):\n    if root is None: return\n    q = deque([root])\n    while q:\n        node = q.popleft()\n        print(node.val, end=\' \')\n        if node.left: q.append(node.left)\n        if node.right: q.append(node.right)',
            language: 'python',
          },
        ],
        key_concepts: ['前序遍历', '中序遍历', '后序遍历', '层序遍历', '递归调用栈'],
        learning_tips: ['递归出口（root is None）是终止条件，忘记写会导致栈溢出', '画一棵3-5个节点的小树，手动模拟每种遍历的访问顺序', '四种遍历的命名中"前/中/后"指的是根节点的访问位置'],
        recommended_usage: '先看图示理解遍历路径，再手动画一棵三层二叉树，用不同颜色标出每种遍历的访问顺序，最后对照代码验证。',
        profile_dimension: '学生偏好图示讲解和分步骤解释，薄弱点为递归出口和遍历顺序，本资源用图示+口诀+代码三重方式覆盖。',
        next_steps: '完成本资源后，进入"知识点思维导图"梳理结构关系，再完成"遍历顺序判断题"自测理解程度。',
      }

    case '知识点思维导图':
      return {
        learning_objectives: '建立二叉树、递归、遍历顺序之间的结构关系，形成清晰的知识网络。',
        sections: [
          {
            heading: '二叉树遍历 — 知识体系',
            content: '中心节点：二叉树遍历\n\n分支一：深度优先遍历（DFS）\n  ├── 前序遍历（根→左→右）→ 应用：复制树、前缀表达式\n  ├── 中序遍历（左→根→右）→ 应用：BST 有序输出\n  └── 后序遍历（左→右→根）→ 应用：删除树、表达式求值\n\n分支二：广度优先遍历（BFS）\n  └── 层序遍历 → 应用：按层处理、最短路径\n\n分支三：实现方式\n  ├── 递归实现（代码简洁，需注意递归出口）\n  └── 迭代实现（用栈/队列模拟，帮助理解调用栈）\n\n分支四：常见错误\n  ├── 忘记递归出口 → 栈溢出\n  ├── 遍历顺序混淆\n  └── 空树未处理',
          },
        ],
        key_concepts: ['DFS', 'BFS', '递归与迭代', '四种遍历顺序', '调用栈'],
        learning_tips: ['"前/中/后"是指根节点在第几位被访问', '建议对照代码一起看，加深记忆'],
        recommended_usage: '先看整体结构把握全貌，再对照"个性化讲解文档"中的代码，逐个分支理解，最后尝试自己画出思维导图。',
        profile_dimension: '学生需要区分遍历顺序和递归调用过程，思维导图将四种遍历的差异可视化。',
        next_steps: '进入"代码示例与注释"，将导图中的每个分支对应到具体代码实现。',
      }

    case '代码示例与注释':
      return {
        learning_objectives: '能读懂并修改 Python 二叉树遍历代码，理解递归与迭代两种实现方式。',
        sections: [
          {
            heading: '二叉树节点定义',
            content: '首先定义二叉树的节点结构，每个节点包含值和左右子节点引用。',
            codeBlock: 'class TreeNode:\n    """二叉树节点"""\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val      # 节点值\n        self.left = left    # 左子节点\n        self.right = right  # 右子节点',
            language: 'python',
          },
          {
            heading: '前序遍历 — 递归 + 迭代',
            content: '递归版直观简洁，适合理解遍历思想；迭代版用栈模拟递归过程，帮助理解调用栈。',
            codeBlock: '# === 递归版（推荐先理解这个）===\ndef preorder_rec(root):\n    if root is None:          # 递归出口\n        return []\n    return [root.val] + preorder_rec(root.left) + preorder_rec(root.right)\n\n# === 迭代版（栈模拟调用栈）===\ndef preorder_it(root):\n    if root is None: return []\n    res, stack = [], [root]\n    while stack:\n        node = stack.pop()     # 弹出栈顶\n        res.append(node.val)   # 访问节点\n        if node.right: stack.append(node.right)  # 先压右\n        if node.left: stack.append(node.left)    # 再压左\n    return res',
            language: 'python',
          },
          {
            heading: '中序遍历 — 迭代版',
            content: '沿左子树一路走到底，再回溯访问。这是面试常考点。',
            codeBlock: 'def inorder_it(root):\n    res, stack, curr = [], [], root\n    while curr or stack:\n        while curr:               # 一路向左\n            stack.append(curr)\n            curr = curr.left\n        curr = stack.pop()        # 回溯访问\n        res.append(curr.val)\n        curr = curr.right         # 转向右子树\n    return res',
            language: 'python',
          },
          {
            heading: '测试用例',
            content: '用下面的测试树验证你对遍历的理解：',
            codeBlock: '# 构建测试树:\n#       1\n#      / \\\n#     2   3\n#    / \\\n#   4   5\nroot = TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3))\nprint("前序:", preorder_rec(root))   # [1, 2, 4, 5, 3]\nprint("中序:", inorder_it(root))    # [4, 2, 5, 1, 3]',
            language: 'python',
          },
        ],
        key_concepts: ['递归出口', '调用栈', '栈模拟递归', '迭代遍历'],
        learning_tips: ['先运行代码看结果，再对照注释理解每一行', '在编辑器中打断点，单步观察 stack 的变化', '尝试修改测试树的结构，观察输出如何变化'],
        recommended_usage: '先运行代码观察输出，再改变节点顺序（如把4和5互换）观察输出变化，加深对遍历顺序的理解。',
        profile_dimension: '学生会 Python，偏好代码案例学习，薄弱点为函数调用顺序。代码逐行注释直击这些需求。',
        next_steps: '完成"代码补全题"练习，在给定框架代码中补全缺失的遍历函数。',
      }

    case '分层练习题':
      return {
        learning_objectives: '从基础判断逐步过渡到代码补全，巩固遍历顺序理解和递归编程能力。',
        sections: [
          {
            heading: '🟢 基础层：遍历顺序判断（3题）',
            content: '题1：二叉树 [3, 9, 20, null, null, 15, 7] 的前序遍历结果是什么？\n  A. [3, 9, 20, 15, 7]  B. [9, 3, 15, 20, 7]  C. [3, 9, 15, 20, 7]\n\n题2：递归出口判断 — 以下代码缺少什么？\n  def traverse(root):\n      print(root.val)\n      traverse(root.left)\n      traverse(root.right)\n\n题3：判断对错："中序遍历 BST 得到的结果是从小到大有序的。"',
          },
          {
            heading: '🟡 进阶层：代码补全（3题）',
            content: '题4：补全后序遍历的递归实现（请在 ____ 处填入正确代码）\n  def postorder(root):\n      if ____: return\n      postorder(____)\n      postorder(____)\n      print(root.val)\n\n题5：补全层序遍历的队列操作\n题6：实现 count_nodes(root) 统计二叉树节点总数',
          },
          {
            heading: '🔴 提高层：综合应用（2题）',
            content: '题7：判断两棵二叉树是否完全相同（结构和值都相等）\n题8：实现二叉树的镜像翻转（交换每个节点的左右子树）',
          },
        ],
        key_concepts: ['遍历顺序判断', '递归出口', '代码补全', '树的比较', '镜像翻转'],
        learning_tips: ['基础层全做，进阶层至少做2题，提高层选做1题', '每道题先自己思考，再看提示', '注意空节点的处理——这是大多数bug的来源'],
        recommended_usage: '按顺序完成三层练习：先做基础层的遍历顺序选择题和判断题，再做进阶层代码补全，最后挑战提高层综合题。',
        profile_dimension: '学生容易在递归出口和遍历顺序上出错，基础层针对遍历顺序，进阶层针对递归出口设计。',
        next_steps: '完成练习后查看错题反馈，针对薄弱点复习"个性化讲解文档"中对应部分。',
      }

    case '拓展阅读资料':
      return {
        learning_objectives: '了解二叉树遍历的进阶方向，建立从基础到进阶的学习路径意识。',
        sections: [
          {
            heading: '方向一：递归调用栈深入理解',
            content: '深入理解每次递归调用时栈帧的创建与销毁过程。使用 Python 的 traceback 模块或调试器观察调用栈的变化，理解"递归出口"是如何终止递归链的。',
          },
          {
            heading: '方向二：非递归（迭代）遍历',
            content: '使用栈和队列替代递归实现遍历。这是面试常考内容，也是理解"递归本质上是栈"的最好方式。建议先用纸笔模拟栈操作，再写代码验证。',
          },
          {
            heading: '方向三：表达式树与后序遍历',
            content: '数学表达式可以表示为二叉树：叶子节点是操作数，内部节点是运算符。后序遍历表达式树恰好得到后缀表达式，可直接用于求值。这是遍历在编译原理中的实际应用。',
          },
          {
            heading: '方向四：文件目录树遍历',
            content: '操作系统的文件系统是一个树结构。用前序遍历可以"先访问文件夹再进入子文件夹"，用后序遍历可以"先处理子文件夹再处理父文件夹"（如计算目录大小）。',
          },
          {
            heading: '方向五：树结构在搜索中的应用',
            content: '二叉搜索树（BST）、平衡树（AVL）、B树等变体在数据库索引、文件系统中有广泛应用，核心操作都离不开遍历。',
          },
        ],
        key_concepts: ['调用栈', '迭代遍历', '表达式树', '文件目录树', 'BST应用'],
        learning_tips: ['不需要一次读完所有方向，选择最感兴趣的一个深入', '每个方向都建议配合代码实践，不要只看理论'],
        recommended_usage: '完成基础学习后，选择一个感兴趣的方向（建议从"非递归遍历"或"文件目录树"开始），配合代码实践深入探索。',
        profile_dimension: '学生掌握基础后可以进入进阶主题。建议优先选择"递归调用栈"方向，匹配薄弱点。',
        next_steps: '尝试"文件目录树遍历"项目案例，将遍历知识应用到真实场景中。',
      }

    case '项目式学习案例':
      return {
        learning_objectives: '把二叉树遍历迁移到真实场景，通过简化"文件目录树遍历"项目提升综合实践能力。',
        sections: [
          {
            heading: '项目概述：文件目录树遍历工具',
            content: '设计一个简化版文件目录树遍历工具。\n\n输入：目录结构的 JSON 表示\n输出：按指定遍历顺序排列的文件路径列表\n\n你将练习：树结构定义、递归遍历、前序/后序的实际应用区别。',
          },
          {
            heading: '第一阶段：定义目录树结构',
            content: '用 TreeNode 类表示目录树：节点名称为文件/文件夹名，is_folder 标记是否为文件夹，children 列表存储子节点。',
            codeBlock: 'class DirNode:\n    def __init__(self, name, is_folder=False):\n        self.name = name\n        self.is_folder = is_folder\n        self.children = []  # 子文件/子文件夹\n\n# 示例目录结构:\n# project/\n# ├── src/\n# │   ├── main.py\n# │   └── utils.py\n# └── README.md',
            language: 'python',
          },
          {
            heading: '第二阶段：实现前序遍历列出文件',
            content: '前序遍历：先访问当前文件夹，再递归遍历子节点。输出格式为带缩进的文件树。',
            codeBlock: 'def list_files_preorder(node, depth=0):\n    """前序遍历：先访问当前节点，再遍历子节点"""\n    indent = "  " * depth\n    print(f"{indent}{node.name}")\n    for child in node.children:\n        list_files_preorder(child, depth + 1)',
            language: 'python',
          },
          {
            heading: '第三阶段：实现后序遍历计算目录大小',
            content: '后序遍历：先递归计算子节点大小，再汇总到当前节点。这正是操作系统计算文件夹大小的方式。',
            codeBlock: 'def calc_size_postorder(node):\n    """后序遍历：先算子节点，再汇总"""\n    if not node.is_folder:\n        return 100  # 假设每个文件100KB\n    total = 0\n    for child in node.children:\n        total += calc_size_postorder(child)\n    print(f"文件夹 {node.name}: {total}KB")\n    return total',
            language: 'python',
          },
        ],
        key_concepts: ['目录树建模', '前序遍历应用', '后序遍历应用', '递归汇总'],
        learning_tips: ['先画目录树结构图，再写递归函数', '对比前序和后序在这个项目中的不同作用', '尝试增加新功能：按文件名搜索、统计文件数量'],
        recommended_usage: '先画出示例目录树的结构图，标注每种遍历的访问顺序，再对照代码实现。最后尝试修改目录结构看输出变化。',
        profile_dimension: '学生需要通过小项目提升实践能力，薄弱点为递归出口和函数调用顺序。项目中的递归函数有明确的终止条件和调用链。',
        next_steps: '加入学习路径，完成项目全部三个阶段，并尝试增加"按文件名搜索"扩展功能。',
      }

    default:
      return {
        learning_objectives: '',
        sections: [],
        key_concepts: [],
        learning_tips: [],
        recommended_usage: '',
        profile_dimension: '',
        next_steps: '',
      }
  }
}

function buildRecursionDetail(type: string): DetailContent {
  switch (type) {
    case '个性化讲解文档':
      return {
        learning_objectives: '理解递归的基本原理：基准情形、递归情形和调用栈的工作过程。',
        sections: [
          {
            heading: '什么是递归？',
            content: '递归是函数调用自身来解决问题的方法。每个递归必须包含两个要素：基准情形（停止条件）和递归情形（缩小问题规模）。',
            codeBlock: 'def factorial(n):\n    if n <= 1:        # 基准情形\n        return 1\n    return n * factorial(n - 1)  # 递归情形',
            language: 'python',
          },
          {
            heading: '调用栈的可视化理解',
            content: '每次递归调用都会在调用栈上压入一个新的栈帧。以 factorial(3) 为例：\n\nfactorial(3) → 等待 factorial(2)\n  factorial(2) → 等待 factorial(1)\n    factorial(1) → 返回 1\n  factorial(2) → 返回 2\nfactorial(3) → 返回 6\n\n当到达基准情形时，调用栈开始逐层弹出并返回结果。',
          },
          {
            heading: '常见递归模式',
            content: '1. 线性递归：每次调用只产生一个递归调用（阶乘、斐波那契）\n2. 二分递归：每次产生两个递归调用（二叉树遍历、归并排序）\n3. 尾递归：递归调用是函数最后一步（可被编译器优化）',
          },
        ],
        key_concepts: ['基准情形', '递归情形', '调用栈', '栈帧', '尾递归'],
        learning_tips: ['画图追踪每次递归调用时的参数和返回值', '调试时观察调用栈面板，理解栈帧的创建和销毁'],
        recommended_usage: '先用阶乘理解递归的基本结构，再画调用栈图追踪过程，最后尝试斐波那契数列加深理解。',
        profile_dimension: '学生偏好图示讲解和分步骤解释，薄弱点为递归出口和函数调用顺序。',
        next_steps: '完成"递归调用栈判断题"，验证对调用栈的理解。',
      }

    case '知识点思维导图':
      return {
        learning_objectives: '建立递归的知识体系全景图，理清基准情形、递归情形、调用栈和常见模式之间的关联。',
        sections: [
          {
            heading: '递归 — 知识体系',
            content: '中心节点：递归\n\n分支一：核心要素\n  ├── 基准情形（停止条件）— 防止无限递归\n  └── 递归情形（缩小规模）— 向基准情形逼近\n\n分支二：调用栈\n  ├── 每次递归调用压入栈帧\n  ├── 到达基准情形后逐层弹出\n  └── 栈溢出：缺少或错误的基准情形\n\n分支三：常见模式\n  ├── 线性递归（阶乘、链表遍历）\n  ├── 二分递归（二叉树、归并排序）\n  └── 尾递归（编译器可优化为循环）\n\n分支四：常见错误\n  ├── 忘记基准情形 → 无限递归\n  ├── 递归情形未缩小规模\n  └── 混淆递归与迭代的适用场景',
          },
        ],
        key_concepts: ['基准情形', '递归情形', '调用栈', '尾递归', '分治思想'],
        learning_tips: ['对照思维导图，用自己的话解释每个分支的含义'],
        recommended_usage: '先看整体结构，再逐一对照代码实例理解每个分支的具体含义。',
        profile_dimension: '学生需要理清递归调用过程和函数调用顺序，思维导图将抽象概念结构化。',
        next_steps: '进入"代码示例与注释"，用具体代码验证思维导图中的每个概念。',
      }

    case '代码示例与注释':
      return {
        learning_objectives: '能读懂并修改经典递归代码，掌握阶乘、斐波那契、汉诺塔、二分查找等常见递归实现。',
        sections: [
          {
            heading: '示例1：阶乘（线性递归）',
            content: '最简单的递归示例，帮助理解基准情形和递归情形。',
            codeBlock: 'def factorial(n):\n    if n <= 1:        # 基准情形：n=0或1时停止\n        return 1\n    return n * factorial(n - 1)  # 递归情形：n! = n × (n-1)!',
            language: 'python',
          },
          {
            heading: '示例2：斐波那契数列（二分递归）',
            content: '每次产生两个递归调用。注意：此实现有重复计算问题，可用记忆化优化。',
            codeBlock: 'def fib(n):\n    if n <= 1:        # 基准情形\n        return n\n    return fib(n - 1) + fib(n - 2)  # 两个递归调用',
            language: 'python',
          },
          {
            heading: '示例3：汉诺塔（经典递归问题）',
            content: '将n个盘子从A柱移到C柱，借助B柱。递归思想：先移n-1个盘子到辅助柱，再移最大的盘子到目标柱。',
            codeBlock: 'def hanoi(n, src, aux, dst):\n    if n == 1:                    # 基准情形：只有1个盘子\n        print(f"{src} → {dst}")\n        return\n    hanoi(n-1, src, dst, aux)     # 将n-1个移到辅助柱\n    print(f"{src} → {dst}")        # 移最大的盘子\n    hanoi(n-1, aux, src, dst)     # 将n-1个移到目标柱',
            language: 'python',
          },
        ],
        key_concepts: ['线性递归', '二分递归', '汉诺塔', '记忆化', '递归深度'],
        learning_tips: ['先运行代码观察输出，再打断点跟踪调用栈', '尝试在纸上画出 fib(4) 的完整调用树'],
        recommended_usage: '先运行代码观察输出，再在编辑器中打断点单步跟踪调用栈的变化，最后尝试修改参数观察行为。',
        profile_dimension: '学生会 Python，偏好代码案例。代码包含多种递归模式，匹配不同学习阶段。',
        next_steps: '完成"递归代码补全题"，在框架代码中补全缺失的递归函数。',
      }

    case '分层练习题':
      return {
        learning_objectives: '从基础递归判断逐步过渡到分治算法，巩固递归思维和编程能力。',
        sections: [
          {
            heading: '🟢 基础层：递归理解（3题）',
            content: '题1：以下代码的基准情形是什么？\n  def mystery(n):\n      if n < 10: return n\n      return n % 10 + mystery(n // 10)\n\n题2：写出 fib(5) 的完整调用树\n\n题3：判断对错："尾递归可以被编译器优化为循环"',
          },
          {
            heading: '🟡 进阶层：代码补全（3题）',
            content: '题4：补全二分查找的递归实现\n题5：补全归并排序的合并步骤\n题6：实现递归版反转链表',
          },
          {
            heading: '🔴 提高层：综合应用（2题）',
            content: '题7：实现全排列生成（回溯算法）\n题8：N皇后问题 — 在N×N棋盘上放置N个皇后使其互不攻击',
          },
        ],
        key_concepts: ['基准情形识别', '调用树', '分治算法', '回溯算法'],
        learning_tips: ['基础层全做，进阶层至少做2题', '回溯类问题先画决策树，再写代码'],
        recommended_usage: '按顺序完成三层练习：先做基础层理解递归，再做进阶层巩固编程，最后挑战回溯算法。',
        profile_dimension: '学生容易在递归出口和函数调用顺序上出错，基础层重点考察这两个方面。',
        next_steps: '完成练习后查看错题反馈，巩固薄弱环节。',
      }

    case '拓展阅读资料':
      return {
        learning_objectives: '了解递归的进阶方向：尾递归优化、递归与迭代的转换、记忆化搜索与动态规划。',
        sections: [
          {
            heading: '方向一：尾递归优化',
            content: '尾递归是指递归调用是函数最后一步操作。编译器可以将尾递归优化为循环，避免栈溢出。Python 默认不支持尾递归优化，但可以通过理解尾递归来写出更高效的递归代码。',
          },
          {
            heading: '方向二：递归与迭代的转换',
            content: '任何递归都可以转换为迭代（使用显式栈）。理解这种转换是掌握递归本质的关键。建议尝试将阶乘和斐波那契的递归版改写为迭代版。',
          },
          {
            heading: '方向三：记忆化搜索',
            content: '当递归出现大量重复计算时（如斐波那契），可以使用字典缓存已计算的结果，将时间复杂度从指数降到线性。这是动态规划的基础。',
          },
          {
            heading: '方向四：分治算法',
            content: '分治是递归思想的重要应用：将大问题分解为小问题，递归求解后合并结果。归并排序、快速排序都是经典的分治算法。',
          },
          {
            heading: '方向五：回溯算法',
            content: '回溯是一种系统搜索解空间的方法，通过递归尝试所有可能的选择，在遇到死路时回退。全排列、N皇后、数独求解都是经典的回溯问题。',
          },
        ],
        key_concepts: ['尾递归', '迭代转换', '记忆化', '分治', '回溯'],
        learning_tips: ['不需要一次学完所有方向', '建议优先学习"记忆化搜索"，它与动态规划直接相关'],
        recommended_usage: '完成基础学习后，选择一个方向深入。建议优先学习"记忆化搜索"，为后续数据结构课程中的动态规划做准备。',
        profile_dimension: '学生掌握基础递归后可进入进阶主题。建议优先学习尾递归和记忆化，匹配函数调用顺序的薄弱点。',
        next_steps: '尝试将斐波那契的递归版用记忆化搜索改写，对比运行时间。',
      }

    case '项目式学习案例':
      return {
        learning_objectives: '将递归应用到真实场景，实现文件系统目录树遍历工具。',
        sections: [
          {
            heading: '项目概述：文件系统目录遍历工具',
            content: '实现一个简化版目录遍历工具。\n\n功能一：递归列出目录下所有文件（前序遍历）\n功能二：计算目录大小（后序遍历）\n功能三：按文件名搜索（递归+条件判断）',
          },
          {
            heading: '第一阶段：定义目录结构',
            content: '用递归数据结构表示目录树：每个节点有名称、是否文件夹、子节点列表。',
            codeBlock: 'class DirNode:\n    def __init__(self, name, is_folder=False):\n        self.name = name\n        self.is_folder = is_folder\n        self.children = []',
            language: 'python',
          },
          {
            heading: '第二阶段：实现递归遍历',
            content: '用递归实现列出所有文件、计算目录大小、搜索文件三个功能。',
            codeBlock: 'def list_all(node, depth=0):\n    print("  " * depth + node.name)\n    for child in node.children:\n        list_all(child, depth + 1)\n\ndef search(node, keyword):\n    results = []\n    if keyword in node.name:\n        results.append(node.name)\n    for child in node.children:\n        results.extend(search(child, keyword))\n    return results',
            language: 'python',
          },
        ],
        key_concepts: ['目录树建模', '递归列出', '递归搜索', '后序汇总'],
        learning_tips: ['先画目录结构图，再写递归函数', '对比"列出"和"搜索"两个功能的递归差异'],
        recommended_usage: '先画目录树结构图，标注递归的访问顺序，再实现各个功能。最后尝试用真实目录结构测试。',
        profile_dimension: '学生需要通过小项目提升实践能力。项目中的递归函数有明确的终止条件（叶子节点）和递归链。',
        next_steps: '加入学习路径，完成全部功能，并尝试增加"统计文件类型分布"扩展功能。',
      }

    default:
      return { learning_objectives: '', sections: [], key_concepts: [], learning_tips: [], recommended_usage: '', profile_dimension: '', next_steps: '' }
  }
}

function buildGenericDetail(type: string, displayTopic: string): DetailContent {
  const sections: Record<string, ResourceSection[]> = {
    '个性化讲解文档': [
      { heading: `什么是${displayTopic}？`, content: `围绕"${displayTopic}"的核心概念与基本原理，结合当前学习者的学习画像，提供个性化的分步骤讲解。内容将根据学生的学习风格自动调整讲解方式。` },
      { heading: '核心要点', content: `本讲解文档聚焦"${displayTopic}"的关键知识点，用图示和示例帮助理解。后续接入大模型后将生成更具体的个性化内容。` },
    ],
    '知识点思维导图': [
      { heading: `${displayTopic} — 知识体系`, content: `中心节点：${displayTopic}\n\n├── 核心概念\n├── 基本原理\n├── 常见应用\n├── 实现方式\n└── 易错点与注意事项\n\n后续接入大模型后将生成更详细的知识体系。` },
    ],
    '代码示例与注释': [
      { heading: `${displayTopic} 代码示例`, content: `提供"${displayTopic}"相关的 Python 代码示例，每行附详细中文注释。当前为通用模板，后续接入大模型后将生成针对性代码。`, codeBlock: `# ${displayTopic} 代码示例（模板）\n# TODO: 接入大模型后根据具体主题生成代码\n\ndef example():\n    """示例函数 — 请根据具体主题替换"""\n    pass`, language: 'python' },
    ],
    '分层练习题': [
      { heading: '🟢 基础层', content: `关于"${displayTopic}"的基础概念题和理解题` },
      { heading: '🟡 进阶层', content: `关于"${displayTopic}"的应用和变体题` },
      { heading: '🔴 提高层', content: `关于"${displayTopic}"的综合挑战题` },
    ],
    '拓展阅读资料': [
      { heading: `${displayTopic} 进阶学习方向`, content: `围绕"${displayTopic}"，推荐探索相关进阶话题和应用场景。后续接入大模型后将根据学生画像提供个性化推荐。` },
      { heading: '建议学习路线', content: `1. 先掌握${displayTopic}的基础概念\n2. 通过代码实践加深理解\n3. 探索进阶话题和工程应用` },
    ],
    '项目式学习案例': [
      { heading: `综合实践：${displayTopic} 项目`, content: `设计一个围绕"${displayTopic}"的小型实战项目，综合运用所学知识。当前为通用模板，后续接入大模型后将生成定制化项目方案。` },
      { heading: '项目要点', content: `1. 明确项目目标和输入输出\n2. 设计数据结构\n3. 实现核心功能\n4. 测试与优化` },
    ],
  }

  const recs: Record<string, string> = {
    '个性化讲解文档': `先阅读${displayTopic}的讲解文档建立概念，再对照思维导图梳理结构。`,
    '知识点思维导图': `先浏览${displayTopic}的整体知识结构，再逐一对照代码实例理解每个分支。`,
    '代码示例与注释': `先运行代码观察输出，再对照注释理解实现细节。`,
    '分层练习题': `按顺序完成三层练习，从基础到进阶逐步巩固${displayTopic}。`,
    '拓展阅读资料': `完成${displayTopic}的基础学习后，选择一个感兴趣的进阶方向深入探索。`,
    '项目式学习案例': `先理解${displayTopic}的项目需求，再分阶段实现，最后测试和优化。`,
  }

  const profileInfo = `学生认知风格：图示优先、示例驱动 | 薄弱点：递归出口、遍历顺序 | 当前学习主题：${displayTopic}`

  return {
    learning_objectives: `掌握"${displayTopic}"的核心概念和基本原理。`,
    sections: sections[type] || [],
    key_concepts: [displayTopic],
    learning_tips: [`建议配合${displayTopic}相关的教材和在线资源一起学习`],
    recommended_usage: recs[type] || `围绕"${displayTopic}"进行系统学习。`,
    profile_dimension: profileInfo,
    next_steps: `完成"${displayTopic}"本资源后，建议进入学习路径规划页面继续学习。`,
  }
}

// ========== Resource summary builder ==========

const SUMMARIES_BT: Record<string, string> = {
  '个性化讲解文档': '针对当前学习者"图示优先"的认知风格，用图示和口诀逐步讲解前序、中序、后序、层序遍历的原理与递归调用过程。',
  '知识点思维导图': '以"二叉树遍历"为中心节点，分支包括四种遍历方式、DFS/BFS对比、递归与迭代实现、常见错误。适合图示优先型学习者。',
  '代码示例与注释': '提供二叉树节点定义、前序/中序/后序遍历的递归与迭代实现，每行附详细注释，包含测试用例。',
  '分层练习题': '三层递进练习：基础层判断遍历顺序，进阶层代码补全，提高层综合应用。每题配有提示。',
  '拓展阅读资料': '五大进阶方向：调用栈深入、非递归遍历、表达式树、文件目录树、树搜索应用。不含虚构链接。',
  '项目式学习案例': '实现文件目录树遍历工具：前序列出文件、后序计算大小、递归搜索。分三阶段完成。',
}

const SUMMARIES_RECURSION: Record<string, string> = {
  '个性化讲解文档': '用调用栈图示逐步讲解递归的核心要素：基准情形、递归情形、栈帧的创建与销毁。包含阶乘、斐波那契等经典示例。',
  '知识点思维导图': '以"递归"为中心节点，分支包括核心要素、调用栈、常见模式、常见错误四大方向。',
  '代码示例与注释': '提供阶乘（线性递归）、斐波那契（二分递归）、汉诺塔（经典递归）的 Python 实现，每行注释。',
  '分层练习题': '三层练习：基础层识别基准情形，进阶层代码补全，提高层回溯算法。',
  '拓展阅读资料': '五大方向：尾递归优化、递归迭代转换、记忆化搜索、分治算法、回溯算法。',
  '项目式学习案例': '实现文件系统目录树遍历工具，用递归实现列出文件、计算大小、按名搜索三项功能。',
}

// ========== Topic-adapted summary function ==========

function getSummary(topic: string, type: string, displayTopic: string): string {
  if (topic === 'binary-tree') return SUMMARIES_BT[type] || `关于${displayTopic}的学习资源。`
  if (topic === 'recursion') return SUMMARIES_RECURSION[type] || `关于${displayTopic}的学习资源。`
  const generic: Record<string, string> = {
    '个性化讲解文档': `围绕"${displayTopic}"的核心概念与原理，结合当前学习者的学习画像，提供个性化的分步骤讲解内容。`,
    '知识点思维导图': `系统梳理"${displayTopic}"的知识体系，以结构化导图帮助建立整体认知。`,
    '代码示例与注释': `提供"${displayTopic}"相关的 Python 代码示例，每行附详细中文注释。`,
    '分层练习题': `从基础到综合的分层练习，帮助逐步掌握"${displayTopic}"。`,
    '拓展阅读资料': `深入拓展"${displayTopic}"的进阶话题、工程应用与学习路线建议。`,
    '项目式学习案例': `通过实际项目综合运用"${displayTopic}"的相关知识，提升实践能力。`,
  }
  return generic[type] || `关于"${displayTopic}"的学习资源。`
}

// ========== LLM placeholder ==========

// LLM_REPLACE: generateResourcesWithLLM(topic: string, course: string, profile: StudentProfile) => ResourceCard[]
// TODO: 后续接入真实大模型，根据学生画像和输入主题动态生成个性化资源
export function generateResourcesWithLLM(_topic: string, _course: string, _profile?: unknown): ResourceCard[] {
  return []
}

// ========== Main generation function ==========

let resourceIdCounter = 100

// LLM_REPLACE: generateResourcesForTopicWithLLM(topic, course, profile, resourceTypes)
export function generateResourcesForTopicMock(
  topic: string,
  course: string,
  resourceTypes: string[],
): ResourceCard[] {
  const normalized = normalizeKnowledgePointMock(topic)
  const displayTopic = TOPIC_DISPLAY_NAMES[normalized] || topic.trim()

  const typeFilter = resourceTypes.length > 0
    ? TYPE_META.filter((t) => resourceTypes.includes(t.key))
    : TYPE_META

  return typeFilter.map((meta) => {
    // Get type-specific detail content
    let detail: DetailContent
    if (normalized === 'binary-tree') {
      detail = buildBinaryTreeDetail(meta.key)
    } else if (normalized === 'recursion') {
      detail = buildRecursionDetail(meta.key)
    } else {
      detail = buildGenericDetail(meta.key, displayTopic)
    }

    const title = `${displayTopic}${meta.key}`

    return {
      id: `res-gen-${resourceIdCounter++}`,
      title,
      type: meta.key,
      course,
      knowledge_point: displayTopic,
      difficulty: meta.difficulty,
      language: meta.language,
      teaching_style: meta.teaching_style,
      summary: getSummary(normalized, meta.key, displayTopic),
      match_reason: `匹配当前学习者的"${meta.teaching_style}"偏好和薄弱点`,
      learning_objectives: detail.learning_objectives,
      sections: detail.sections,
      key_concepts: detail.key_concepts,
      learning_tips: detail.learning_tips,
      recommended_usage: detail.recommended_usage,
      profile_dimension: detail.profile_dimension,
      next_steps: detail.next_steps,
      estimated_time: meta.estimated_time,
      student_name: '当前学习者',
      generated_at: new Date().toLocaleString('zh-CN'),
      added_to_path: false,
    }
  })
}

// ========== Mock API ==========

export function generateResourcesMock(params: ResourceGenerateParams): ResourceCard[] {
  const { course_id, learning_topic, resource_types = [] } = params
  return generateResourcesForTopicMock(learning_topic, course_id, resource_types)
}

export const mockResources: ResourceGenerateResponse = {
  resource_cards: generateResourcesForTopicMock('二叉树遍历', '数据结构与算法', [
    '个性化讲解文档', '知识点思维导图', '代码示例与注释',
    '分层练习题', '拓展阅读资料', '项目式学习案例',
  ]),
}
