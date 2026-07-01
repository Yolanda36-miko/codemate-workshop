import { useEffect, useState, useMemo } from 'react'
import { BookOpen } from 'lucide-react'
import { Link } from 'react-router-dom'
import { getUserProfile } from '../services/api'
import { hasUsableProfile, buildPersonalizedTransition } from '../services/personalizedPath'
import type { Course, BackendProfile } from '../types'
import { dataStructureModules } from '../config/courseFocus'
import CourseCard from '../components/courses/CourseCard'
import CourseDetailPanel from '../components/courses/CourseDetailPanel'
import AnimatedSection from '../components/common/AnimatedSection'

const CURRENT_USER_ID = 1

function parseTags(raw: string | null): string[] {
  if (!raw) return []
  try {
    const arr = JSON.parse(raw)
    return Array.isArray(arr) ? arr : []
  } catch {
    return []
  }
}

function computePriorityCourses(profile: BackendProfile | null, courses: Course[]): Set<string> {
  if (!profile || !hasUsableProfile(profile)) return new Set()
  const profileTerms = [
    ...parseTags(profile.error_patterns),
    ...parseTags(profile.learning_goals),
  ].map((t) => t.toLowerCase())
  if (profileTerms.length === 0) return new Set()
  const priority = new Set<string>()
  for (const c of courses) {
    const courseTerms = [
      ...(c.knowledge_points ?? []),
      ...(c.typical_difficulties ?? []),
      c.name,
    ].map((t) => t.toLowerCase())
    if (courseTerms.some((ct) => profileTerms.some((pt) => ct.includes(pt) || pt.includes(ct)))) {
      priority.add(c.id)
    }
  }
  return priority
}

export default function CourseCenter() {
  const [selectedId, setSelectedId] = useState<string | null>(dataStructureModules[0]?.id ?? null)
  const [hoveredId, setHoveredId] = useState<string | null>(null)
  const [profile, setProfile] = useState<BackendProfile | null>(null)
  const [profileLoading, setProfileLoading] = useState(true)

  useEffect(() => {
    getUserProfile(CURRENT_USER_ID)
      .then((p) => setProfile(p))
      .catch(() => setProfile(null))
      .finally(() => setProfileLoading(false))
  }, [])

  const selected = dataStructureModules.find((c) => c.id === selectedId) ?? null
  const usable = hasUsableProfile(profile)
  const transition = profile ? buildPersonalizedTransition(profile, dataStructureModules) : null
  const priorityCourses = useMemo(() => computePriorityCourses(profile, dataStructureModules), [profile])

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-8 pb-12">
      {/* ===== Top: Title ===== */}
      <AnimatedSection>
        <div className="flex items-center gap-2">
          <BookOpen className="w-6 h-6 text-primary-600" />
          <h1 className="text-2xl font-bold text-gray-900">数据结构与算法模块中心</h1>
        </div>
      </AnimatedSection>

      {/* ===== Personalized Recommendation Banner ===== */}
      <AnimatedSection delay={0.05}>
        {profileLoading ? (
          <div className="bg-gray-50 rounded-2xl border border-gray-100 px-5 py-4 animate-pulse">
            <div className="h-5 bg-gray-200 rounded w-48 mb-2" />
            <div className="h-4 bg-gray-200 rounded w-96" />
          </div>
        ) : usable && transition ? (
          <div className="bg-gradient-to-r from-primary-50 to-purple-50 rounded-2xl border border-primary-100/50 px-5 py-4 flex items-center gap-4">
            <div className="flex items-center gap-3 shrink-0">
              <span className="px-3 py-1.5 rounded-xl bg-white text-sm font-semibold text-gray-800 shadow-sm border border-primary-100">
                {transition.from}
              </span>
              <span className="text-primary-500 font-bold text-lg">→</span>
              <span className="px-3 py-1.5 rounded-xl bg-white text-sm font-semibold text-gray-800 shadow-sm border border-primary-200 ring-1 ring-primary-200">
                {transition.to}
              </span>
            </div>
            <div className="border-l border-primary-200 pl-4">
              <p className="text-xs font-semibold text-primary-700 mb-0.5">基于你的学习画像推荐</p>
              <p className="text-xs text-gray-600 leading-relaxed">{transition.reason}</p>
              {transition.basedOn.length > 0 && (
                <div className="flex items-center gap-1 mt-1.5 flex-wrap">
                  <span className="text-[10px] text-gray-400">依据：</span>
                  {transition.basedOn.map((tag) => (
                    <span key={tag} className="px-1.5 py-0.5 rounded-full bg-white/80 text-primary-600 text-[10px] font-medium border border-primary-100">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="bg-gradient-to-r from-gray-50 to-blue-50 rounded-2xl border border-gray-100 px-5 py-6 text-center">
            <BookOpen className="w-8 h-8 text-gray-300 mx-auto mb-3" />
            <p className="text-sm font-semibold text-gray-700 mb-1">完成学习画像后，CodeBuddy 将为你推荐适合的模块学习顺序。</p>
            <p className="text-xs text-gray-500 mb-4">完善你的学习画像，让智能体了解你的薄弱模块与学习目标，推荐最合适的模块学习路径。</p>
            <Link
              to="/profile"
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-primary-500 text-white text-sm font-medium hover:bg-primary-600 transition-colors"
            >
              去完善学习画像
            </Link>
          </div>
        )}
      </AnimatedSection>

      {/* ===== General Course Catalog ===== */}
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
                  isPriority={priorityCourses.has(c.id)}
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
            />
          </AnimatedSection>
        </div>
      </div>
    </div>
  )
}
