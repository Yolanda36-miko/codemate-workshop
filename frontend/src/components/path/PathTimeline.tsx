import { motion, AnimatePresence } from 'framer-motion'
import { Clock, Circle, CheckCircle2, PlayCircle } from 'lucide-react'
import type { PathNode } from '../../types'

const statusConfig = {
  pending: { icon: Circle, color: 'text-gray-300', bg: 'bg-gray-300', card: 'border-gray-100' },
  in_progress: { icon: PlayCircle, color: 'text-primary-500', bg: 'bg-primary-500', card: 'border-primary-200 bg-primary-50/20' },
  completed: { icon: CheckCircle2, color: 'text-green-500', bg: 'bg-green-500', card: 'border-green-100 bg-green-50/20' },
}

interface PathTimelineProps {
  nodes: PathNode[]
  selectedId: string | null
  onSelect: (node: PathNode) => void
  onStatusChange: (nodeId: string, status: 'pending' | 'in_progress' | 'completed') => void
  isPersonalizedMode?: boolean
}

export default function PathTimeline({ nodes, selectedId, onSelect, onStatusChange, isPersonalizedMode = false }: PathTimelineProps) {
  return (
    <div className="relative">
      <div className="absolute left-[19px] top-3 bottom-3 w-0.5 bg-gray-200" />

      <div className="space-y-2">
        <AnimatePresence>
          {nodes.map((node, index) => {
            const config = statusConfig[node.status]
            const StatusIcon = config.icon
            const isSelected = selectedId === node.id

            return (
              <motion.div
                key={node.id}
                initial={{ opacity: 0, x: -16 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.04, duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
                className="relative flex items-start gap-3 ml-0 pl-10"
              >
                <button
                  onClick={() => onStatusChange(node.id, node.status === 'pending' ? 'in_progress' : node.status === 'in_progress' ? 'completed' : 'pending')}
                  className={`absolute left-[13px] top-2 w-3.5 h-3.5 rounded-full border-2 border-white ${config.bg} transition-colors hover:ring-2 hover:ring-offset-1 hover:ring-primary-200 z-10`}
                />

                <motion.button
                  onClick={() => onSelect(node)}
                  className={`flex-1 text-left bg-white rounded-xl p-3.5 shadow-card border transition-all ${isSelected ? 'border-primary-300 shadow-md ring-1 ring-primary-100' : config.card} hover:shadow-card-hover`}
                  whileHover={{ y: -1 }}
                >
                  <div className="flex items-center gap-2.5">
                    <span className="text-[10px] font-medium text-gray-400 bg-gray-50 px-2 py-0.5 rounded-full shrink-0">
                      阶段 {index + 1}
                    </span>
                    <h3 className={`font-semibold text-sm truncate ${node.status === 'completed' ? 'text-gray-400 line-through' : 'text-gray-800'}`}>
                      {node.name}
                    </h3>
                    {isPersonalizedMode && node.isFocus && (
                      <span className="text-[9px] font-medium text-amber-600 bg-amber-50 border border-amber-200 px-1.5 py-0.5 rounded-full shrink-0">
                        重点
                      </span>
                    )}
                    <StatusIcon className={`w-4 h-4 ${config.color} shrink-0 ${isPersonalizedMode && node.isFocus ? '' : 'ml-auto'}`} />
                  </div>

                  <div className="flex items-center gap-3 text-[10px] text-gray-400 mt-2">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      预计 {node.duration}
                    </span>
                    <span>系统推荐 {node.defaultResources.length} 项资源</span>
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
