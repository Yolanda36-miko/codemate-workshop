import type { BackendProfile, Course, PathNode, PersonalizedPathResult, DSProfileData } from '../types'
import { mockLearningPath } from '../mock/path'

// =====================================================================
// Types
// =====================================================================

export interface NormalizedSignals {
  difficulties: string[]
  goals: string[]
  preferences: string[]
  foundationLevel: string | null
  knowledgeLevel: number | null
  practiceLevel: number | null
  programmingLanguage: string | null
  learnedCourses: string[]
  errorPronePoints: string[]
}

// =====================================================================
// localStorage profile draft
// =====================================================================

export function loadLocalProfileDraft(): Record<string, unknown> | null {
  try {
    const raw = localStorage.getItem('codemate_profile_draft')
    if (!raw) return null
    const data = JSON.parse(raw)
    if (!data || typeof data !== 'object' || Object.keys(data).length === 0) return null
    return data as Record<string, unknown>
  } catch {
    return null
  }
}

/**
 * Check if localStorage draft has any key fields that can drive path personalization.
 * A draft is "usable" if it has current_difficulties, learning_difficulties,
 * learning_goal, or expression_preferences.
 */
export function hasUsableLocalProfileDraft(): boolean {
  const draft = loadLocalProfileDraft()
  if (!draft) return false

  const hasDiffs =
    splitTags(draft.current_difficulties).length > 0 ||
    splitTags(draft.learning_difficulties).length > 0
  const hasGoal = splitTags(draft.learning_goal).length > 0
  const hasPrefs = splitTags(draft.expression_preferences).length > 0

  return hasDiffs || hasGoal || hasPrefs
}

// =====================================================================
// Tag helpers — handles both string ("a、b") and array (["a","b"])
// =====================================================================

function splitTags(val: unknown): string[] {
  if (!val) return []
  if (Array.isArray(val)) return val.map((t) => String(t).trim()).filter(Boolean)
  if (typeof val === 'string') return val.split('、').map((t) => t.trim()).filter(Boolean)
  return []
}

function parseJsonArray(field: string | null): string[] {
  if (!field) return []
  try {
    const arr = JSON.parse(field)
    return Array.isArray(arr) ? arr : []
  } catch {
    return []
  }
}

// =====================================================================
// Normalize profile signals from any source
// =====================================================================

export function normalizeProfileSignals(
  source: BackendProfile | Record<string, unknown> | null,
): NormalizedSignals | null {
  if (!source) return null

  // localStorage draft (Record<string, unknown>)
  if (!('user_id' in source) && !('diagnosis_status' in source)) {
    const draft = source as Record<string, unknown>
    const rawDiffs = [
      ...splitTags(draft.current_difficulties),
      ...splitTags(draft.learning_difficulties),
    ]
    return {
      difficulties: [...new Set(rawDiffs)],
      goals: splitTags(draft.learning_goal),
      preferences: splitTags(draft.expression_preferences),
      foundationLevel: (draft.foundation_level as string) || null,
      knowledgeLevel: null,
      practiceLevel: null,
      programmingLanguage: (draft.programming_language as string) || null,
      learnedCourses: splitTags(draft.learned_courses),
      errorPronePoints: splitTags(draft.error_prone_points),
    }
  }

  // BackendProfile
  const bp = source as BackendProfile
  let dsProfile: DSProfileData | null = null
  if (bp.profile_summary) {
    try {
      dsProfile = JSON.parse(bp.profile_summary)
    } catch {
      /* ignore malformed JSON */
    }
  }

  const difficulties = [
    ...parseJsonArray(bp.error_patterns),
    ...(dsProfile?.current_difficulties ?? []),
    ...(dsProfile?.learning_difficulties ?? []),
    ...(dsProfile?.error_prone_points ?? []),
  ]
  const goals = [
    ...parseJsonArray(bp.learning_goals),
    ...(dsProfile?.learning_goal ? [dsProfile.learning_goal] : []),
  ]
  const preferences = [
    ...parseJsonArray(bp.resource_preferences),
    ...(dsProfile?.expression_preferences ?? []),
  ]

  return {
    difficulties: [...new Set(difficulties)],
    goals: [...new Set(goals)],
    preferences: [...new Set(preferences)],
    foundationLevel: dsProfile?.foundation_level ?? null,
    knowledgeLevel: bp.knowledge_base_score,
    practiceLevel: bp.practice_ability_score,
    programmingLanguage: dsProfile?.programming_language ?? null,
    learnedCourses: dsProfile?.learned_courses ?? [],
    errorPronePoints: dsProfile?.error_prone_points ?? [],
  }
}

// =====================================================================
// Profile usability check
// =====================================================================

export function hasUsableProfile(profile: BackendProfile | null): boolean {
  // Priority 1: localStorage draft (highest priority)
  if (hasUsableLocalProfileDraft()) return true

  // Priority 2: backend profile fields
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

// =====================================================================
// Difficulty → DS module mapping
// Order matters: more specific matches must come first.
// ds-4 before ds-3 so "递归调用栈" matches "递归" not bare "栈".
// =====================================================================

const DIFFICULTY_MODULE_MAP: [string[], string, string][] = [
  [['复杂度', '大O', '时间复杂度', '空间复杂度', '渐进分析', 'O(', 'O(n)', 'O(log'], 'ds-1', '复杂度分析与基础概念'],
  [['链表', '顺序表', '线性表', '单链表', '双向链表', '循环链表', '链式存储'], 'ds-2', '线性表'],
  // ds-4 BEFORE ds-3 so "递归调用栈" hits "递归" not bare "栈"
  [['递归', '调用栈', '递归调用栈', '栈帧', '尾递归', '汉诺塔', '全排列', '终止条件'], 'ds-4', '递归与调用栈'],
  [['栈', '队列', 'LIFO', 'FIFO', '单调栈', '循环队列', '括号匹配', '表达式求值'], 'ds-3', '栈与队列'],
  [['树遍历', '树', '二叉树', 'BST', '前序', '中序', '后序', '层序', '堆', '优先队列', '二叉搜索树', '遍历顺序'], 'ds-5', '树与二叉树'],
  [['图遍历', '图', 'BFS', 'DFS', 'Dijkstra', '拓扑排序', '邻接表', '邻接矩阵', '最短路径', '连通'], 'ds-6', '图结构与图算法'],
  [['排序', '快排', '快速排序', '归并排序', '堆排序', '二分查找', '二分', '查找', '稳定性'], 'ds-7', '排序与查找'],
  [['哈希', '散列', '散列表', '冲突', '链地址', '开放地址', '负载因子', 'unordered'], 'ds-8', '散列表'],
  [['动态规划', 'DP', '背包', '状态转移', '记忆化搜索', '最优子结构', '重叠子问题', '状态定义'], 'ds-9', '动态规划入门'],
]

function mapDifficultiesToModules(difficulties: string[]): Map<string, string[]> {
  const result = new Map<string, string[]>()
  for (const diff of difficulties) {
    for (const [terms, moduleId] of DIFFICULTY_MODULE_MAP) {
      if (terms.some((t) => diff.includes(t))) {
        const existing = result.get(moduleId) || []
        if (!existing.includes(diff)) existing.push(diff)
        result.set(moduleId, existing)
        break
      }
    }
  }
  return result
}

// =====================================================================
// Goal / Preference → Resource type mapping (ordered by priority)
// =====================================================================

function getPreferredResourceTypes(signals: NormalizedSignals): string[] {
  const types: string[] = []

  // Preferences first (higher weight)
  for (const pref of signals.preferences) {
    if (pref.includes('图解')) addOnce(types, '图解讲义')
    if (pref.includes('代码示例') || pref.includes('代码')) addOnce(types, '代码示例与注释')
    if (pref.includes('易错')) addOnce(types, '个性化讲解文档')
    if (pref.includes('练习') || pref.includes('分层')) addOnce(types, '分层练习题')
    if (pref.includes('项目') || pref.includes('案例')) addOnce(types, '项目式学习案例')
    if (pref.includes('思维导图') || pref.includes('知识梳理')) addOnce(types, '知识点思维导图')
  }

  // Goals second
  for (const goal of signals.goals) {
    if (goal.includes('刷题')) { addOnce(types, '分层练习题'); addOnce(types, '代码示例与注释') }
    if (goal.includes('考试')) { addOnce(types, '个性化讲解文档'); addOnce(types, '知识点思维导图') }
    if (goal.includes('项目')) { addOnce(types, '项目式学习案例'); addOnce(types, '代码示例与注释') }
    if (goal.includes('概念') || goal.includes('理解')) { addOnce(types, '图解讲义'); addOnce(types, '个性化讲解文档') }
  }

  return types
}

function addOnce(arr: string[], val: string) {
  if (!arr.includes(val)) arr.push(val)
}

// =====================================================================
// Supplementary resource title helper
// =====================================================================

const TYPE_SHORT_LABEL: Record<string, string> = {
  '图解讲义': '图解讲义',
  '代码示例与注释': '代码示例',
  '个性化讲解文档': '核心讲解',
  '分层练习题': '分层练习',
  '项目式学习案例': '项目案例',
  '知识点思维导图': '思维导图',
  '拓展阅读资料': '拓展阅读',
}

function suppTitle(nodeName: string, resType: string): string {
  const label = TYPE_SHORT_LABEL[resType] || resType
  return `${nodeName}${label}`
}

// =====================================================================
// Personalized transition (used by CourseCenter)
// =====================================================================

export interface PersonalizedTransition {
  from: string
  to: string
  reason: string
  basedOn: string[]
  isPersonalized: boolean
}

export function buildPersonalizedTransition(
  profile: BackendProfile | null,
  courses: Course[],
): PersonalizedTransition | null {
  let signals: NormalizedSignals | null = null
  if (profile) {
    signals = normalizeProfileSignals(profile)
  }
  if (!signals) {
    const draft = loadLocalProfileDraft()
    if (draft) signals = normalizeProfileSignals(draft)
  }
  if (!signals || signals.difficulties.length === 0) {
    if (courses.length > 0) {
      return {
        from: courses[0].name,
        to: courses.length > 1 ? courses[1].name : courses[0].name,
        reason: '根据你的学习画像，建议从基础模块开始逐步深入。',
        basedOn: ['学习画像综合分析'],
        isPersonalized: true,
      }
    }
    return null
  }

  const moduleMap = mapDifficultiesToModules(signals.difficulties)
  const allDiffs = [...new Set([...moduleMap.values()].flat())]
  const firstModule = courses[0]
  if (!firstModule) return null

  const matchedModules = [...moduleMap.entries()]
  if (matchedModules.length > 0) {
    const [, diffs] = matchedModules[0]
    // Find module name from DIFFICULTY_MODULE_MAP
    const entry = DIFFICULTY_MODULE_MAP.find(([, id]) => id === matchedModules[0][0])
    const moduleName = entry?.[2] || '相关模块'
    return {
      from: firstModule.name,
      to: moduleName,
      reason: `根据你的学习画像，你在「${diffs.join('、')}」方面存在学习困难，建议重点学习「${moduleName}」模块。`,
      basedOn: allDiffs.slice(0, 6),
      isPersonalized: true,
    }
  }

  return {
    from: firstModule.name,
    to: courses.length > 1 ? courses[1].name : firstModule.name,
    reason: '根据你的学习画像，建议从基础模块开始逐步深入。',
    basedOn: signals.difficulties.slice(0, 3),
    isPersonalized: true,
  }
}

// =====================================================================
// Build personalized learning path (10 DS modules)
// =====================================================================

export function buildPersonalizedPath(
  profile: BackendProfile | null,
  _courses: Course[],
): PersonalizedPathResult | null {
  let signals: NormalizedSignals | null = null
  let source: 'backend' | 'localStorage' = 'backend'

  // Priority 1: localStorage draft (always highest priority)
  const draft = loadLocalProfileDraft()
  if (draft && hasUsableLocalProfileDraft()) {
    signals = normalizeProfileSignals(draft)
    source = 'localStorage'
  }

  // Priority 2: fall back to backend profile only if no usable localStorage
  if (!signals && profile) {
    signals = normalizeProfileSignals(profile)
    source = 'backend'
  }

  if (!signals) return null

  const modulePriorities = mapDifficultiesToModules(signals.difficulties)
  const preferredTypes = getPreferredResourceTypes(signals)
  const focusModuleIds = new Set(modulePriorities.keys())

  // ---- Step 1: build enriched node objects ----
  const enrichedNodes: PathNode[] = mockLearningPath.nodes.map((baseNode) => {
    const isFocus = focusModuleIds.has(baseNode.id)

    // Reorder defaultResources so preferred types come first
    let resources = [...baseNode.defaultResources]
    if (preferredTypes.length > 0) {
      resources.sort((a, b) => {
        const aIdx = preferredTypes.indexOf(a.type)
        const bIdx = preferredTypes.indexOf(b.type)
        if (aIdx >= 0 && bIdx >= 0) return aIdx - bIdx
        if (aIdx >= 0) return -1
        if (bIdx >= 0) return 1
        return 0
      })

      // For focus nodes: add up to 2 supplementary resources for missing preferred types
      if (isFocus) {
        let added = 0
        for (const pt of preferredTypes) {
          if (added >= 2) break
          const hasType = resources.some((r) => r.type === pt)
          if (!hasType) {
            resources.push({
              resourceId: `${baseNode.id}-sup-${added}`,
              title: suppTitle(baseNode.name, pt),
              type: pt,
              estimatedTime: '20 分钟',
              source: 'default',
            })
            added++
          }
        }
      }
    }

    // Adjust duration based on foundation level
    let duration = baseNode.duration
    if (signals!.foundationLevel === '基础薄弱') {
      if (duration === '1-3 天') duration = '2-4 天'
      else if (duration === '2-3 天') duration = '3-5 天'
      else if (duration === '2-4 天') duration = '3-5 天'
    } else if (signals!.foundationLevel === '较好') {
      if (duration === '4-6 天') duration = '3-4 天'
      else if (duration === '5-7 天') duration = '4-5 天'
      else if (duration === '4-7 天') duration = '3-5 天'
      else if (duration === '1-2 周') duration = '5-7 天'
    }

    return {
      ...baseNode,
      duration,
      defaultResources: resources,
      matchedResources: [],
      isFocus,
      reason: baseNode.reason,
    }
  })

  // ---- Step 2: reorder — ds-1 first, then focus modules, then rest ----
  const reordered: PathNode[] = []

  // ds-1 always first
  const ds1 = enrichedNodes.find((n) => n.id === 'ds-1')
  if (ds1) reordered.push(ds1)

  // Focus modules in original relative order
  for (const node of enrichedNodes) {
    if (node.id !== 'ds-1' && focusModuleIds.has(node.id)) {
      reordered.push(node)
    }
  }

  // Non-focus modules in original relative order
  for (const node of enrichedNodes) {
    if (node.id !== 'ds-1' && !focusModuleIds.has(node.id)) {
      reordered.push(node)
    }
  }

  // ---- Step 3: build result metadata ----
  const basisParts: string[] = []
  if (signals.difficulties.length > 0) {
    basisParts.push(`学习困难：${signals.difficulties.slice(0, 4).join('、')}`)
  }
  if (signals.goals.length > 0) {
    basisParts.push(`学习目标：${signals.goals.slice(0, 3).join('、')}`)
  }
  if (source === 'localStorage') {
    basisParts.push('基于本地学习画像生成')
  }

  const profileFieldsUsed: string[] = []
  if (signals.difficulties.length > 0) profileFieldsUsed.push('current_difficulties')
  if (signals.goals.length > 0) profileFieldsUsed.push('learning_goal')
  if (signals.preferences.length > 0) profileFieldsUsed.push('expression_preferences')
  if (signals.foundationLevel) profileFieldsUsed.push('foundation_level')
  if (profileFieldsUsed.length === 0) profileFieldsUsed.push('profile_summary')

  // ---- DEV debug output ----
  if (import.meta.env.DEV) {
    const localDraft = loadLocalProfileDraft()
    console.log('[Path personalization]', {
      localDraft: localDraft
        ? {
            learning_goal: localDraft.learning_goal,
            current_difficulties: localDraft.current_difficulties,
            learning_difficulties: localDraft.learning_difficulties,
            expression_preferences: localDraft.expression_preferences,
            foundation_level: localDraft.foundation_level,
            programming_language: localDraft.programming_language,
          }
        : null,
      source,
      focusModules: [...focusModuleIds],
      orderedModuleTitles: reordered.map((n) => n.name),
      resourcePreferences: preferredTypes,
    })
  }

  return {
    name: '数据结构与算法个性化学习路径',
    nodes: reordered,
    personalizedBasis: basisParts.length > 0 ? basisParts.join('；') : null,
    profileFieldsUsed,
  }
}
