import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  X, Maximize2, Minimize2, Clock, Bookmark, XCircle,
  ChevronDown, ChevronRight,
} from 'lucide-react'
import type { ResourceCard, ResourceSection } from '../../types'

interface ResourceDetailModalProps {
  resource: ResourceCard | null
  onClose: () => void
  onSaveToPackage?: (id: string) => void
  savedToPackage?: boolean
}

// ========== Helpers ==========

function safeContent(content: unknown): string {
  if (content == null) return ''
  if (typeof content === 'string') return content
  if (Array.isArray(content)) return content.map((c) => String(c)).join('\n')
  if (typeof content === 'object') {
    try { return JSON.stringify(content, null, 2) } catch { return String(content) }
  }
  return String(content)
}

function langLabel(lang?: string): string | null {
  if (!lang) return null
  const l = lang.toLowerCase()
  if (l === 'python' || l === 'py') return 'Python'
  if (l === 'c') return 'C'
  if (l === 'c++' || l === 'cpp' || l === 'cxx') return 'C++'
  if (l === 'java') return 'Java'
  return lang
}

// ========== Collapsible Answer Block ==========

function CollapsibleAnswer({ section }: { section: ResourceSection }) {
  const [open, setOpen] = useState(false)
  const contentText = safeContent(section.content)
  const heading = section.heading || section.title || ''

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-2 px-3 py-2 text-left hover:bg-gray-50 transition-colors"
      >
        {open ? (
          <ChevronDown className="w-3.5 h-3.5 text-gray-400 shrink-0" />
        ) : (
          <ChevronRight className="w-3.5 h-3.5 text-gray-400 shrink-0" />
        )}
        <span className="text-xs font-medium text-gray-600">
          {heading || '展开参考答案'}
        </span>
      </button>
      {open && (
        <div className="px-3 pb-3 pt-1 border-t border-gray-100">
          {contentText && (
            <p className="text-xs text-gray-600 leading-relaxed whitespace-pre-line">
              {contentText}
            </p>
          )}
          {!contentText && section.items && section.items.length > 0 && (
            <ul className="space-y-1">
              {section.items.map((item, i) => (
                <li key={i} className="text-xs text-gray-600 leading-relaxed flex items-start gap-1.5">
                  <span className="text-gray-300 mt-0.5">•</span>
                  {item}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}

// ========== Section Block (unified, clean style) ==========

function SectionBlock({ section }: { section: ResourceSection; compact?: boolean }) {
  const kind = (section.kind || 'text').toLowerCase()
  const heading = section.heading || section.title || ''

  // ── divider ──
  if (kind === 'divider') {
    return <hr className="my-3 border-gray-150" />
  }

  // ── answer: collapsible ──
  if (kind === 'answer') {
    return <CollapsibleAnswer section={section} />
  }

  // ── code ──
  if (kind === 'code') {
    const label = langLabel(section.language)
    const codeText = safeContent(section.content)
    return (
      <div className="space-y-1.5">
        {heading && (
          <h4 className="text-xs font-semibold text-gray-700">{heading}</h4>
        )}
        {label && (
          <span className="inline-block px-1.5 py-0.5 rounded text-[10px] font-medium bg-gray-200 text-gray-500 mb-1">
            {label}
          </span>
        )}
        <div className="rounded-lg p-4 bg-gray-900 overflow-x-auto">
          <pre className="text-xs leading-relaxed font-mono whitespace-pre text-green-300">
            {codeText}
          </pre>
        </div>
      </div>
    )
  }

  // ── diagram ──
  if (kind === 'diagram') {
    const diagramText = safeContent(section.content)
    return (
      <div className="space-y-1.5">
        {heading && (
          <h4 className="text-xs font-semibold text-gray-700">{heading}</h4>
        )}
        <div className="rounded-lg p-4 bg-gray-50 border border-gray-200 overflow-x-auto">
          <pre className="text-xs leading-relaxed font-mono whitespace-pre text-gray-700">
            {diagramText}
          </pre>
        </div>
      </div>
    )
  }

  // ── steps ──
  if (kind === 'steps') {
    const stepItems: string[] = (() => {
      if (section.items && section.items.length > 0) return section.items
      if (section.steps && section.steps.length > 0) return section.steps
      const c = section.content
      if (Array.isArray(c)) return c.map(String)
      if (typeof c === 'string') return c.split('\n').filter(Boolean)
      return []
    })()
    return (
      <div className="space-y-1.5">
        {heading && (
          <h4 className="text-xs font-semibold text-gray-700">{heading}</h4>
        )}
        <div className="space-y-1">
          {stepItems.map((item, i) => (
            <div key={i} className="flex items-start gap-2">
              <span className="w-5 h-5 rounded-full bg-gray-100 text-gray-500 flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5">
                {i + 1}
              </span>
              <span className="text-xs text-gray-600 leading-relaxed">{item}</span>
            </div>
          ))}
        </div>
      </div>
    )
  }

  // ── practice / task with items ──
  if ((kind === 'practice' || kind === 'task' || kind === 'compare') && section.items && section.items.length > 0) {
    return (
      <div className="space-y-1.5">
        {heading && (
          <h4 className="text-xs font-semibold text-gray-700">{heading}</h4>
        )}
        <ul className="space-y-1">
          {section.items.map((item, i) => (
            <li key={i} className="flex items-start gap-1.5 text-xs text-gray-600 leading-relaxed">
              <span className="text-gray-300 mt-0.5 shrink-0">•</span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
        {section.content != null && (
          <p className="text-xs text-gray-500 leading-relaxed">{safeContent(section.content)}</p>
        )}
      </div>
    )
  }

  // ── default: text / highlight / warning / complexity / test_cases / evaluation / design ──
  const contentText = safeContent(section.content)

  // warning gets a subtle left border, everything else is plain
  const isWarning = kind === 'warning'

  return (
    <div className={`space-y-1 ${isWarning ? 'border-l-2 border-amber-300 pl-3 py-0.5' : ''}`}>
      {heading && (
        <h4 className="text-xs font-semibold text-gray-700">{heading}</h4>
      )}
      {contentText && (
        <p className="text-xs text-gray-600 leading-relaxed whitespace-pre-line">
          {contentText}
        </p>
      )}
      {!contentText && section.items && section.items.length > 0 && (
        <ul className="space-y-0.5">
          {section.items.map((item, i) => (
            <li key={i} className="text-xs text-gray-600 leading-relaxed flex items-start gap-1.5">
              <span className="text-gray-300 mt-0.5 shrink-0">•</span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

// ========== Modal Component ==========

export default function ResourceDetailModal({
  resource,
  onClose,
  onSaveToPackage,
  savedToPackage,
}: ResourceDetailModalProps) {
  const [isFullscreen, setIsFullscreen] = useState(false)

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        if (isFullscreen) {
          setIsFullscreen(false)
        } else {
          onClose()
        }
      }
    },
    [onClose, isFullscreen],
  )

  useEffect(() => {
    if (resource) {
      document.addEventListener('keydown', handleKeyDown)
      document.body.style.overflow = 'hidden'
      return () => {
        document.removeEventListener('keydown', handleKeyDown)
        document.body.style.overflow = ''
      }
    }
  }, [resource, handleKeyDown])

  useEffect(() => {
    if (!resource) setIsFullscreen(false)
  }, [resource])

  const r = resource
  if (!r) return null

  const knowledgeTags: string[] = r.knowledge_points ?? (r.knowledge_point ? [r.knowledge_point] : [])
  const progLang = r.programming_language_used || r.language || ''
  const typeBadge = (() => {
    const colors: Record<string, string> = {
      '图解讲解': 'bg-purple-50 text-purple-700 border-purple-100',
      '代码示例': 'bg-emerald-50 text-emerald-700 border-emerald-100',
      '易错点':   'bg-amber-50 text-amber-700 border-amber-100',
      '分层练习': 'bg-blue-50 text-blue-700 border-blue-100',
      '项目案例': 'bg-rose-50 text-rose-700 border-rose-100',
    }
    return colors[r.type] ?? 'bg-gray-50 text-gray-600 border-gray-100'
  })()

  const hasFullSections = r.sections && r.sections.length > 0
  const hasFallbackContent = r.content || r.description || r.summary
  const summaryText = r.summary || r.description || ''

  return (
    <AnimatePresence>
      {resource && (
        <motion.div
          className="fixed inset-0 z-[60] flex items-center justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
        >
          {/* Backdrop */}
          <motion.div
            className="absolute inset-0 bg-black/40 backdrop-blur-sm"
            onClick={onClose}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          />

          {/* Modal container */}
          <motion.div
            className={
              isFullscreen
                ? 'fixed inset-2 z-10 bg-white rounded-2xl shadow-2xl flex flex-col overflow-hidden'
                : 'relative z-10 w-full max-w-3xl max-h-[85vh] mx-4 bg-white rounded-2xl shadow-2xl flex flex-col overflow-hidden'
            }
            initial={isFullscreen ? { opacity: 0 } : { opacity: 0, y: 24, scale: 0.97 }}
            animate={isFullscreen ? { opacity: 1 } : { opacity: 1, y: 0, scale: 1 }}
            exit={isFullscreen ? { opacity: 0 } : { opacity: 0, y: 24, scale: 0.97 }}
            transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
          >
            {/* ── Header ── */}
            <div className="shrink-0 px-6 py-4 border-b border-gray-100 flex items-start gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1.5">
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium border ${typeBadge}`}>
                    {r.type}
                  </span>
                  {r.estimated_time && (
                    <span className="flex items-center gap-1 text-[10px] text-gray-400">
                      <Clock className="w-3 h-3" />
                      {r.estimated_time}
                    </span>
                  )}
                  {r.difficulty && (
                    <span className="text-[10px] text-gray-400">{r.difficulty}</span>
                  )}
                </div>
                <h2 className="text-base font-bold text-gray-800 leading-snug mb-0.5">{r.title}</h2>
                <div className="flex items-center flex-wrap gap-x-3 gap-y-0.5 text-[10px] text-gray-400">
                  {r.related_module && <span>模块：{r.related_module}</span>}
                  {r.course && <span>课程：{r.course}</span>}
                  {progLang && <span>语言：{progLang}</span>}
                </div>
                {knowledgeTags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {knowledgeTags.slice(0, 6).map((kp) => (
                      <span key={kp} className="px-1.5 py-0.5 rounded-full bg-gray-100 text-[10px] text-gray-500">
                        {kp}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Action buttons */}
              <div className="flex items-center gap-1 shrink-0">
                <button
                  onClick={() => setIsFullscreen(!isFullscreen)}
                  className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-gray-100 transition-colors"
                  title={isFullscreen ? '退出全屏' : '全屏'}
                >
                  {isFullscreen ? (
                    <Minimize2 className="w-4 h-4 text-gray-500" />
                  ) : (
                    <Maximize2 className="w-4 h-4 text-gray-500" />
                  )}
                </button>
                <button
                  onClick={onClose}
                  className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-gray-100 transition-colors"
                  title="关闭"
                >
                  <X className="w-4 h-4 text-gray-500" />
                </button>
              </div>
            </div>

            {/* ── Body ── */}
            <div className="flex-1 overflow-y-auto px-6 py-5">
              {hasFullSections ? (
                <div className="space-y-4">
                  {/* Summary line */}
                  {summaryText && (
                    <p className="text-xs text-gray-500 leading-relaxed pb-3 border-b border-gray-100">
                      {summaryText}
                    </p>
                  )}

                  {/* Sections rendered in order — clean, unified style */}
                  {r.sections!.map((section, si) => (
                    <SectionBlock key={si} section={section} />
                  ))}
                </div>
              ) : hasFallbackContent ? (
                <div className="space-y-3">
                  {r.content && (
                    <p className="text-xs text-gray-600 leading-relaxed whitespace-pre-line">{r.content}</p>
                  )}
                  {r.description && !r.content && (
                    <p className="text-xs text-gray-600 leading-relaxed">{r.description}</p>
                  )}
                  {r.summary && !r.content && !r.description && (
                    <p className="text-xs text-gray-600 leading-relaxed">{r.summary}</p>
                  )}
                </div>
              ) : (
                <div className="flex items-center justify-center py-16">
                  <p className="text-sm text-gray-400">暂无完整内容</p>
                </div>
              )}
            </div>

            {/* ── Footer ── */}
            <div className="shrink-0 px-6 py-4 border-t border-gray-100 flex items-center gap-3">
              <div className="flex-1" />
              {onSaveToPackage && (
                <button
                  onClick={() => onSaveToPackage(r.id)}
                  className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-medium transition-all ${
                    savedToPackage
                      ? 'text-rose-600 border border-rose-200 hover:bg-rose-50'
                      : 'bg-gradient-to-r from-amber-400 to-amber-600 text-white hover:shadow-glow hover:-translate-y-0.5'
                  }`}
                >
                  {savedToPackage ? (
                    <>
                      <XCircle className="w-3.5 h-3.5" />
                      取消加入
                    </>
                  ) : (
                    <>
                      <Bookmark className="w-3.5 h-3.5" />
                      加入资源包
                    </>
                  )}
                </button>
              )}
              <button
                onClick={onClose}
                className="px-4 py-2 rounded-xl text-xs text-gray-500 border border-gray-200 hover:bg-gray-50 transition-colors"
              >
                关闭
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
