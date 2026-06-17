import type { DiagnosisQuestion, AssessmentResult, TutorChatResponse, ConversationContext, PathNode } from '../types'
import type { PathResourceItem } from '../types'
import { loadPathResources } from '../utils/pathResources'

// ========== Challenge Question Type ==========

export interface ChallengeQuestion extends DiagnosisQuestion {
  level: number
  levelName: string
  source: '来自本轮提问' | '来自当前路径' | '来自我的资源包' | '来自画像易错点' | '系统综合推荐'
  source_basis: string
  path_node_title?: string
  path_node_stage?: string
}

// ========== Challenge Result Type ==========

export interface ChallengeResult {
  totalLevels: number
  completedLevels: number
  correctCount: number
  score: number
  growth: { knowledge_base: number; practice_ability: number }
  badges: string[]
  wrongPoints: Array<{ knowledge_point: string; reason: string }>
  levelResults: Record<string, boolean>
}

// =====================================================================
// Keyword → domain mapping for topic detection
// =====================================================================

export const TOPIC_KEYWORDS: Record<string, string[]> = {
  'recursion': ['递归', '调用栈', '出口', '基准情形', '栈帧', '递推'],
  'binary-tree': ['二叉树', '前序', '中序', '后序', '遍历', '层序', '树'],
  'array': ['数组', '下标', '越界', '边界', '列表索引'],
  'linked-list': ['链表', '节点指针', '头结点', '尾结点'],
  'sorting': ['排序', '查找', '搜索', '冒泡', '快速排序', '二分', '归并', '选择排序', '插入排序'],
  'sql': ['sql', '数据库', '索引', '查询', '表连接', 'join', '事务', '增删改查'],
  'function-call': ['函数', '调用', '参数', '返回值', '作用域', '嵌套调用'],
  'debug': ['调试', 'debug', '报错', '错误', '异常', '排错', '排查'],
  'project': ['项目', '实践', '开发', '应用构建', '综合实战'],
}

function detectTopics(input: string): string[] {
  const lower = input.toLowerCase()
  const topics: string[] = []
  for (const [topic, keywords] of Object.entries(TOPIC_KEYWORDS)) {
    if (keywords.some((kw) => lower.includes(kw.toLowerCase()))) {
      topics.push(topic)
    }
  }
  return topics
}

// =====================================================================
// Path node matching — find the best path node for a user question
// =====================================================================

export interface PathNodeMatch {
  node: PathNode
  score: number
  matchedVia: string[]
}

export function findBestPathNode(userQuestion: string, pathNodes: PathNode[]): PathNodeMatch | null {
  if (!pathNodes.length) return null

  const lower = userQuestion.toLowerCase()
  const questionTopics = detectTopics(userQuestion)

  const scored: PathNodeMatch[] = pathNodes.map((node) => {
    const nodeText = [
      node.name,
      node.goal,
      node.reason,
      node.taskDescription,
      ...node.keywords,
      ...node.learningObjectives,
    ].join(' ').toLowerCase()

    let score = 0
    const matchedVia: string[] = []

    // Check keyword overlap from TOPIC_KEYWORDS
    for (const topic of questionTopics) {
      const keywords = TOPIC_KEYWORDS[topic] || []
      for (const kw of keywords) {
        if (nodeText.includes(kw.toLowerCase())) {
          score += 2
          matchedVia.push(`节点关键词匹配: ${kw}`)
        }
      }
    }

    // Direct keyword match from user question against node keywords
    for (const kw of node.keywords) {
      if (lower.includes(kw.toLowerCase())) {
        score += 3
        matchedVia.push(`用户提问匹配节点关键词: ${kw}`)
      }
    }

    // Match against node name
    if (lower.includes(node.name.toLowerCase()) || node.name.toLowerCase().includes(lower.slice(0, 4))) {
      score += 4
      matchedVia.push(`匹配节点名称: ${node.name}`)
    }

    // Match against stage
    const matchingResources = node.matchedResources.length + node.defaultResources.length
    if (matchingResources > 0 && score > 0) {
      score += 1
      matchedVia.push('节点包含可用资源')
    }

    return { node, score, matchedVia }
  })

  scored.sort((a, b) => b.score - a.score)
  return scored[0]?.score > 0 ? scored[0] : null
}

// =====================================================================
// Question Pool (tagged by knowledge domain)
// =====================================================================

interface PoolQuestion {
  id: string
  levelName: string
  question: string
  options: string[]
  correct: string
  knowledge_point: string
  explanation: string
  tags: string[]
}

const QUESTION_POOL: PoolQuestion[] = [
  // --- recursion ---
  {
    id: 'q-rec-1', levelName: '递归出口判断', tags: ['recursion'],
    question: '递归函数中，基准情形（Base Case）的作用是什么？',
    options: ['A. 加速递归', 'B. 终止递归，防止无限调用', 'C. 创建新节点', 'D. 调整遍历顺序'], correct: 'B',
    knowledge_point: '递归出口', explanation: '基准情形是递归的停止条件，防止函数无限调用自身导致栈溢出。',
  },
  {
    id: 'q-rec-2', levelName: '调用栈理解', tags: ['recursion'],
    question: '每次递归调用时，函数信息存储在哪里？',
    options: ['A. 堆内存', 'B. 调用栈', 'C. 寄存器', 'D. 硬盘'], correct: 'B',
    knowledge_point: '调用栈', explanation: '每次递归调用在调用栈上压入一个栈帧，到达基准情形后逐层弹出返回。',
  },
  {
    id: 'q-rec-3', levelName: '递归深度判断', tags: ['recursion'],
    question: '递归深度过大时，最常见的问题是什么？',
    options: ['A. 程序运行更快', 'B. 栈溢出', 'C. 自动优化', 'D. 内存释放'], correct: 'B',
    knowledge_point: '递归深度', explanation: '递归过深时调用栈空间耗尽，触发栈溢出错误。Python 默认递归深度约 1000 层。',
  },
  {
    id: 'q-rec-4', levelName: '递归出口理解', tags: ['recursion', 'binary-tree'],
    question: '在二叉树递归遍历中，遇到空节点时通常应该怎么处理？',
    options: ['A. 继续访问左子树', 'B. 返回，不再继续递归', 'C. 创建新节点', 'D. 重复访问根节点'], correct: 'B',
    knowledge_point: '递归出口', explanation: '空节点是递归的基准情形。遇到时直接返回，终止当前分支，防止栈溢出。',
  },
  {
    id: 'q-rec-5', levelName: '递归实践', tags: ['recursion', 'function-call'],
    question: '以下阶乘函数 f(5) 的返回值是？\ndef f(n):\n    if n <= 1: return 1\n    return n * f(n - 1)',
    options: ['A. 15', 'B. 24', 'C. 120', 'D. 720'], correct: 'C',
    knowledge_point: '递归实践', explanation: 'f(5)=5×f(4)=5×4×3×2×1=120。每次递归 n 减 1，直到 n=1 触发出口。',
  },

  // --- binary-tree ---
  {
    id: 'q-bt-1', levelName: '前序遍历判断', tags: ['binary-tree'],
    question: '某二叉树根节点为 A，左子节点为 B，右子节点为 C。它的前序遍历结果是？',
    options: ['A. A B C', 'B. B A C', 'C. B C A', 'D. C B A'], correct: 'A',
    knowledge_point: '前序遍历', explanation: '前序遍历（根→左→右）：先访问根节点 A，再遍历左 B，最后右 C，结果为 A B C。',
  },
  {
    id: 'q-bt-2', levelName: '中序遍历判断', tags: ['binary-tree'],
    question: '对于根节点 A、左子节点 B、右子节点 C 的二叉树，中序遍历结果是？',
    options: ['A. A B C', 'B. B A C', 'C. B C A', 'D. C A B'], correct: 'B',
    knowledge_point: '中序遍历', explanation: '中序遍历（左→根→右）：先遍历左 B，再访问根 A，最后右 C，结果为 B A C。',
  },
  {
    id: 'q-bt-3', levelName: '后序遍历判断', tags: ['binary-tree'],
    question: '后序遍历的口诀是什么？',
    options: ['A. 根左右', 'B. 左根右', 'C. 左右根', 'D. 右左根'], correct: 'C',
    knowledge_point: '后序遍历', explanation: '后序遍历（左→右→根）：先递归左右子树，最后处理根节点。口诀"左右根"。',
  },
  {
    id: 'q-bt-4', levelName: '层序遍历理解', tags: ['binary-tree'],
    question: '层序遍历（广度优先遍历）使用什么数据结构辅助实现？',
    options: ['A. 栈', 'B. 队列', 'C. 优先队列', 'D. 数组'], correct: 'B',
    knowledge_point: '层序遍历', explanation: '层序遍历（BFS）使用队列实现，从上到下、从左到右逐层访问每个节点。',
  },
  {
    id: 'q-bt-5', levelName: '遍历选择判断', tags: ['binary-tree', 'recursion'],
    question: '二叉树遍历中，哪种遍历方式最适合"先处理子问题再汇总"的场景？',
    options: ['A. 前序遍历', 'B. 中序遍历', 'C. 后序遍历', 'D. 层序遍历'], correct: 'C',
    knowledge_point: '遍历应用', explanation: '后序遍历先处理左右子树再汇总到根节点，适合需要子问题结果汇总的场景，如计算树的高度。',
  },

  // --- array ---
  {
    id: 'q-arr-1', levelName: '数组下标判断', tags: ['array'],
    question: '在 Python 中，如果列表长度为 n，最后一个元素的下标是？',
    options: ['A. n', 'B. n - 1', 'C. n + 1', 'D. 1'], correct: 'B',
    knowledge_point: '数组下标', explanation: 'Python 列表索引从 0 开始，长度为 n 时有效下标为 0~n-1。',
  },
  {
    id: 'q-arr-2', levelName: '越界判断', tags: ['array'],
    question: '访问 arr[len(arr)] 会导致什么？',
    options: ['A. 返回最后一个元素', 'B. 返回 None', 'C. 抛出 IndexError', 'D. 返回 0'], correct: 'C',
    knowledge_point: '数组越界', explanation: 'len(arr) 超出了有效下标范围 0~len(arr)-1，访问 arr[len(arr)] 会导致越界错误。',
  },
  {
    id: 'q-arr-3', levelName: '循环条件设置', tags: ['array'],
    question: '遍历长度为 n 的数组，正确的循环写法是？',
    options: ['A. for i in range(n+1)', 'B. for i in range(n)', 'C. for i in range(1, n)', 'D. for i in range(-1, n-1)'], correct: 'B',
    knowledge_point: '循环条件', explanation: 'range(n) 生成 0 到 n-1 的整数序列，正好覆盖长度为 n 的数组所有下标。',
  },
  {
    id: 'q-arr-4', levelName: '边界条件判断', tags: ['array'],
    question: '在 while 循环中遍历数组，循环条件通常怎么写？',
    options: ['A. while i <= n', 'B. while i < n', 'C. while i > n', 'D. while i == n'], correct: 'B',
    knowledge_point: '边界条件', explanation: '用 while i < n 保证 i 从 0 到 n-1，不会越界。条件 i <= n 会导致访问 arr[n] 越界。',
  },
  {
    id: 'q-arr-5', levelName: '多维数组判断', tags: ['array'],
    question: '二维数组 arr[2][3] 表示什么？',
    options: ['A. 2个元素，每个是长度为3的数组', 'B. 3行2列的矩阵', 'C. 2行3列的矩阵', 'D. 6个独立元素'], correct: 'C',
    knowledge_point: '数组结构', explanation: 'arr[2][3] 表示 2 行 3 列的矩阵，外层有 2 个子数组，每个子数组有 3 个元素。',
  },

  // --- function-call ---
  {
    id: 'q-fc-1', levelName: '参数传递', tags: ['function-call'],
    question: 'Python 中，以下代码输出什么？\ndef f(x):\n    x = x + 1\n    return x\na = 5\nf(a)\nprint(a)',
    options: ['A. 5', 'B. 6', 'C. None', 'D. 报错'], correct: 'A',
    knowledge_point: '参数传递', explanation: 'Python 中整数是不可变对象，函数内 x 的修改不影响外部变量 a，print(a) 输出 5。',
  },
  {
    id: 'q-fc-2', levelName: '返回值判断', tags: ['function-call'],
    question: '以下代码输出什么？\ndef add(a, b):\n    return a + b\nresult = add(3, 4)\nprint(result)',
    options: ['A. None', 'B. 7', 'C. add(3,4)', 'D. 报错'], correct: 'B',
    knowledge_point: '返回值', explanation: 'add(3, 4) 返回 7，result 被赋值为 7，打印 7。',
  },
  {
    id: 'q-fc-3', levelName: '调用顺序', tags: ['function-call'],
    question: '以下代码的执行顺序是？\ndef a():\n    print("A")\ndef b():\n    a()\n    print("B")\nb()',
    options: ['A. A B', 'B. B A', 'C. A', 'D. B'], correct: 'A',
    knowledge_point: '调用顺序', explanation: 'b() 先调用 a() 打印 A，然后 b() 继续执行打印 B。输出 A B。',
  },
  {
    id: 'q-fc-4', levelName: '作用域判断', tags: ['function-call'],
    question: '函数内部定义的变量属于什么作用域？',
    options: ['A. 全局作用域', 'B. 局部作用域', 'C. 模块作用域', 'D. 内置作用域'], correct: 'B',
    knowledge_point: '作用域', explanation: '函数内部定义的变量是局部变量，只在函数内部有效，外部无法直接访问。',
  },
  {
    id: 'q-fc-5', levelName: '嵌套调用理解', tags: ['function-call'],
    question: '以下代码中，函数 f(3) 会被调用几次？\ndef f(n):\n    if n <= 1: return 1\n    return f(n-1) + f(n-1)',
    options: ['A. 3次', 'B. 4次', 'C. 7次', 'D. 8次'], correct: 'C',
    knowledge_point: '函数调用', explanation: 'f(3)→f(2)+f(2)，每个f(2)→f(1)+f(1)，共调用1次f(3)+2次f(2)+4次f(1)=7次。',
  },

  // --- debug ---
  {
    id: 'q-dbg-1', levelName: '错误定位', tags: ['debug'],
    question: '代码报错信息中通常包含什么？',
    options: ['A. 只有文件名', 'B. 错误类型、行号和堆栈信息', 'C. 只有行号', 'D. 只有错误描述'], correct: 'B',
    knowledge_point: '错误定位', explanation: 'Python 报错信息包含错误类型（如 IndexError）、出错行号和调用堆栈，帮助定位问题。',
  },
  {
    id: 'q-dbg-2', levelName: '递归错误判断', tags: ['debug', 'recursion'],
    question: 'RecursionError 通常表示什么？',
    options: ['A. 递归执行成功', 'B. 递归深度超过限制', 'C. 数组越界', 'D. 语法错误'], correct: 'B',
    knowledge_point: '递归错误', explanation: 'RecursionError 表示递归调用层数超过了 Python 的限制（默认约 1000 层），通常是缺少出口导致。',
  },
  {
    id: 'q-dbg-3', levelName: '调试策略', tags: ['debug'],
    question: '调试代码时，最有效的第一步通常是什么？',
    options: ['A. 重写整个代码', 'B. 仔细阅读报错信息和出错行', 'C. 重启电脑', 'D. 随机删除代码'], correct: 'B',
    knowledge_point: '调试策略', explanation: '先仔细阅读报错信息，定位出错行和错误类型，通常可以快速找到问题所在。',
  },
  {
    id: 'q-dbg-4', levelName: '边界测试', tags: ['debug', 'array'],
    question: '测试函数时，应该重点测试哪些输入？',
    options: ['A. 只有正常输入', 'B. 正常值、边界值和异常值', 'C. 只测边界值', 'D. 不需要测试'], correct: 'B',
    knowledge_point: '边界测试', explanation: '良好的测试应覆盖正常输入、边界条件（如空数组、n=0）和异常输入，确保函数健壮。',
  },
  {
    id: 'q-dbg-5', levelName: '调试技巧', tags: ['debug'],
    question: 'print 调试法指的是什么？',
    options: ['A. 打印所有代码', 'B. 在关键位置插入 print 输出中间值', 'C. 使用打印机输出', 'D. 删除所有 print'], correct: 'B',
    knowledge_point: '调试技巧', explanation: 'print 调试是最简单实用的方法，在关键变量处插入 print 语句，观察中间值是否符合预期。',
  },

  // --- linked-list (Phase 10) ---
  {
    id: 'q-ll-1', levelName: '链表结构判断', tags: ['linked-list'],
    question: '单向链表的每个节点至少包含哪两个部分？',
    options: ['A. 数据和索引', 'B. 数据和指针', 'C. 指针和索引', 'D. 键和值'], correct: 'B',
    knowledge_point: '链表结构', explanation: '单向链表每个节点包含数据域和指向下一个节点的指针域。',
  },
  {
    id: 'q-ll-2', levelName: '链表遍历', tags: ['linked-list'],
    question: '遍历单向链表时，循环的终止条件通常是什么？',
    options: ['A. 当前节点为 None', 'B. 当前节点的 next 为 None', 'C. 计数器等于链表长度', 'D. 到达数组末尾'], correct: 'A',
    knowledge_point: '链表遍历', explanation: '遍历时判断 curr is None 停止，此时已访问完所有节点（包括最后一个节点的 next 为 None 的下一次循环）。',
  },
  {
    id: 'q-ll-3', levelName: '链表插入', tags: ['linked-list'],
    question: '在单向链表中插入新节点时，正确的操作顺序是？',
    options: ['A. 先断链再连新节点', 'B. 新节点先指向后继，再修改前驱指针', 'C. 先修改前驱指针，新节点再指向后继', 'D. 同时修改两个指针'], correct: 'B',
    knowledge_point: '链表插入', explanation: '先让新节点的 next 指向后继节点（防止丢失），再让前驱节点的 next 指向新节点。',
  },
  {
    id: 'q-ll-4', levelName: '链表与数组对比', tags: ['linked-list', 'array'],
    question: '与数组相比，链表的主要优势是什么？',
    options: ['A. 随机访问更快', 'B. 插入删除不需要移动其他元素', 'C. 占用内存更少', 'D. 排序更快'], correct: 'B',
    knowledge_point: '链表特性', explanation: '链表插入删除只需修改指针，而数组需要移动后续所有元素。但链表不支持随机访问。',
  },
  {
    id: 'q-ll-5', levelName: '链表边界情况', tags: ['linked-list'],
    question: '删除单向链表的头结点时，需要做什么特殊处理？',
    options: ['A. 不需要特殊处理', 'B. 将头指针指向第二个节点', 'C. 删除整个链表', 'D. 将尾指针置空'], correct: 'B',
    knowledge_point: '链表删除', explanation: '删除头结点时，需要更新头指针指向原头结点的 next（即第二个节点），否则链表会断开。',
  },

  // --- sorting (Phase 10) ---
  {
    id: 'q-srt-1', levelName: '排序稳定性', tags: ['sorting'],
    question: '归并排序是稳定排序，这意味着什么？',
    options: ['A. 速度最快', 'B. 相等元素的相对顺序保持不变', 'C. 占内存最少', 'D. 不需要递归'], correct: 'B',
    knowledge_point: '排序稳定性', explanation: '稳定排序保证相等元素在排序前后的相对位置不变。归并排序是稳定的，快速排序是不稳定的。',
  },
  {
    id: 'q-srt-2', levelName: '时间复杂度', tags: ['sorting'],
    question: '快速排序的平均时间复杂度是？',
    options: ['A. O(n)', 'B. O(n log n)', 'C. O(n^2)', 'D. O(log n)'], correct: 'B',
    knowledge_point: '算法复杂度', explanation: '快速排序平均 O(n log n)，但最坏情况（已排序数组选到最小/最大基准）为 O(n^2)。',
  },
  {
    id: 'q-srt-3', levelName: '冒泡排序', tags: ['sorting'],
    question: '冒泡排序每一轮遍历后，什么元素会被放到正确的位置？',
    options: ['A. 最小的元素', 'B. 当前未排序部分的最大元素', 'C. 随机元素', 'D. 中间元素'], correct: 'B',
    knowledge_point: '冒泡排序', explanation: '每轮冒泡将当前未排序部分的最大元素"浮"到最后面，因此每轮减少一次比较。',
  },
  {
    id: 'q-srt-4', levelName: '二分查找前提', tags: ['sorting', 'array'],
    question: '使用二分查找的前提条件是什么？',
    options: ['A. 数组已排序', 'B. 数组元素唯一', 'C. 数组长度是 2 的幂', 'D. 使用链表存储'], correct: 'A',
    knowledge_point: '二分查找', explanation: '二分查找要求数组已排序，这样才能通过比较中间值来折半缩小搜索范围。',
  },
  {
    id: 'q-srt-5', levelName: '分治思想', tags: ['sorting', 'recursion'],
    question: '快速排序和归并排序共同体现的核心算法思想是什么？',
    options: ['A. 贪心', 'B. 动态规划', 'C. 分治', 'D. 回溯'], correct: 'C',
    knowledge_point: '分治思想', explanation: '两者都用分治：将大问题分解为小问题独立解决，再合并结果。快速排序先分区再递归，归并排序先递归再合并。',
  },

  // --- sql (Phase 10) ---
  {
    id: 'q-sql-1', levelName: '索引作用', tags: ['sql'],
    question: '数据库索引的主要作用是什么？',
    options: ['A. 增加存储空间', 'B. 加速数据查询', 'C. 自动备份数据', 'D. 加密数据'], correct: 'B',
    knowledge_point: '数据库索引', explanation: '索引类似书的目录，帮助数据库快速定位数据行，避免全表扫描，大幅提升查询速度。',
  },
  {
    id: 'q-sql-2', levelName: '主键约束', tags: ['sql'],
    question: '数据库表中，主键（Primary Key）的特性是什么？',
    options: ['A. 可以重复', 'B. 可以为空', 'C. 唯一且非空', 'D. 自动递增即可'], correct: 'C',
    knowledge_point: '主键约束', explanation: '主键必须满足唯一性（不重复）和非空性，用于唯一标识表中的每一行。',
  },
  {
    id: 'q-sql-3', levelName: 'JOIN 理解', tags: ['sql'],
    question: 'INNER JOIN 的作用是什么？',
    options: ['A. 返回左表所有行', 'B. 返回两个表中匹配的行', 'C. 返回右表所有行', 'D. 返回两表所有行'], correct: 'B',
    knowledge_point: '表连接', explanation: 'INNER JOIN 只返回两个表中满足连接条件的行，不匹配的行不会出现在结果中。',
  },
  {
    id: 'q-sql-4', levelName: '查询优化', tags: ['sql'],
    question: '以下哪种方式能最有效地提升大数据量查询性能？',
    options: ['A. 使用 SELECT *', 'B. 在 WHERE 条件列上创建索引', 'C. 增加更多列', 'D. 每次查询后重启数据库'], correct: 'B',
    knowledge_point: '查询优化', explanation: '在 WHERE、JOIN、ORDER BY 涉及的列上创建索引，是提升查询性能最直接有效的方法。',
  },
  {
    id: 'q-sql-5', levelName: '事务特性', tags: ['sql'],
    question: '数据库事务的 ACID 特性中，A 代表什么？',
    options: ['A. 自动化（Auto）', 'B. 原子性（Atomicity）', 'C. 匿名（Anonymous）', 'D. 异步（Async）'], correct: 'B',
    knowledge_point: '事务特性', explanation: 'ACID 中 A 是原子性：事务中的所有操作要么全部完成，要么全部不执行，保证数据一致性。',
  },
]

const SOURCES: ChallengeQuestion['source'][] = [
  '来自本轮提问', '来自当前路径', '来自我的资源包', '来自画像易错点', '系统综合推荐',
]

// =====================================================================
// Context Inference (Mock)
// =====================================================================

export function inferConversationContextMock(
  userQuestion: string,
  pathNodes?: PathNode[],
): ConversationContext {
  const resources = loadPathResources()

  const topics = detectTopics(userQuestion)

  // Match against learning path if available
  const pathMatch = pathNodes ? findBestPathNode(userQuestion, pathNodes) : null

  // Default weak points — prefer path node info when available
  const weakPoints: string[] = []
  if (pathMatch) {
    // Use the matched path node's keywords as reference for weak points
    weakPoints.push(...pathMatch.node.keywords.slice(0, 2))
  } else {
    if (topics.includes('recursion')) weakPoints.push('递归出口')
    if (topics.includes('binary-tree')) weakPoints.push('遍历顺序')
    if (topics.includes('array')) weakPoints.push('数组边界')
    if (topics.includes('linked-list')) weakPoints.push('指针操作')
    if (topics.includes('sorting')) weakPoints.push('算法选择')
    if (topics.includes('sql')) weakPoints.push('查询优化')
    if (weakPoints.length === 0) {
      weakPoints.push('知识巩固')
    }
  }

  if (topics.length === 0 && !pathMatch) {
    topics.push('binary-tree', 'recursion')
  }

  const questionSummary = userQuestion
    ? (userQuestion.length > 20 ? userQuestion.slice(0, 20) + '…' : userQuestion)
    : '等待输入'

  // Build path node display name
  let pathNodeDisplay: string
  let matchNote: string | undefined
  if (pathMatch) {
    pathNodeDisplay = pathMatch.node.name
    matchNote = undefined
  } else if (pathNodes && pathNodes.length > 0) {
    pathNodeDisplay = '当前未找到匹配节点'
    matchNote = '当前学习路径中暂无完全匹配节点，以下题目基于通用知识点生成'
  } else {
    pathNodeDisplay = topics[0] ? `${topics[0]}相关知识点` : '当前学习节点'
    matchNote = pathNodes && pathNodes.length === 0 ? undefined : '当前未检测到学习路径，题目根据你的提问生成'
  }

  return {
    currentQuestion: questionSummary,
    pathNode: pathNodeDisplay,
    resourceCount: resources.length,
    weakPoints,
    inferredTopics: [...new Set(topics)],
    matchedPathNodeId: pathMatch?.node.id,
    matchedPathNodeTitle: pathMatch?.node.name,
    matchedPathNodeStage: pathMatch?.node.stage,
    pathNodeMatchNote: matchNote,
  }
}

// =====================================================================
// Challenge Generation from Context (Mock)
// =====================================================================

export function generateChallengeByContextMock(
  context: ConversationContext,
  pathNodes?: PathNode[],
): ChallengeQuestion[] {
  const { inferredTopics, matchedPathNodeId, matchedPathNodeTitle, matchedPathNodeStage } = context

  // Find the matched path node if available
  const matchedNode = matchedPathNodeId
    ? (pathNodes || []).find((n) => n.id === matchedPathNodeId) ?? null
    : null

  // Build source_basis for each scenario
  const questionPreview = context.currentQuestion !== '等待输入' ? context.currentQuestion : ''

  // Expand scoring tags: if a path node is matched, boost its keywords
  const pathNodeKeywords = new Set<string>()
  if (matchedNode) {
    for (const kw of matchedNode.keywords) {
      pathNodeKeywords.add(kw.toLowerCase())
    }
    for (const kw of matchedNode.learningObjectives) {
      pathNodeKeywords.add(kw.toLowerCase())
    }
  }

  const scored = QUESTION_POOL.map((q) => {
    let score = q.tags.filter((t) => inferredTopics.includes(t)).length

    // Boost score for questions whose knowledge_point or tags match path node keywords
    if (matchedNode) {
      const qText = (q.knowledge_point + ' ' + q.tags.join(' ') + ' ' + q.levelName).toLowerCase()
      for (const kw of pathNodeKeywords) {
        if (qText.includes(kw)) score += 2
      }
    }

    return { ...q, score }
  })

  scored.sort((a, b) => b.score - a.score)

  // Build a human-readable source_basis
  function buildSourceBasis(): string {
    if (matchedNode && questionPreview) {
      return `依据：你的提问「${questionPreview}」+ 学习路径节点「${matchedNode.name}」（${matchedNode.stage}）`
    }
    if (matchedNode) {
      return `依据：学习路径节点「${matchedNode.name}」（${matchedNode.stage}）`
    }
    if (questionPreview && pathNodes && pathNodes.length > 0) {
      return `依据：你的提问「${questionPreview}」——当前学习路径中暂无完全匹配节点，以下基于通用知识点生成`
    }
    if (questionPreview) {
      return `依据：你的提问「${questionPreview}」——当前未检测到学习路径，题目根据提问关键词生成`
    }
    if (pathNodes && pathNodes.length > 0) {
      return '依据：学习路径综合分析'
    }
    return '依据：通用知识点评估'
  }

  const sourceBasis = buildSourceBasis()

  // If no questions match and no path node match, shuffle and provide fallback
  if (scored.every((q) => q.score === 0)) {
    const shuffled = [...QUESTION_POOL].sort(() => Math.random() - 0.5)
    return shuffled.slice(0, 5).map((q, i) => ({
      id: q.id,
      level: i + 1,
      levelName: q.levelName,
      source: SOURCES[i % SOURCES.length],
      source_basis: sourceBasis,
      path_node_title: matchedNode?.name,
      path_node_stage: matchedNode?.stage,
      question: q.question,
      options: q.options,
      correct: q.correct,
      knowledge_point: q.knowledge_point,
      explanation: q.explanation,
    }))
  }

  const selected: ChallengeQuestion[] = []
  const usedIds = new Set<string>()

  for (let i = 0; i < scored.length && selected.length < 5; i++) {
    const q = scored[i]
    if (usedIds.has(q.id)) continue
    usedIds.add(q.id)
    selected.push({
      id: q.id,
      level: selected.length + 1,
      levelName: q.levelName,
      source: matchedNode ? '来自当前路径' : SOURCES[selected.length],
      source_basis: sourceBasis,
      path_node_title: matchedNode?.name,
      path_node_stage: matchedNode?.stage,
      question: q.question,
      options: q.options,
      correct: q.correct,
      knowledge_point: q.knowledge_point,
      explanation: q.explanation,
    })
  }

  return selected
}

// =====================================================================
// Contextual Example Questions (Mock)
// =====================================================================

export function getContextualExampleQuestions(context: ConversationContext): string[] {
  const { inferredTopics, resourceCount } = context

  const questions: string[] = []

  if (inferredTopics.includes('recursion')) {
    questions.push('递归调用栈为什么容易弄混？')
    questions.push('为什么递归函数一定要有出口？')
  }

  if (inferredTopics.includes('binary-tree')) {
    questions.push('树的前序遍历和中序遍历有什么区别？')
    questions.push('二叉树遍历代码应该怎么写？')
  }

  if (inferredTopics.includes('array')) {
    questions.push('如何避免数组越界？')
    questions.push('数组的边界条件怎么处理？')
  }

  if (inferredTopics.includes('linked-list')) {
    questions.push('链表和数组有什么区别？')
    questions.push('链表的插入删除怎么实现？')
  }

  if (inferredTopics.includes('sorting')) {
    questions.push('快速排序和归并排序有什么区别？')
    questions.push('二分查找的前提条件是什么？')
  }

  if (inferredTopics.includes('sql')) {
    questions.push('SQL 查询为什么要用索引？')
    questions.push('数据库索引的工作原理是什么？')
  }

  if (inferredTopics.includes('function-call')) {
    questions.push('函数调用时参数是怎么传递的？')
    questions.push('如何理解函数的作用域？')
  }

  if (inferredTopics.includes('debug')) {
    questions.push('代码报错后应该怎么排查？')
    questions.push('如何高效地调试递归函数？')
  }

  if (resourceCount > 0) {
    questions.push('我加入的资源应该先学哪一个？')
  }

  if (questions.length < 4) {
    const fallbacks = [
      '递归和迭代有什么区别？',
      '能不能结合我的资源包讲一下调用栈？',
      '我应该按什么顺序学习这些知识点？',
      '二叉树的层序遍历有什么用？',
      '如何设计一个简单的数据库表？',
    ]
    for (const fb of fallbacks) {
      if (questions.length >= 5) break
      if (!questions.includes(fb)) questions.push(fb)
    }
  }

  return questions.slice(0, 5)
}

// =====================================================================
// Resource Recommendation from Context (Mock)
// =====================================================================

export function recommendResourcesByContextMock(context: ConversationContext): Array<{
  title: string
  type: string
  estimatedTime: string
  topic: string
}> {
  const resources = loadPathResources()
  const { inferredTopics, weakPoints } = context

  const matchedFromPackage: Array<{ title: string; type: string; estimatedTime: string; topic: string }> = []

  for (const res of resources) {
    const text = (res.title + res.topic + res.type).toLowerCase()
    const matches = inferredTopics.some((t) => {
      const kwMap: Record<string, string[]> = {
        'recursion': ['递归', '调用栈', '出口'],
        'binary-tree': ['二叉树', '遍历', '树'],
        'array': ['数组', '下标', '越界', '边界'],
        'linked-list': ['链表', '节点', '指针'],
        'sorting': ['排序', '查找', '搜索', '二分'],
        'sql': ['sql', '数据库', '索引', '查询'],
        'function-call': ['函数', '调用', '参数', '返回'],
        'debug': ['调试', 'debug', '错误', '报错'],
        'project': ['项目', '实践', '开发'],
      }
      return (kwMap[t] || []).some((kw) => text.includes(kw))
    })
    if (matches) {
      matchedFromPackage.push({
        title: res.title,
        type: res.type,
        estimatedTime: res.estimatedTime,
        topic: res.topic,
      })
    }
  }

  if (matchedFromPackage.length > 0) {
    return matchedFromPackage.slice(0, 3)
  }

  // Fallback: topic-aware default recommendations
  const defaults: Array<{ title: string; type: string; estimatedTime: string; topic: string }> = []

  const topicResourceMap: Record<string, Array<{ title: string; type: string; estimatedTime: string; topic: string }>> = {
    'recursion': [
      { title: '递归调用栈图解讲义', type: '个性化讲解文档', estimatedTime: '25 分钟', topic: '递归' },
      { title: '递归代码示例与逐行注释', type: '代码示例与注释', estimatedTime: '30 分钟', topic: '递归' },
    ],
    'binary-tree': [
      { title: '二叉树遍历图解讲义', type: '个性化讲解文档', estimatedTime: '25 分钟', topic: '二叉树遍历' },
      { title: '遍历代码示例与注释', type: '代码示例与注释', estimatedTime: '25 分钟', topic: '二叉树遍历' },
    ],
    'array': [
      { title: '数组操作与边界条件讲解', type: '个性化讲解文档', estimatedTime: '20 分钟', topic: '数组操作' },
      { title: '数组练习题集', type: '分层练习题', estimatedTime: '30 分钟', topic: '数组' },
    ],
    'linked-list': [
      { title: '链表数据结构图解', type: '个性化讲解文档', estimatedTime: '25 分钟', topic: '链表' },
      { title: '链表操作代码示例', type: '代码示例与注释', estimatedTime: '25 分钟', topic: '链表' },
    ],
    'sorting': [
      { title: '排序算法对比讲解', type: '个性化讲解文档', estimatedTime: '30 分钟', topic: '排序算法' },
      { title: '排序算法代码模板', type: '代码示例与注释', estimatedTime: '25 分钟', topic: '排序' },
    ],
    'sql': [
      { title: '数据库索引原理讲解', type: '个性化讲解文档', estimatedTime: '25 分钟', topic: '数据库索引' },
      { title: 'SQL 查询优化实践', type: '代码示例与注释', estimatedTime: '30 分钟', topic: 'SQL' },
    ],
    'function-call': [
      { title: '函数调用机制深度讲解', type: '个性化讲解文档', estimatedTime: '20 分钟', topic: '函数调用' },
      { title: 'Python 函数调用示例', type: '代码示例与注释', estimatedTime: '20 分钟', topic: '函数' },
    ],
    'debug': [
      { title: '代码调试方法论', type: '个性化讲解文档', estimatedTime: '20 分钟', topic: '调试技巧' },
      { title: '常见错误类型速查手册', type: '拓展阅读资料', estimatedTime: '15 分钟', topic: '调试' },
    ],
  }

  for (const topic of inferredTopics) {
    const items = topicResourceMap[topic]
    if (items) {
      for (const item of items) {
        if (!defaults.some((d) => d.title === item.title)) {
          defaults.push(item)
        }
      }
    }
  }

  if (defaults.length === 0) {
    defaults.push(
      { title: `${weakPoints[0] || '基础知识'}个性化讲解文档`, type: '个性化讲解文档', estimatedTime: '20 分钟', topic: weakPoints[0] || '综合' },
      { title: '代码示例与注释', type: '代码示例与注释', estimatedTime: '25 分钟', topic: '综合辅导' },
    )
  }

  return defaults.slice(0, 3)
}

// =====================================================================
// Challenge Result Generator
// =====================================================================

export function generateChallengeResult(answers: Record<string, string>, questions: ChallengeQuestion[]): ChallengeResult {
  let correct = 0
  const wrongPoints: Array<{ knowledge_point: string; reason: string }> = []
  const levelResults: Record<string, boolean> = {}

  for (const q of questions) {
    const isCorrect = answers[q.id] === q.correct
    levelResults[q.id] = isCorrect
    if (isCorrect) correct++
    else wrongPoints.push({ knowledge_point: q.knowledge_point, reason: q.explanation })
  }

  const total = questions.length
  const score = Math.round((correct / total) * 100)
  const allCorrect = correct === total

  return {
    totalLevels: total, completedLevels: Object.keys(answers).length, correctCount: correct, score,
    growth: { knowledge_base: allCorrect ? 5 : correct * 2, practice_ability: allCorrect ? 4 : Math.max(1, correct) },
    badges: allCorrect ? ['知识闯关达人'] : correct >= 3 ? ['继续前进'] : [],
    wrongPoints, levelResults,
  }
}

// =====================================================================
// Keyword-Driven Tutor Response System (Phase 10)
//
// Each domain has a response builder that generates a relevant,
// structured tutoring response. The dispatcher matches the user's
// question to the best domain and routes accordingly.
// =====================================================================

function buildRecursionResponse(): TutorChatResponse {
  return {
    greeting: '关于递归这个问题，我来帮你梳理清楚！',
    approach: '递归的核心是把大问题分解成小问题，每次递归调用都解决一个更小的子问题，直到遇到基准情形（Base Case）为止。',
    steps: [
      '第一步：明确递归函数的定义——它要解决什么问题，输入和输出分别是什么。',
      '第二步：找到基准情形——最简单、不需要再递归的情况，这是递归的出口。',
      '第三步：写出递归关系——如何把当前问题转化为更小的、同类型的子问题。',
      '第四步：在纸上模拟调用栈的压入和弹出过程，理解每次递归调用时参数变化和返回值传递。',
    ],
    code_example: 'def factorial(n):\n    if n <= 1:         # 基准情形：递归出口\n        return 1\n    return n * factorial(n - 1)  # 递归关系\n\n# f(4) = 4 × f(3) = 4 × 3 × f(2)\n#      = 4 × 3 × 2 × f(1)\n#      = 4 × 3 × 2 × 1 = 24',
    recommended_resources: [
      { title: '递归调用栈图解讲义', url: '#' },
      { title: '递归代码示例与逐行注释', url: '#' },
    ],
    suggested_exercise: '尝试用递归实现斐波那契数列，并在一张纸上画出 f(5) 的完整调用栈图。',
  }
}

function buildBinaryTreeResponse(): TutorChatResponse {
  return {
    greeting: '二叉树遍历是数据结构中最核心的操作之一，让我帮你理清思路！',
    approach: '三种遍历的核心区别在于"根节点被访问的时机"：前序先访问根，中序中间访问根，后序最后访问根。',
    steps: [
      '第一步：理解遍历的本质——遍历就是按照一定顺序访问树中的每个节点，每个节点恰好访问一次。',
      '第二步：前序遍历（根→左→右）——先处理根节点，再递归左子树，最后递归右子树。',
      '第三步：中序遍历（左→根→右）——先递归左子树，再处理根节点，最后递归右子树。对二叉搜索树（BST）会得到有序序列。',
      '第四步：后序遍历（左→右→根）——先递归左右子树，最后处理根。适合需要子节点结果汇总的场景，如计算树的高度。',
    ],
    code_example: 'class TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\ndef preorder(root):\n    if root is None: return      # 出口\n    print(root.val, end=" ")     # 根\n    preorder(root.left)          # 左\n    preorder(root.right)         # 右',
    recommended_resources: [
      { title: '二叉树遍历图解讲义', url: '#' },
      { title: '遍历代码示例与注释', url: '#' },
    ],
    suggested_exercise: '用同一棵 3 层二叉树分别跑前序、中序、后序遍历，对比三种输出结果的差异。',
  }
}

function buildArrayResponse(): TutorChatResponse {
  return {
    greeting: '数组是编程中最常用的数据结构，我来帮你理清基本概念！',
    approach: '数组操作的核心是理解"索引从 0 开始"和"边界条件"。大部分数组错误都来自越界访问或循环条件写错。',
    steps: [
      '第一步：明确索引范围——长度为 n 的数组，有效索引是 0 到 n-1，arr[n] 会越界。',
      '第二步：遍历数组时，循环条件用 i < n 而不是 i <= n，防止访问 arr[n]。',
      '第三步：处理多维数组时，逐层理解——arr[i][j] 中 i 是行号，j 是列号。',
      '第四步：注意边界情况——空数组（len=0）、单元素数组、首尾元素的特殊处理。',
    ],
    code_example: 'arr = [10, 20, 30, 40, 50]\nn = len(arr)              # n = 5\n# 安全的遍历方式\nfor i in range(n):        # range(5) → 0,1,2,3,4\n    print(arr[i])\n# 不安全的访问\n# arr[n]                  # IndexError!',
    recommended_resources: [
      { title: '数组操作基础讲解', url: '#' },
      { title: '数组边界条件练习题', url: '#' },
    ],
    suggested_exercise: '写一个函数反转数组，分别用循环遍历和切片两种方式实现，测试空数组和单元素数组的情况。',
  }
}

function buildLinkedListResponse(): TutorChatResponse {
  return {
    greeting: '链表是理解指针和动态数据结构的基础，让我来帮你理清！',
    approach: '链表的核心是每个节点包含数据域和指向下一个节点的指针。理解指针的"指向关系"是掌握链表的关键。',
    steps: [
      '第一步：理解节点结构——每个节点包含数据域（val）和指针域（next），next 指向下一个节点。',
      '第二步：掌握链表遍历——从头结点开始，沿着 next 指针逐个访问，直到遇到 None。',
      '第三步：理解插入操作——新节点的 next 先指向后继节点，然后修改前驱节点的 next 指向新节点。',
      '第四步：注意空链表、头结点操作、尾结点操作的边界情况。',
    ],
    code_example: 'class ListNode:\n    def __init__(self, val=0, next=None):\n        self.val = val\n        self.next = next\n\ndef traverse(head):\n    curr = head\n    while curr is not None:\n        print(curr.val)\n        curr = curr.next',
    recommended_resources: [
      { title: '链表数据结构图解讲义', url: '#' },
      { title: '链表操作代码示例与注释', url: '#' },
    ],
    suggested_exercise: '实现链表的三个基本操作：遍历、插入、删除，画出每一步指针变化的图示。',
  }
}

function buildSortingResponse(): TutorChatResponse {
  return {
    greeting: '排序和查找是算法学习的经典起点，让我帮你理清思路！',
    approach: '学习排序算法的推荐路径：先掌握简单排序（冒泡、选择、插入），再学习高效排序（快速、归并），最后理解它们的适用场景和复杂度差异。',
    steps: [
      '第一步：从冒泡排序入手——理解比较和交换的基本操作，每轮将最大元素"冒泡"到最后。',
      '第二步：学习快速排序的分治思想——选基准（pivot）、分区（partition）、递归排序子数组。',
      '第三步：理解归并排序——先递归分成小数组，再合并有序子数组。是稳定排序的代表。',
      '第四步：掌握二分查找——前提是数组已排序，每次通过中间值折半缩小搜索范围。',
    ],
    code_example: 'def bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        swapped = False\n        for j in range(n - i - 1):\n            if arr[j] > arr[j + 1]:\n                arr[j], arr[j + 1] = arr[j + 1], arr[j]\n                swapped = True\n        if not swapped: break\n    return arr',
    recommended_resources: [
      { title: '排序算法可视化对比', url: '#' },
      { title: '排序算法代码模板集', url: '#' },
    ],
    suggested_exercise: '用 Python 实现冒泡排序和快速排序，分别在随机数组和已排序数组上测试性能差异。',
  }
}

function buildSqlResponse(): TutorChatResponse {
  return {
    greeting: '数据库查询优化是实际开发中很重要的技能，让我来帮你理解！',
    approach: 'SQL 查询优化的核心是理解索引的工作原理。索引就像书的目录，帮你快速定位数据，避免逐行扫描整张表。',
    steps: [
      '第一步：理解全表扫描的问题——没有索引时，数据库必须逐行检查所有数据，数据量大时非常慢。',
      '第二步：理解索引原理——索引是一个排序的数据结构（通常是 B+ 树），支持 O(log n) 的快速查找。',
      '第三步：知道什么时候该建索引——频繁出现在 WHERE、JOIN、ORDER BY 中的列。',
      '第四步：了解索引的代价——索引占用额外存储空间，并在插入、更新、删除时带来维护开销。',
    ],
    code_example: '-- 没有索引 → 全表扫描\nSELECT * FROM students WHERE name = \'Tom\';\n\n-- 创建索引后 → 快速定位\nCREATE INDEX idx_name ON students(name);\n\n-- 索引对范围查询同样有效\nSELECT * FROM orders\nWHERE order_date > \'2025-01-01\'\nORDER BY order_date;',
    recommended_resources: [
      { title: '数据库索引原理讲解', url: '#' },
      { title: 'SQL 查询优化实践指南', url: '#' },
    ],
    suggested_exercise: '创建一个包含 1000 行数据的测试表，分别在有无索引时执行相同的查询，对比 EXPLAIN 输出和执行时间。',
  }
}

function buildFunctionCallResponse(): TutorChatResponse {
  return {
    greeting: '函数调用机制是理解程序执行流程的核心，我来帮你讲清楚！',
    approach: '理解函数调用的关键是三个概念：参数传递方式、返回值机制和调用栈的工作原理。',
    steps: [
      '第一步：理解参数传递——Python 中不可变对象（int、str、tuple）传值，可变对象（list、dict）传引用。',
      '第二步：掌握返回值——函数通过 return 将结果返回给调用者，没有 return 时默认返回 None。',
      '第三步：理解调用栈——每次函数调用会创建一个栈帧（存储参数、局部变量、返回地址），返回时弹栈。',
      '第四步：注意作用域规则——函数内部变量是局部的（local），外部无法直接访问；需要访问外部变量时用 global 或 nonlocal。',
    ],
    code_example: 'def add(a, b):\n    result = a + b      # result 是局部变量\n    return result        # 返回给调用者\n\nx = add(3, 4)           # x = 7\n# print(result)          # NameError: result 未定义',
    recommended_resources: [
      { title: '函数调用机制详解', url: '#' },
      { title: 'Python 作用域与闭包讲解', url: '#' },
    ],
    suggested_exercise: '定义三个嵌套函数（outer → middle → inner），在纸面上追踪每次调用的参数、局部变量和返回值。',
  }
}

function buildDebugResponse(): TutorChatResponse {
  return {
    greeting: '调试是每个开发者必须掌握的实用技能，我来分享一些有效的方法！',
    approach: '调试的核心是"假设→验证"循环：根据错误信息提出假设，用工具或 print 验证假设，逐步缩小问题范围。',
    steps: [
      '第一步：仔细阅读错误信息——错误类型（如 IndexError）、出错行号和调用堆栈是最重要的三个线索。',
      '第二步：从堆栈最底层（你的代码）开始向上追溯，定位问题源头。',
      '第三步：在可疑位置插入 print 输出关键变量值，验证你的假设是否正确。',
      '第四步：重点检查边界条件——空值、零值、数组首尾元素、递归出口，这些是最常见的错误来源。',
    ],
    code_example: '# 调试技巧示例\ndef binary_search(arr, target):\n    print(f"搜索 {target} 在 {arr} 中")\n    left, right = 0, len(arr) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        print(f"  left={left}, mid={mid}, right={right}, val={arr[mid]}")\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return -1',
    recommended_resources: [
      { title: '代码调试方法论与技巧', url: '#' },
      { title: '常见错误类型速查手册', url: '#' },
    ],
    suggested_exercise: '故意写一个包含越界错误的数组访问函数，通过阅读错误信息定位问题，然后用 print 调试法验证修复。',
  }
}

function buildProjectResponse(): TutorChatResponse {
  return {
    greeting: '项目实践是把知识转化为真实能力的关键一步！',
    approach: '项目学习的最佳策略是从小到大、从模仿到创新。先完成一个简单但完整的项目，再逐步增加复杂度。',
    steps: [
      '第一步：明确项目目标——确定核心功能和预期效果，不要一开始就追求完美。',
      '第二步：拆解任务——把大项目分解为独立的小模块，每个模块完成后可以单独测试。',
      '第三步：先写核心逻辑——从最简单的功能开始，确保基本流程能跑通。',
      '第四步：逐步完善——添加错误处理、边界条件、用户交互，最后优化代码结构。',
    ],
    code_example: null,
    recommended_resources: [
      { title: '项目式学习案例集', url: '#' },
      { title: '从零搭建完整项目指南', url: '#' },
    ],
    suggested_exercise: '选择一个你感兴趣的小项目（如命令行计算器、待办事项管理器），按上述四步从零开始实现。',
  }
}

function buildGenericResponse(input: string): TutorChatResponse {
  const preview = input.length > 40 ? input.slice(0, 40) + '…' : input
  return {
    greeting: `关于"${preview}"这个问题，我来帮你分析一下！`,
    approach: '根据你的问题，我建议从基础概念入手，逐步深入理解相关知识点。',
    steps: [
      '第一步：明确问题涉及的核心概念和知识点范围。',
      '第二步：查阅相关基础资料，建立概念框架。',
      '第三步：结合代码示例加深理解，动手运行验证。',
      '第四步：完成相关练习，检验掌握程度。',
    ],
    code_example: null,
    recommended_resources: [
      { title: '个性化讲解文档', url: '#' },
      { title: '知识点思维导图', url: '#' },
    ],
    suggested_exercise: '尝试用自己的语言复述该知识点，然后找一道相关练习题来检验理解。',
  }
}

// ========== Response Dispatcher ==========

const DOMAIN_BUILDERS: Record<string, () => TutorChatResponse> = {
  'recursion': buildRecursionResponse,
  'binary-tree': buildBinaryTreeResponse,
  'array': buildArrayResponse,
  'linked-list': buildLinkedListResponse,
  'sorting': buildSortingResponse,
  'sql': buildSqlResponse,
  'function-call': buildFunctionCallResponse,
  'debug': buildDebugResponse,
  'project': buildProjectResponse,
}

export function getTutorResponse(input: string): TutorChatResponse {
  if (!input.trim()) return buildGenericResponse('')

  const topics = detectTopics(input)

  if (topics.length > 0) {
    const builder = DOMAIN_BUILDERS[topics[0]]
    if (builder) return builder()
  }

  return buildGenericResponse(input)
}

// =====================================================================
// LLM-ready stubs (preserved for future integration)
// =====================================================================

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export function inferConversationContextWithLLM(_userQuestion: string, _pathNode: string, _resources: PathResourceItem[], _profile: Record<string, unknown>): Promise<ConversationContext> {
  throw new Error('Not implemented — use inferConversationContextMock for now')
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export function generateChallengeWithLLM(_context: ConversationContext): Promise<ChallengeQuestion[]> {
  throw new Error('Not implemented — use generateChallengeByContextMock for now')
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export function recommendResourcesWithLLM(_context: ConversationContext): Promise<Array<{ title: string; type: string; estimatedTime: string; topic: string }>> {
  throw new Error('Not implemented — use recommendResourcesByContextMock for now')
}

// =====================================================================
// Backward-compatible exports for api.ts
// =====================================================================

export const DEFAULT_RECOMMENDED_RESOURCES = [
  { title: '个性化讲解文档', type: '个性化讲解文档', estimatedTime: '20 分钟', topic: '综合' },
  { title: '代码示例与注释', type: '代码示例与注释', estimatedTime: '25 分钟', topic: '综合' },
  { title: '分层练习题', type: '分层练习题', estimatedTime: '45 分钟', topic: '综合' },
]

export const mockQuestions: DiagnosisQuestion[] = (() => {
  const ctx = inferConversationContextMock('', [])
  return generateChallengeByContextMock(ctx, [])
})()

export const mockAssessmentResult: AssessmentResult = {
  score: 85,
  total: 100,
  growth: { knowledge_base: 8, practice_ability: 6 },
  badges: ['知识探索者'],
  remedial_resources: [
    { knowledge_point: '递归出口', reason: '递归终止条件判断需要加强' },
    { knowledge_point: '遍历顺序', reason: '中序与前序概念容易混淆' },
  ],
}

export const mockTutorResponse: TutorChatResponse = getTutorResponse('递归')
