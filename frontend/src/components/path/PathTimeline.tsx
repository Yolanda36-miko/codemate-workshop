import { motion, AnimatePresence } from 'framer-motion'
import { Clock, Circle, CheckCircle2, PlayCircle, Package } from 'lucide-react'
import type { PathNode } from '../../types'

const statusConfig = {
  pending: { icon: Circle, color: 'text-gray-300', bg: 'bg-gray-300', card: 'border-gray-100' },
  in_progress: { icon: PlayCircle, color: 'text-primary-500', bg: 'bg-primary-500', card: 'border-primary-200 bg-primary-50/20' },
  completed: { icon: CheckCircle2, color: 'text-green-500', bg: 'bg-green-500', card: 'border-green-100 bg-green-50/20' },
}

const STAGE_LABELS: Record<string, string> = {
  '基础概念': '阶段一',
  '核心理解': '阶段二',
  '代码实现': '阶段三',
  '练习巩固': '阶段四',
  '项目应用': '阶段五',
}

interface PathTimelineProps {
  nodes: PathNode[]
  selectedId: string | null
  onSelect: (node: PathNode) => void
  onStatusChange: (nodeId: string, status: 'pending' | 'in_progress' | 'completed') => void
}

export default function PathTimeline({ nodes, selectedId, onSelect, onStatusChange }: PathTimelineProps) {
  return (
    <div className="relative">
      <div className="absolute left-[19px] top-3 bottom-3 w-0.5 bg-gray-200" />

      <div className="space-y-2">
        <AnimatePresence>
          {nodes.map((node, index) => {
            const config = statusConfig[node.status]
            const StatusIcon = config.icon
            const isSelected = selectedId === node.id
            const matchedCount = node.matchedResources.length

            return (
              <motion.div
                key={node.id}
                initial={{ opacity: 0, x: -16 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.06, duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
                className="relative flex items-start gap-3 ml-0 pl-10"
              >
                <button
                  onClick={() => onStatusChange(node.id, node.status === 'pending' ? 'in_progress' : node.status === 'in_progress' ? 'completed' : 'pending')}
                  className={`absolute left-[13px] top-2 w-3.5 h-3.5 rounded-full border-2 border-white ${config.bg} transition-colors hover:ring-2 hover:ring-offset-1 hover:ring-primary-200 z-10`}
                />

                <motion.button
                  onClick={() => onSelect(node)}
                  className={`flex-1 text-left bg-white rounded-2xl p-4 shadow-card border transition-all ${isSelected ? 'border-primary-300 shadow-md ring-1 ring-primary-100' : config.card} hover:shadow-card-hover`}
                  whileHover={{ y: -1 }}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-medium text-gray-400 bg-gray-50 px-2 py-0.5 rounded-full">
                        {index + 1}
                      </span>
                      <div>
                        <div className="flex items-center gap-1.5 mb-0.5">
                          <h3 className={`font-semibold text-sm ${node.status === 'completed' ? 'text-gray-500 line-through' : 'text-gray-800'}`}>
                            {node.name}
                          </h3>
                          {STAGE_LABELS[node.stage] && (
                            <span className="text-[9px] text-gray-400 bg-gray-50 px-1.5 py-0.5 rounded">
                              {STAGE_LABELS[node.stage]}
                            </span>
                          )}
                        </div>
                        <span className="text-[10px] text-primary-500">{node.course}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-1.5 shrink-0">
                      {matchedCount > 0 && (
                        <span className="flex items-center gap-0.5 text-[9px] text-primary-500 font-medium bg-primary-50 px-1.5 py-0.5 rounded-full">
                          <Package className="w-2.5 h-2.5" />
                          {matchedCount}
                        </span>
                      )}
                      <StatusIcon className={`w-5 h-5 ${config.color}`} />
                    </div>
                  </div>

                  <p className="text-xs text-gray-500 mb-2">{node.goal}</p>

                  <div className="flex items-center gap-3 text-[10px] text-gray-400 flex-wrap">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      预计 {node.duration}
                    </span>
                    <span>{node.defaultResources.length} 项系统推荐</span>
                    {matchedCount > 0 && (
                      <span className="text-primary-500 font-medium">
                        已匹配你的资源包
                      </span>
                    )}
                    <span
                      className={`font-medium ${
                        node.status === 'completed' ? 'text-green-500' : node.status === 'in_progress' ? 'text-primary-500' : 'text-gray-400'
                      }`}
                    >
                      {node.status === 'completed' ? '已完成' : node.status === 'in_progress' ? '学习中' : '未开始'}
                    </span>
                  </div>
                </motion.button>
              </motion.div>
            )
          })}
        </AnimatePresence>
      </div>
    </div>
  )
}
