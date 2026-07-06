import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  X, Maximize2, Minimize2, Clock, Lightbulb, Bookmark, XCircle,
  Zap, ListOrdered, Code, AlertTriangle, CheckCircle2, GitCompare,
  HelpCircle, FileText, Minus, Layers,
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

// ========== Section kind config ==========

interface KindConfig {
  icon: React.ComponentType<{ className?: string }>
  bg: string
  border: string
  text: string
  defaultHeading: string
}

const kindConfigMap: Record<string, KindConfig> = {
  highlight:  { icon: Zap,            bg: 'bg-primary-50/60',  border: 'border-primary-200/60', text: 'text-primary-800',  defaultHeading: '重点' },
  steps:      { icon: ListOrdered,    bg: 'bg-white',          border: 'border-gray-150',       text: 'text-gray-700',     defaultHeading: '步骤' },
  code:       { icon: Code,           bg: 'bg-gray-900',       border: 'border-gray-800',       text: 'text-green-300',    defaultHeading: '代码' },
  warning:    { icon: AlertTriangle,  bg: 'bg-amber-50/70',    border: 'border-amber-200',      text: 'text-amber-800',    defaultHeading: '易错提醒' },
  practice:   { icon: CheckCircle2,   bg: 'bg-emerald-50/50',  border: 'border-emerald-200',    text: 'text-emerald-800',  defaultHeading: '练习' },
  compare:    { icon: GitCompare,     bg: 'bg-indigo-50/50',   border: 'border-indigo-200',     text: 'text-indigo-800',   defaultHeading: '对比' },
  answer_hint:{ icon: HelpCircle,     bg: 'bg-cyan-50/50',     border: 'border-cyan-200',       text: 'text-cyan-800',     defaultHeading: '答案提示' },
  task:       { icon: FileText,       bg: 'bg-orange-50/50',   border: 'border-orange-200',     text: 'text-orange-800',   defaultHeading: '任务要求' },
  complexity: { icon: Layers,         bg: 'bg-violet-50/50',   border: 'border-violet-200',     text: 'text-violet-800',   defaultHeading: '复杂度分析' },
  text:       { icon: FileText,       bg: 'bg-white',          border: 'border-gray-100',       text: 'text-gray-600',     defaultHeading: '' },
  divider:    { icon: Minus,          bg: 'bg-transparent',    border: 'border-transparent',    text: 'text-gray-300',     defaultHeading: '' },
}

const fallbackKindConfig: KindConfig = {
  icon: FileText, bg: 'bg-white', border: 'border-gray-100', text: 'text-gray-600', defaultHeading: '',
}

// ========== Section Renderer ==========

function SectionBlock({ section }: { section: ResourceSection }) {
  const kind = (section.kind || 'text').toLowerCase()
  const config = kindConfigMap[kind] ?? fallbackKindConfig
  const Icon = config.icon
  const heading = section.heading || section.title || config.defaultHeading

  // ── divider ──
  if (kind === 'divider') {
    return <hr className="my-3 border-gray-200" />
  }

  // ── code ──
  if (kind === 'code') {
    const label = langLabel(section.language)
    const codeText = safeContent(section.content)
    return (
      <div className="space-y-1.5">
        <div className="flex items-center gap-2">
          {heading && (
            <div className="flex items-center gap-1.5">
              <Icon className="w-3.5 h-3.5 text-gray-500" />
              <span className="text-xs font-semibold text-gray-600">{heading}</span>
            </div>
          )}
          {label && (
            <span className="px-1.5 py-0.5 rounded text-[10px] font-medium bg-gray-200 text-gray-500">
              {label} 示例
            </span>
          )}
        </div>
        <div className={`rounded-xl p-4 ${config.bg} border ${config.border} overflow-x-auto`}>
          <pre className={`text-xs leading-relaxed font-mono whitespace-pre ${config.text}`}>
            {codeText}
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
      <div className="space-y-2">
        {heading && (
          <div className="flex items-center gap-1.5">
            <Icon className="w-3.5 h-3.5 text-gray-500" />
            <span className="text-xs font-semibold text-gray-600">{heading}</span>
          </div>
        )}
        <div className="space-y-1.5">
          {stepItems.map((item, i) => (
            <div key={i} className="flex items-start gap-2">
              <span className="w-5 h-5 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5">
                {i + 1}
              </span>
              <span className="text-xs text-gray-600 leading-relaxed">{item}</span>
            </div>
          ))}
        </div>
      </div>
    )
  }

  // ── practice / compare (with items) ──
  if ((kind === 'practice' || kind === 'compare') && section.items && section.items.length > 0) {
    return (
      <div className={`rounded-xl p-4 ${config.bg} border ${config.border} space-y-2`}>
        {heading && (
          <div className="flex items-center gap-1.5">
            <Icon className="w-3.5 h-3.5" />
            <span className={`text-xs font-semibold ${config.text}`}>{heading}</span>
          </div>
        )}
        <ul className="space-y-1.5">
          {section.items.map((item, i) => (
            <li key={i} className="flex items-start gap-2">
              {kind === 'practice' ? (
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
              ) : (
                <span className="w-1 h-1 rounded-full bg-indigo-400 shrink-0 mt-2" />
              )}
              <span className="text-xs text-gray-600 leading-relaxed">{item}</span>
            </li>
          ))}
        </ul>
        {section.content != null && (
          <p className={`text-xs ${config.text} leading-relaxed`}>{safeContent(section.content)}</p>
        )}
      </div>
    )
  }

  // ── default: highlight / warning / answer_hint / task / complexity / text / unknown ──
  const contentText = safeContent(section.content)
  return (
    <div className={`rounded-xl p-4 ${config.bg} border ${config.border} space-y-1.5`}>
      {heading && (
        <div className="flex items-center gap-1.5">
          <Icon className="w-3.5 h-3.5" />
          <span className={`text-xs font-semibold ${config.text}`}>{heading}</span>
        </div>
      )}
      {contentText && (
        <p className={`text-xs ${config.text} opacity-90 leading-relaxed whitespace-pre-line`}>
          {contentText}
        </p>
      )}
      {!contentText && section.items && section.items.length > 0 && (
        <ul className="space-y-1">
          {section.items.map((item, i) => (
            <li key={i} className="text-xs leading-relaxed opacity-90" style={{ color: 'inherit' }}>
              {item}
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

  // ESC key handler
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

  // Reset fullscreen on close
  useEffect(() => {
    if (!resource) setIsFullscreen(false)
  }, [resource])

  const r = resource
  if (!r) return null

  const highlightSection = r.sections?.find((s) => (s.kind || '').toLowerCase() === 'highlight')
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
            {/* ── Header bar (sticky) ── */}
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
                <h2 className="text-base font-bold text-gray-800 leading-snug mb-1">{r.title}</h2>
                <div className="flex items-center flex-wrap gap-x-3 gap-y-0.5 text-[10px] text-gray-400">
                  {r.related_module && <span>模块：{r.related_module}</span>}
                  {r.course && <span>课程：{r.course}</span>}
                  {progLang && <span>语言：{progLang}</span>}
                </div>
                {knowledgeTags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {knowledgeTags.slice(0, 6).map((kp) => (
                      <span key={kp} className="px-1.5 py-0.5 rounded-full bg-primary-50 text-[10px] text-primary-600 border border-primary-100">
                        {kp}
                      </span>
                    ))}
                  </div>
                )}
                {r.personalized_reason && (
                  <div className="flex items-start gap-1.5 mt-2">
                    <Lightbulb className="w-3 h-3 text-primary-400 shrink-0 mt-0.5" />
                    <p className="text-[11px] text-primary-600/70 leading-relaxed italic">
                      {r.personalized_reason}
                    </p>
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

            {/* ── Scrollable body ── */}
            <div className="flex-1 overflow-y-auto px-6 py-5 space-y-3">
              {hasFullSections ? (
                r.sections!.map((section, i) => <SectionBlock key={i} section={section} />)
              ) : hasFallbackContent ? (
                <div className="space-y-3">
                  {r.content && (
                    <div className="rounded-xl p-4 bg-white border border-gray-100">
                      <p className="text-sm text-gray-600 leading-relaxed whitespace-pre-line">{r.content}</p>
                    </div>
                  )}
                  {r.description && !r.content && (
                    <div className="rounded-xl p-4 bg-white border border-gray-100">
                      <p className="text-sm text-gray-600 leading-relaxed">{r.description}</p>
                    </div>
                  )}
                  {r.summary && !r.content && !r.description && (
                    <div className="rounded-xl p-4 bg-white border border-gray-100">
                      <p className="text-sm text-gray-600 leading-relaxed">{r.summary}</p>
                    </div>
                  )}
                  {r.next_action && (
                    <div className="flex items-start gap-2 px-4 py-3 rounded-xl bg-purple-50 border border-purple-100">
                      <Lightbulb className="w-4 h-4 text-purple-500 shrink-0 mt-0.5" />
                      <div>
                        <p className="text-xs font-semibold text-purple-700 mb-0.5">下一步行动</p>
                        <p className="text-xs text-purple-600">{r.next_action}</p>
                      </div>
                    </div>
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
              {r.next_action && hasFullSections && (
                <p className="flex-1 text-[11px] text-purple-600 truncate">
                  下一步：{r.next_action}
                </p>
              )}
              {(!r.next_action || !hasFullSections) && <div className="flex-1" />}
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
