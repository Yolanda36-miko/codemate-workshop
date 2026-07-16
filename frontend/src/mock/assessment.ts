import type { DiagnosisQuestion, AssessmentResult, TutorChatResponse, ConversationContext, PathNode } from '../types'
import type { PathResourceItem } from '../types'
import { loadPathResources } from '../utils/pathResources'

// ========== Challenge Question Type ==========

export interface ChallengeQuestion extends DiagnosisQuestion {
  level: number
  levelName: string
  source: '来自本轮提问' | '来自当前路径' | '来自已保存资源' | '来自画像易错点' | '系统综合推荐'
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
  'complexity': ['复杂度', '大O', '时间复杂度', '空间复杂度', '渐进', '效率分析'],
  'recursion': ['递归', '调用栈', '出口', '基准情形', '栈帧', '递推', '终止条件'],
  'binary-tree': ['二叉树', '前序', '中序', '后序', '遍历', '层序', '树'],
  'array': ['数组', '下标', '越界', '边界', '列表索引'],
  'linked-list': ['链表', '节点指针', '头结点', '尾结点'],
  'graph': ['图', 'DFS', 'BFS', '邻接表', '邻接矩阵', '最短路径', '拓扑排序', 'visited', '连通'],
  'sorting': ['排序', '查找', '搜索', '冒泡', '快速排序', '二分', '归并', '选择排序', '插入排序', '稳定性'],
  'hash-table': ['散列表', '哈希', 'hash', '冲突', '负载因子', '链地址', '开放地址', 'unordered_map'],
  'dp': ['动态规划', '状态转移', '最优子结构', '重叠子问题', '记忆化', '背包'],
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

  // --- dp (Phase 10) ---
  {
    id: 'q-dp-1', levelName: '状态定义', tags: ['dp'],
    question: '动态规划中"状态定义"指的是什么？',
    options: ['A. 定义变量名', 'B. 定义 dp 数组每个位置的含义', 'C. 定义输入数据格式', 'D. 定义输出的格式'],
    correct: 'B',
    knowledge_point: '状态定义', explanation: '状态定义是 DP 的核心，即明确 dp[i] 或 dp[i][j] 表示什么含义，是推导转移方程的基础。',
  },
  {
    id: 'q-dp-2', levelName: '最优子结构', tags: ['dp'],
    question: '一个问题能用动态规划求解，必须满足什么性质？',
    options: ['A. 数据有序', 'B. 最优子结构和重叠子问题', 'C. 可以暴力枚举', 'D. 输入规模很小'],
    correct: 'B',
    knowledge_point: '最优子结构', explanation: 'DP 的两大核心性质：最优子结构（大问题的最优解包含子问题的最优解）和重叠子问题（子问题被重复计算）。',
  },
  {
    id: 'q-dp-3', levelName: '记忆化搜索', tags: ['dp'],
    question: '记忆化搜索和动态规划的主要关系是什么？',
    options: ['A. 完全不同', 'B. 记忆化搜索是自顶向下，DP 是自底向上', 'C. DP 比记忆化搜索快很多', 'D. 两者没有关系'],
    correct: 'B',
    knowledge_point: '记忆化搜索', explanation: '记忆化搜索（自顶向下递归+缓存）和 DP（自底向上迭代）本质相同，只是求解方向不同，时间/空间复杂度通常一致。',
  },
]

const SOURCES: ChallengeQuestion['source'][] = [
  '来自本轮提问', '来自当前路径', '来自已保存资源', '来自画像易错点', '系统综合推荐',
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
    if (topics.includes('dp')) weakPoints.push('状态定义')
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

  if (inferredTopics.includes('dp')) {
    questions.push('动态规划为什么要定义状态？')
    questions.push('记忆化搜索和动态规划有什么区别？')
  }

  if (resourceCount > 0) {
    questions.push('我加入的资源应该先学哪一个？')
  }

  if (questions.length < 4) {
    const fallbacks = [
      '递归和迭代有什么区别？',
      '能不能结合已保存的资源讲一下调用栈？',
      '我应该按什么顺序学习这些知识点？',
      '二叉树的层序遍历有什么用？',
      '如何分析递归算法的时间复杂度？',
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
        'dp': ['动态规划', '状态', '转移方程', '最优子结构'],
        'graph': ['图', 'DFS', 'BFS', '邻接', '遍历'],
        'hash-table': ['散列表', '哈希', 'hash', '冲突'],
        'complexity': ['复杂度', '大O', '分析'],
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
    'dp': [
      { title: '动态规划入门讲解', type: '个性化讲解文档', estimatedTime: '30 分钟', topic: '动态规划' },
      { title: '经典DP问题代码示例', type: '代码示例与注释', estimatedTime: '25 分钟', topic: 'DP' },
    ],
    'graph': [
      { title: '图结构与图算法核心讲解', type: '个性化讲解文档', estimatedTime: '30 分钟', topic: '图算法' },
      { title: 'BFS与DFS对比图解', type: '图解讲义', estimatedTime: '25 分钟', topic: '图遍历' },
    ],
    'hash-table': [
      { title: '散列表核心讲解', type: '个性化讲解文档', estimatedTime: '25 分钟', topic: '散列表' },
      { title: '散列表冲突解决图解', type: '图解讲义', estimatedTime: '20 分钟', topic: '散列表' },
    ],
    'complexity': [
      { title: '复杂度分析核心讲解', type: '个性化讲解文档', estimatedTime: '25 分钟', topic: '复杂度' },
      { title: '复杂度分析思维导图', type: '知识点思维导图', estimatedTime: '15 分钟', topic: '复杂度' },
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
    core_explanation: '递归调用栈容易混，是因为每次函数调用都会生成新的栈帧，执行过程不是"一次走到底"，而是先不断调用，再逐层返回。理解时要同时看清"调用顺序"和"返回顺序"。',
    key_points: [
      '每次递归调用都有独立栈帧',
      '递归出口决定何时停止',
      '返回过程与调用过程相反',
    ],
    next_step: '建议你用一个 3 层递归例子手动画出调用栈变化。',
  }
}

function buildBinaryTreeResponse(): TutorChatResponse {
  return {
    core_explanation: '三种遍历的核心区别在于根节点的访问时机。前序先访问根，中序中间访问根，后序最后访问根。理解这个就能区分三种遍历。',
    key_points: [
      '前序：根→左→右',
      '中序：左→根→右',
      '后序：左→右→根',
    ],
    next_step: '用同一棵 3 层二叉树分别写出三种遍历的输出序列，对比差异。',
  }
}

function buildArrayResponse(): TutorChatResponse {
  return {
    core_explanation: '数组操作的核心是理解索引从 0 开始和边界条件。大部分数组错误来自越界访问或循环条件写错。',
    key_points: [
      '长度 n，有效索引 0 到 n-1',
      '循环条件用 i < n 防止越界',
      '空数组和首尾元素要特殊处理',
    ],
    next_step: '写一个数组反转函数，测试空数组和单元素数组两种边界情况。',
  }
}

function buildLinkedListResponse(): TutorChatResponse {
  return {
    core_explanation: '链表每个节点包含数据和指向下一节点的指针。理解指针的指向关系是掌握链表的关键，插入删除只需修改指针，不需要移动元素。',
    key_points: [
      '遍历沿 next 指针逐个访问',
      '插入：新节点先指向后继，再改前驱',
      '注意空链表和头尾节点边界',
    ],
    next_step: '实现链表的插入和删除操作，画出每一步指针变化图。',
  }
}

function buildSortingResponse(): TutorChatResponse {
  return {
    core_explanation: '排序算法的学习路径：先掌握简单排序（冒泡、选择、插入），再学习高效排序（快速、归并），最后理解它们的适用场景和复杂度差异。',
    key_points: [
      '冒泡每轮把最大元素浮到最后',
      '快排选基准、分区、递归',
      '归并先分后合，是稳定排序',
    ],
    next_step: '用 Python 实现冒泡和快排，对比随机数组与已排序数组的性能差异。',
  }
}

function buildDpResponse(): TutorChatResponse {
  return {
    core_explanation: '动态规划的核心是状态定义和状态转移方程。把大问题分解成子问题，找到子问题之间的递推关系，然后自底向上计算。',
    key_points: [
      '状态定义是 DP 最关键的一步',
      '转移方程描述状态间递推关系',
      '从记忆化搜索入门，再过渡到递推',
    ],
    next_step: '从斐波那契数列开始，用记忆化和递推两种方式实现，对比差异。',
  }
}

function buildComplexityResponse(): TutorChatResponse {
  return {
    core_explanation: '复杂度分析关注算法运行时间随输入规模增长的趋势，而非精确时间。大 O 表示法只保留增长最快的那一项。',
    key_points: [
      '单层循环 O(n)，嵌套 O(n²)',
      '每次迭代减半为 O(log n)',
      '递归问题画递归树分析',
    ],
    next_step: '分别分析遍历数组、二分查找、冒泡排序三种代码的复杂度，写出推导过程。',
  }
}

function buildGraphResponse(): TutorChatResponse {
  return {
    core_explanation: 'BFS 一层一层向外扩展，用队列实现；DFS 沿着一条路径深入到底，用递归或栈实现。二者最容易混的地方是访问顺序和 visited 标记时机。',
    key_points: [
      'BFS 适合最短步数问题',
      'DFS 适合路径搜索和连通性',
      'visited 要避免重复访问',
    ],
    next_step: '用同一张小图分别写出 BFS 和 DFS 的访问序列，对比差异。',
  }
}

function buildHashTableResponse(): TutorChatResponse {
  return {
    core_explanation: '散列表通过哈希函数将键映射到数组下标实现 O(1) 查找。当多个键映射到同一位置时产生冲突，需要链地址法或开放地址法解决。',
    key_points: [
      '哈希函数决定键的存储位置',
      '链地址法用链表存储冲突键',
      '负载因子过高时需扩容 rehash',
    ],
    next_step: '实现一个简易散列表（链地址法），用它解决两数之和问题。',
  }
}

// ========== Off-topic detection ==========

const OFF_TOPIC_KEYWORDS = [
  'SQL', '数据库', '建表', '查询语句', 'MySQL',
  '网络协议', 'HTTP', 'TCP', 'IP', 'OSI', 'DNS',
  '进程', '线程', '操作系统', '死锁', '调度',
  '计算机组成', 'CPU', '内存管理', '指令集',
  '软件工程', '设计模式', '架构', '需求分析',
  '编译', '链接', '汇编',
]

function isOffTopic(input: string): boolean {
  const lower = input.toLowerCase()
  return OFF_TOPIC_KEYWORDS.some((kw) => lower.includes(kw.toLowerCase()))
}

function buildOffTopicResponse(input: string): TutorChatResponse {
  const preview = input.length > 40 ? input.slice(0, 40) + '…' : input
  return {
    core_explanation: `关于"${preview}"，当前平台主要聚焦数据结构与算法学习，这个问题超出了当前辅导范围。`,
    key_points: [
      '不展开其他计算机领域内容',
      '可转向相关数据结构问题',
      '可练习查找、图、散列等主题',
    ],
    next_step: '你可以改问"哈希表如何支持快速查询？"或"图搜索如何理解？"',
  }
}

// ========== Generic fallback response ==========

function buildGenericResponse(input: string): TutorChatResponse {
  const preview = input.length > 40 ? input.slice(0, 40) + '…' : input
  return {
    core_explanation: `关于"${preview}"，建议从数据结构的基础概念入手，逐步理解相关算法和知识点。`,
    key_points: [
      '先明确涉及的 DS 知识点',
      '查阅相关讲解建立概念框架',
      '结合代码示例加深理解',
    ],
    next_step: '尝试用自己的话复述该知识点，然后做一道相关练习来检验理解。',
  }
}

// ========== Response Dispatcher ==========

const DOMAIN_BUILDERS: Record<string, () => TutorChatResponse> = {
  'complexity': buildComplexityResponse,
  'recursion': buildRecursionResponse,
  'binary-tree': buildBinaryTreeResponse,
  'array': buildArrayResponse,
  'linked-list': buildLinkedListResponse,
  'graph': buildGraphResponse,
  'sorting': buildSortingResponse,
  'hash-table': buildHashTableResponse,
  'dp': buildDpResponse,
}

export function getTutorResponse(input: string): TutorChatResponse {
  if (!input.trim()) return buildGenericResponse('')

  // Check for off-topic questions first
  if (isOffTopic(input)) return buildOffTopicResponse(input)

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
