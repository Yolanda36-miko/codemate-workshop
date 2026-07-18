import { useState, useMemo } from 'react'
import { BookOpen } from 'lucide-react'
import { dataStructureModules } from '../config/courseFocus'
import CourseCard from '../components/courses/CourseCard'
import CourseDetailPanel from '../components/courses/CourseDetailPanel'
import AnimatedSection from '../components/common/AnimatedSection'

// ── Difficulty keyword → module ID mapping ──
const DIFFICULTY_TO_MODULE: Record<string, string> = {
  '递归调用栈': 'recursion-callstack', '递归': 'recursion-callstack',
  '树遍历': 'tree', '二叉树': 'tree', '前序遍历': 'tree', '中序遍历': 'tree', '后序遍历': 'tree',
  '图遍历': 'graph', 'BFS': 'graph', 'DFS': 'graph', '图': 'graph', 'Dijkstra': 'graph', '最短路径': 'graph',
  '动态规划': 'dp', 'DP': 'dp', '背包': 'dp',
  '排序': 'sort-search', '快速排序': 'sort-search', '归并排序': 'sort-search',
  '哈希': 'hash', '散列': 'hash', '散列表': 'hash',
  '链表': 'linear-list', '线性表': 'linear-list',
  '栈': 'stack-queue', '队列': 'stack-queue',
  '复杂度': 'complexity', '时间复杂度': 'complexity',
}

/** Topological order of module IDs (by prerequisites). */
const MODULE_ORDER = [
  'complexity', 'linear-list', 'stack-queue', 'recursion-callstack',
  'tree', 'sort-search', 'graph', 'hash', 'dp', 'ds-project',
]

/** Normalize a profile field value (string | string[] | undefined) to string[]. */
function toTextArray(value: unknown): string[] {
  if (Array.isArray(value)) {
    return value
      .flatMap((item) => toTextArray(item))
      .map((item) => String(item).trim())
      .filter(Boolean)
  }
  if (typeof value === 'string') {
    return value
      .split(/[、,，/|；;\s]+/)
      .map((item) => item.trim())
      .filter(Boolean)
  }
  if (value == null) return []
  return [String(value).trim()].filter(Boolean)
}

interface ProfileDraft {
  learning_goal?: string
  foundation_level?: string
  current_difficulties?: string[]
  learning_difficulties?: string[]
  expression_preferences?: string[]
  programming_language?: string
}

function loadProfileDraft(): ProfileDraft | null {
  try {
    const raw = localStorage.getItem('codemate_profile_draft')
    if (!raw) return null
    const obj = JSON.parse(raw)
    if (!obj || typeof obj !== 'object') return null
    return obj as ProfileDraft
  } catch {
    return null
  }
}

function resolveModuleIds(difficulties: string[]): string[] {
  const seen = new Set<string>()
  const ids: string[] = []
  for (const d of difficulties) {
    const id = DIFFICULTY_TO_MODULE[d] ?? DIFFICULTY_TO_MODULE[d.trim()]
    if (id && !seen.has(id)) {
      seen.add(id)
      ids.push(id)
    }
  }
  return ids
}

function buildFocusTransition(
  moduleIds: string[],
  extendedIds: string[],
): { from: string; to: string } | null {
  if (moduleIds.length === 0) return null
  // Order ALL ids (matched + prereqs) by topological order
  const allOrdered = MODULE_ORDER.filter((id) => extendedIds.includes(id))
  const matchedOrdered = MODULE_ORDER.filter((id) => moduleIds.includes(id))
  if (allOrdered.length === 0 || matchedOrdered.length === 0) return null

  const firstMatched = matchedOrdered[0]
  const firstModule = dataStructureModules.find((m) => m.id === firstMatched)
  if (!firstModule) return null

  // If the first matched module has exactly one prereq in our module list,
  // use that prereq as the "from" (e.g. stack-queue → recursion-callstack)
  const prereqs = firstModule.prerequisites ?? []
  const prereqsInList = prereqs.filter((p) => dataStructureModules.some((m) => m.id === p))
  const fromId = prereqsInList.length === 1 ? prereqsInList[0] : firstMatched
  const toId = prereqsInList.length === 1 ? firstMatched : matchedOrdered[matchedOrdered.length - 1]

  const fromMod = dataStructureModules.find((m) => m.id === fromId)
  const toMod = dataStructureModules.find((m) => m.id === toId)
  if (!fromMod || !toMod) return null
  return { from: fromMod.name, to: toMod.name }
}

function buildFocusDescription(profile: ProfileDraft): string {
  const diffs = profile.learning_difficulties ?? profile.current_difficulties ?? []
  const prefs = profile.expression_preferences ?? []
  const lang = profile.programming_language ?? ''

  const diffList = toTextArray(diffs)
  const prefList = toTextArray(prefs)

  const diffStr = diffList.length > 0 ? `「${diffList.slice(0, 3).join('、')}」` : ''
  const parts: string[] = []

  if (diffStr) {
    parts.push(`系统识别出你在${diffStr}方面需要进一步加强`)
  }
  if (lang || prefList.length > 0) {
    const tools = [...(lang ? [lang] : []), ...prefList.slice(0, 2)].join(' ')
    parts.push(`建议结合${tools}，先理解过程推演，再配合基础题训练`)
  }

  if (parts.length === 0) return '建议完善学习画像以获取个性化模块推荐。'
  return `根据你的学习画像，${parts.join('。')}。`
}

export default function CourseCenter() {
  const [selectedId, setSelectedId] = useState<string | null>(dataStructureModules[0]?.id ?? null)
  const [hoveredId, setHoveredId] = useState<string | null>(null)

  const profileDraft = useMemo(() => loadProfileDraft(), [])
  const hasProfile = profileDraft !== null

  const difficulties = useMemo(
    () => toTextArray(profileDraft?.learning_difficulties ?? profileDraft?.current_difficulties),
    [profileDraft],
  )
  const preferences = useMemo(
    () => toTextArray(profileDraft?.expression_preferences),
    [profileDraft],
  )
  const language = typeof profileDraft?.programming_language === 'string'
    ? profileDraft.programming_language.trim()
    : ''
  const learningGoal = typeof profileDraft?.learning_goal === 'string'
    ? profileDraft.learning_goal.trim()
    : ''
  const moduleIds = useMemo(() => resolveModuleIds(difficulties), [difficulties])

  // Compute focus modules: difficulty-matched + single prereqs + ds-project
  const focusModules = useMemo(() => {
    const set = new Set(moduleIds)
    // Only include prereqs for modules with exactly ONE prerequisite
    for (const mid of moduleIds) {
      const mod = dataStructureModules.find((m) => m.id === mid)
      const prereqs = (mod?.prerequisites ?? []).filter((p) =>
        dataStructureModules.some((m) => m.id === p),
      )
      if (prereqs.length === 1) {
        set.add(prereqs[0])
      }
    }
    if (learningGoal === '项目实践' || preferences.includes('项目案例')) {
      set.add('ds-project')
    }
    return set
  }, [moduleIds, learningGoal, preferences])

  const focusList = useMemo(() => [...focusModules], [focusModules])
  const transition = useMemo(() => buildFocusTransition(moduleIds, focusList), [moduleIds, focusList])

  // All tags shown in the banner
  const bannerTags: string[] = []
  if (difficulties.length > 0) bannerTags.push(...difficulties.slice(0, 3))
  if (preferences.length > 0) bannerTags.push(...preferences.slice(0, 2))
  if (language) bannerTags.push(language)

  const selected = dataStructureModules.find((c) => c.id === selectedId) ?? null

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-8 pb-12">
      {/* ===== Top: Title ===== */}
      <AnimatedSection>
        <div className="flex items-center gap-2">
          <BookOpen className="w-6 h-6 text-primary-600" />
          <h1 className="text-2xl font-bold text-gray-900">数据结构与算法模块中心</h1>
        </div>
      </AnimatedSection>

      {/* ===== Profile-based Learning Focus Banner ===== */}
      <AnimatedSection delay={0.05}>
        <div className="bg-gradient-to-r from-primary-50 to-purple-50 rounded-2xl border border-primary-100/50 px-5 py-4 flex items-center gap-4">
          {/* Left: module blocks + arrow */}
          <div className="flex items-center gap-3 shrink-0">
            <span className="px-3 py-1.5 rounded-xl bg-white text-sm font-semibold text-gray-800 shadow-sm border border-primary-100">
              {hasProfile && transition ? transition.from : '完成画像'}
            </span>
            <span className="text-primary-500 font-bold text-lg">→</span>
            <span className={`px-3 py-1.5 rounded-xl bg-white text-sm font-semibold text-gray-800 shadow-sm border ${
              hasProfile ? 'border-primary-200 ring-1 ring-primary-200' : 'border-primary-100'
            }`}>
              {hasProfile && transition ? transition.to : '生成关注点'}
            </span>
          </div>

          {/* Right: title + description + tags */}
          <div className="border-l border-primary-200 pl-4 min-w-0">
            <p className="text-xs font-semibold text-primary-700 mb-0.5">
              {hasProfile ? '基于画像的学习关注点' : '完成画像后生成学习关注点'}
            </p>
            <p className="text-xs text-gray-600 leading-relaxed">
              {hasProfile
                ? buildFocusDescription(profileDraft!)
                : '完成学习画像后，系统会根据你的学习目标、当前困难和资源偏好，推荐需要优先关注的数据结构与算法模块。'
              }
            </p>
            <div className="flex items-center gap-1 mt-1.5 flex-wrap">
              {hasProfile && bannerTags.length > 0 && (
                <span className="text-[10px] text-gray-400 mr-0.5">依据：</span>
              )}
              {(hasProfile ? bannerTags : ['学习画像', '模块推荐', '个性化关注']).map((tag) => (
                <span key={tag} className="px-1.5 py-0.5 rounded-full bg-white/80 text-primary-600 text-[10px] font-medium border border-primary-100">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>
      </AnimatedSection>

      {/* ===== Section label ===== */}
      <AnimatedSection delay={0.08}>
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">数据结构与算法模块体系</span>
        </div>
      </AnimatedSection>

      {/* ===== Bottom: Cards + Detail ===== */}
      <div className="grid grid-cols-12 gap-6">
        {/* Left: Course cards grid */}
        <div className="col-span-7">
          <AnimatedSection delay={0.1}>
            <div className="grid grid-cols-2 gap-3 overflow-visible">
              {dataStructureModules.map((c, i) => (
                <CourseCard
                  key={c.id}
                  course={c}
                  isSelected={c.id === selectedId}
                  isHovered={c.id === hoveredId}
                  anyHovered={hoveredId !== null}
                  onClick={() => setSelectedId(c.id)}
                  onHover={(id) => setHoveredId(id)}
                  index={i}
                  isFocus={hasProfile && focusModules.has(c.id)}
                />
              ))}
            </div>
          </AnimatedSection>
        </div>

        {/* Right: Course detail */}
        <div className="col-span-5">
          <AnimatedSection delay={0.15} direction="right">
            <CourseDetailPanel
              course={selected}
              allCourses={dataStructureModules}
              onSelectCourse={setSelectedId}
              isFocus={hasProfile && selected ? focusModules.has(selected.id) : false}
            />
          </AnimatedSection>
        </div>
      </div>
    </div>
  )
}
