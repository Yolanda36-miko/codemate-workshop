import type { LearningPathResponse } from '../types'

/**
 * 数据结构与算法通用参考学习路径 — 10 个递进模块。
 * 当用户画像不足以生成个性化路径时使用。
 */
export const mockLearningPath: LearningPathResponse = {
  name: '数据结构与算法学习路径',
  nodes: [
    // ===================================================================
    // 1. 复杂度分析与基础概念
    // ===================================================================
    {
      id: 'ds-1',
      name: '复杂度分析与基础概念',
      course: '数据结构与算法',
      goal: '理解算法效率的度量方式，建立复杂度分析的思维框架',
      duration: '1-3 天',
      status: 'pending',
      keywords: ['时间复杂度', '空间复杂度', '大O表示法', '渐进分析', '最好/最坏/平均'],
      learningObjectives: [
        '理解时间与空间复杂度的定义，掌握大O表示法和常见复杂度级别',
      ],
      defaultResources: [
        { resourceId: 'ds1-r1', title: '复杂度分析核心讲解', type: '个性化讲解文档', estimatedTime: '25 分钟', source: 'default' },
        { resourceId: 'ds1-r2', title: '复杂度分析思维导图', type: '知识点思维导图', estimatedTime: '15 分钟', source: 'default' },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '知识基础', value: 10 },
        { label: '分析能力', value: 10 },
      ],
      taskDescription: '阅读讲解文档并完成复杂度分析练习',
      stage: '基础概念',
      reason: '复杂度分析是评估和比较算法效率的基本功，是学习所有后续模块的前提',
    },

    // ===================================================================
    // 2. 线性表
    // ===================================================================
    {
      id: 'ds-2',
      name: '线性表',
      course: '数据结构与算法',
      goal: '掌握顺序表与链表的结构特性、操作实现和应用场景',
      duration: '2-4 天',
      status: 'pending',
      keywords: ['顺序表', '链表', '单链表', '双向链表', '循环链表', '顺序存储', '链式存储'],
      learningObjectives: [
        '理解顺序表与链表的存储差异，掌握链表基本操作和经典题型',
      ],
      defaultResources: [
        { resourceId: 'ds2-r1', title: '线性表深度讲解', type: '个性化讲解文档', estimatedTime: '30 分钟', source: 'default' },
        { resourceId: 'ds2-r2', title: '链表操作代码示例', type: '代码示例与注释', estimatedTime: '25 分钟', source: 'default' },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '实现能力', value: 12 },
        { label: '理解深度', value: 10 },
      ],
      taskDescription: '实现链表基本操作并完成反转和环检测练习',
      stage: '核心理解',
      reason: '线性表是最基础的动态数据结构，链表的指针操作是培养数据结构思维的关键',
    },

    // ===================================================================
    // 3. 栈与队列
    // ===================================================================
    {
      id: 'ds-3',
      name: '栈与队列',
      course: '数据结构与算法',
      goal: '掌握栈（LIFO）和队列（FIFO）的原理、实现和经典应用',
      duration: '2-3 天',
      status: 'pending',
      keywords: ['栈', '队列', 'LIFO', 'FIFO', '括号匹配', '表达式求值', '单调栈', '循环队列'],
      learningObjectives: [
        '理解栈与队列的特性，掌握括号匹配和表达式求值等经典应用',
      ],
      defaultResources: [
        { resourceId: 'ds3-r1', title: '栈与队列深度讲解', type: '个性化讲解文档', estimatedTime: '30 分钟', source: 'default' },
        { resourceId: 'ds3-r2', title: '栈与队列经典应用代码', type: '代码示例与注释', estimatedTime: '25 分钟', source: 'default' },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '实现能力', value: 12 },
        { label: '应用能力', value: 10 },
      ],
      taskDescription: '实现顺序栈和循环队列，完成括号匹配练习',
      stage: '核心理解',
      reason: '栈与队列是最常用的受限线性结构，是递归、BFS、表达式计算等高级主题的基础',
    },

    // ===================================================================
    // 4. 递归与调用栈
    // ===================================================================
    {
      id: 'ds-4',
      name: '递归与调用栈',
      course: '数据结构与算法',
      goal: '深入理解递归的运行机制、调用栈模型和常见递归模式',
      duration: '2-4 天',
      status: 'pending',
      keywords: ['递归', '调用栈', '栈帧', '递归出口', '尾递归', '递归树', '分治'],
      learningObjectives: [
        '理解递归调用栈机制，掌握终止条件与递推关系',
      ],
      defaultResources: [
        { resourceId: 'ds4-r1', title: '递归与调用栈核心讲解', type: '个性化讲解文档', estimatedTime: '30 分钟', source: 'default' },
        { resourceId: 'ds4-r2', title: '递归——调用栈图解', type: '图解讲义', estimatedTime: '20 分钟', source: 'default' },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '递归思维', value: 15 },
        { label: '理解深度', value: 12 },
      ],
      taskDescription: '画图跟踪调用栈变化，完成 2 道递归基础题',
      stage: '核心理解',
      reason: '递归是树、图、动态规划等高级数据结构与算法的思维基础，递归调用栈的理解至关重要',
    },

    // ===================================================================
    // 5. 树与二叉树
    // ===================================================================
    {
      id: 'ds-5',
      name: '树与二叉树',
      course: '数据结构与算法',
      goal: '掌握树的表示、二叉树遍历、BST操作和堆的实现',
      duration: '4-6 天',
      status: 'pending',
      keywords: ['二叉树', '遍历', '前序', '中序', '后序', '层序', 'BST', '堆', '优先队列'],
      learningObjectives: [
        '掌握二叉树四种遍历方式，理解 BST 和堆的结构性质',
      ],
      defaultResources: [
        { resourceId: 'ds5-r1', title: '树与二叉树深度讲解', type: '个性化讲解文档', estimatedTime: '40 分钟', source: 'default' },
        { resourceId: 'ds5-r2', title: '二叉树遍历代码示例', type: '代码示例与注释', estimatedTime: '30 分钟', source: 'default' },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '递归思维', value: 15 },
        { label: '代码能力', value: 12 },
      ],
      taskDescription: '实现二叉树遍历和 BST 操作，完成 Top-K 练习',
      stage: '代码实现',
      reason: '树与二叉树是数据结构的核心章节，是面试和算法竞赛的高频考点',
    },

    // ===================================================================
    // 6. 图结构与图算法
    // ===================================================================
    {
      id: 'ds-6',
      name: '图结构与图算法',
      course: '数据结构与算法',
      goal: '掌握图的存储方式、DFS/BFS遍历和最短路径算法',
      duration: '5-7 天',
      status: 'pending',
      keywords: ['图', '邻接表', '邻接矩阵', 'DFS', 'BFS', '最短路径', 'Dijkstra', '拓扑排序'],
      learningObjectives: [
        '掌握图的存储方式，理解 DFS/BFS 遍历和最短路径算法',
      ],
      defaultResources: [
        { resourceId: 'ds6-r1', title: '图结构与图算法核心讲解', type: '个性化讲解文档', estimatedTime: '45 分钟', source: 'default' },
        { resourceId: 'ds6-r2', title: 'BFS与DFS对比图解', type: '图解讲义', estimatedTime: '25 分钟', source: 'default' },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '综合应用', value: 15 },
        { label: '算法能力', value: 12 },
      ],
      taskDescription: '实现图的存储和遍历，完成最短路径和拓扑排序练习',
      stage: '代码实现',
      reason: '图算法是数据结构中最具挑战性的章节，DFS/BFS是解决大量算法问题的核心模式',
    },

    // ===================================================================
    // 7. 排序与查找
    // ===================================================================
    {
      id: 'ds-7',
      name: '排序与查找',
      course: '数据结构与算法',
      goal: '掌握经典排序算法的实现、对比和二分查找及其变体',
      duration: '4-6 天',
      status: 'pending',
      keywords: ['快速排序', '归并排序', '堆排序', '稳定性', '二分查找', '边界条件', '分治'],
      learningObjectives: [
        '掌握经典排序算法的实现与对比，理解二分查找及其变体',
      ],
      defaultResources: [
        { resourceId: 'ds7-r1', title: '排序算法详解与对比', type: '个性化讲解文档', estimatedTime: '40 分钟', source: 'default' },
        { resourceId: 'ds7-r2', title: '排序算法代码模板', type: '代码示例与注释', estimatedTime: '30 分钟', source: 'default' },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '算法能力', value: 15 },
        { label: '熟练度', value: 12 },
      ],
      taskDescription: '实现快排和归并排序，完成二分查找边界练习',
      stage: '练习巩固',
      reason: '排序与查找是面试和实际开发中最常用的算法，二分查找的边界处理是典型易错点',
    },

    // ===================================================================
    // 8. 散列表
    // ===================================================================
    {
      id: 'ds-8',
      name: '散列表',
      course: '数据结构与算法',
      goal: '理解散列表的哈希原理、冲突解决方法和实际应用',
      duration: '2-4 天',
      status: 'pending',
      keywords: ['散列表', '哈希函数', '冲突', '链地址法', '开放地址法', '负载因子', 'unordered_map'],
      learningObjectives: [
        '理解散列表的哈希原理和冲突解决策略',
      ],
      defaultResources: [
        { resourceId: 'ds8-r1', title: '散列表核心讲解', type: '个性化讲解文档', estimatedTime: '25 分钟', source: 'default' },
        { resourceId: 'ds8-r2', title: '散列表冲突解决图解', type: '图解讲义', estimatedTime: '20 分钟', source: 'default' },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '理解深度', value: 10 },
        { label: '应用能力', value: 10 },
      ],
      taskDescription: '实现链地址法散列表，完成两数之和等经典题',
      stage: '练习巩固',
      reason: '散列表是实际开发中使用频率最高的数据结构之一，理解其内部机制有助于正确高效使用',
    },

    // ===================================================================
    // 9. 动态规划入门
    // ===================================================================
    {
      id: 'ds-9',
      name: '动态规划入门',
      course: '数据结构与算法',
      goal: '理解动态规划的核心思想，掌握状态定义与转移方程的推导方法',
      duration: '4-7 天',
      status: 'pending',
      keywords: ['动态规划', '状态定义', '状态转移', '最优子结构', '重叠子问题', '记忆化搜索', '自底向上'],
      learningObjectives: [
        '理解最优子结构和重叠子问题，掌握状态转移方程推导',
      ],
      defaultResources: [
        { resourceId: 'ds9-r1', title: '动态规划入门讲解', type: '个性化讲解文档', estimatedTime: '40 分钟', source: 'default' },
        { resourceId: 'ds9-r2', title: '动态规划经典题集', type: '分层练习题', estimatedTime: '45 分钟', source: 'default' },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '解题能力', value: 18 },
        { label: '知识迁移', value: 12 },
      ],
      taskDescription: '从记忆化搜索入手，完成爬楼梯和背包问题',
      stage: '练习巩固',
      reason: '动态规划是算法学习的制高点，培养状态建模和递推思维对解决复杂问题至关重要',
    },

    // ===================================================================
    // 10. 综合项目实践
    // ===================================================================
    {
      id: 'ds-10',
      name: '综合项目实践',
      course: '数据结构与算法',
      goal: '综合运用所学数据结构与算法知识，完成一个完整的项目实践',
      duration: '1-2 周',
      status: 'pending',
      keywords: ['综合', '项目', '实践', '知识迁移', '系统设计', '算法综合', '代码重构'],
      learningObjectives: [
        '综合运用所学数据结构与算法，完成一个完整的项目实践',
      ],
      defaultResources: [
        { resourceId: 'ds10-r1', title: '综合项目案例——数据结构实战', type: '项目式学习案例', estimatedTime: '60 分钟', source: 'default' },
        { resourceId: 'ds10-r2', title: '算法设计模式与知识迁移', type: '拓展阅读资料', estimatedTime: '25 分钟', source: 'default' },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '综合应用', value: 18 },
        { label: '知识迁移', value: 15 },
      ],
      taskDescription: '选择一个综合项目，从设计到实现全流程完成',
      stage: '项目应用',
      reason: '综合项目实践是检验学习成果、将分散知识点串联成体系的最佳方式',
    },
  ],
}
