import { motion, AnimatePresence } from 'framer-motion'
import { Target, BookOpen, ArrowRight, TrendingUp, Clock, Tag, Eye, Plus, Check } from 'lucide-react'
import type { PathNode, PathNodeResource } from '../../types'

const STAGE_COLORS: Record<string, string> = {
  '基础概念': 'bg-blue-50 text-blue-600 border-blue-100',
  '核心理解': 'bg-purple-50 text-purple-600 border-purple-100',
  '代码实现': 'bg-emerald-50 text-emerald-600 border-emerald-100',
  '练习巩固': 'bg-amber-50 text-amber-600 border-amber-100',
  '项目应用': 'bg-rose-50 text-rose-600 border-rose-100',
}

interface PathNodeDetailProps {
  node: PathNode | null
  addedResourceIds: Set<string>
  onStatusChange: (nodeId: string, status: 'pending' | 'in_progress' | 'completed') => void
  onViewResource: (resource: PathNodeResource) => void
  onAddToPackage: (resource: PathNodeResource) => void
}

export default function PathNodeDetail({ node, addedResourceIds, onStatusChange, onViewResource, onAddToPackage }: PathNodeDetailProps) {
  return (
    <AnimatePresence mode="wait">
      {node ? (
        <motion.div
          key={node.id}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
          className="bg-white rounded-2xl shadow-card border border-gray-100 overflow-hidden"
        >
          {/* Header */}
          <div className="px-4 py-3 border-b border-gray-50">
            <div className="flex items-center justify-between mb-1">
              <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full border ${STAGE_COLORS[node.stage] || 'bg-gray-50 text-gray-500 border-gray-100'}`}>
                {node.stage}
              </span>
              <span
                className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${
                  node.status === 'completed' ? 'bg-green-50 text-green-600' : node.status === 'in_progress' ? 'bg-primary-50 text-primary-600' : 'bg-gray-50 text-gray-400'
                }`}
              >
                {node.status === 'completed' ? '已完成' : node.status === 'in_progress' ? '学习中' : '未开始'}
              </span>
            </div>
            <h3 className="text-sm font-semibold text-gray-800 mt-1">{node.name}</h3>
            <div className="flex items-center gap-2 mt-1.5 text-[10px] text-gray-400">
              <Clock className="w-3 h-3" />
              <span>预计 {node.duration}</span>
            </div>
          </div>

          <div className="p-4 space-y-3">
            {/* Learning objective — single sentence */}
            {node.learningObjectives.length > 0 && (
              <div className="flex items-start gap-1.5">
                <Target className="w-3.5 h-3.5 text-primary-500 mt-0.5 shrink-0" />
                <p className="text-xs text-gray-500 leading-relaxed">
                  <span className="font-medium text-gray-700">学习目标：</span>
                  {node.learningObjectives[0]}
                </p>
              </div>
            )}

            {/* Task description — single sentence */}
            {node.taskDescription && (
              <div className="flex items-start gap-1.5">
                <BookOpen className="w-3.5 h-3.5 text-primary-500 mt-0.5 shrink-0" />
                <p className="text-xs text-gray-500 leading-relaxed">
                  <span className="font-medium text-gray-700">任务说明：</span>
                  {node.taskDescription.replace(/^[-•·]\s*/, '')}
                </p>
              </div>
            )}

            {/* Matched resources from package */}
            {node.matchedResources.length > 0 && (
              <div>
                <div className="flex items-center gap-1.5 mb-2">
                  <Tag className="w-3.5 h-3.5 text-primary-500" />
                  <span className="text-xs font-medium text-gray-700">学习资源匹配</span>
                  <span className="text-[10px] text-primary-500 font-medium bg-primary-50 px-1.5 py-0.5 rounded-full">
                    {node.matchedResources.length} 项
                  </span>
                </div>
                <div className="space-y-1.5">
                  {node.matchedResources.map((r) => (
                      <div key={r.resourceId} className="flex items-center gap-2 px-3 py-2 rounded-xl bg-primary-50/30 border border-primary-100">
                        <div className="flex-1 min-w-0">
                          <p className="text-[11px] font-medium text-gray-700 truncate">{r.title}</p>
                        </div>
                        <button
                          onClick={(e) => { e.stopPropagation(); onViewResource(r) }}
                          className="flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] text-primary-500 border border-primary-200 hover:bg-primary-50 transition-colors shrink-0"
                        >
                          <Eye className="w-3 h-3" />
                          打开资源
                        </button>
                      </div>
                    ))}
                </div>
              </div>
            )}

            {/* System recommended resources — simplified, max 3 */}
            <div>
              <div className="flex items-center gap-1.5 mb-2">
                <Tag className="w-3.5 h-3.5 text-gray-400" />
                <span className="text-xs font-medium text-gray-700">系统推荐资源</span>
                <span className="text-[10px] text-gray-400">({node.defaultResources.length} 项)</span>
              </div>
              <div className="space-y-1">
                {node.defaultResources.slice(0, 3).map((r) => {
                  const isAdded = addedResourceIds.has(r.resourceId)
                  return (
                    <div key={r.resourceId} className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-50 border border-gray-100">
                      <span className="text-[11px] text-gray-600 truncate flex-1 min-w-0">{r.title}</span>
                      <button
                        onClick={(e) => { e.stopPropagation(); onViewResource(r) }}
                        className="text-[10px] text-primary-500 hover:text-primary-600 shrink-0"
                      >
                        查看
                      </button>
                      {isAdded ? (
                        <span className="text-[10px] text-green-500 shrink-0">
                          <Check className="w-3 h-3 inline" />
                        </span>
                      ) : (
                        <button
                          onClick={(e) => { e.stopPropagation(); onAddToPackage(r) }}
                          className="text-[10px] text-primary-500 hover:text-primary-600 shrink-0"
                        >
                          <Plus className="w-3 h-3 inline" />
                        </button>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Action buttons */}
            <div className="flex items-center gap-2 pt-1 border-t border-gray-50">
              {node.status === 'pending' && (
                <button
                  onClick={() => onStatusChange(node.id, 'in_progress')}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-primary-500 text-white text-xs font-medium hover:bg-primary-600 transition-colors"
                >
                  <ArrowRight className="w-3.5 h-3.5" />
                  标记为学习中
                </button>
              )}
              {node.status === 'in_progress' && (
                <button
                  onClick={() => onStatusChange(node.id, 'completed')}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-green-500 text-white text-xs font-medium hover:bg-green-600 transition-colors"
                >
                  <TrendingUp className="w-3.5 h-3.5" />
                  标记为已完成
                </button>
              )}
              {node.status === 'completed' && (
                <button
                  onClick={() => onStatusChange(node.id, 'pending')}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl border border-gray-200 text-gray-500 text-xs font-medium hover:bg-gray-50 transition-colors"
                >
                  重置为未开始
                </button>
              )}
            </div>
          </div>
        </motion.div>
      ) : (
        <motion.div
          key="empty"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-white rounded-2xl shadow-card border border-gray-100 p-6 text-center"
        >
          <BookOpen className="w-8 h-8 text-gray-300 mx-auto mb-2" />
          <p className="text-xs text-gray-400">选择一个路径节点查看详情</p>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
