import type { BackendProfile, Course, PathNode, PersonalizedPathResult } from '../types'

// ========== Profile usability check ==========

export function hasUsableProfile(profile: BackendProfile | null): boolean {
  if (!profile) return false

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

  if (profile.knowledge_base_score !== null && profile.knowledge_base_score !== undefined) return true
  if (profile.practice_ability_score !== null && profile.practice_ability_score !== undefined) return true

  if (profile.profile_summary && profile.profile_summary.trim().length > 0) return true

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
  knowledgeLevel: number | null
  practiceLevel: number | null
} {
  return {
    difficulties: parseTags(profile.error_patterns),
    goals: parseTags(profile.learning_goals),
    preferences: parseTags(profile.resource_preferences),
    styles: parseTags(profile.cognitive_styles),
    knowledgeLevel: profile.knowledge_base_score,
    practiceLevel: profile.practice_ability_score,
  }
}

// ========== Helper: text matching ==========

function hasAnyMatch(texts: string[], terms: string[]): boolean {
  return texts.some((t) => terms.some((term) => t.includes(term)))
}

function findFirstMatch(texts: string[], terms: string[]): string | undefined {
  return texts.find((t) => terms.some((term) => t.includes(term)))
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

  const programmingCourse = courses.find((c) => c.id === 'programming-basics')
  const dsCourse = courses.find((c) => c.id === 'data-structures')

  const reasons: string[] = []
  const basedOn: string[] = []

  const recursionTerms = ['递归', '调用栈', '栈', '树', '二叉树', '遍历']
  if (hasAnyMatch(kw.difficulties, recursionTerms)) {
    reasons.push('你在递归与树结构方面存在学习困难')
    basedOn.push(...kw.difficulties.filter((d) => recursionTerms.some((t) => d.includes(t))))
  }

  if (kw.practiceLevel !== null && kw.practiceLevel < 50) {
    reasons.push('你的代码实践能力有待加强')
    basedOn.push('实践能力偏弱')
  }

  if (kw.knowledgeLevel !== null && kw.knowledgeLevel < 50) {
    reasons.push('你的基础知识需要巩固')
    basedOn.push('基础知识薄弱')
  }

  const projectTerms = ['项目', '实践', '开发', '应用']
  if (hasAnyMatch(kw.goals, projectTerms)) {
    reasons.push('你的学习目标偏向项目实践')
    basedOn.push(...kw.goals.filter((g) => projectTerms.some((t) => g.includes(t))))
  }

  if (reasons.length > 0 && programmingCourse && dsCourse) {
    return {
      from: programmingCourse.name,
      to: dsCourse.name,
      reason: reasons.join('；') + '，建议优先学习数据结构与算法核心内容。',
      basedOn: [...new Set(basedOn)].slice(0, 6),
      isPersonalized: true,
    }
  }

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

// =====================================================================
// Personalized learning path generation (Phase 9)
//
// Always produces exactly 5 stages in strict prerequisite order:
//   基础概念 → 核心理解 → 代码实现 → 练习巩固 → 项目应用
//
// Each stage is personalized using profile data:
//   - error_patterns    → topic focus, difficulty keywords
//   - learning_goals    → project stage focus
//   - resource_preferences → resource type selection
//   - knowledge_base_score  → pace and depth
//   - practice_ability_score → practice emphasis
//   - cognitive_styles  → resource format hints
// =====================================================================

const STAGE_ORDER = ['基础概念', '核心理解', '代码实现', '练习巩固', '项目应用'] as const

const BASIC_TERMS = ['数组', '函数', '循环', '基础', '变量', '语法', '指针', '类型']
const DS_TERMS = ['递归', '栈', '树', '二叉树', '遍历', '队列', '链表', '图']
const ALGO_TERMS = ['排序', '搜索', '算法', '复杂度', '动态规划', '贪心']
const PROJECT_TERMS = ['项目', '实践', '开发', '综合', '应用', '系统']
const EXAM_TERMS = ['考试', '通过', '成绩', '期末', '测试']
const DIAGRAM_TERMS = ['图解', '导图', '可视化', '图示', '画图']
const CODE_TERMS = ['代码', '示例', '编程', '实现']
const PRACTICE_TERMS = ['练习', '题目', '实操', '做题']

export function buildPersonalizedPath(
  profile: BackendProfile,
  courses: Course[],
): PersonalizedPathResult | null {
  if (!hasUsableProfile(profile)) return null

  const kw = extractProfileKeywords(profile)
  const nodes: PathNode[] = []

  // ---- Extract profile signals ----
  const hasBasicIssue = hasAnyMatch(kw.difficulties, BASIC_TERMS)
  const hasDSIssue = hasAnyMatch(kw.difficulties, DS_TERMS)
  const hasAlgoIssue = hasAnyMatch(kw.difficulties, ALGO_TERMS)
  const hasProjectGoal = hasAnyMatch(kw.goals, PROJECT_TERMS)
  const hasExamGoal = hasAnyMatch(kw.goals, EXAM_TERMS)
  const prefersDiagrams = hasAnyMatch(kw.preferences, DIAGRAM_TERMS) || hasAnyMatch(kw.styles, DIAGRAM_TERMS)
  const prefersCode = hasAnyMatch(kw.preferences, CODE_TERMS) || hasAnyMatch(kw.styles, CODE_TERMS)
  const prefersPractice = hasAnyMatch(kw.preferences, PRACTICE_TERMS)
  const knowledgeLow = kw.knowledgeLevel !== null && kw.knowledgeLevel < 50
  const practiceLow = kw.practiceLevel !== null && kw.practiceLevel < 60

  // ---- Determine topic focus ----
  const difficultyTopics = [
    ...kw.difficulties.filter((d) => [...BASIC_TERMS, ...DS_TERMS, ...ALGO_TERMS].some((t) => d.includes(t))),
  ]
  const primaryTopic = difficultyTopics[0] || kw.goals[0] || '数据结构基础'
  const dsCourse = courses.find((c) => c.id === 'data-structures')
  const progCourse = courses.find((c) => c.id === 'programming-basics')
  const primaryCourse = dsCourse || progCourse || courses[0]
  const primaryCourseName = primaryCourse?.name ?? '数据结构与算法'
  const basicCourseName = progCourse?.name ?? primaryCourseName

  // ---- Resource type preference ----
  const preferredResourceType = prefersDiagrams ? '图解讲义' : prefersCode ? '代码示例' : '讲解文档'
  const altResourceType = prefersPractice ? '分层练习题' : '代码示例与注释'

  // ---- Build personalized basis ----
  const profileFieldsUsed: string[] = []
  const basisParts: string[] = []

  if (kw.difficulties.length > 0) {
    profileFieldsUsed.push('error_patterns')
    basisParts.push(`学习困难：${kw.difficulties.slice(0, 4).join('、')}`)
  }
  if (kw.goals.length > 0) {
    profileFieldsUsed.push('learning_goals')
    basisParts.push(`学习目标：${kw.goals.slice(0, 3).join('、')}`)
  }
  if (kw.preferences.length > 0) {
    profileFieldsUsed.push('resource_preferences')
    basisParts.push(`资源偏好：${kw.preferences.slice(0, 3).join('、')}`)
  }
  if (kw.knowledgeLevel !== null) {
    profileFieldsUsed.push('knowledge_base_score')
    basisParts.push(`知识基础：${kw.knowledgeLevel}/100`)
  }
  if (kw.practiceLevel !== null) {
    profileFieldsUsed.push('practice_ability_score')
    basisParts.push(`实践能力：${kw.practiceLevel}/100`)
  }
  if (kw.styles.length > 0) {
    profileFieldsUsed.push('cognitive_styles')
  }

  const personalizedBasis = basisParts.length > 0 ? basisParts.join('；') : null

  let nodeId = 1

  // ================================================================
  // STAGE 1: 基础概念
  // ================================================================
  {
    const topic = hasBasicIssue
      ? (findFirstMatch(kw.difficulties, BASIC_TERMS) || '编程基础')
      : (hasDSIssue ? '数据结构前置基础' : '核心概念入门')
    const isSlowPace = knowledgeLow || hasBasicIssue

    nodes.push({
      id: `stage-${nodeId++}`,
      name: `${topic}概念梳理`,
      course: basicCourseName,
      goal: hasBasicIssue
        ? `消除${topic}相关的知识盲区，建立完整的基础概念体系`
        : `建立${topic}的清晰概念框架，为后续学习打好基础`,
      duration: isSlowPace ? '3-5 天' : '1-3 天',
      status: 'pending',
      keywords: hasBasicIssue
        ? kw.difficulties.filter((d) => BASIC_TERMS.some((t) => d.includes(t)))
        : [topic, '基础概念', '定义与原理', '前置知识'],
      learningObjectives: [
        `理解${topic}的定义、分类和核心原理`,
        `梳理${topic}相关的知识体系与依赖关系`,
        '明确学习路径和阶段性目标',
      ],
      defaultResources: [
        { resourceId: `s1-r1`, title: `${topic}核心概念讲解`, type: preferredResourceType, estimatedTime: '25 分钟', source: 'default' },
        { resourceId: `s1-r2`, title: `${topic}知识体系导图`, type: '知识点思维导图', estimatedTime: '15 分钟', source: 'default' },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '知识基础', value: knowledgeLow ? 15 : 8 },
        { label: '概念清晰度', value: 10 },
      ],
      taskDescription: hasBasicIssue
        ? `根据你的学习画像，你在${topic}方面存在困难，建议先从基础概念入手，消除知识盲区。`
        : `从${topic}入手建立清晰的概念框架，为后续深入学习做好准备。`,
      stage: '基础概念',
      reason: hasBasicIssue
        ? `你的学习画像显示在「${topic}」方面需要加强，打好基础是后续学习的关键`
        : '建立清晰的概念框架是高效学习的第一步',
    })
  }

  // ================================================================
  // STAGE 2: 核心理解
  // ================================================================
  {
    const topic = hasDSIssue
      ? (findFirstMatch(kw.difficulties, DS_TERMS) || '数据结构核心机制')
      : (hasAlgoIssue
        ? (findFirstMatch(kw.difficulties, ALGO_TERMS) || '算法核心机制')
        : primaryTopic)
    const isSlowPace = knowledgeLow

    nodes.push({
      id: `stage-${nodeId++}`,
      name: `${topic}原理深入`,
      course: primaryCourseName,
      goal: `深入理解${topic}的工作原理、内部机制和关键过程`,
      duration: isSlowPace ? '1-2 周' : '3-5 天',
      status: 'pending',
      keywords: kw.difficulties.length > 0
        ? kw.difficulties.filter((d) => [...DS_TERMS, ...ALGO_TERMS].some((t) => d.includes(t)))
        : [topic, '原理分析', '工作机制', '推导过程'],
      learningObjectives: [
        `深入理解${topic}的内部工作机制和关键过程`,
        `掌握${topic}的推导、分析和验证方法`,
        '能够用自己的语言解释核心概念和原理',
      ],
      defaultResources: [
        {
          resourceId: `s2-r1`,
          title: prefersDiagrams ? `${topic}原理图解讲义` : `${topic}原理深度讲解`,
          type: prefersDiagrams ? '图解讲义' : '个性化讲解文档',
          estimatedTime: '35 分钟',
          source: 'default',
        },
        {
          resourceId: `s2-r2`,
          title: `${topic}易错点与常见误区`,
          type: '个性化讲解文档',
          estimatedTime: '20 分钟',
          source: 'default',
        },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '理解深度', value: 15 },
        { label: '分析能力', value: 10 },
      ],
      taskDescription: hasDSIssue || hasAlgoIssue
        ? `根据你的学习画像，重点突破${topic}的核心理解。${prefersDiagrams ? '推荐先看图解建立直观认识，再深入文字讲解。' : ''}`
        : `深入理解${topic}的核心原理，为后续代码实现打好理论基础。`,
      stage: '核心理解',
      reason: hasDSIssue || hasAlgoIssue
        ? `你的学习画像显示在「${topic}」方面存在困难，需要重点突破核心概念`
        : '深入理解核心机制是写好代码的前提条件',
    })
  }

  // ================================================================
  // STAGE 3: 代码实现
  // ================================================================
  {
    const topic = hasDSIssue
      ? (findFirstMatch(kw.difficulties, DS_TERMS) || '数据结构')
      : primaryTopic

    nodes.push({
      id: `stage-${nodeId++}`,
      name: `${topic}代码实现`,
      course: primaryCourseName,
      goal: `将${topic}的理论知识转化为可运行、可验证的代码实现`,
      duration: practiceLow ? '1-2 周' : '3-5 天',
      status: 'pending',
      keywords: [topic, '代码实现', '编程', '调试', '测试'],
      learningObjectives: [
        `用代码实现${topic}的核心数据结构和算法`,
        `理解代码的执行流程、边界条件和结果验证`,
        '掌握基本的调试技巧和错误排查方法',
      ],
      defaultResources: [
        {
          resourceId: `s3-r1`,
          title: `${topic}代码实现与逐行注释`,
          type: '代码示例与注释',
          estimatedTime: '40 分钟',
          source: 'default',
        },
        {
          resourceId: `s3-r2`,
          title: `${topic}编程模板与测试用例`,
          type: '代码示例与注释',
          estimatedTime: '25 分钟',
          source: 'default',
        },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '代码能力', value: practiceLow ? 18 : 12 },
        { label: '实现能力', value: 12 },
      ],
      taskDescription: practiceLow
        ? `你的代码实践能力需要加强（当前 ${kw.practiceLevel}/100），建议仔细阅读代码示例，逐行理解后动手修改运行。`
        : `动手实现${topic}的核心代码，运行测试用例验证理解是否正确。`,
      stage: '代码实现',
      reason: practiceLow
        ? `你的实践能力评分为 ${kw.practiceLevel}/100，建议通过代码实现加强动手能力`
        : '将理论知识转化为代码是检验理解的最佳方式',
    })
  }

  // ================================================================
  // STAGE 4: 练习巩固
  // ================================================================
  {
    const topic = hasDSIssue
      ? (findFirstMatch(kw.difficulties, DS_TERMS) || '数据结构')
      : primaryTopic
    const weakPoints = kw.difficulties.slice(0, 3)

    nodes.push({
      id: `stage-${nodeId++}`,
      name: `${topic}分层练习`,
      course: primaryCourseName,
      goal: `通过分层递进练习巩固${topic}知识，发现并修正薄弱环节`,
      duration: practiceLow ? '1-2 周' : '3-5 天',
      status: 'pending',
      keywords: [topic, '练习', '错题', '巩固', '分层', '测试', '复习'],
      learningObjectives: [
        '通过基础层练习验证核心概念掌握程度',
        '通过进阶层练习提升分析和解题能力',
        '收集错题并针对薄弱点进行回顾复习',
      ],
      defaultResources: [
        {
          resourceId: `s4-r1`,
          title: `${topic}分层练习题集`,
          type: '分层练习题',
          estimatedTime: '45 分钟',
          source: 'default',
        },
        {
          resourceId: `s4-r2`,
          title: `${topic}错题分析与回顾指南`,
          type: '拓展阅读资料',
          estimatedTime: '20 分钟',
          source: 'default',
        },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '解题能力', value: 15 },
        { label: '熟练度', value: 12 },
      ],
      taskDescription: weakPoints.length > 0
        ? `重点练习以下薄弱环节：${weakPoints.join('、')}。完成练习后检查错题并回顾对应知识点。`
        : '按顺序完成三层练习（基础→进阶→提高），针对错题回顾对应知识点。',
      stage: '练习巩固',
      reason: weakPoints.length > 0
        ? `针对你的薄弱环节（${weakPoints.join('、')}）进行刻意练习`
        : '通过刻意练习发现知识盲区并加以巩固',
    })
  }

  // ================================================================
  // STAGE 5: 项目应用
  // ================================================================
  {
    const projectFocus = hasProjectGoal
      ? (findFirstMatch(kw.goals, PROJECT_TERMS) || '综合实战')
      : (hasExamGoal ? '考试重点应用' : (hasDSIssue ? '数据结构综合实战' : '综合应用'))

    nodes.push({
      id: `stage-${nodeId++}`,
      name: `${projectFocus}实战`,
      course: primaryCourseName,
      goal: hasProjectGoal
        ? `结合${projectFocus}需求，综合运用所学知识完成实战项目`
        : `将所学知识应用到实际场景中，完成综合案例练习`,
      duration: '1-2 周',
      status: 'pending',
      keywords: [primaryTopic, '项目', '应用', '综合', '实战', '案例', '项目式学习'],
      learningObjectives: [
        '综合运用多个知识点解决实际场景中的问题',
        '完成一个完整的项目式学习案例',
        '培养知识迁移和综合应用能力',
      ],
      defaultResources: [
        {
          resourceId: `s5-r1`,
          title: hasProjectGoal ? `${projectFocus}项目案例` : `${primaryTopic}综合应用案例`,
          type: '项目式学习案例',
          estimatedTime: '60 分钟',
          source: 'default',
        },
        {
          resourceId: `s5-r2`,
          title: '知识迁移与拓展方向',
          type: '拓展阅读资料',
          estimatedTime: '25 分钟',
          source: 'default',
        },
      ],
      matchedResources: [],
      growthDimensions: [
        { label: '综合应用', value: 18 },
        { label: '知识迁移', value: 15 },
      ],
      taskDescription: hasProjectGoal
        ? `根据你的学习目标（${kw.goals.filter((g) => PROJECT_TERMS.some((t) => g.includes(t))).join('、')}），通过实战项目巩固和迁移所学知识。`
        : '将分散的知识点串联起来，在实际场景中综合运用，检验学习成果。',
      stage: '项目应用',
      reason: hasProjectGoal
        ? `你的学习目标偏向项目实践，通过实战巩固所学内容`
        : '综合应用是检验学习成果、培养知识迁移能力的最佳方式',
    })
  }

  return {
    name: 'CodeBuddy 为你定制的个性化学习路径',
    nodes,
    personalizedBasis,
    profileFieldsUsed,
  }
}
