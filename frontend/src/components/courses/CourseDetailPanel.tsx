import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  GraduationCap, ChevronRight, Link2, Tags, AlertCircle,
  Lightbulb, FileText, GitBranch, BookOpen, ArrowRight,
} from 'lucide-react'
import type { Course } from '../../types'

interface CourseDetailPanelProps {
  course: Course | null
  allCourses: Course[]
  onSelectCourse: (id: string) => void
}

export default function CourseDetailPanel({ course, allCourses, onSelectCourse }: CourseDetailPanelProps) {
  return (
    <AnimatePresence mode="wait">
      {course ? (
        <motion.div
          key={course.id}
          className="bg-white rounded-2xl shadow-card border border-gray-100 p-5 space-y-5"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.25 }}
        >
          {/* Header */}
          <div>
            <div className="flex items-center gap-2.5 mb-1">
              <div className="w-9 h-9 rounded-xl bg-primary-50 flex items-center justify-center shrink-0">
                <GraduationCap className="w-5 h-5 text-primary-600" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-base font-semibold text-gray-800">{course.name}</h2>
                </div>
                <p className="text-xs text-gray-400">{course.stage} · {(course.knowledge_points ?? []).length} 个核心知识点</p>
              </div>
            </div>
            <p className="text-sm text-gray-600 leading-relaxed mt-2">{course.description}</p>
          </div>

          {/* Knowledge points */}
          <div>
            <div className="flex items-center gap-1.5 mb-2">
              <Tags className="w-4 h-4 text-primary-500" />
              <span className="text-xs font-semibold text-gray-700">核心知识点</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {(course.knowledge_points ?? []).map((kp) => (
                <span key={kp} className="px-2.5 py-1 bg-gray-50 rounded-full text-xs text-gray-700 border border-gray-100">
                  {kp}
                </span>
              ))}
            </div>
          </div>

          {/* Typical difficulties */}
          {course.typical_difficulties && course.typical_difficulties.length > 0 && (
            <div>
              <div className="flex items-center gap-1.5 mb-2">
                <AlertCircle className="w-4 h-4 text-amber-500" />
                <span className="text-xs font-semibold text-gray-700">典型学习困难</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {course.typical_difficulties.map((d) => (
                  <span key={d} className="px-2 py-1 bg-amber-50 rounded-full text-xs text-amber-700 border border-amber-100">
                    {d}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Learning suggestion */}
          {course.learning_suggestion && (
            <div className="flex items-start gap-2 px-3 py-2.5 rounded-xl bg-primary-50/50 border border-primary-100/50">
              <Lightbulb className="w-4 h-4 text-primary-500 shrink-0 mt-0.5" />
              <p className="text-xs text-primary-700 leading-relaxed">{course.learning_suggestion}</p>
            </div>
          )}

          {/* Prerequisites */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500 shrink-0">先修课程</span>
            <div className="flex flex-wrap gap-1">
              {(course.prerequisites ?? []).length > 0
                ? (course.prerequisites ?? []).map((p) => {
                    const c = allCourses.find((x) => x.id === p)
                    return (
                      <button
                        key={p}
                        onClick={() => onSelectCourse(p)}
                        className="px-2 py-0.5 bg-primary-50 text-primary-700 rounded-full text-xs hover:bg-primary-100 transition-colors"
                      >
                        {c?.name ?? p}
                      </button>
                    )
                  })
                : <span className="text-xs text-gray-400">无（入门课程）</span>}
            </div>
          </div>

          {/* Related courses */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500 shrink-0">关联课程</span>
            <div className="flex flex-wrap gap-1">
              {(course.related_courses ?? []).map((r) => {
                const c = allCourses.find((x) => x.id === r)
                return (
                  <button
                    key={r}
                    onClick={() => onSelectCourse(r)}
                    className="px-2 py-0.5 bg-purple-50 text-purple-700 rounded-full text-xs hover:bg-purple-100 transition-colors"
                  >
                    {c?.name ?? r}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Resource types */}
          <div>
            <div className="flex items-center gap-1.5 mb-2">
              <BookOpen className="w-4 h-4 text-primary-500" />
              <span className="text-xs font-semibold text-gray-700">可生成资源</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {(course.resource_types ?? []).length > 0
                ? (course.resource_types ?? []).map((rt) => (
                    <span key={rt} className="px-2 py-1 bg-gray-50 rounded-full text-xs text-gray-600 border border-gray-100">
                      {rt}
                    </span>
                  ))
                : <span className="text-xs text-gray-400">暂无</span>}
            </div>
          </div>

          {/* Prerequisite hint for DS&A */}
          {course.id === 'data-structures' && (
            <div className="p-3 rounded-xl bg-gradient-to-r from-primary-50 to-purple-50 border border-primary-100/50">
              <div className="flex items-center gap-1.5 mb-1">
                <ChevronRight className="w-3.5 h-3.5 text-primary-500" />
                <span className="text-xs font-semibold text-primary-700">先修关系推荐</span>
              </div>
              <p className="text-xs text-gray-600 leading-relaxed">
                建议先巩固<strong>程序设计基础</strong>中的函数、数组和递归等核心内容，再开始数据结构的学习。可先回顾递归调用栈和数组操作的代码练习。
              </p>
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
          className="bg-white rounded-2xl shadow-card border border-gray-100 p-6 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <BookOpen className="w-8 h-8 text-gray-300 mx-auto mb-2" />
          <p className="text-sm text-gray-400">选择一门课程查看详情</p>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
