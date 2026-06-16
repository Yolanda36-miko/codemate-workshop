import { motion, AnimatePresence } from 'framer-motion'
import {
  X, Clock, Target, BookOpen, Lightbulb, User, ArrowRight, Bookmark, XCircle,
} from 'lucide-react'
import type { ResourceCard } from '../../types'

interface ResourceDetailPanelProps {
  resource: ResourceCard | null
  onClose: () => void
  onSaveToPackage?: (id: string) => void
  savedToPackage?: boolean
}

const typeBadgeColors: Record<string, string> = {
  '个性化讲解文档': 'bg-blue-50 text-blue-700 border-blue-100',
  '知识点思维导图': 'bg-purple-50 text-purple-700 border-purple-100',
  '代码示例与注释': 'bg-emerald-50 text-emerald-700 border-emerald-100',
  '分层练习题': 'bg-amber-50 text-amber-700 border-amber-100',
  '拓展阅读资料': 'bg-indigo-50 text-indigo-700 border-indigo-100',
  '项目式学习案例': 'bg-rose-50 text-rose-700 border-rose-100',
}

export default function ResourceDetailPanel({ resource, onClose, onSaveToPackage, savedToPackage }: ResourceDetailPanelProps) {
  return (
    <AnimatePresence>
      {resource && (
        <motion.div
          className="fixed inset-0 z-50 flex items-start justify-end"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            className="absolute inset-0 bg-black/20"
            onClick={onClose}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          />

          <motion.div
            className="relative w-full max-w-xl h-full bg-white shadow-2xl overflow-y-auto"
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          >
            <button
              onClick={onClose}
              className="absolute top-4 right-4 w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors z-10"
            >
              <X className="w-4 h-4 text-gray-500" />
            </button>

            <div className="p-6 pt-12 space-y-5">
              {/* Header */}
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${typeBadgeColors[resource.type] ?? 'bg-gray-50 text-gray-600 border-gray-100'}`}>
                    {resource.type}
                  </span>
                  <span className="text-xs text-gray-400">{resource.difficulty}</span>
                  {resource.estimated_time && (
                    <span className="flex items-center gap-1 text-xs text-gray-400">
                      <Clock className="w-3 h-3" />
                      {resource.estimated_time}
                    </span>
                  )}
                </div>
                <h2 className="text-lg font-bold text-gray-800 mb-1">{resource.title}</h2>
                <p className="text-xs text-gray-400">
                  {resource.course} · {resource.knowledge_point} · {resource.language}
                </p>
              </div>

              {/* Match reason */}
              {resource.match_reason && (
                <div className="flex items-start gap-2 px-3 py-2.5 rounded-xl bg-primary-50/50 border border-primary-100/50">
                  <Lightbulb className="w-4 h-4 text-primary-400 shrink-0 mt-0.5" />
                  <p className="text-xs text-primary-700">{resource.match_reason}</p>
                </div>
              )}

              {/* Section 1: Learning objectives */}
              {resource.learning_objectives && (
                <div>
                  <div className="flex items-center gap-1.5 mb-2">
                    <Target className="w-4 h-4 text-primary-500" />
                    <span className="text-xs font-semibold text-gray-700">学习目标</span>
                  </div>
                  <p className="text-sm text-gray-600 leading-relaxed">{resource.learning_objectives}</p>
                </div>
              )}

              {/* Section 2: Core content */}
              <div>
                <div className="flex items-center gap-1.5 mb-2">
                  <BookOpen className="w-4 h-4 text-primary-500" />
                  <span className="text-xs font-semibold text-gray-700">核心内容</span>
                </div>
                {resource.detailed_content ? (
                  <div className="text-sm text-gray-600 leading-relaxed whitespace-pre-line mb-3">
                    {resource.detailed_content}
                  </div>
                ) : resource.sections?.length ? (
                  resource.sections.map((s, i) => (
                    <div key={i} className="mb-3">
                      <h3 className="text-sm font-semibold text-gray-800 mb-1">{s.heading}</h3>
                      <p className="text-sm text-gray-600 leading-relaxed whitespace-pre-line mb-1.5">{s.content}</p>
                      {s.codeBlock && (
                        <div className="bg-gray-900 rounded-xl p-3 overflow-x-auto">
                          <pre className="text-xs text-green-300 leading-relaxed font-mono">{s.codeBlock}</pre>
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <div>
                    {resource.summary && (
                      <p className="text-sm text-gray-600 leading-relaxed mb-2">{resource.summary}</p>
                    )}
                    <p className="text-xs text-gray-400">暂无更详细内容，可参考上方摘要信息。</p>
                  </div>
                )}
                {resource.key_concepts && resource.key_concepts.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {resource.key_concepts.map((kc) => (
                      <span key={kc} className="px-2 py-0.5 bg-primary-50 rounded-full text-[11px] text-primary-700 border border-primary-100">
                        {kc}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Section 3: Recommended usage */}
              {resource.recommended_usage && (
                <div>
                  <div className="flex items-center gap-1.5 mb-2">
                    <ArrowRight className="w-4 h-4 text-primary-500" />
                    <span className="text-xs font-semibold text-gray-700">推荐使用方式</span>
                  </div>
                  <p className="text-xs text-gray-600 leading-relaxed">{resource.recommended_usage}</p>
                </div>
              )}

              {/* Section 4: Profile dimension mapping */}
              {resource.profile_dimension && (
                <div>
                  <div className="flex items-center gap-1.5 mb-2">
                    <User className="w-4 h-4 text-primary-500" />
                    <span className="text-xs font-semibold text-gray-700">对应画像维度</span>
                  </div>
                  <p className="text-xs text-gray-600 leading-relaxed">{resource.profile_dimension}</p>
                </div>
              )}

              {/* Section 5: Next steps */}
              {resource.next_steps && (
                <div>
                  <div className="flex items-center gap-1.5 mb-2">
                    <ArrowRight className="w-4 h-4 text-purple-500" />
                    <span className="text-xs font-semibold text-gray-700">下一步建议</span>
                  </div>
                  <p className="text-xs text-gray-600 leading-relaxed">{resource.next_steps}</p>
                </div>
              )}

              {/* Learning tips */}
              {resource.learning_tips && resource.learning_tips.length > 0 && (
                <div className="flex items-start gap-2.5 px-4 py-3 rounded-xl bg-amber-50 border border-amber-200">
                  <Lightbulb className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
                  <div>
                    <p className="text-xs font-semibold text-amber-700 mb-1">学习建议</p>
                    <ul className="space-y-1">
                      {resource.learning_tips.map((tip, i) => (
                        <li key={i} className="text-xs text-amber-600">{tip}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {/* Action buttons */}
              {onSaveToPackage && (
                <div className="pt-2 space-y-2">
                  <button
                    onClick={() => onSaveToPackage(resource.id)}
                    className={`w-full flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-medium transition-all ${
                      savedToPackage
                        ? 'bg-rose-50 text-rose-600 border border-rose-200 hover:bg-rose-100'
                        : 'bg-gradient-to-r from-amber-400 to-amber-600 text-white hover:shadow-glow hover:-translate-y-0.5'
                    }`}
                  >
                    {savedToPackage ? (
                      <>
                        <XCircle className="w-4 h-4" />
                        取消加入
                      </>
                    ) : (
                      <>
                        <Bookmark className="w-4 h-4" />
                        加入资源包
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
