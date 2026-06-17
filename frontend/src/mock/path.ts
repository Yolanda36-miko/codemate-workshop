import type { LearningPathResponse } from '../types'

/**
 * Generic reference learning path — 5 stages in strict prerequisite order.
 * Used as fallback when the user's profile is not yet usable for personalization.
 * Not a demo story — content is intentionally neutral and course-agnostic.
 */
export const mockLearningPath: LearningPathResponse = {
  name: '通用参考路径',
  nodes: [
    {
      id: 'ref-1',
      name: '基础概念梳理',
      course: '程序设计基础',
      goal: '建立核心概念框架，梳理知识点之间的依赖关系',
      duration: '1-3 天',
      status: 'pending',
      keywords: ['基础概念', '定义', '分类', '前置知识', '知识体系'],
      learningObjectives: [
        '理解核心概念的定义和分类',
        '梳理知识点之间的前后依赖关系',
        '明确学习路径和阶段性目标',
      ],
      defaultResources: [
        { resourceId: 'ref-1-1', title: '核心概念讲解文档', type: '个性化讲解文档', estimatedTime: '25 分钟', source: 'default' },
        { resourceId: 'ref-1-2', title: '知识体系思维导图', type: '知识点思维导图', estimatedTime: '15 分钟', source: 'default' },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '知识基础', value: 10 },
        { label: '概念清晰度', value: 10 },
      ],
      taskDescription: '阅读核心概念讲解文档，对照思维导图建立整体知识框架。',
      stage: '基础概念',
      reason: '建立清晰的概念框架是高效学习的第一步',
    },
    {
      id: 'ref-2',
      name: '核心机制理解',
      course: '数据结构与算法',
      goal: '深入理解核心机制的工作原理和内部过程',
      duration: '3-5 天',
      status: 'pending',
      keywords: ['原理分析', '工作机制', '推导过程', '内部实现', '核心机制'],
      learningObjectives: [
        '深入理解核心机制的工作原理',
        '掌握关键过程的推导和分析方法',
        '能够用自己的语言解释核心概念',
      ],
      defaultResources: [
        { resourceId: 'ref-2-1', title: '核心机制深度讲解', type: '个性化讲解文档', estimatedTime: '35 分钟', source: 'default' },
        { resourceId: 'ref-2-2', title: '易错点与常见误区总结', type: '个性化讲解文档', estimatedTime: '20 分钟', source: 'default' },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '理解深度', value: 15 },
        { label: '分析能力', value: 10 },
      ],
      taskDescription: '逐节阅读讲解文档，用自己的话复述核心过程，标记不理解的部分后续重点回顾。',
      stage: '核心理解',
      reason: '深入理解核心机制是写好代码的前提条件',
    },
    {
      id: 'ref-3',
      name: '代码实现练习',
      course: '数据结构与算法',
      goal: '将理论知识转化为可运行、可验证的代码实现',
      duration: '3-5 天',
      status: 'pending',
      keywords: ['代码实现', '编程', '调试', '测试', '代码示例'],
      learningObjectives: [
        '用代码实现核心数据结构与算法',
        '理解代码执行流程和边界条件',
        '掌握基本的调试技巧和错误排查',
      ],
      defaultResources: [
        { resourceId: 'ref-3-1', title: '核心代码实现与逐行注释', type: '代码示例与注释', estimatedTime: '40 分钟', source: 'default' },
        { resourceId: 'ref-3-2', title: '编程模板与测试用例', type: '代码示例与注释', estimatedTime: '25 分钟', source: 'default' },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '代码能力', value: 15 },
        { label: '实现能力', value: 12 },
      ],
      taskDescription: '逐行阅读代码示例，理解每行的作用后在编辑器中运行，尝试修改参数观察输出变化。',
      stage: '代码实现',
      reason: '将理论知识转化为代码是检验理解的最佳方式',
    },
    {
      id: 'ref-4',
      name: '分层巩固练习',
      course: '数据结构与算法',
      goal: '通过分层递进练习巩固知识，发现并修正薄弱环节',
      duration: '3-5 天',
      status: 'pending',
      keywords: ['练习', '错题', '巩固', '分层', '测试', '复习'],
      learningObjectives: [
        '通过基础层练习验证核心概念掌握程度',
        '通过进阶层练习提升分析和解题能力',
        '收集错题并针对薄弱点回顾复习',
      ],
      defaultResources: [
        { resourceId: 'ref-4-1', title: '分层练习题集', type: '分层练习题', estimatedTime: '45 分钟', source: 'default' },
        { resourceId: 'ref-4-2', title: '错题分析与回顾指南', type: '拓展阅读资料', estimatedTime: '20 分钟', source: 'default' },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '解题能力', value: 15 },
        { label: '熟练度', value: 12 },
      ],
      taskDescription: '按基础→进阶→提高的顺序完成三层练习，每层完成后检查错题并回顾对应知识点。',
      stage: '练习巩固',
      reason: '通过刻意练习发现知识盲区并加以巩固',
    },
    {
      id: 'ref-5',
      name: '综合应用实战',
      course: '数据结构与算法',
      goal: '将分散的知识点串联起来，在实际场景中综合运用',
      duration: '1-2 周',
      status: 'pending',
      keywords: ['项目', '应用', '综合', '实战', '案例', '知识迁移'],
      learningObjectives: [
        '综合运用多个知识点解决实际问题',
        '完成一个完整的项目式学习案例',
        '培养知识迁移和综合应用能力',
      ],
      defaultResources: [
        { resourceId: 'ref-5-1', title: '综合应用案例', type: '项目式学习案例', estimatedTime: '60 分钟', source: 'default' },
        { resourceId: 'ref-5-2', title: '知识迁移与拓展方向', type: '拓展阅读资料', estimatedTime: '25 分钟', source: 'default' },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '综合应用', value: 18 },
        { label: '知识迁移', value: 15 },
      ],
      taskDescription: '完成综合案例的全部功能，尝试增加扩展功能以加深理解。',
      stage: '项目应用',
      reason: '综合应用是检验学习成果、培养知识迁移能力的最佳方式',
    },
  ],
}
