import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Package, FolderPlus, Clock, Trash2, Edit3, Check, X,
} from 'lucide-react'
import type { PathResourceItem } from '../../types'
import { getTypeTag, parseEstimatedMinutes } from '../../utils/pathResources'

const PURPOSE_OPTIONS = ['', '课前预习', '课堂理解', '课后练习', '项目实践', '错题复习'] as const
const PRIORITY_OPTIONS = ['', '必学', '推荐', '拓展'] as const

interface PathResourcePackageProps {
  items: PathResourceItem[]
  onRemove: (resourceId: string) => void
  onUpdate: (resourceId: string, updates: { note?: string; purpose?: string; priority?: string }) => void
  onClear: () => void
  onToast: (msg: string) => void
}

export default function PathResourcePackage({ items, onRemove, onUpdate, onClear, onToast }: PathResourcePackageProps) {
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editNote, setEditNote] = useState('')
  const [editPurpose, setEditPurpose] = useState('')
  const [editPriority, setEditPriority] = useState('')

  const totalMinutes = items.reduce((sum, i) => sum + parseEstimatedMinutes(i.estimatedTime), 0)
  const typeSet = new Set(items.map((i) => i.type))
  const typeTags = Array.from(typeSet).map((t) => getTypeTag(t))

  const startEdit = (item: PathResourceItem) => {
    setEditingId(item.resourceId)
    setEditNote(item.note || '')
    setEditPurpose(item.purpose || '')
    setEditPriority(item.priority || '')
  }

  const cancelEdit = () => {
    setEditingId(null)
  }

  const saveEdit = (resourceId: string) => {
    onUpdate(resourceId, { note: editNote, purpose: editPurpose, priority: editPriority })
    setEditingId(null)
    onToast('备注已保存')
  }

  return (
    <div className="bg-white rounded-2xl shadow-card border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Package className="w-4 h-4 text-primary-500" />
          <span className="text-sm font-semibold text-gray-800">学习路径资源包</span>
        </div>
        {items.length > 0 && (
          <button
            onClick={() => { onClear(); onToast('资源包已清空') }}
            className="text-[10px] text-gray-400 hover:text-red-500 transition-colors"
          >
            清空
          </button>
        )}
      </div>

      {/* Content */}
      <div className="p-4">
        {items.length === 0 ? (
          /* Empty state */
          <div className="text-center py-6">
            <FolderPlus className="w-8 h-8 text-gray-300 mx-auto mb-2" />
            <p className="text-xs font-medium text-gray-500 mb-1">暂无已加入资源</p>
            <p className="text-[10px] text-gray-400 leading-relaxed">
              从左侧资源卡片中点击"加入资源包"，<br />即可构建你的专属资源包。
            </p>
          </div>
        ) : (
          /* Resource list */
          <div className="space-y-1.5">
            <AnimatePresence>
              {items.map((item) => {
                const tag = getTypeTag(item.type)
                const isEditing = editingId === item.resourceId
                return (
                  <motion.div
                    key={item.resourceId}
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    <div className={`rounded-xl border transition-colors ${isEditing ? 'border-primary-200 bg-primary-50/30' : 'border-gray-100 bg-gray-50/50'}`}>
                      {/* Item row */}
                      <div className="flex items-start gap-2 px-3 py-2.5">
                        <div className="flex-1 min-w-0">
                          <p className="text-[11px] font-medium text-gray-800 truncate">{item.title}</p>
                          <div className="flex items-center gap-1.5 mt-1">
                            <span className={`px-1.5 py-0.5 rounded text-[9px] font-medium ${tag.color}`}>
                              {tag.label}
                            </span>
                            <span className="flex items-center gap-0.5 text-[9px] text-gray-400">
                              <Clock className="w-2.5 h-2.5" />
                              {item.estimatedTime}
                            </span>
                            {item.purpose && (
                              <span className="text-[9px] text-gray-400">· {item.purpose}</span>
                            )}
                            {item.priority && (
                              <span className={`text-[9px] font-medium ${item.priority === '必学' ? 'text-red-500' : item.priority === '推荐' ? 'text-primary-500' : 'text-gray-400'}`}>
                                {item.priority}
                              </span>
                            )}
                          </div>
                          {item.note && !isEditing && (
                            <p className="text-[10px] text-gray-400 mt-1 truncate">备注：{item.note}</p>
                          )}
                        </div>
                        <div className="flex items-center gap-0.5 shrink-0">
                          <button
                            onClick={() => startEdit(item)}
                            className="w-6 h-6 rounded-lg flex items-center justify-center hover:bg-gray-200 transition-colors"
                          >
                            <Edit3 className="w-3 h-3 text-gray-400" />
                          </button>
                          <button
                            onClick={() => { onRemove(item.resourceId); onToast('已从资源包移除') }}
                            className="w-6 h-6 rounded-lg flex items-center justify-center hover:bg-red-50 transition-colors"
                          >
                            <Trash2 className="w-3 h-3 text-gray-400 hover:text-red-500" />
                          </button>
                        </div>
                      </div>

                      {/* Edit area */}
                      <AnimatePresence>
                        {isEditing && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            transition={{ duration: 0.2 }}
                            className="overflow-hidden"
                          >
                            <div className="px-3 pb-3 space-y-2 border-t border-primary-100 pt-2">
                              {/* Note */}
                              <div>
                                <label className="text-[10px] text-gray-400 block mb-1">学习备注</label>
                                <input
                                  type="text"
                                  value={editNote}
                                  onChange={(e) => setEditNote(e.target.value)}
                                  placeholder="例如：先看图示，再做代码补全题。"
                                  className="w-full rounded-lg border border-gray-200 px-2 py-1.5 text-[11px] focus:outline-none focus:ring-1 focus:ring-primary-200"
                                />
                              </div>
                              {/* Purpose + Priority */}
                              <div className="grid grid-cols-2 gap-2">
                                <div>
                                  <label className="text-[10px] text-gray-400 block mb-1">资源用途</label>
                                  <select
                                    value={editPurpose}
                                    onChange={(e) => setEditPurpose(e.target.value)}
                                    className="w-full rounded-lg border border-gray-200 px-2 py-1.5 text-[11px] focus:outline-none focus:ring-1 focus:ring-primary-200 bg-white"
                                  >
                                    {PURPOSE_OPTIONS.map((o) => (
                                      <option key={o} value={o}>{o || '未设置'}</option>
                                    ))}
                                  </select>
                                </div>
                                <div>
                                  <label className="text-[10px] text-gray-400 block mb-1">优先级</label>
                                  <select
                                    value={editPriority}
                                    onChange={(e) => setEditPriority(e.target.value)}
                                    className="w-full rounded-lg border border-gray-200 px-2 py-1.5 text-[11px] focus:outline-none focus:ring-1 focus:ring-primary-200 bg-white"
                                  >
                                    {PRIORITY_OPTIONS.map((o) => (
                                      <option key={o} value={o}>{o || '未设置'}</option>
                                    ))}
                                  </select>
                                </div>
                              </div>
                              {/* Action buttons */}
                              <div className="flex items-center gap-2">
                                <button
                                  onClick={() => saveEdit(item.resourceId)}
                                  className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-primary-500 text-white text-[10px] font-medium hover:bg-primary-600 transition-colors"
                                >
                                  <Check className="w-3 h-3" />
                                  保存
                                </button>
                                <button
                                  onClick={cancelEdit}
                                  className="flex items-center gap-1 px-3 py-1.5 rounded-lg border border-gray-200 text-gray-500 text-[10px] hover:bg-gray-50 transition-colors"
                                >
                                  <X className="w-3 h-3" />
                                  取消
                                </button>
                              </div>
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  </motion.div>
                )
              })}
            </AnimatePresence>
          </div>
        )}

        {/* Stats footer */}
        {items.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-50 flex items-center gap-3 flex-wrap">
            <span className="text-[10px] text-gray-500">
              已加入 <span className="font-semibold text-primary-600">{items.length}</span> 项
            </span>
            <span className="text-[10px] text-gray-400">·</span>
            <span className="text-[10px] text-gray-500">
              预计 <span className="font-semibold text-gray-700">{totalMinutes}</span> 分钟
            </span>
            {typeTags.length > 0 && (
              <>
                <span className="text-[10px] text-gray-400">·</span>
                <span className="text-[10px] text-gray-500">覆盖：</span>
                <div className="flex items-center gap-1">
                  {typeTags.map((t, i) => (
                    <span key={i} className={`px-1.5 py-0.5 rounded text-[9px] font-medium ${t.color}`}>
                      {t.label}
                    </span>
                  ))}
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
