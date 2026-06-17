import type { BackendProfile, Course, PathNode } from '../types'

// ========== Profile usability check ==========

export function hasUsableProfile(profile: BackendProfile | null): boolean {
  if (!profile) return false

  // Check JSON-encoded tag fields
  const hasTags = (field: string | null): boolean => {
    if (!field) return false
    try {
      const arr = JSON.parse(field)
      return Array.isArray(arr) && arr.length > 0
    } catch {
      return false
    }
  }

  if (hasTags(profile.cognitive_styles)) return true
  if (hasTags(profile.error_patterns)) return true
  if (hasTags(profile.learning_goals)) return true
  if (hasTags(profile.resource_preferences)) return true

  // Check score fields
  if (profile.knowledge_base_score !== null && profile.knowledge_base_score !== undefined) return true
  if (profile.practice_ability_score !== null && profile.practice_ability_score !== undefined) return true

  // Check summary
  if (profile.profile_summary && profile.profile_summary.trim().length > 0) return true

  // Check diagnosis status
  if (profile.diagnosis_status && profile.diagnosis_status !== 'not_started') return true

  return false
}

// ========== Helper: parse JSON-encoded tag fields ==========

function parseTags(field: string | null): string[] {
  if (!field) return []
  try {
    const arr = JSON.parse(field)
    return Array.isArray(arr) ? arr : []
  } catch {
    return []
  }
}

// ========== Helper: extract keywords from profile ==========

function extractProfileKeywords(profile: BackendProfile): {
  difficulties: string[]
  goals: string[]
  preferences: string[]
  styles: string[]
  errorPatterns: string[]
  knowledgeLevel: number | null
  practiceLevel: number | null
} {
  return {
    difficulties: parseTags(profile.error_patterns),
    goals: parseTags(profile.learning_goals),
    preferences: parseTags(profile.resource_preferences),
    styles: parseTags(profile.cognitive_styles),
    errorPatterns: parseTags(profile.error_patterns),
    knowledgeLevel: profile.knowledge_base_score,
    practiceLevel: profile.practice_ability_score,
  }
}

// ========== Personalized course recommendations ==========

export interface PersonalizedTransition {
  from: string
  to: string
  reason: string
  basedOn: string[]
  isPersonalized: boolean
}

export function buildPersonalizedTransition(
  profile: BackendProfile,
  courses: Course[],
): PersonalizedTransition | null {
  const kw = extractProfileKeywords(profile)
  if (!hasUsableProfile(profile)) return null

  // Look up courses relevant to user's difficulties/goals
  const programmingCourse = courses.find((c) => c.id === 'programming-basics')
  const dsCourse = courses.find((c) => c.id === 'data-structures')
  const osCourse = courses.find((c) => c.id === 'operating-system')
  const dbCourse = courses.find((c) => c.id === 'database-system')

  const reasons: string[] = []
  const basedOn: string[] = []

  // Rule: recursion/stack/tree difficulty → recommend DS&A
  const recursionTerms = ['递归', '调用栈', '栈', '树', '二叉树', '遍历']
  const hasRecursionIssue = kw.difficulties.some((d) =>
    recursionTerms.some((t) => d.includes(t)),
  )
  if (hasRecursionIssue) {
    reasons.push('你在递归与树结构方面存在学习困难')
    basedOn.push(...kw.difficulties.filter((d) => recursionTerms.some((t) => d.includes(t))))
  }

  // Rule: low practice → recommend code practice
  if (kw.practiceLevel !== null && kw.practiceLevel < 50) {
    reasons.push('你的代码实践能力有待加强')
    basedOn.push('实践能力偏弱')
  }

  // Rule: low knowledge → recommend fundamentals
  if (kw.knowledgeLevel !== null && kw.knowledgeLevel < 50) {
    reasons.push('你的基础知识需要巩固')
    basedOn.push('基础知识薄弱')
  }

  // Rule: project goals → recommend applied courses
  const projectTerms = ['项目', '实践', '开发', '应用']
  const hasProjectGoal = kw.goals.some((g) =>
    projectTerms.some((t) => g.includes(t)),
  )
  if (hasProjectGoal) {
    reasons.push('你的学习目标偏向项目实践')
    basedOn.push(...kw.goals.filter((g) => projectTerms.some((t) => g.includes(t))))
  }

  // Build recommendation
  if (reasons.length > 0 && programmingCourse && dsCourse) {
    return {
      from: programmingCourse.name,
      to: dsCourse.name,
      reason: reasons.join('；') + '，建议优先学习数据结构与算法核心内容。',
      basedOn: [...new Set(basedOn)].slice(0, 6),
      isPersonalized: true,
    }
  }

  // Fallback: general recommendation with simple reasoning
  if (programmingCourse && dsCourse) {
    return {
      from: programmingCourse.name,
      to: dsCourse.name,
      reason: '根据你的学习画像，建议在巩固程序设计基础后进入数据结构学习。',
      basedOn: ['学习画像综合分析'],
      isPersonalized: true,
    }
  }

  return null
}

// ========== Personalized learning path generation ==========

export function buildPersonalizedPath(
  profile: BackendProfile,
  courses: Course[],
): { name: string; nodes: PathNode[] } | null {
  if (!hasUsableProfile(profile)) return null

  const kw = extractProfileKeywords(profile)
  const nodes: PathNode[] = []
  let nodeId = 1

  // Detect user needs from profile
  const needsFundamentals =
    (kw.knowledgeLevel !== null && kw.knowledgeLevel < 50) ||
    kw.difficulties.some((d) => ['数组', '函数', '循环', '基础'].some((t) => d.includes(t)))
  const needsDataStructures =
    kw.difficulties.some((d) =>
      ['递归', '栈', '树', '队列', '链表', '遍历'].some((t) => d.includes(t)),
    ) || true // Most CS students need this
  const needsPractice =
    (kw.practiceLevel !== null && kw.practiceLevel < 60) ||
    kw.goals.some((g) => ['项目', '实践', '开发'].some((t) => g.includes(t)))
  const prefersDiagrams = kw.preferences.some((p) =>
    ['图解', '导图', '可视化', '图示'].some((t) => p.includes(t)),
  )
  const prefersCode = kw.preferences.some((p) =>
    ['代码', '示例', '编程'].some((t) => p.includes(t)),
  )
  const hasProjectGoal = kw.goals.some((g) =>
    ['项目', '实践', '开发', '综合'].some((t) => g.includes(t)),
  )

  const difficultyKeyword = (kw.difficulties.length > 0 ? kw.difficulties[0] : '')
  const goalKeyword = (kw.goals.length > 0 ? kw.goals[0] : '')

  // Stage 1: Foundation consolidation (if needed)
  if (needsFundamentals) {
    const courseName = courses.find((c) => c.id === 'programming-basics')?.name ?? '程序设计基础'
    nodes.push({
      id: `personalized-${nodeId++}`,
      name: '基础巩固阶段',
      course: courseName,
      goal: '巩固编程核心概念：函数定义与调用、数组操作、循环控制、基础调试技巧',
      duration: '2-3 周',
      status: 'pending',
      keywords: ['函数', '数组', '循环', '调试', '基础语法'],
      learningObjectives: [
        '掌握函数调用栈的基本概念',
        '理解数组内存模型与常见操作',
        '能独立完成基础代码调试',
      ],
      defaultResources: [
        { resourceId: 'def-func', title: '函数与调用栈图解', type: '图解讲义', estimatedTime: '30 分钟', source: 'default' },
        { resourceId: 'def-array', title: '数组操作练习', type: '代码示例', estimatedTime: '45 分钟', source: 'default' },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '基础知识', value: kw.knowledgeLevel ?? 30 },
        { label: '代码能力', value: kw.practiceLevel ?? 30 },
      ],
      taskDescription: needsFundamentals
        ? `因为你${difficultyKeyword ? '在' + difficultyKeyword + '方面存在学习困难' : '的基础知识需要巩固'}，建议先夯实编程核心概念。`
        : '夯实编程核心概念，为后续学习奠定基础。',
    })
  }

  // Stage 2: Core concepts (data structures, always useful)
  if (needsDataStructures) {
    const courseName = courses.find((c) => c.id === 'data-structures')?.name ?? '数据结构与算法'
    const resourceType = prefersDiagrams ? '图解讲义' : prefersCode ? '代码示例' : '讲解文档'
    nodes.push({
      id: `personalized-${nodeId++}`,
      name: '核心数据结构理解阶段',
      course: courseName,
      goal: '深入理解递归调用栈、树结构与二叉树遍历算法',
      duration: '3-4 周',
      status: 'pending',
      keywords: ['递归', '栈', '二叉树', '遍历', '队列'],
      learningObjectives: [
        '理解递归调用栈的工作原理',
        '掌握二叉树前序、中序、后序遍历',
        '能用代码实现栈和队列的基本操作',
      ],
      defaultResources: [
        {
          resourceId: 'def-recur',
          title: prefersDiagrams ? '递归调用栈图解讲义' : '递归原理与代码示例',
          type: resourceType,
          estimatedTime: '40 分钟',
          source: 'default',
        },
        {
          resourceId: 'def-tree',
          title: prefersDiagrams ? '二叉树遍历可视化图示' : '二叉树遍历代码实现',
          type: resourceType,
          estimatedTime: '50 分钟',
          source: 'default',
        },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '数据结构', value: 40 },
        { label: '算法思维', value: 35 },
      ],
      taskDescription: difficultyKeyword
        ? `因为你提到${difficultyKeyword}理解困难，本阶段重点突破递归与树结构核心概念。${prefersDiagrams ? '优先使用图解资源辅助理解。' : ''}`
        : '本阶段聚焦递归与树结构核心概念，为算法学习奠定基础。',
    })
  }

  // Stage 3: Code practice (if needed)
  if (needsPractice) {
    nodes.push({
      id: `personalized-${nodeId++}`,
      name: '代码实践强化阶段',
      course: courses.find((c) => c.id === 'data-structures')?.name ?? '数据结构与算法',
      goal: '通过分层练习和代码补全任务提升动手能力',
      duration: '2-3 周',
      status: 'pending',
      keywords: ['代码练习', '分层题', '代码补全', '调试', prefersCode ? '项目实践' : '练习题'],
      learningObjectives: [
        '完成至少 10 道分层练习题',
        '独立实现栈、队列、二叉树的代码版本',
        '能调试并修复常见的递归错误',
      ],
      defaultResources: [
        {
          resourceId: 'def-prac1',
          title: '数据结构分层练习题集',
          type: '分层练习题',
          estimatedTime: '60 分钟',
          source: 'default',
        },
        {
          resourceId: 'def-prac2',
          title: prefersCode ? 'LeetCode 精选代码题目' : '栈与队列应用练习',
          type: prefersCode ? '代码示例' : '练习题',
          estimatedTime: '45 分钟',
          source: 'default',
        },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '代码实践', value: kw.practiceLevel ?? 35 },
        { label: '解题能力', value: 40 },
      ],
      taskDescription: kw.practiceLevel !== null && kw.practiceLevel < 60
        ? `因为你的代码实践能力评分为 ${kw.practiceLevel}，建议通过分层练习提升动手编码能力。${prefersCode ? '优先推荐代码示例类资源。' : ''}`
        : '通过分层练习提升动手编码能力和解题技巧。',
    })
  }

  // Stage 4: Comprehensive application
  if (hasProjectGoal) {
    nodes.push({
      id: `personalized-${nodeId++}`,
      name: '综合应用阶段',
      course: courses.find((c) => c.id === 'data-structures')?.name ?? '数据结构与算法',
      goal: `结合实际项目场景，综合运用所学知识完成${goalKeyword ? goalKeyword + '相关' : '一个综合'}小项目`,
      duration: '2-4 周',
      status: 'pending',
      keywords: ['综合项目', '文件系统', '搜索算法', '排序算法', '项目实践'],
      learningObjectives: [
        '综合运用栈、队列、树结构解决实际问题',
        '完成一个完整的项目式学习案例',
        '掌握项目开发的基本流程和调试方法',
      ],
      defaultResources: [
        {
          resourceId: 'def-proj1',
          title: prefersCode ? '文件目录树项目代码骨架' : '文件目录树项目案例',
          type: '项目式学习案例',
          estimatedTime: '90 分钟',
          source: 'default',
        },
        {
          resourceId: 'def-proj2',
          title: '综合项目评估与反思指南',
          type: '拓展阅读资料',
          estimatedTime: '30 分钟',
          source: 'default',
        },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '综合应用', value: 50 },
        { label: '项目经验', value: 45 },
      ],
      taskDescription: goalKeyword
        ? `因为你希望${goalKeyword}，本阶段结合项目式学习案例，综合运用所学知识。`
        : '结合项目式学习案例，综合运用数据结构知识解决实际问题。',
    })
  }

  // If no nodes were generated, add a minimal fallback
  if (nodes.length === 0) {
    nodes.push({
      id: `personalized-${nodeId++}`,
      name: '基础学习阶段',
      course: courses.find((c) => c.id === 'data-structures')?.name ?? courses[0]?.name ?? '数据结构与算法',
      goal: '根据你的学习画像，从核心数据结构开始系统学习。',
      duration: '4-6 周',
      status: 'pending',
      keywords: ['递归', '栈', '树', '遍历'],
      learningObjectives: ['掌握递归与树结构的基本概念', '完成基础代码练习'],
      defaultResources: [
        { resourceId: 'def-basic', title: '数据结构入门讲义', type: '讲解文档', estimatedTime: '45 分钟', source: 'default' },
      ],
      matchedResources: [],
      growthDimensions: [{ label: '基础知识', value: 40 }],
      taskDescription: '根据你的学习画像综合分析，推荐从数据结构核心概念开始系统学习。',
    })
  }

  return {
    name: 'CodeBuddy 为你定制的个性化学习路径',
    nodes,
  }
}
