import { motion, AnimatePresence } from 'framer-motion'
import { X, Clock, BookOpen, ArrowRight, FileText } from 'lucide-react'
import type { PathResourceItem, PathNodeResource } from '../../types'
import { getTypeTag } from '../../utils/pathResources'

interface PathResourceDetailModalProps {
  resource: PathResourceItem | PathNodeResource | null
  onClose: () => void
}

interface ResourceDetail {
  title: string
  type: string
  estimatedTime: string
  topic: string
  course: string
  note: string
  purpose: string
  priority: string
  source: string
  coreContent: string
  recommendedUsage: string
  nextSteps: string
}

function isPathResourceItem(r: PathResourceItem | PathNodeResource): r is PathResourceItem {
  return 'topic' in r && 'course' in r && 'note' in r
}

function getSource(resource: PathResourceItem | PathNodeResource): string {
  if (isPathResourceItem(resource)) return '已保存资源'
  return resource.source === 'resource_package' ? '已保存资源' : '系统推荐'
}

function getDefaultDetail(resource: PathResourceItem | PathNodeResource): ResourceDetail {
  if (isPathResourceItem(resource)) {
    return {
      title: resource.title || '未命名资源',
      type: resource.type || '通用资源',
      estimatedTime: resource.estimatedTime || '未知',
      topic: resource.topic || '通用知识',
      course: resource.course || '通用课程',
      note: resource.note || '',
      purpose: resource.purpose || '',
      priority: resource.priority || '',
      source: '已保存资源',
      coreContent: getMockCoreContent(resource.type, resource.title),
      recommendedUsage: getMockRecommendedUsage(resource.type),
      nextSteps: getMockNextSteps(resource.type),
    }
  }

  return {
    title: resource.title,
    type: resource.type,
    estimatedTime: resource.estimatedTime,
    topic: '数据结构与算法',
    course: '通用课程',
    note: '',
    purpose: '',
    priority: '',
    source: getSource(resource),
    coreContent: getMockCoreContent(resource.type, resource.title),
    recommendedUsage: getMockRecommendedUsage(resource.type),
    nextSteps: getMockNextSteps(resource.type),
  }
}

function getMockCoreContent(type: string, title: string): string {
  const map: Record<string, string> = {
    '个性化讲解文档': `围绕"${title}"的核心概念，采用图示优先 + 分步骤解释的方式，帮助你建立直观理解。内容涵盖知识点定义、原理剖析、常见误区与纠正。`,
    '知识点思维导图': `以"${title}"为中心节点，梳理相关概念、分支关系和应用场景，形成结构化的知识网络。建议对照代码一起看，加深记忆。`,
    '代码示例与注释': `提供完整的 Python 代码示例，每行附带详细中文注释。包括函数定义、测试用例和输出结果，可直接运行验证。`,
    '分层练习题': `从基础判断到代码补全，再到综合应用的三层递进练习。每道题配有提示，帮助你逐步巩固知识。`,
    '拓展阅读资料': `围绕进阶方向，深入探讨调用栈、迭代转换、实际应用等话题。每个方向建议配合代码实践，不要只看理论。`,
    '项目式学习案例': `通过实际项目综合运用所学知识，分阶段完成。包括需求分析、数据结构设计、核心功能实现和测试优化。`,
  }
  return map[type] || `关于"${title}"的学习资源，包含核心概念讲解和实践指导。`
}

function getMockRecommendedUsage(type: string): string {
  const map: Record<string, string> = {
    '个性化讲解文档': '先阅读全文建立概念，再对照图示理解关键过程，最后尝试用自己的话复述一遍。',
    '知识点思维导图': '先浏览整体结构把握全貌，再逐一对照代码实例理解每个分支。',
    '代码示例与注释': '先运行代码观察输出，再对照注释理解实现细节，最后修改参数观察变化。',
    '分层练习题': '按顺序完成三层练习，基础层全做，进阶层至少做2题，提高层选做1题。',
    '拓展阅读资料': '选择一个感兴趣的方向深入阅读，配合代码实践加深理解。',
    '项目式学习案例': '先理解需求，再分阶段实现，最后测试并尝试增加扩展功能。',
  }
  return map[type] || '根据个人学习进度灵活使用本资源。'
}

function getMockNextSteps(type: string): string {
  const map: Record<string, string> = {
    '个性化讲解文档': '完成本资源后，建议进入思维导图梳理结构关系，再通过代码示例巩固理解。',
    '知识点思维导图': '进入代码示例与注释，将导图中的每个分支对应到具体代码实现。',
    '代码示例与注释': '完成分层练习题中的代码补全题，在给定框架中补全核心逻辑。',
    '分层练习题': '查看错题反馈，针对薄弱点回顾讲解文档中的对应部分。',
    '拓展阅读资料': '尝试项目式学习案例，将理论知识应用到真实场景中。',
    '项目式学习案例': '完成全部功能，尝试增加搜索、统计等扩展功能。',
  }
  return map[type] || '继续下一阶段的学习。'
}

export default function PathResourceDetailModal({ resource, onClose }: PathResourceDetailModalProps) {
  return (
    <AnimatePresence>
      {resource && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.15 }}
        >
          <motion.div
            className="absolute inset-0 bg-black/30"
            onClick={onClose}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          />

          <motion.div
            className="relative bg-white rounded-2xl shadow-xl border border-gray-100 w-full max-w-md max-h-[80vh] overflow-y-auto"
            initial={{ opacity: 0, scale: 0.95, y: 12 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 12 }}
            transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
          >
            {(() => {
              const detail = getDefaultDetail(resource)
              const tag = getTypeTag(detail.type)

              return (
                <>
                  <div className="sticky top-0 bg-white z-10 px-5 py-4 border-b border-gray-50 flex items-start justify-between gap-3 rounded-t-2xl">
                    <div className="min-w-0">
                      <h2 className="text-sm font-semibold text-gray-800 leading-snug">{detail.title}</h2>
                      <div className="flex items-center gap-1.5 mt-1.5 flex-wrap">
                        <span className={`px-1.5 py-0.5 rounded text-[9px] font-medium ${tag.color}`}>
                          {tag.label}
                        </span>
                        <span className="flex items-center gap-0.5 text-[9px] text-gray-400">
                          <Clock className="w-2.5 h-2.5" />
                          {detail.estimatedTime}
                        </span>
                        {detail.priority && (
                          <span className={`text-[9px] font-medium px-1.5 py-0.5 rounded ${
                            detail.priority === '必学' ? 'text-red-500 bg-red-50' : detail.priority === '推荐' ? 'text-primary-500 bg-primary-50' : 'text-gray-400 bg-gray-50'
                          }`}>
                            {detail.priority}
                          </span>
                        )}
                        <span className={`text-[9px] font-medium px-1.5 py-0.5 rounded ${
                          detail.source === '已保存资源' ? 'text-primary-500 bg-primary-50' : 'text-gray-400 bg-gray-100'
                        }`}>
                          {detail.source}
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={onClose}
                      className="w-7 h-7 rounded-lg flex items-center justify-center hover:bg-gray-100 transition-colors shrink-0"
                    >
                      <X className="w-4 h-4 text-gray-400" />
                    </button>
                  </div>

                  <div className="px-5 py-4 space-y-4">
                    <div className="grid grid-cols-2 gap-2">
                      <div className="bg-gray-50 rounded-xl px-3 py-2">
                        <span className="text-[9px] text-gray-400 block mb-0.5">所属课程</span>
                        <span className="text-[11px] text-gray-700 font-medium">{detail.course}</span>
                      </div>
                      <div className="bg-gray-50 rounded-xl px-3 py-2">
                        <span className="text-[9px] text-gray-400 block mb-0.5">学习主题</span>
                        <span className="text-[11px] text-gray-700 font-medium truncate">{detail.topic}</span>
                      </div>
                      {detail.purpose && (
                        <div className="bg-gray-50 rounded-xl px-3 py-2">
                          <span className="text-[9px] text-gray-400 block mb-0.5">资源用途</span>
                          <span className="text-[11px] text-gray-700 font-medium">{detail.purpose}</span>
                        </div>
                      )}
                      {detail.note && (
                        <div className="bg-gray-50 rounded-xl px-3 py-2">
                          <span className="text-[9px] text-gray-400 block mb-0.5">学习备注</span>
                          <span className="text-[11px] text-gray-700 font-medium truncate">{detail.note}</span>
                        </div>
                      )}
                    </div>

                    <div>
                      <div className="flex items-center gap-1.5 mb-1.5">
                        <FileText className="w-3.5 h-3.5 text-primary-500" />
                        <span className="text-[11px] font-medium text-gray-700">核心内容</span>
                      </div>
                      <p className="text-[11px] text-gray-500 leading-relaxed">{detail.coreContent}</p>
                    </div>

                    <div>
                      <div className="flex items-center gap-1.5 mb-1.5">
                        <BookOpen className="w-3.5 h-3.5 text-primary-500" />
                        <span className="text-[11px] font-medium text-gray-700">推荐使用方式</span>
                      </div>
                      <p className="text-[11px] text-gray-500 leading-relaxed">{detail.recommendedUsage}</p>
                    </div>

                    <div>
                      <div className="flex items-center gap-1.5 mb-1.5">
                        <ArrowRight className="w-3.5 h-3.5 text-primary-500" />
                        <span className="text-[11px] font-medium text-gray-700">下一步建议</span>
                      </div>
                      <p className="text-[11px] text-gray-500 leading-relaxed">{detail.nextSteps}</p>
                    </div>
                  </div>

                  <div className="px-5 py-3 border-t border-gray-50 flex items-center justify-end">
                    <button
                      onClick={onClose}
                      className="px-4 py-2 rounded-xl bg-gray-100 text-gray-600 text-[11px] font-medium hover:bg-gray-200 transition-colors"
                    >
                      关闭
                    </button>
                  </div>
                </>
              )
            })()}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
