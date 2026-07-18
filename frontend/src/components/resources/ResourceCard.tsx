import { motion } from 'framer-motion'
import { Clock, Eye, Bookmark, XCircle } from 'lucide-react'
import type { ResourceCard as ResourceCardType } from '../../types'

interface ResourceCardProps {
  resource: ResourceCardType
  index: number
  onViewDetail: (resource: ResourceCardType) => void
  onSaveToPackage?: (id: string) => void
  savedToPackage?: boolean
  showSaveToPackage?: boolean
}

const typeBadgeColors: Record<string, string> = {
  '图解讲解': 'bg-purple-50 text-purple-700 border-purple-100',
  '代码示例': 'bg-emerald-50 text-emerald-700 border-emerald-100',
  '易错点': 'bg-amber-50 text-amber-700 border-amber-100',
  '分层练习': 'bg-blue-50 text-blue-700 border-blue-100',
  '项目案例': 'bg-rose-50 text-rose-700 border-rose-100',
}

export default function ResourceCard({
  resource,
  index,
  onViewDetail,
  onSaveToPackage,
  savedToPackage,
  showSaveToPackage = false,
}: ResourceCardProps) {
  const r = resource
  const knowledgeTags: string[] = r.knowledge_points ?? (r.knowledge_point ? [r.knowledge_point] : [])

  return (
    <motion.div
      className="bg-white rounded-2xl border border-gray-100 shadow-card overflow-hidden"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06, duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
      whileHover={{ y: -1, boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)' }}
    >
      <div className="p-4">
        <div className="flex items-start gap-3">
          {/* Left: content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium border ${typeBadgeColors[r.type] ?? 'bg-gray-50 text-gray-600 border-gray-100'}`}>
                {r.type}
              </span>
              {r.estimated_time && (
                <span className="flex items-center gap-1 text-[10px] text-gray-400">
                  <Clock className="w-3 h-3" />
                  {r.estimated_time}
                </span>
              )}
            </div>

            <h3 className="text-sm font-semibold text-gray-800 mb-1.5 leading-snug">{r.title}</h3>

            {(r.description || r.summary) && (
              <p className="text-xs text-gray-500 leading-relaxed line-clamp-1 mb-2">
                {r.description || r.summary}
              </p>
            )}

            {/* Knowledge points tags */}
            {knowledgeTags.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {knowledgeTags.slice(0, 6).map((kp) => (
                  <span key={kp} className="px-1.5 py-0.5 rounded-full bg-gray-100 text-[10px] text-gray-500">
                    {kp}
                  </span>
                ))}
                {knowledgeTags.length > 6 && (
                  <span className="px-1.5 py-0.5 rounded-full bg-gray-50 text-[10px] text-gray-400">
                    +{knowledgeTags.length - 6}
                  </span>
                )}
              </div>
            )}
          </div>

          {/* Right: action buttons */}
          <div className="flex flex-col gap-1.5 shrink-0">
            <button
              onClick={(e) => { e.stopPropagation(); onViewDetail(r) }}
              className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-[11px] text-primary-600 border border-primary-200 hover:bg-primary-50 transition-colors"
            >
              <Eye className="w-3 h-3" />
              查看详情
            </button>
            {showSaveToPackage && onSaveToPackage && (
              <button
                onClick={(e) => { e.stopPropagation(); onSaveToPackage(r.id) }}
                className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-[11px] font-medium transition-all ${
                  savedToPackage
                    ? 'text-rose-600 border border-rose-200 hover:bg-rose-50'
                    : 'text-amber-600 border border-amber-200 hover:bg-amber-50'
                }`}
              >
                {savedToPackage ? (
                  <>
                    <XCircle className="w-3 h-3" />
                    取消加入
                  </>
                ) : (
                  <>
                    <Bookmark className="w-3 h-3" />
                    加入资源包
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  )
}
