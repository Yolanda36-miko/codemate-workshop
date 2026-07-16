/**
 * ProfileInterviewService — State-machine driven learning profile interview.
 *
 * Stages: collect_profile → ask_prerequisite → ask_error_points → summary → complete
 *
 * Key rules:
 * 1. Starts directly with DS learning questions — no name collection
 * 2. Each stage asks targeted questions to fill missing profile fields
 * 3. Stage only moves forward, never backwards
 * 4. Profile merge: strings only on new detection, arrays always union-merge
 * 5. localStorage persistence with versioned schema
 */

import type { DiagnosisQuestion, StudentProfile, ProfileDimension, BackendProfile, ProfileUpdatePayload, DSProfileData, QuickProfile, ProfileChatResponse } from '../types'
import { USE_MOCK } from './api'
import { mockDiagnosisQuestions, mockStudentProfile } from '../mock/profile'

// ---- Storage version ----
export const PROFILE_STORAGE_VERSION = 3
const STORAGE_KEYS = {
  version: 'codemate_profile_version',
  messages: 'codemate_profile_messages',
  draft: 'codemate_profile_draft',
  stage: 'codemate_profile_stage',
}

// ---- Types ----

export interface Message {
  role: 'buddy' | 'user'
  content: string
}

export type InterviewStage =
  | 'collect_profile'
  | 'ask_prerequisite'
  | 'ask_error_points'
  | 'summary'
  | 'complete'

export interface InterviewState {
  messages: Message[]
  profileDraft: Record<string, unknown>
  missingFields: string[]
  stage: InterviewStage
}

// ---- Key profile fields ----

const KEY_FIELDS = [
  'programming_language',
  'learning_goal',
  'foundation_level',
  'current_difficulties',
  'expression_preferences',
  'learned_courses',
  'error_prone_points',
]

const PREREQUISITE_FIELDS = ['foundation_level', 'learned_courses']
const ERROR_FIELDS = ['error_prone_points']

// ---- Safe value helpers (handle string | string[] | number | null | undefined) ----

export function draftValueToText(value: unknown): string {
  if (value === null || value === undefined) return ''
  if (Array.isArray(value)) return value.filter(Boolean).join('、')
  if (typeof value === 'string') return value
  if (typeof value === 'number' || typeof value === 'boolean') return String(value)
  return ''
}

export function hasDraftValue(value: unknown): boolean {
  return draftValueToText(value).trim().length > 0
}

export function draftValueToList(value: unknown): string[] {
  if (Array.isArray(value)) return value.map(String).filter(Boolean)
  const text = draftValueToText(value).trim()
  if (!text) return []
  return text.split(/[、,，]/).map(t => t.trim()).filter(Boolean)
}

// ---- Tag helpers ----

function splitTags(val: unknown): Set<string> {
  const list = draftValueToList(val)
  return new Set(list)
}

function extractLanguage(message: string): string | null {
  const lower = message.toLowerCase()
  // substring matching for C++ — avoid \b which fails on "+" (non-word char) after Chinese punctuation
  if (lower.includes('c++') || lower.includes('cpp') || lower.includes('cplusplus') || lower.includes('c plus plus')) return 'C++'
  if (lower.includes('python')) return 'Python'
  if (lower.includes('java') && !lower.includes('javascript')) return 'Java'
  if (/c语言|用\s*c\b|\bc\s*语言/i.test(lower) && !lower.includes('c++') && !lower.includes('python')) return 'C'
  return null
}

function extractGoal(message: string): string[] {
  const lower = message.toLowerCase()
  const goals: string[] = []
  if (/刷题|题目|leetcode|力扣|牛客/i.test(lower)) goals.push('刷题训练')
  if (/考试|复习|期末/i.test(lower)) goals.push('考试复习')
  if (/课程作业|作业/i.test(lower)) goals.push('课程作业')
  if (/项目实践/i.test(lower)) goals.push('项目实践')
  if ((/项目|实践/.test(lower)) && !goals.includes('项目实践')) goals.push('项目实践')
  if (/理解|概念|入门/.test(lower)) goals.push('概念理解')
  return goals
}

function extractFoundation(message: string): string | null {
  const lower = message.toLowerCase()
  if (/薄弱|差|不好|零基础|基础差|一般偏弱/i.test(lower)) return '基础薄弱'
  if (/一般|还行|中等/i.test(lower)) return '一般'
  if (/较好|熟悉|扎实|比较会/i.test(lower)) return '较好'
  return null
}

function extractDifficulties(message: string): string[] {
  const lower = message.toLowerCase()
  const tags: string[] = []
  if (/递归/.test(lower)) tags.push('递归调用栈')
  if (/二叉树|前序|中序|后序/.test(lower)) tags.push('树遍历')
  if (/树/.test(lower) && !/二叉树/.test(lower)) tags.push('树遍历')
  if (/遍历/.test(lower) && !/二叉树/.test(lower)) tags.push('树遍历')
  if (/bfs|dfs|最短路|连通/i.test(lower)) tags.push('图遍历')
  if (/图/.test(lower) && !/图解/.test(lower)) tags.push('图遍历')
  if (/排序|快排|快速排序/.test(lower)) tags.push('排序算法')
  if (/动态规划|dp|背包/i.test(lower)) tags.push('动态规划')
  if (/哈希|散列|冲突/.test(lower)) tags.push('哈希冲突')
  if (/二分/.test(lower)) tags.push('二分查找边界')
  return tags
}

function extractPreferences(message: string): string[] {
  const lower = message.toLowerCase()
  const tags: string[] = []
  if (/图解|图示|可视化/.test(lower)) tags.push('图解讲解')
  if (/代码示例|示例代码|模板/.test(lower)) tags.push('代码示例')
  if (/代码/.test(lower) && !/代码示例/.test(lower) && !/示例代码/.test(lower)) tags.push('代码示例')
  if (/易错|错题|坑点/.test(lower)) tags.push('易错点')
  if (/练习|题目|刷题/.test(lower)) tags.push('分层练习')
  if (/项目|案例|实践/.test(lower) && !/项目实践/.test(lower)) tags.push('项目案例')
  return tags
}

function extractErrorPoints(message: string): string[] {
  const lower = message.toLowerCase()
  const tags: string[] = []
  const hasError = /搞混|搞反|搞错|出错|写错|漏写|忘记|不对|总是错|经常错/.test(lower)
  if (/递归/.test(lower) && (hasError || /终止条件/.test(lower))) tags.push('递归终止条件')
  if (/遍历/.test(lower) && hasError) tags.push('遍历顺序混淆')
  if (/复杂度|大O/.test(lower) && hasError) tags.push('复杂度判断')
  if (/visited|标记/.test(lower) && hasError) tags.push('visited 标记时机')
  if (/状态转移|转移方程/.test(lower) && hasError) tags.push('状态转移方程')
  return tags
}

function extractCourses(message: string): string[] {
  const lower = message.toLowerCase()
  const tags: string[] = []
  if (/程序设计|C语言程序设计|C程序设计|Python基础|Java基础/i.test(lower)) tags.push('程序设计基础')
  if (/离散数学|离散/.test(lower)) tags.push('离散数学')
  if (/数据结构/.test(lower) && /学过|修过|上过|完成|之前/.test(lower)) tags.push('数据结构')
  if (/计算机导论/.test(lower)) tags.push('计算机导论')
  if (/编程语言基础/.test(lower)) tags.push('编程语言基础')
  return tags
}

// ---- Profile merge (core) ----

function mergeProfile(profile: Record<string, unknown>, message: string): Record<string, unknown> {
  const merged: Record<string, unknown> = { ...profile }

  // Single-value: only set if detected in current message
  const lang = extractLanguage(message)
  if (lang) merged.programming_language = lang

  const goals = extractGoal(message)
  if (goals.length > 0) merged.learning_goal = goals.join('、')

  const foundation = extractFoundation(message)
  if (foundation) merged.foundation_level = foundation

  // Multi-value: union-merge
  const diffs = extractDifficulties(message)
  if (diffs.length > 0) {
    const existing = splitTags(merged.current_difficulties || '')
    diffs.forEach(d => existing.add(d))
    merged.current_difficulties = [...existing].sort().join('、')
  }

  const prefs = extractPreferences(message)
  if (prefs.length > 0) {
    const existing = splitTags(merged.expression_preferences || '')
    prefs.forEach(p => existing.add(p))
    merged.expression_preferences = [...existing].sort().join('、')
  }

  const errors = extractErrorPoints(message)
  if (errors.length > 0) {
    const existing = splitTags(merged.error_prone_points || '')
    errors.forEach(e => existing.add(e))
    merged.error_prone_points = [...existing].sort().join('、')
  }

  const courses = extractCourses(message)
  if (courses.length > 0) {
    const existing = splitTags(merged.learned_courses || '')
    courses.forEach(c => existing.add(c))
    merged.learned_courses = [...existing].sort().join('、')
  }

  return merged
}

function computeMissingFields(profile: Record<string, unknown>): string[] {
  return KEY_FIELDS.filter(f => !hasDraftValue(profile[f]))
}

// ---- Stage transition engine ----

function determineNextStage(profile: Record<string, unknown>, currentStage: InterviewStage): InterviewStage {
  const hasPrereq = PREREQUISITE_FIELDS.some(f => hasDraftValue(profile[f]))
  const hasErrors = ERROR_FIELDS.some(f => hasDraftValue(profile[f]))
  const keyFieldsFilled = KEY_FIELDS.filter(f => hasDraftValue(profile[f])).length >= 4

  if (currentStage === 'collect_profile') {
    if (keyFieldsFilled && !hasPrereq) return 'ask_prerequisite'
    if (keyFieldsFilled && hasPrereq && !hasErrors) return 'ask_error_points'
    if (keyFieldsFilled && hasPrereq && hasErrors) return 'summary'
    return 'collect_profile'
  }

  if (currentStage === 'ask_prerequisite') {
    const nowHasPrereq = PREREQUISITE_FIELDS.some(f => hasDraftValue(profile[f]))
    if (nowHasPrereq && hasErrors) return 'summary'
    if (nowHasPrereq && !hasErrors) return 'ask_error_points'
    return 'ask_prerequisite'
  }

  if (currentStage === 'ask_error_points') {
    const nowHasErrors = ERROR_FIELDS.some(f => hasDraftValue(profile[f]))
    return nowHasErrors || keyFieldsFilled ? 'summary' : 'ask_error_points'
  }

  // summary: stay at summary, allow continued input
  return 'summary'
}

function generateReply(stage: InterviewStage, profile: Record<string, unknown>, _userMessage: string): string {
  const diffs = draftValueToText(profile.current_difficulties)
  const lang = draftValueToText(profile.programming_language)
  const goal = draftValueToText(profile.learning_goal)
  const prefs = draftValueToText(profile.expression_preferences)

  switch (stage) {
    case 'collect_profile': {
      if (diffs && lang && goal && prefs) {
        return `好的，我记下了：你主要用 ${lang}，目标是${goal}，困难点在${diffs}，偏好${prefs}。接下来能跟我说说你之前的先修基础吗？比如学过程序设计基础、离散数学吗？基础水平如何？`
      }
      if (diffs && !lang) {
        return `了解了${diffs}这些困难点。你平时写算法题主要用哪种语言？C++、Python、Java 还是 C？`
      }
      if (lang && !goal) {
        return `你目前学习数据结构与算法的目标是什么？刷题训练、考试复习、课程作业，还是项目实践？`
      }
      if (lang && !prefs) {
        return `你更喜欢哪种学习资源？图解讲解、代码示例、易错点归纳，还是分层练习？`
      }
      return `能再跟我说说你的学习情况吗？你常用什么语言？有什么学习目标？喜欢什么资源形式？`
    }

    case 'ask_prerequisite':
      return `你之前学过哪些先修课程？程序设计基础、离散数学、计算机导论？另外你觉得自己的基础水平如何——基础薄弱、一般，还是比较扎实？`

    case 'ask_error_points':
      return `你在写算法题时容易在哪些地方出错？比如递归终止条件漏写、遍历顺序搞混、复杂度分析算错，还是状态转移方程推不出来？`

    case 'summary': {
      const lines: string[] = []
      if (hasDraftValue(profile.programming_language)) lines.push(`编程语言：${lang}`)
      if (hasDraftValue(profile.learning_goal)) lines.push(`学习目标：${goal}`)
      if (hasDraftValue(profile.foundation_level)) lines.push(`基础水平：${draftValueToText(profile.foundation_level)}`)
      if (hasDraftValue(profile.current_difficulties)) lines.push(`薄弱模块：${diffs}`)
      if (hasDraftValue(profile.expression_preferences)) lines.push(`偏好资源：${prefs}`)
      if (hasDraftValue(profile.error_prone_points)) lines.push(`易错点：${draftValueToText(profile.error_prone_points)}`)

      if (lines.length > 0) {
        return `你的学习画像已经比较完整了！以下是摘要：\n${lines.join('\n')}\n\n你可以继续补充更多信息，我会实时更新画像。也可以切换到资源生成页面查看个性化资源。`
      }
      return `你的学习画像已经比较完整了！你可以继续补充更多信息，我会实时更新画像。`
    }

    default:
      return '还有其他想告诉我的吗？'
  }
}

// =====================================================================
// Core state transition
// =====================================================================

export function processMessage(state: InterviewState, userText: string): InterviewState {
  // 1. Merge profile from user message
  const newProfile = mergeProfile(state.profileDraft, userText)

  // 2. Determine next stage (only moves forward)
  const nextStage = determineNextStage(newProfile, state.stage)

  // 3. Generate reply for the NEW stage
  const reply = generateReply(nextStage, newProfile, userText)

  // 4. Compute missing fields
  const missing = computeMissingFields(newProfile)

  return {
    messages: [
      ...state.messages,
      { role: 'user' as const, content: userText },
      { role: 'buddy' as const, content: reply },
    ],
    profileDraft: newProfile,
    missingFields: missing,
    stage: nextStage,
  }
}

// Normalize profile draft values: convert arrays to '、'-joined strings for internal consistency
function normalizeDraft(draft: Record<string, unknown>): Record<string, unknown> {
  const normalized: Record<string, unknown> = {}
  for (const [key, value] of Object.entries(draft)) {
    if (Array.isArray(value)) {
      normalized[key] = value.filter(Boolean).join('、')
    } else {
      normalized[key] = value
    }
  }
  return normalized
}

export function createInitialState(existingProfile?: Record<string, unknown>): InterviewState {
  const savedVersion = (() => { try { return localStorage.getItem(STORAGE_KEYS.version) } catch { return null } })()

  // Clear stale caches if version changed
  if (savedVersion && String(savedVersion) !== String(PROFILE_STORAGE_VERSION)) {
    try {
      for (const key of Object.values(STORAGE_KEYS)) {
        localStorage.removeItem(key)
      }
    } catch { /* ignore */ }
  }
  try { localStorage.setItem(STORAGE_KEYS.version, String(PROFILE_STORAGE_VERSION)) } catch { /* ignore */ }

  // Restore from localStorage if available
  try {
    const savedMessages = localStorage.getItem(STORAGE_KEYS.messages)
    const savedDraft = localStorage.getItem(STORAGE_KEYS.draft)
    const savedStage = localStorage.getItem(STORAGE_KEYS.stage)

    if (savedMessages && savedDraft && savedStage) {
      const messages = JSON.parse(savedMessages) as Message[]
      const rawDraft = JSON.parse(savedDraft) as Record<string, unknown>
      const profileDraft = normalizeDraft(rawDraft)
      const stage = savedStage as InterviewStage

      if (messages.length > 0 && ['collect_profile', 'ask_prerequisite', 'ask_error_points', 'summary', 'complete'].includes(stage)) {
        return {
          messages,
          profileDraft,
          missingFields: computeMissingFields(profileDraft),
          stage,
        }
      }
    }
  } catch { /* ignore */ }

  const profile = { ...(existingProfile || {}) }

  // Start directly at collect_profile — no name collection
  const greeting = '你好，我是你的学习伙伴 CodeBuddy。为了帮你生成更合适的数据结构学习资源，我想先了解你的学习情况：你目前最吃力的是递归调用栈、二叉树遍历、图算法、排序算法、散列表，还是动态规划？你也可以告诉我常用编程语言、学习目标和喜欢的资源形式。'
  return {
    messages: [{ role: 'buddy', content: greeting }],
    profileDraft: profile,
    missingFields: KEY_FIELDS,
    stage: 'collect_profile',
  }
}

export function persistState(state: InterviewState): void {
  try {
    localStorage.setItem(STORAGE_KEYS.messages, JSON.stringify(state.messages))
    localStorage.setItem(STORAGE_KEYS.draft, JSON.stringify(state.profileDraft))
    localStorage.setItem(STORAGE_KEYS.stage, state.stage)
  } catch { /* ignore */ }
}

// =====================================================================
// Mock chat response builder (for api.ts USE_MOCK path)
// =====================================================================

export function buildMockChatResponse(
  message: string,
  currentProfile: Record<string, unknown>,
  currentStage: string,
): ProfileChatResponse {
  // 1. Merge profile
  const newProfile = mergeProfile(currentProfile, message)

  // 2. Determine next stage
  const nextStage = determineNextStage(newProfile, currentStage as InterviewStage)

  // 3. Generate reply
  const reply = generateReply(nextStage, newProfile, message)

  // 4. Compute missing
  const missing = computeMissingFields(newProfile)
  const isComplete = nextStage === 'summary'

  return {
    message: reply,
    reply,
    profile: newProfile as Record<string, unknown>,
    extracted_fields: newProfile as Record<string, unknown>,
    missing_fields: missing,
    stage: nextStage,
    is_complete: isComplete,
  }
}

// =====================================================================
// Profile generation (from collected profileDraft)
// =====================================================================

export function generateFinalProfileMock(
  profileDraft: Record<string, unknown>,
): StudentProfile {
  const baseStudent = USE_MOCK ? { ...mockStudentProfile.student } : {
    name: '小栈',
    display_name: '小栈',
    grade: '',
    major: '',
    background: '',
  }
  const baseProfile = USE_MOCK ? { ...mockStudentProfile.profile } : {}

  baseProfile.programming_language = {
    label: '编程语言',
    tags: hasDraftValue(profileDraft.programming_language) ? [draftValueToText(profileDraft.programming_language)] : [],
  }
  baseProfile.learning_goal = {
    label: '学习目标',
    tags: draftValueToList(profileDraft.learning_goal),
  }
  baseProfile.learning_difficulties = {
    label: '学习困难',
    tags: draftValueToList(profileDraft.current_difficulties),
  }
  baseProfile.expression_preferences = {
    label: '资源偏好',
    tags: draftValueToList(profileDraft.expression_preferences),
  }
  baseProfile.weak_points = {
    label: '易错点',
    tags: draftValueToList(profileDraft.error_prone_points),
  }

  baseProfile.knowledge_base = baseProfile.knowledge_base || { label: '知识基础', max_score: 100 }
  baseProfile.practice_ability = baseProfile.practice_ability || { label: '实践能力', max_score: 100 }

  return { student: baseStudent, profile: baseProfile }
}

// =====================================================================
// Backend profile mapping (unchanged from prior version)
// =====================================================================

function safeJsonParse(raw: string | null): string[] {
  if (!raw) return []
  try { const parsed = JSON.parse(raw); return Array.isArray(parsed) ? parsed : [] }
  catch { return [] }
}

function safeJsonParseObj(raw: string | null): Record<string, unknown> {
  if (!raw) return {}
  try { const parsed = JSON.parse(raw); return typeof parsed === 'object' && parsed !== null && !Array.isArray(parsed) ? parsed as Record<string, unknown> : {} }
  catch { return {} }
}

function encodeDSProfileData(profile: StudentProfile): string {
  const dims = profile.profile
  const data: DSProfileData = {
    current_course: '数据结构与算法',
    programming_language: dims.programming_language?.tags?.[0] || undefined,
    learning_goal: dims.learning_goal?.tags?.[0] || undefined,
    learned_courses: safeJsonParse(null),
    current_difficulties: dims.learning_difficulties?.tags || [],
    expression_preferences: dims.expression_preferences?.tags || [],
    learning_difficulties: dims.learning_difficulties?.tags || [],
    error_prone_points: dims.weak_points?.tags || [],
  }
  return JSON.stringify(data)
}

export function decodeDSProfileData(summary: string | null): DSProfileData {
  if (!summary) return {}
  const obj = safeJsonParseObj(summary)
  if (obj.current_course || obj.programming_language || obj.learning_goal) {
    return {
      current_course: typeof obj.current_course === 'string' ? obj.current_course : undefined,
      learned_courses: Array.isArray(obj.learned_courses) ? obj.learned_courses : undefined,
      programming_language: typeof obj.programming_language === 'string' ? obj.programming_language : undefined,
      learning_goal: typeof obj.learning_goal === 'string' ? obj.learning_goal : undefined,
      foundation_level: typeof obj.foundation_level === 'string' ? obj.foundation_level : undefined,
      current_difficulties: Array.isArray(obj.current_difficulties) ? obj.current_difficulties : undefined,
      expression_preferences: Array.isArray(obj.expression_preferences) ? obj.expression_preferences : undefined,
      learning_difficulties: Array.isArray(obj.learning_difficulties) ? obj.learning_difficulties : undefined,
      error_prone_points: Array.isArray(obj.error_prone_points) ? obj.error_prone_points : undefined,
    }
  }
  return {}
}

function scoreToStars(score: number): number {
  if (score >= 85) return 5
  if (score >= 70) return 4
  if (score >= 55) return 3
  if (score >= 40) return 2
  return 1
}

export function mapBackendProfileToStudentProfile(backend: BackendProfile, studentName?: string): StudentProfile {
  const kbScore = backend.knowledge_base_score ?? undefined
  const paScore = backend.practice_ability_score ?? undefined
  const dsData = decodeDSProfileData(backend.profile_summary)

  return {
    student: {
      name: studentName || '小栈',
      display_name: studentName || '小栈',
      grade: '',
      major: '',
      background: backend.profile_summary && !backend.profile_summary.startsWith('{')
        ? backend.profile_summary
        : '',
    },
    profile: {
      knowledge_base: {
        label: '知识基础',
        ...(kbScore != null ? { stars: scoreToStars(kbScore), score: kbScore } : {}),
        max_score: 100,
        note: backend.diagnosis_status || undefined,
      },
      practice_ability: {
        label: '实践能力',
        ...(paScore != null ? { stars: scoreToStars(paScore), score: paScore } : {}),
        max_score: 100,
        note: backend.diagnosis_status || undefined,
      },
      programming_language: {
        label: '编程语言',
        tags: dsData.programming_language ? [dsData.programming_language] : safeJsonParse(backend.cognitive_styles),
      },
      learning_goal: {
        label: '学习目标',
        tags: dsData.learning_goal ? [dsData.learning_goal] : safeJsonParse(backend.learning_goals),
      },
      learning_difficulties: {
        label: '学习困难',
        tags: dsData.learning_difficulties || dsData.current_difficulties || safeJsonParse(backend.error_patterns),
      },
      expression_preferences: {
        label: '资源偏好',
        tags: dsData.expression_preferences || safeJsonParse(backend.resource_preferences),
      },
      weak_points: {
        label: '易错点',
        tags: dsData.error_prone_points || [],
      },
    },
  }
}

export function mapStudentProfileToBackend(profile: StudentProfile): ProfileUpdatePayload {
  const dsJson = encodeDSProfileData(profile)
  return {
    knowledge_base_score: profile.profile.knowledge_base?.score ?? undefined,
    practice_ability_score: profile.profile.practice_ability?.score ?? undefined,
    cognitive_styles: profile.profile.programming_language?.tags?.length
      ? JSON.stringify(profile.profile.programming_language.tags) : undefined,
    error_patterns: profile.profile.learning_difficulties?.tags?.length
      ? JSON.stringify(profile.profile.learning_difficulties.tags) : undefined,
    learning_goals: profile.profile.learning_goal?.tags?.length
      ? JSON.stringify(profile.profile.learning_goal.tags) : undefined,
    resource_preferences: profile.profile.expression_preferences?.tags?.length
      ? JSON.stringify(profile.profile.expression_preferences.tags) : undefined,
    profile_summary: dsJson,
    diagnosis_status: profile.profile.knowledge_base?.note || undefined,
  }
}

export function extractQuickProfileFromStudentProfile(profile: StudentProfile): QuickProfile {
  const dims = profile.profile
  return {
    programming_language: dims.programming_language?.tags?.[0] || undefined,
    learning_goal: dims.learning_goal?.tags?.[0] || undefined,
    foundation_level: undefined,
    current_difficulties: dims.learning_difficulties?.tags || [],
    expression_preferences: dims.expression_preferences?.tags || [],
  }
}

export function extractQuickProfileFromDSData(dsData: DSProfileData): QuickProfile {
  return {
    programming_language: dsData.programming_language || undefined,
    learning_goal: dsData.learning_goal || undefined,
    foundation_level: dsData.foundation_level || undefined,
    current_difficulties: dsData.current_difficulties || [],
    expression_preferences: dsData.expression_preferences || [],
  }
}

export function isProfileComplete(backend: BackendProfile): boolean {
  if (!backend) return false
  const hasTags = (field: string | null): boolean => {
    if (!field) return false
    try { const arr = JSON.parse(field); return Array.isArray(arr) && arr.length > 0 }
    catch { return false }
  }
  if (backend.profile_summary) {
    const dsData = decodeDSProfileData(backend.profile_summary)
    if (dsData.programming_language || dsData.learning_goal ||
        (dsData.current_difficulties && dsData.current_difficulties.length > 0) ||
        (dsData.expression_preferences && dsData.expression_preferences.length > 0)) {
      return true
    }
  }
  if (hasTags(backend.cognitive_styles)) return true
  if (hasTags(backend.error_patterns)) return true
  if (hasTags(backend.learning_goals)) return true
  if (hasTags(backend.resource_preferences)) return true
  if (backend.knowledge_base_score !== null && backend.knowledge_base_score !== undefined) return true
  if (backend.practice_ability_score !== null && backend.practice_ability_score !== undefined) return true
  if (backend.profile_summary && backend.profile_summary.trim().length > 0) return true
  if (backend.diagnosis_status && backend.diagnosis_status !== 'not_started') return true
  return false
}
