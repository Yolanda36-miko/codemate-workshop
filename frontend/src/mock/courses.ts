import type { CourseListResponse } from '../types'

export const mockCourses: CourseListResponse = {
  courses: [
    {
      id: 'programming-basics',
      name: '程序设计基础',
      description: '学习程序设计的基本概念和方法，掌握变量、数据类型、控制结构、函数、数组、递归等核心编程思想，是后续所有课程的前置基础。',
      summary: '为数据结构学习打好编程基础。',
      stage: '大一上',
      positioning: '课程群支撑',
      prerequisites: [],
      related_courses: ['data-structures', 'computer-organization', 'database-system'],
      knowledge_points: ['变量与数据类型', '条件与循环', '函数', '数组', '递归', '基础调试'],
      resource_types: ['讲解文档', '思维导图', '代码示例', '分层练习', '拓展阅读', '项目案例'],
      typical_difficulties: ['递归思维建立', '函数调用过程理解', '数组与指针的关系', '调试技巧掌握'],
      learning_suggestion: '建议多写代码练习，从简单题目逐步建立编程思维。递归部分可结合图示理解调用栈。',
      color: '#7c3aed',
    },
    {
      id: 'data-structures',
      name: '数据结构与算法',
      description: '学习常用数据结构和基础算法，包括线性表、栈与队列、树与二叉树、图、排序与查找算法，是计算机专业核心课程。',
      summary: '连接编程基础与核心算法能力。',
      stage: '大一下',
      positioning: '课程群支撑',
      prerequisites: ['programming-basics'],
      related_courses: ['programming-basics', 'operating-system', 'database-system'],
      knowledge_points: ['线性表', '栈与队列', '树与二叉树', '递归思想', '排序算法', '查找算法', '时间复杂度'],
      resource_types: ['讲解文档', '思维导图', '代码示例', '分层练习', '拓展阅读', '项目案例'],
      typical_difficulties: ['递归到非递归的转换', '树与二叉树遍历', '时间复杂度分析', '算法设计思路'],
      learning_suggestion: '建议先巩固程序设计基础中的函数、数组和递归，再逐步深入数据结构。多用图示理解树和图的遍历过程。',
      color: '#6d28d9',
    },
    {
      id: 'computer-organization',
      name: '计算机组成原理',
      description: '学习计算机硬件系统的基本组成和工作原理，包括数据表示、运算器、存储器层次结构、指令系统和CPU数据通路。',
      summary: '帮助理解程序运行背后的硬件机制。',
      stage: '大二上',
      positioning: '课程群支撑',
      prerequisites: ['programming-basics'],
      related_courses: ['programming-basics', 'operating-system'],
      knowledge_points: ['数据表示与运算', '运算器设计', '存储器层次结构', '指令系统', 'CPU数据通路', '流水线技术'],
      resource_types: ['讲解文档', '思维导图', '代码示例', '分层练习', '拓展阅读', '项目案例'],
      typical_difficulties: ['数据表示与转换', '指令执行过程', '流水线冲突理解', 'Cache映射方式'],
      learning_suggestion: '结合C语言理解底层数据表示，用模拟器观察指令执行过程，有助于建立系统观。',
      color: '#8b5cf6',
    },
    {
      id: 'operating-system',
      name: '操作系统',
      description: '学习操作系统的基本概念、进程管理、内存管理、文件系统和I/O系统，理解系统软件的工作原理。',
      summary: '建立系统资源管理与并发执行的理解。',
      stage: '大二下',
      positioning: '课程群支撑',
      prerequisites: ['programming-basics', 'computer-organization'],
      related_courses: ['computer-organization', 'data-structures', 'computer-network'],
      knowledge_points: ['进程与线程', '处理机调度', '死锁', '内存管理', '虚拟内存', '文件系统'],
      resource_types: ['讲解文档', '思维导图', '代码示例', '分层练习', '拓展阅读', '项目案例'],
      typical_difficulties: ['进程同步与互斥', '死锁检测与避免', '页面置换算法', '文件系统实现'],
      learning_suggestion: '建议先复习计算机组成原理中的存储和中断机制。进程同步部分可结合代码实验加深理解。',
      color: '#a78bfa',
    },
    {
      id: 'computer-network',
      name: '计算机网络',
      description: '学习计算机网络体系结构、各层协议原理和网络应用开发，理解从物理层到应用层的完整通信过程。',
      summary: '理解网络通信与互联网应用基础。',
      stage: '大二下',
      positioning: '课程群支撑',
      prerequisites: ['operating-system'],
      related_courses: ['operating-system', 'database-system'],
      knowledge_points: ['网络体系结构', '应用层协议', '传输层协议', '网络层协议', '数据链路层', '网络安全基础'],
      resource_types: ['讲解文档', '思维导图', '代码示例', '分层练习', '拓展阅读', '项目案例'],
      typical_difficulties: ['TCP拥塞控制', 'IP路由算法', '子网划分', '各层协议交互过程'],
      learning_suggestion: '建议使用抓包工具观察真实网络通信，结合Socket编程实践理解传输层和应用层协议。',
      color: '#c4b5fd',
    },
    {
      id: 'database-system',
      name: '数据库系统',
      description: '学习数据库系统的基本原理，包括关系模型、SQL语言、数据库设计范式和事务管理，培养数据建模与工程实践能力。',
      summary: '支撑数据管理与工程项目实践。',
      stage: '大二上',
      positioning: '课程群支撑',
      prerequisites: ['programming-basics', 'data-structures'],
      related_courses: ['data-structures', 'operating-system'],
      knowledge_points: ['关系模型', 'SQL查询语言', '数据库设计', '规范化理论', '事务与并发控制', '索引与查询优化'],
      resource_types: ['讲解文档', '思维导图', '代码示例', '分层练习', '拓展阅读', '项目案例'],
      typical_difficulties: ['范式与反范式设计', '复杂SQL编写', '事务隔离级别', '索引优化策略'],
      learning_suggestion: '建议结合一个实际项目（如学生选课系统）练习数据库设计和SQL。多用EXPLAIN分析查询性能。',
      color: '#6366f1',
    },
  ],
}

// ========== Recommended Transition ==========

export interface RecommendedTransition {
  from: string
  to: string
  reason: string
  basedOn: string[]
}

// Default: general recommendation — used as fallback when no profile available
export const defaultTransition: RecommendedTransition = {
  from: '程序设计基础',
  to: '数据结构与算法',
  reason: '学习数据结构前，建议先巩固函数、数组、递归和基础调试。',
  basedOn: ['递归', '数组', '二叉树遍历', '代码实践'],
}

// Alternative transitions for different student needs
// LLM_REPLACE: getRecommendedTransitionWithLLM(studentProfile)
export const transitionOptions: Record<string, RecommendedTransition> = {
  algorithms: {
    from: '程序设计基础',
    to: '数据结构与算法',
    reason: '学习数据结构前，建议先巩固函数、数组、递归和基础调试。',
    basedOn: ['递归', '数组', '二叉树遍历', '代码实践'],
  },
  'os-memory': {
    from: '计算机组成原理',
    to: '操作系统',
    reason: '学习操作系统前，建议先巩固计算机组成原理中的数据表示、存储系统和中断机制。',
    basedOn: ['进程调度', '内存管理', '中断', '存储系统'],
  },
  'network-tcp': {
    from: '操作系统',
    to: '计算机网络',
    reason: '学习计算机网络前，建议先理解操作系统的进程通信和I/O机制。',
    basedOn: ['网络协议', 'HTTP', 'TCP/IP', 'Socket'],
  },
  'sql-modeling': {
    from: '程序设计基础',
    to: '数据库系统',
    reason: '学习数据库系统前，建议先巩固程序设计中的逻辑思维和数据组织能力。',
    basedOn: ['SQL', '数据建模', '项目实践'],
  },
}
