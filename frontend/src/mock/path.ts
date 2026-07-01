import type { LearningPathResponse } from '../types'

/**
 * 数据结构与算法通用参考学习路径 — 5 阶段严格递进。
 * 当用户画像不足以生成个性化路径时使用。
 */
export const mockLearningPath: LearningPathResponse = {
  name: '数据结构与算法通用参考路径',
  nodes: [
    {
      id: 'ref-1',
      name: '复杂度与基础概念',
      course: '数据结构与算法',
      goal: '理解算法效率的度量方式，建立复杂度分析的思维框架',
      duration: '1-3 天',
      status: 'pending',
      keywords: ['时间复杂度', '空间复杂度', '大O表示法', '渐进分析', '基础概念'],
      learningObjectives: [
        '理解时间复杂度与空间复杂度的定义',
        '掌握大O表示法和常见复杂度级别',
        '能够分析简单循环和递归的复杂度',
      ],
      defaultResources: [
        { resourceId: 'ref-1-1', title: '复杂度分析核心讲解', type: '个性化讲解文档', estimatedTime: '25 分钟', source: 'default' },
        { resourceId: 'ref-1-2', title: '复杂度分析思维导图', type: '知识点思维导图', estimatedTime: '15 分钟', source: 'default' },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '知识基础', value: 10 },
        { label: '分析能力', value: 10 },
      ],
      taskDescription: '阅读复杂度分析讲解文档，对照思维导图建立复杂度评估的整体框架。',
      stage: '基础概念',
      reason: '复杂度分析是评估和比较算法的基本功',
    },
    {
      id: 'ref-2',
      name: '线性表与栈队列',
      course: '数据结构与算法',
      goal: '掌握线性结构（顺序表、链表、栈、队列）的原理与实现',
      duration: '3-5 天',
      status: 'pending',
      keywords: ['线性表', '链表', '栈', '队列', '顺序存储', '链式存储'],
      learningObjectives: [
        '实现顺序表与链表的基本操作',
        '理解栈的LIFO特性和队列的FIFO特性',
        '掌握表达式求值、括号匹配等栈的经典应用',
      ],
      defaultResources: [
        { resourceId: 'ref-2-1', title: '线性表与栈队列深度讲解', type: '个性化讲解文档', estimatedTime: '35 分钟', source: 'default' },
        { resourceId: 'ref-2-2', title: '链表操作易错点总结', type: '个性化讲解文档', estimatedTime: '20 分钟', source: 'default' },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '理解深度', value: 15 },
        { label: '实现能力', value: 12 },
      ],
      taskDescription: '逐节阅读讲解文档，动手实现链表的基本操作和栈的经典应用。',
      stage: '核心理解',
      reason: '线性结构是所有复杂数据结构的基础',
    },
    {
      id: 'ref-3',
      name: '递归、树与二叉树',
      course: '数据结构与算法',
      goal: '掌握递归思想与树结构的遍历、搜索和构建算法',
      duration: '5-7 天',
      status: 'pending',
      keywords: ['递归', '调用栈', '二叉树', '遍历', 'BST', '堆'],
      learningObjectives: [
        '深入理解递归调用栈的工作机制',
        '掌握二叉树四种遍历方式的递归与非递归实现',
        '实现BST的插入、查找、删除操作',
      ],
      defaultResources: [
        { resourceId: 'ref-3-1', title: '递归与树结构核心讲解', type: '个性化讲解文档', estimatedTime: '40 分钟', source: 'default' },
        { resourceId: 'ref-3-2', title: '二叉树遍历代码示例', type: '代码示例与注释', estimatedTime: '30 分钟', source: 'default' },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '递归思维', value: 18 },
        { label: '代码能力', value: 15 },
      ],
      taskDescription: '先画图理解递归调用栈，再用代码实现四种遍历方式，对比递归与非递归的区别。',
      stage: '代码实现',
      reason: '递归与树结构是数据结构课程的核心难点',
    },
    {
      id: 'ref-4',
      name: '排序、查找与散列表',
      course: '数据结构与算法',
      goal: '掌握经典排序算法、二分查找和散列表的实现与对比',
      duration: '5-7 天',
      status: 'pending',
      keywords: ['排序', '快速排序', '归并排序', '二分查找', '散列表', '哈希'],
      learningObjectives: [
        '实现快速排序、归并排序等经典排序算法',
        '掌握二分查找及其变体',
        '理解散列表的哈希函数与冲突解决',
      ],
      defaultResources: [
        { resourceId: 'ref-4-1', title: '排序与查找算法详解', type: '个性化讲解文档', estimatedTime: '40 分钟', source: 'default' },
        { resourceId: 'ref-4-2', title: '排序算法对比练习', type: '分层练习题', estimatedTime: '35 分钟', source: 'default' },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '算法能力', value: 15 },
        { label: '熟练度', value: 12 },
      ],
      taskDescription: '逐个实现排序算法并对比性能，完成二分查找的边界条件练习，实现一个简单的散列表。',
      stage: '练习巩固',
      reason: '排序与查找是面试和实际开发中最常用的算法',
    },
    {
      id: 'ref-5',
      name: '图算法、动态规划与综合实战',
      course: '数据结构与算法',
      goal: '掌握图算法和动态规划入门，完成综合项目实践',
      duration: '1-2 周',
      status: 'pending',
      keywords: ['图', 'DFS', 'BFS', '最短路径', '动态规划', '项目', '综合应用'],
      learningObjectives: [
        '掌握图的DFS/BFS遍历和最短路径算法',
        '理解动态规划的状态定义与转移方程',
        '完成一个综合项目实践',
      ],
      defaultResources: [
        { resourceId: 'ref-5-1', title: '图算法与动态规划讲解', type: '个性化讲解文档', estimatedTime: '50 分钟', source: 'default' },
        { resourceId: 'ref-5-2', title: '综合项目实践案例', type: '项目式学习案例', estimatedTime: '60 分钟', source: 'default' },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '综合应用', value: 18 },
        { label: '知识迁移', value: 15 },
      ],
      taskDescription: '实现图的DFS/BFS和Dijkstra算法，完成动态规划经典题目，最后完成综合项目。',
      stage: '项目应用',
      reason: '综合应用是检验学习成果、培养算法思维的最佳方式',
    },
  ],
}
