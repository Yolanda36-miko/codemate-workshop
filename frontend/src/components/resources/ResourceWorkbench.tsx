import { useState, useEffect } from 'react'
import { Sparkles, BookOpen, Edit3, Code, User, AlertCircle, CheckCircle2, ChevronDown, ChevronRight } from 'lucide-react'
import type { QuickProfile } from '../../types'

const SESSION_KEY = 'codemate_resource_quick_profile'

const FOUNDATION_LEVELS = [
  { key: '基础薄弱', label: '基础薄弱', desc: '概念不扎实' },
  { key: '一般', label: '基础一般', desc: '能理解但写不出' },
  { key: '较好', label: '基础较好', desc: '可独立实现' },
]
const LEARNING_GOALS = [
  { key: '概念理解', label: '概念理解' },
  { key: '考试复习', label: '考试复习' },
  { key: '刷题训练', label: '刷题训练' },
  { key: '项目实践', label: '项目实践' },
]
const PROG_LANGUAGES = ['Python', 'C', 'C++', 'Java', '暂不确定']
const DIFFICULTY_OPTIONS = [
  '递归调用栈', '二叉树遍历', 'BFS与DFS', '快速排序', '动态规划入门',
  '散列表冲突', '图的存储', '二分查找', '归并排序', '栈与队列',
]
const EXPRESSION_PREFS = [
  { key: '图解', label: '图解' },
  { key: '代码', label: '代码示例' },
  { key: '练习', label: '分层练习' },
  { key: '案例', label: '项目案例' },
]

const RESOURCE_TYPES = [
  { key: '图解讲解', icon: BookOpen, label: '图解讲解', desc: '结构化图示讲解' },
  { key: '代码示例', icon: Code, label: '代码示例', desc: '可运行的代码范例' },
  { key: '易错点', icon: AlertCircle, label: '易错点', desc: '常见错误归纳' },
  { key: '分层练习', icon: Edit3, label: '分层练习', desc: '基础到进阶练习' },
  { key: '项目案例', icon: Code, label: '项目案例', desc: '综合实战项目' },
]

const RECOMMENDED_TOPICS = [
  '递归调用栈', '二叉树遍历', '图的 BFS 与 DFS', '快速排序', '动态规划入门',
]

// Default empty quick profile
function emptyQP(): QuickProfile {
  return {
    foundation_level: '',
    learning_goal: '',
    programming_language: 'Python',
    current_difficulties: [],
    expression_preferences: [],
  }
}

// Load from sessionStorage
function loadQP(): QuickProfile {
  try {
    const raw = sessionStorage.getItem(SESSION_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      return {
        foundation_level: parsed.foundation_level || '',
        learning_goal: parsed.learning_goal || '',
        programming_language: parsed.programming_language || 'Python',
        current_difficulties: Array.isArray(parsed.current_difficulties) ? parsed.current_difficulties : [],
        expression_preferences: Array.isArray(parsed.expression_preferences) ? parsed.expression_preferences : [],
      }
    }
  } catch { /* ignore */ }
  return emptyQP()
}

function saveQP(qp: QuickProfile) {
  try {
    sessionStorage.setItem(SESSION_KEY, JSON.stringify(qp))
  } catch { /* ignore */ }
}

function clearQP() {
  try {
    sessionStorage.removeItem(SESSION_KEY)
  } catch { /* ignore */ }
}

export interface WorkbenchParams {
  courseId: string
  learningTopic: string
  language: string
  selectedTypes: string[]
  quickProfile: QuickProfile
}

interface ResourceWorkbenchProps {
  onGenerate: (params: WorkbenchParams) => void
  generating: boolean
  hasExistingProfile?: boolean
}

export default function ResourceWorkbench({ onGenerate, generating, hasExistingProfile = false }: ResourceWorkbenchProps) {
  const [courseId, setCourseId] = useState('data-structures')
  const [learningTopic, setLearningTopic] = useState('')
  const [selectedTypes, setSelectedTypes] = useState<string[]>([])
  const [showQuickProfile, setShowQuickProfile] = useState(false) // default collapsed

  // Quick profile from sessionStorage
  const [qp, setQP] = useState<QuickProfile>(loadQP)

  // Auto-expand hint state
  const [autoExpandHint, setAutoExpandHint] = useState(false)

  // Persist to sessionStorage on every change
  useEffect(() => { saveQP(qp) }, [qp])

  const toggleType = (key: string) => {
    setSelectedTypes((prev) =>
      prev.includes(key) ? prev.filter((x) => x !== key) : [...prev, key],
    )
  }

  const hasQuickProfile =
    (qp.foundation_level && qp.foundation_level !== '') ||
    (qp.learning_goal && qp.learning_goal !== '') ||
    (qp.current_difficulties && qp.current_difficulties.length > 0)

  const hasPersonalization = hasExistingProfile || hasQuickProfile

  const canGenerate =
    !generating &&
    learningTopic.trim().length > 0 &&
    selectedTypes.length > 0 &&
    hasPersonalization

  const missingItems: string[] = []
  if (!learningTopic.trim()) missingItems.push('学习主题')
  if (selectedTypes.length === 0) missingItems.push('资源类型')
  if (!hasPersonalization) missingItems.push('个性化依据')

  const handleGenerate = () => {
    if (!canGenerate) {
      // If only missing personalization, auto-expand quick profile and show hint
      if (learningTopic.trim() && selectedTypes.length > 0 && !hasPersonalization) {
        setShowQuickProfile(true)
        setAutoExpandHint(true)
      }
      return
    }
    setAutoExpandHint(false)
    onGenerate({
      courseId,
      learningTopic: learningTopic.trim(),
      language: qp.programming_language || 'Python',
      selectedTypes,
      quickProfile: {
        foundation_level: qp.foundation_level || undefined,
        learning_goal: qp.learning_goal || undefined,
        programming_language: qp.programming_language || 'Python',
        current_difficulties: (qp.current_difficulties && qp.current_difficulties.length > 0) ? qp.current_difficulties : undefined,
        expression_preferences: (qp.expression_preferences && qp.expression_preferences.length > 0) ? qp.expression_preferences : undefined,
      },
    })
  }

  const handleClearQP = () => {
    clearQP()
    setQP(emptyQP())
  }

  return (
    <div className="bg-white rounded-2xl p-5 shadow-card border border-gray-100 space-y-4">
      {/* Topic input */}
      <div>
        <label className="block text-xs font-medium text-gray-500 mb-1.5">
          <span className="inline-flex items-center gap-1">
            <Edit3 className="w-3 h-3 text-primary-400" />
            学习主题
          </span>
        </label>
        <input
          type="text"
          value={learningTopic}
          onChange={(e) => setLearningTopic(e.target.value)}
          placeholder="输入你想学习的数据结构知识点，例如：递归调用栈、二叉树遍历、图的最短路径"
          className="w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-200 bg-white placeholder:text-gray-300"
        />
        <div className="mt-1.5">
          <span className="text-[10px] text-gray-400 mr-2">推荐主题：</span>
          <div className="inline-flex flex-wrap gap-1.5">
            {RECOMMENDED_TOPICS.map((topic) => (
              <button
                key={topic}
                onClick={() => setLearningTopic(topic)}
                className={`px-2.5 py-1 rounded-full text-[11px] border transition-all ${
                  learningTopic === topic
                    ? 'bg-primary-100 border-primary-300 text-primary-700 font-medium'
                    : 'bg-gray-50 border-gray-100 text-gray-500 hover:border-primary-200 hover:text-primary-600'
                }`}
              >
                {topic}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Resource type selection */}
      <div>
        <label className="block text-xs font-medium text-gray-500 mb-2">
          资源类型（至少选一种）
        </label>
        <div className="grid grid-cols-5 gap-2">
          {RESOURCE_TYPES.map((rt) => {
            const selected = selectedTypes.includes(rt.key)
            const Icon = rt.icon
            return (
              <button
                key={rt.key}
                onClick={() => toggleType(rt.key)}
                className={`flex flex-col items-center gap-1 px-2 py-2.5 rounded-xl border transition-all text-center ${
                  selected
                    ? 'bg-primary-50 border-primary-300 shadow-sm'
                    : 'bg-white border-gray-100 hover:border-gray-200'
                }`}
              >
                <Icon className={`w-4 h-4 ${selected ? 'text-primary-500' : 'text-gray-300'}`} />
                <span className={`text-[10px] font-medium ${selected ? 'text-primary-700' : 'text-gray-500'}`}>
                  {rt.label}
                </span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Profile status / Quick profile toggle */}
      <div className="border-t border-gray-100 pt-3">
        {hasExistingProfile ? (
          /* Has profile: show status + still allow quick profile as supplement */
          <div className="space-y-2">
            <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-green-50/60 border border-green-200">
              <CheckCircle2 className="w-3.5 h-3.5 text-green-500 shrink-0" />
              <span className="text-[11px] text-green-700">
                已检测到学习画像，将优先依据画像生成资源
              </span>
            </div>
            <button
              onClick={() => setShowQuickProfile(!showQuickProfile)}
              className="flex items-center gap-1 text-[10px] text-gray-400 hover:text-gray-600 transition-colors"
            >
              {showQuickProfile ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
              快速定制信息（可选，用于临时补充或覆盖画像）
            </button>
          </div>
        ) : (
          /* No profile: show quick profile toggle */
          <button
            onClick={() => setShowQuickProfile(!showQuickProfile)}
            className={`flex items-center gap-1.5 text-xs font-medium transition-colors w-full ${
              autoExpandHint ? 'text-primary-600' : 'text-gray-500 hover:text-primary-600'
            }`}
          >
            <User className="w-3.5 h-3.5" />
            快速定制信息
            {showQuickProfile ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
            <span className="text-[10px] text-gray-400 ml-1">
              没有完整学习画像时，可用 30 秒补充基础、目标和偏好
            </span>
            {hasQuickProfile && <CheckCircle2 className="w-3 h-3 text-green-400 ml-auto" />}
          </button>
        )}
      </div>

      {/* Quick profile panel */}
      {showQuickProfile && (
        <div className="p-4 rounded-xl bg-gray-50/70 border border-gray-100 space-y-3">
          {autoExpandHint && (
            <div className="flex items-start gap-2 px-3 py-2.5 rounded-xl bg-amber-50 border border-amber-200">
              <AlertCircle className="w-3.5 h-3.5 text-amber-500 shrink-0 mt-0.5" />
              <div className="text-[11px] text-amber-700 space-y-0.5">
                <p className="font-medium">当前缺少个性化依据</p>
                <p>请先填写下方的快速定制信息，或前往画像页完善学习画像。</p>
              </div>
            </div>
          )}

          <p className="text-[10px] text-gray-400">
            补充以下信息，让生成的资源更贴合你的实际情况
          </p>

          {/* Programming language — prominently placed first */}
          <div>
            <span className="text-[10px] text-gray-500 mb-1.5 block">
              编程语言（决定代码示例语言）
            </span>
            <div className="flex gap-2">
              {PROG_LANGUAGES.map((l) => (
                <button
                  key={l}
                  onClick={() => setQP((prev) => ({ ...prev, programming_language: l }))}
                  className={`flex-1 py-1.5 rounded-lg text-[11px] border transition-all ${
                    qp.programming_language === l
                      ? 'bg-emerald-50 border-emerald-300 text-emerald-700 font-medium'
                      : 'bg-white border-gray-150 text-gray-500 hover:border-gray-250'
                  }`}
                >
                  {l}
                </button>
              ))}
            </div>
            {qp.programming_language === '暂不确定' && (
              <p className="text-[9px] text-gray-400 mt-1">
                默认使用 Python 展示，可后续改写为 C++ / Java
              </p>
            )}
          </div>

          {/* Foundation level */}
          <div>
            <span className="text-[10px] text-gray-500 mb-1.5 block">当前基础</span>
            <div className="flex gap-2">
              {FOUNDATION_LEVELS.map((fl) => (
                <button
                  key={fl.key}
                  onClick={() => setQP((prev) => ({ ...prev, foundation_level: fl.key }))}
                  className={`flex-1 py-1.5 rounded-lg text-[11px] border transition-all ${
                    qp.foundation_level === fl.key
                      ? 'bg-primary-50 border-primary-300 text-primary-700 font-medium'
                      : 'bg-white border-gray-150 text-gray-500 hover:border-gray-250'
                  }`}
                >
                  <span className="block">{fl.label}</span>
                  <span className="text-[9px] text-gray-400">{fl.desc}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Learning goal */}
          <div>
            <span className="text-[10px] text-gray-500 mb-1.5 block">学习目标</span>
            <div className="flex gap-2">
              {LEARNING_GOALS.map((g) => (
                <button
                  key={g.key}
                  onClick={() => setQP((prev) => ({ ...prev, learning_goal: g.key }))}
                  className={`flex-1 py-1.5 rounded-lg text-[11px] border transition-all ${
                    qp.learning_goal === g.key
                      ? 'bg-primary-50 border-primary-300 text-primary-700 font-medium'
                      : 'bg-white border-gray-150 text-gray-500 hover:border-gray-250'
                  }`}
                >
                  {g.label}
                </button>
              ))}
            </div>
          </div>

          {/* Current difficulties */}
          <div>
            <span className="text-[10px] text-gray-500 mb-1.5 block">当前困难点（可选，可多选）</span>
            <div className="flex flex-wrap gap-1.5">
              {DIFFICULTY_OPTIONS.map((d) => (
                <button
                  key={d}
                  onClick={() => setQP((prev) => {
                    const arr = prev.current_difficulties || []
                    return { ...prev, current_difficulties: arr.includes(d) ? arr.filter((x) => x !== d) : [...arr, d] }
                  })}
                  className={`px-2 py-1 rounded-full text-[10px] border transition-all ${
                    (qp.current_difficulties || []).includes(d)
                      ? 'bg-amber-50 border-amber-300 text-amber-700'
                      : 'bg-white border-gray-150 text-gray-500 hover:border-gray-250'
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>

          {/* Expression preferences */}
          <div>
            <span className="text-[10px] text-gray-500 mb-1.5 block">表达偏好（可选，可多选）</span>
            <div className="flex gap-2">
              {EXPRESSION_PREFS.map((ep) => (
                <button
                  key={ep.key}
                  onClick={() => setQP((prev) => {
                    const arr = prev.expression_preferences || []
                    return { ...prev, expression_preferences: arr.includes(ep.key) ? arr.filter((x) => x !== ep.key) : [...arr, ep.key] }
                  })}
                  className={`px-3 py-1.5 rounded-lg text-[10px] border transition-all ${
                    (qp.expression_preferences || []).includes(ep.key)
                      ? 'bg-primary-50 border-primary-300 text-primary-700 font-medium'
                      : 'bg-white border-gray-150 text-gray-500 hover:border-gray-250'
                  }`}
                >
                  {ep.label}
                </button>
              ))}
            </div>
          </div>

          {/* Clear button */}
          {hasQuickProfile && (
            <button
              onClick={handleClearQP}
              className="text-[10px] text-gray-400 hover:text-rose-500 transition-colors"
            >
              清空快速定制信息
            </button>
          )}
        </div>
      )}

      {/* Hint for missing prerequisites */}
      {!canGenerate && !generating && missingItems.length > 0 && (
        <div className="flex items-start gap-2 px-3 py-2.5 rounded-xl bg-amber-50 border border-amber-200">
          <AlertCircle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
          <p className="text-xs text-amber-700 flex-1">
            {missingItems.includes('个性化依据') ? (
              <>
                为了生成真正个性化的学习资源，请先提供个性化依据：
                <span className="inline-flex items-center gap-2 ml-1">
                  <button
                    onClick={() => { setShowQuickProfile(true); setAutoExpandHint(true) }}
                    className="underline font-medium hover:text-amber-800"
                  >
                    填写快速定制信息
                  </button>
                  <span className="text-gray-400">或</span>
                  <a href="/profile" className="underline font-medium hover:text-amber-800">
                    去制定学习画像
                  </a>
                </span>
              </>
            ) : (
              <>
                为了生成真正个性化的学习资源，请先选择{' '}
                {missingItems.map((item, i) => (
                  <span key={item}>
                    <strong>{item}</strong>
                    {i < missingItems.length - 1 && '、'}
                  </span>
                ))}
                。
              </>
            )}
          </p>
        </div>
      )}

      {/* Generate Button */}
      <button
        onClick={handleGenerate}
        disabled={false /* allow click to trigger auto-expand hint */}
        className={`w-full flex items-center justify-center gap-2 py-3 rounded-xl font-semibold text-sm transition-all ${
          canGenerate
            ? 'bg-gradient-to-r from-primary-500 to-purple-600 text-white hover:from-primary-600 hover:to-purple-700 shadow-md hover:shadow-glow hover:-translate-y-0.5'
            : generating
              ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
              : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
        }`}
      >
        <Sparkles className={`w-4 h-4 ${generating ? 'animate-pulse' : ''}`} />
        {generating ? '智能体生成中...' : '生成个性化资源'}
      </button>
    </div>
  )
}
