import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  FileText, GitBranch, ArrowRight, BookOpen, Star,
} from 'lucide-react'
import type { Course } from '../../types'

const MAX_KNOWLEDGE_POINTS = 4
const MAX_DIFFICULTIES = 3
const MAX_RELATED = 3

interface CourseDetailPanelProps {
  course: Course | null
  allCourses: Course[]
  onSelectCourse: (id: string) => void
  isFocus?: boolean
}

export default function CourseDetailPanel({ course, allCourses, onSelectCourse, isFocus = false }: CourseDetailPanelProps) {
  return (
    <AnimatePresence mode="wait">
      {course ? (
        <motion.div
          key={course.id}
          className="bg-white rounded-3xl shadow-lg border border-slate-100 p-8 space-y-6"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.25 }}
        >
          {/* Header: title + focus badge */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              <h2 className="text-lg font-bold text-gray-900">{course.name}</h2>
              {isFocus && (
                <span className="inline-flex items-center gap-0.5 px-2 py-0.5 rounded-full bg-amber-100 text-amber-700 text-[10px] font-medium">
                  <Star className="w-2.5 h-2.5 text-amber-400 fill-amber-400" />
                  建议关注
                </span>
              )}
            </div>
            <p className="text-sm text-slate-500 leading-relaxed">{course.description}</p>
          </div>

          {/* Knowledge points */}
          <div>
            <h3 className="text-xs font-semibold text-gray-500 mb-2">核心知识点</h3>
            <div className="flex flex-wrap gap-1.5">
              {(course.knowledge_points ?? []).slice(0, MAX_KNOWLEDGE_POINTS).map((kp) => (
                <span key={kp} className="px-2.5 py-1 bg-gray-50 rounded-full text-xs text-gray-600 border border-gray-100">
                  {kp}
                </span>
              ))}
              {(course.knowledge_points ?? []).length > MAX_KNOWLEDGE_POINTS && (
                <span className="px-2.5 py-1 bg-gray-50 rounded-full text-xs text-gray-400 border border-gray-100">
                  +{(course.knowledge_points ?? []).length - MAX_KNOWLEDGE_POINTS} 更多
                </span>
              )}
            </div>
          </div>

          {/* Typical difficulties */}
          {(course.typical_difficulties ?? []).length > 0 && (
            <div>
              <h3 className="text-xs font-semibold text-gray-500 mb-2">典型困难</h3>
              <div className="flex flex-wrap gap-1.5">
                {(course.typical_difficulties ?? []).slice(0, MAX_DIFFICULTIES).map((d) => (
                  <span key={d} className="px-2 py-1 bg-amber-50 rounded-full text-xs text-amber-700 border border-amber-100">
                    {d}
                  </span>
                ))}
                {(course.typical_difficulties ?? []).length > MAX_DIFFICULTIES && (
                  <span className="px-2 py-1 bg-amber-50/50 rounded-full text-xs text-amber-500 border border-amber-100/50">
                    +{(course.typical_difficulties ?? []).length - MAX_DIFFICULTIES} 更多
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Learning suggestion — one line, purple text, no background */}
          {course.learning_suggestion && (
            <div>
              <h3 className="text-xs font-semibold text-gray-500 mb-2">学习建议</h3>
              <p className="text-sm text-purple-600 leading-relaxed">{course.learning_suggestion}</p>
            </div>
          )}

          {/* Related courses */}
          {(course.related_courses ?? []).length > 0 && (
            <div>
              <h3 className="text-xs font-semibold text-gray-500 mb-2">关联模块</h3>
              <div className="flex flex-wrap gap-1.5">
                {(course.related_courses ?? []).slice(0, MAX_RELATED).map((r) => {
                  const c = allCourses.find((x) => x.id === r)
                  return (
                    <button
                      key={r}
                      onClick={() => onSelectCourse(r)}
                      className="px-2.5 py-1 bg-gray-50 text-gray-600 rounded-full text-xs hover:bg-gray-100 transition-colors border border-gray-100"
                    >
                      {c?.name ?? r}
                    </button>
                  )
                })}
              </div>
            </div>
          )}

          {/* CTA buttons */}
          <div className="flex items-center gap-2.5 pt-1">
            <Link
              to="/resources"
              className="flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl bg-gradient-to-r from-primary-500 to-primary-700 text-white text-sm font-medium hover:shadow-glow hover:-translate-y-0.5 transition-all"
            >
              <FileText className="w-4 h-4" />
              生成资源
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
            <Link
              to="/path"
              className="flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl border border-primary-200 text-primary-700 text-sm font-medium bg-white hover:shadow-card hover:-translate-y-0.5 transition-all"
            >
              <GitBranch className="w-4 h-4" />
              规划路径
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </motion.div>
      ) : (
        <motion.div
          key="empty"
          className="bg-white rounded-3xl shadow-lg border border-slate-100 p-8 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <BookOpen className="w-8 h-8 text-gray-300 mx-auto mb-2" />
          <p className="text-sm text-gray-400">选择一个模块查看详情</p>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
