/**
 * ProfileInterviewService
 *
 * Mock implementations for the CodeBuddy multi-round interview flow.
 * Each function marked "Mock" can be replaced with an LLM-backed version
 * without changing the surrounding page logic.
 *
 * LLM replacement targets (search for "LLM_REPLACE"):
 *   extractFieldsMock      → extractFieldsWithLLM
 *   getNextQuestionMock    → getNextQuestionWithLLM
 *   evaluateDiagnosisMock  → evaluateDiagnosisWithLLM
 *   generateFinalProfileMock → generateFinalProfileWithLLM
 */

import type { DiagnosisQuestion, StudentProfile, ProfileDimension, BackendProfile, ProfileUpdatePayload } from '../types'
import { USE_MOCK } from './api'
import { mockDiagnosisQuestions, mockStudentProfile } from '../mock/profile'

const NEUTRAL_STUDENT = {
  name: '当前用户',
  grade: '待完善',
  major: '待完善',
  background: '基于对话与诊断生成的综合学习画像。',
}

const NEUTRAL_PROFILE_DIMENSIONS: Record<string, ProfileDimension> = {
  knowledge_base: {
    label: '知识基础',
    max_score: 100,
    note: '暂未评估',
  },
  practice_ability: {
    label: '实践能力',
    max_score: 100,
    note: '暂未评估',
  },
  cognitive_style: {
    label: '认知风格',
    tags: [],
  },
  weak_points: {
    label: '易错点特征',
    tags: [],
  },
  learning_goals: {
    label: '学习目标',
    tags: [],
  },
  resource_preferences: {
    label: '资源偏好',
    tags: [],
  },
}

// ---- Types ----

export interface Message {
  role: 'buddy' | 'user'
  content: string
}

export type InterviewStage =
  | 'greeting'
  | 'collecting'
  | 'ready_for_diagnosis'
  | 'diagnosis'
  | 'ready_for_profile'
  | 'generating'
  | 'complete'

export interface DiagnosisResult {
  totalCorrect: number
  totalQuestions: number
  knowledgeBaseAdjust: number
  practiceAbilityAdjust: number
  weakPointsAdded: string[]
  note: string
}

export interface InterviewState {
  messages: Message[]
  collectedFields: Record<string, string>
  missingFields: string[]
  stage: InterviewStage
  nextQuestion: string | null
  diagnosisQuestions: DiagnosisQuestion[]
  diagnosisAnswers: Record<string, string>
  diagnosisEvaluated: boolean
  diagnosisResults: DiagnosisResult | null
  finalProfile: StudentProfile | null
}

// ---- Field definitions ----

export const ALL_FIELDS = [
  { key: 'current_courses', label: '当前学习课程', priority: 1 },
  { key: 'completed_courses', label: '已学课程', priority: 5 },
  { key: 'learning_difficulty', label: '学习困难', priority: 2 },
  { key: 'programming_languages', label: '编程语言基础', priority: 3 },
  { key: 'coding_blockers', label: '写代码卡点', priority: 4 },
  { key: 'cognitive_style', label: '认知风格', priority: 6 },
  { key: 'learning_goals', label: '学习目标', priority: 7 },
  { key: 'resource_preference', label: '资源偏好', priority: 8 },
  { key: 'diagnosis_result', label: '诊断题结果', priority: 9 },
]

// ---- Field-specific question templates (used by getNextQuestionMock) ----

const fieldQuestions: Record<string, (prev: Record<string, string>) => string> = {
  current_courses: () => '你最近主要在上哪些计算机专业课呀？有没有哪门课让你觉得特别吃力？',
  learning_difficulty: (prev) => {
    if (prev.current_courses) return '你说到有些知识点不太顺手，能具体说说哪些知识点让你觉得难吗？比如递归、指针、还是某些算法？'
    return '你目前学习中，有没有哪些知识点让你反复琢磨还是不太明白？'
  },
  programming_languages: (prev) => {
    if (prev.learning_difficulty) return '了解你遇到的困难了。那换个话题～你平时写代码主要用哪些语言？Python、C、Java，还是其他？'
    return '你平时写代码主要用哪些编程语言呢？'
  },
  coding_blockers: (prev) => {
    if (prev.programming_languages) return '明白。那你写代码时最容易卡在哪里——是理解题目思路、写具体语法、还是调试找错？'
    if (prev.learning_difficulty) return '写代码时，你觉得自己更容易卡在思路理解上，还是语法和调试上？'
    return '写代码的时候，你觉得最费时间的环节是什么？'
  },
  completed_courses: (prev) => {
    if (prev.current_courses) return '除了现在学的这些，之前你还学过哪些计算机课程呢？'
    return '你之前学过哪些计算机相关课程？'
  },
  cognitive_style: (prev) => {
    if (prev.coding_blockers && prev.coding_blockers.includes('思路') || prev.coding_blockers.includes('理解'))
      return '我了解了，你在理解思路上花的时间比较多。那你学新知识时，更偏好哪种方式？图示讲解、代码示例、分步骤推导，还是项目案例？'
    if (prev.learning_difficulty) return '我记下了。那学新东西时，你更喜欢哪种方式？比如看图示、读代码、跟着步骤推导，还是直接做项目？'
    return '你平时学新知识的时候，最喜欢哪种方式？图示讲解、代码示例、分步骤推导，还是项目实践？'
  },
  learning_goals: (prev) => {
    if (prev.cognitive_style) return '很好，我后面会优先给你匹配图示和代码结合的资源。那你最近想达成什么小目标？比如完成某门课作业、准备考试、掌握某个知识点？'
    return '你最近有什么学习目标吗？比如通过考试、完成大作业，还是想深入掌握某个方向？'
  },
  resource_preference: (prev) => {
    if (prev.learning_goals) return '了解了你的目标。最后问一下～什么样的学习材料对你帮助最大？代码案例、思维导图、分层练习题，还是简洁讲义？'
    if (prev.cognitive_style) return '根据你的学习风格，你更喜欢什么形式的学习材料呢？'
    return '你喜欢什么样的学习材料？代码案例、思维导图、分层练习题，还是讲义？'
  },
}

// ---- Acknowledgments (natural responses that reference prior answers) ----

function pickAcknowledgment(collected: Record<string, string>): string {
  const latest = Object.keys(collected).pop()
  if (!latest) return '好的，我记下了。'

  const map: Record<string, string[]> = {
    current_courses: ['好的，我了解了你的课程情况。', '收到，这些课程很有代表性。'],
    learning_difficulty: ['我明白难点在哪了，这会帮我后面给你匹配合适的资源。', '了解了，这些知识点确实容易卡住。'],
    programming_languages: ['好的，我记下你的编程语言基础了。', '明白了！'],
    coding_blockers: ['了解你的卡点了，这很常见。', '收到，我会在后续资源中多关注这方面。'],
    completed_courses: ['好的，你的基础背景我大致清楚了。', '了解了你的学习历程。'],
    cognitive_style: ['明白了你的学习偏好，这对后续资源生成很重要。', '很好，我知道该怎么准备了。'],
    learning_goals: ['目标很清晰！', '明白你的方向了。'],
    resource_preference: ['好的，我会按照这个偏好来准备资源。', '了解！'],
  }

  const options = map[latest] || ['明白了！', '好的，我记下了。']
  return options[Math.floor(Math.random() * options.length)]
}

// =====================================================================
// MOCK IMPLEMENTATIONS — replace with LLM when ready
// =====================================================================

/** LLM_REPLACE: use LLM to extract structured fields from user message */
export function extractFieldsMock(
  userMessage: string,
  currentFields: Record<string, string>,
  currentMissing: string[],
): { collected: Record<string, string>; missing: string[] } {
  const collected = { ...currentFields }
  const missing = [...currentMissing]

  // Simple keyword-based extraction for mock — LLM would do semantic extraction
  const lower = userMessage.toLowerCase()

  const extractors: Array<{ field: string; match: (msg: string) => boolean }> = [
    { field: 'current_courses', match: (m) => /程序设计|数据结构|操作系统|计算机网络|组成原理|数据库|c语言|python|java/i.test(m) },
    { field: 'learning_difficulty', match: (m) => /递归|数组|指针|遍历|排序|搜索|算法|理解|不.*懂|不.*会|困难|卡/i.test(m) && m.length > 8 },
    { field: 'programming_languages', match: (m) => /python|c语言|java|c\+\+|javascript|编程语言/i.test(m) },
    { field: 'coding_blockers', match: (m) => /思路|语法|调试|错误|bug|参考|示例/i.test(m) },
    { field: 'completed_courses', match: (m) => /学过|修过|上过|完成.*课程|之前.*课/i.test(m) },
    { field: 'cognitive_style', match: (m) => /图示|代码示例|分步骤|推导|项目案例|可视化|讲解/i.test(m) },
    { field: 'learning_goals', match: (m) => /目标|掌握|完成作业|考试|提升|练习|项目|理解/i.test(m) },
    { field: 'resource_preference', match: (m) => /思维导图|代码案例|练习题|讲义|视频|笔记|文档/i.test(m) },
  ]

  for (const { field, match } of extractors) {
    if (missing.includes(field) && match(lower)) {
      collected[field] = userMessage
      const idx = missing.indexOf(field)
      if (idx >= 0) missing.splice(idx, 1)
    }
  }

  // If no specific field matched but we have missing fields, assign to first missing
  if (!extractors.some(({ field, match }) => missing.includes(field) && match(lower)) && missing.length > 0) {
    // Assign to the first available missing field
    const fallbackField = missing[0]
    collected[fallbackField] = userMessage
    missing.splice(0, 1)
  }

  return { collected, missing }
}

/** LLM_REPLACE: use LLM to generate a contextual follow-up question */
export function getNextQuestionMock(
  missing: string[],
  collected: Record<string, string>,
  lastUserMessage: string,
): string {
  if (missing.length === 0) {
    return '好的，我大概了解了你的情况。接下来我们做几道轻量诊断题，帮助我更准确地评估你的知识基础和实践能力，好吗？'
  }

  const nextField = missing[0]
  const questionFn = fieldQuestions[nextField]
  if (!questionFn) {
    return '能再跟我多说说你的学习情况吗？'
  }

  const ack = pickAcknowledgment(collected)
  const question = questionFn(collected)

  return `${ack} ${question}`
}

/** LLM_REPLACE: use LLM to evaluate diagnosis answers and provide calibrated feedback */
export function evaluateDiagnosisMock(answers: Record<string, string>): DiagnosisResult {
  const questions = mockDiagnosisQuestions
  let correct = 0
  const weakPoints: string[] = []

  for (const q of questions) {
    if (answers[q.id] === q.correct) {
      correct++
    } else {
      // Map wrong answers to weak point descriptions
      if (q.knowledge_point === '递归') weakPoints.push('递归出口')
      if (q.knowledge_point === '数组边界') weakPoints.push('数组边界')
      if (q.knowledge_point === '二叉树遍历') weakPoints.push('遍历顺序')
    }
  }

  const ratio = correct / questions.length

  if (ratio >= 1) {
    return {
      totalCorrect: correct,
      totalQuestions: questions.length,
      knowledgeBaseAdjust: 15,
      practiceAbilityAdjust: 12,
      weakPointsAdded: [],
      note: '诊断题校准完成',
    }
  }
  if (ratio >= 0.66) {
    return {
      totalCorrect: correct,
      totalQuestions: questions.length,
      knowledgeBaseAdjust: 6,
      practiceAbilityAdjust: 4,
      weakPointsAdded: weakPoints,
      note: '诊断题校准完成',
    }
  }
  return {
    totalCorrect: correct,
    totalQuestions: questions.length,
    knowledgeBaseAdjust: -6,
    practiceAbilityAdjust: -5,
    weakPointsAdded: weakPoints,
    note: '待针对性练习',
  }
}

/** LLM_REPLACE: use LLM to generate a full 6-dimension profile from collected fields + diagnosis */
export function generateFinalProfileMock(
  collectedFields: Record<string, string>,
  diagnosisResults: DiagnosisResult | null,
): StudentProfile {
  const baseStudent = USE_MOCK ? mockStudentProfile.student : NEUTRAL_STUDENT
  const baseProfile = USE_MOCK ? { ...mockStudentProfile.profile } : structuredClone(NEUTRAL_PROFILE_DIMENSIONS)

  // Adjust knowledge_base based on diagnosis
  if (baseProfile.knowledge_base && diagnosisResults) {
    const kb = baseProfile.knowledge_base
    const baseScore = USE_MOCK ? (kb.score ?? 0) : 50
    const minScore = USE_MOCK ? 30 : 0
    const newScore = Math.max(minScore, Math.min(100, baseScore + diagnosisResults.knowledgeBaseAdjust))
    kb.score = newScore
    kb.stars = scoreToStars(newScore)
    kb.note = diagnosisResults.note
    baseProfile.knowledge_base = kb
  }

  // Adjust practice_ability based on diagnosis
  if (baseProfile.practice_ability && diagnosisResults) {
    const pa = baseProfile.practice_ability
    const baseScore = USE_MOCK ? (pa.score ?? 0) : 50
    const minScore = USE_MOCK ? 30 : 0
    const newScore = Math.max(minScore, Math.min(100, baseScore + diagnosisResults.practiceAbilityAdjust))
    pa.score = newScore
    pa.stars = scoreToStars(newScore)
    pa.note = diagnosisResults.note
    baseProfile.practice_ability = pa
  }

  // Add weak points from diagnosis
  if (baseProfile.weak_points && diagnosisResults && diagnosisResults.weakPointsAdded.length > 0) {
    const existing = baseProfile.weak_points.tags || []
    const merged = [...new Set([...existing, ...diagnosisResults.weakPointsAdded])]
    baseProfile.weak_points = { ...baseProfile.weak_points, tags: merged }
  }

  return { student: baseStudent, profile: baseProfile }
}

function scoreToStars(score: number): number {
  if (score >= 85) return 5
  if (score >= 70) return 4
  if (score >= 55) return 3
  if (score >= 40) return 2
  return 1
}

// =====================================================================
// State machine transitions
// =====================================================================

export function createInitialState(): InterviewState {
  const initialMissing = ALL_FIELDS
    .filter((f) => f.key !== 'diagnosis_result')
    .map((f) => f.key)

  const firstQuestion = '嗨！我是你的学习伙伴 CodeBuddy 🎓 很高兴认识你～我想先了解一下：你最近主要在上哪些计算机专业课呀？有没有哪门课让你觉得比较吃力？'

  return {
    messages: [{ role: 'buddy', content: firstQuestion }],
    collectedFields: {},
    missingFields: initialMissing,
    stage: 'collecting',
    nextQuestion: firstQuestion,
    diagnosisQuestions: mockDiagnosisQuestions,
    diagnosisAnswers: {},
    diagnosisEvaluated: false,
    diagnosisResults: null,
    finalProfile: null,
  }
}

export function processMessage(state: InterviewState, userText: string): InterviewState {
  const next = { ...state }

  // Add user message
  next.messages = [...next.messages, { role: 'user', content: userText }]

  // LLM_REPLACE: extractFieldsWithLLM(userText, currentFields, currentMissing)
  const { collected, missing } = extractFieldsMock(userText, next.collectedFields, next.missingFields)
  next.collectedFields = collected
  next.missingFields = missing

  if (missing.length === 0) {
    next.stage = 'ready_for_diagnosis'
    next.nextQuestion = '好的，我大概了解了你的情况。接下来我们做几道轻量诊断题，帮助我更准确地评估你的知识基础和实践能力，好吗？'
    next.messages = [...next.messages, { role: 'buddy', content: next.nextQuestion }]
  } else {
    // LLM_REPLACE: getNextQuestionWithLLM(missing, collected, userText)
    next.nextQuestion = getNextQuestionMock(missing, collected, userText)
    next.messages = [...next.messages, { role: 'buddy', content: next.nextQuestion }]
  }

  return next
}

export function startDiagnosis(state: InterviewState): InterviewState {
  return {
    ...state,
    stage: 'diagnosis',
  }
}

export function submitDiagnosis(state: InterviewState, answers: Record<string, string>): InterviewState {
  // LLM_REPLACE: evaluateDiagnosisWithLLM(answers, state.collectedFields)
  const results = evaluateDiagnosisMock(answers)

  const next = { ...state }
  next.diagnosisAnswers = answers
  next.diagnosisEvaluated = true
  next.diagnosisResults = results
  next.collectedFields = { ...next.collectedFields, diagnosis_result: `${results.totalCorrect}/${results.totalQuestions} 正确` }
  next.missingFields = next.missingFields.filter((f) => f !== 'diagnosis_result')
  next.stage = 'ready_for_profile'

  const resultMsg = results.totalCorrect === results.totalQuestions
    ? `太棒了！${results.totalQuestions} 道题全部答对 🎉 你的基础很扎实。让我为你生成完整的学习画像吧！`
    : `诊断完成！你答对了 ${results.totalCorrect}/${results.totalQuestions} 题。我已经根据结果校准了你的画像，来看看吧～`

  next.messages = [...next.messages, { role: 'buddy', content: resultMsg }]
  next.nextQuestion = null

  return next
}

export function generateProfile(state: InterviewState): InterviewState {
  // LLM_REPLACE: generateFinalProfileWithLLM(state.collectedFields, state.diagnosisResults)
  const profile = generateFinalProfileMock(state.collectedFields, state.diagnosisResults)

  return {
    ...state,
    stage: 'complete',
    finalProfile: profile,
    messages: [
      ...state.messages,
      { role: 'buddy', content: '你的六维学习画像已经生成好啦！以下是基于我们的对话和诊断题的综合评估。你可以基于此画像生成个性化资源，或者规划专属学习路径。' },
    ],
  }
}

// ---- Demo: Li student quick fill ----

export function applyDemoFill(state: InterviewState): InterviewState {
  const answers: Array<{ field: string; text: string }> = [
    { field: 'current_courses', text: '我在学习程序设计基础和数据结构与算法，对递归、数组操作和二叉树遍历感觉不太顺手。' },
    { field: 'learning_difficulty', text: '递归、二叉树遍历、数组操作这些理解起来比较抽象，写代码时经常要参考示例。' },
    { field: 'programming_languages', text: '我会 Python 和 C 语言基础，Python 用得多一些，C 语言在学数据结构时也在用。' },
    { field: 'coding_blockers', text: '写代码时更容易卡在理解思路上，特别是递归和树的题目，经常需要参考示例代码。' },
    { field: 'completed_courses', text: '之前学过计算机导论和 C 语言程序设计基础。' },
    { field: 'cognitive_style', text: '我更喜欢图示讲解和代码示例，分步骤推导也很好，不太适应纯理论讲解。' },
    { field: 'learning_goals', text: '我想掌握递归、数组和二叉树遍历，完成这学期的课程练习和期末考试。' },
    { field: 'resource_preference', text: '我喜欢代码案例、思维导图、分层练习题和简洁讲义，不太喜欢看太长的视频。' },
  ]

  const messages: Message[] = [
    { role: 'buddy', content: state.messages[0].content },
  ]
  const collected: Record<string, string> = {}

  for (const a of answers) {
    collected[a.field] = a.text
  }

  // Build messages for demo fill
  for (let i = 0; i < answers.length; i++) {
    messages.push({ role: 'user', content: answers[i].text })
    if (i < answers.length - 1) {
      const remainingMissing = answers.slice(i + 1).map((a) => a.field)
      const partialCollected: Record<string, string> = {}
      for (let j = 0; j <= i; j++) {
        partialCollected[answers[j].field] = answers[j].text
      }
      messages.push({ role: 'buddy', content: getNextQuestionMock(remainingMissing, partialCollected, answers[i].text) })
    }
  }

  // Final ready message
  messages.push({
    role: 'buddy',
    content: '好的，我大概了解了你的情况。接下来我们做几道轻量诊断题，帮助我更准确地评估你的知识基础和实践能力，好吗？',
  })

  return {
    ...state,
    messages,
    collectedFields: collected,
    missingFields: ['diagnosis_result'],
    stage: 'ready_for_diagnosis',
    nextQuestion: null,
  }
}

// =====================================================================
// Profile mapping: Backend <-> Frontend (Phase 6A)
// =====================================================================

function safeJsonParse(raw: string | null): string[] {
  if (!raw) return []
  try {
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

/**
 * Convert backend DB profile to frontend StudentProfile format.
 * Used when loading an existing profile to skip the interview.
 */
export function mapBackendProfileToStudentProfile(backend: BackendProfile, studentName?: string): StudentProfile {
  const kbScore = backend.knowledge_base_score ?? 0
  const paScore = backend.practice_ability_score ?? 0

  return {
    student: {
      name: studentName || '当前用户',
      grade: '待完善',
      major: '待完善',
      background: backend.profile_summary || '',
    },
    profile: {
      knowledge_base: {
        label: '知识基础',
        stars: scoreToStars(kbScore),
        score: kbScore,
        max_score: 100,
        note: backend.diagnosis_status || '',
      },
      practice_ability: {
        label: '实践能力',
        stars: scoreToStars(paScore),
        score: paScore,
        max_score: 100,
        note: backend.diagnosis_status || '',
      },
      cognitive_style: {
        label: '认知风格',
        tags: safeJsonParse(backend.cognitive_styles),
      },
      weak_points: {
        label: '易错点特征',
        tags: safeJsonParse(backend.error_patterns),
      },
      learning_goals: {
        label: '学习目标',
        tags: safeJsonParse(backend.learning_goals),
      },
      resource_preferences: {
        label: '资源偏好',
        tags: safeJsonParse(backend.resource_preferences),
      },
    },
  }
}

/**
 * Convert frontend StudentProfile to backend ProfileUpdatePayload for PUT.
 */
export function mapStudentProfileToBackend(profile: StudentProfile): ProfileUpdatePayload {
  return {
    knowledge_base_score: profile.profile.knowledge_base?.score ?? undefined,
    practice_ability_score: profile.profile.practice_ability?.score ?? undefined,
    cognitive_styles: profile.profile.cognitive_style?.tags?.length
      ? JSON.stringify(profile.profile.cognitive_style.tags)
      : undefined,
    error_patterns: profile.profile.weak_points?.tags?.length
      ? JSON.stringify(profile.profile.weak_points.tags)
      : undefined,
    learning_goals: profile.profile.learning_goals?.tags?.length
      ? JSON.stringify(profile.profile.learning_goals.tags)
      : undefined,
    resource_preferences: profile.profile.resource_preferences?.tags?.length
      ? JSON.stringify(profile.profile.resource_preferences.tags)
      : undefined,
    profile_summary: profile.student?.background || undefined,
    diagnosis_status: profile.profile.knowledge_base?.note || undefined,
  }
}

/**
 * Check if a backend profile is complete enough to skip the interview.
 * Requires at minimum knowledge_base_score and practice_ability_score to be set.
 */
export function isProfileComplete(backend: BackendProfile): boolean {
  return backend.knowledge_base_score != null && backend.practice_ability_score != null
}
