import { useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Sparkles } from 'lucide-react'

export interface Message {
  role: 'buddy' | 'user'
  content: string
}

interface ChatPanelProps {
  messages: Message[]
  onSend: (text: string) => void
  disabled?: boolean
  hint?: string
  currentRound: number
  totalRounds: number
}

export default function ChatPanel({ messages, onSend, disabled, hint, currentRound, totalRounds }: ChatPanelProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const val = inputRef.current?.value.trim()
    if (!val || disabled) return
    onSend(val)
    if (inputRef.current) inputRef.current.value = ''
  }

  return (
    <div className="flex flex-col h-full">
      {/* Round progress */}
      <div className="px-4 py-2 border-b border-gray-100 flex items-center justify-between">
        <span className="text-xs text-gray-400">
          对话进度 {Math.min(currentRound + 1, totalRounds)} / {totalRounds}
        </span>
        <div className="flex gap-1">
          {Array.from({ length: totalRounds }).map((_, i) => (
            <div
              key={i}
              className={`w-5 h-1 rounded-full transition-colors ${
                i <= currentRound ? 'bg-primary-400' : 'bg-gray-200'
              }`}
            />
          ))}
        </div>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-3 space-y-3 min-h-[280px] max-h-[400px]">
        <AnimatePresence>
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              {msg.role === 'buddy' ? (
                <div className="flex items-start gap-2 max-w-[85%]">
                  <div className="w-7 h-7 rounded-full bg-gradient-to-br from-primary-400 to-purple-500 flex items-center justify-center shrink-0 mt-0.5">
                    <Sparkles className="w-3.5 h-3.5 text-white" />
                  </div>
                  <div className="bg-gray-50 rounded-2xl rounded-tl-md px-3.5 py-2.5">
                    <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">{msg.content}</p>
                  </div>
                </div>
              ) : (
                <div className="bg-primary-500 rounded-2xl rounded-tr-md px-3.5 py-2.5 max-w-[80%]">
                  <p className="text-sm text-white leading-relaxed">{msg.content}</p>
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Hint */}
      {hint && (
        <div className="px-4 pb-1">
          <p className="text-[11px] text-gray-400">{hint}</p>
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="px-4 py-3 border-t border-gray-100">
        <div className="flex items-center gap-2">
          <input
            ref={inputRef}
            type="text"
            placeholder={disabled ? '请等待...' : '输入你的回答...'}
            disabled={disabled}
            className="flex-1 text-sm px-3.5 py-2.5 rounded-xl border border-gray-200 focus:outline-none focus:border-primary-300 focus:ring-1 focus:ring-primary-200 bg-gray-50 placeholder:text-gray-400 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={disabled}
            className="shrink-0 w-9 h-9 rounded-xl bg-primary-500 text-white flex items-center justify-center hover:bg-primary-600 transition-colors disabled:opacity-40"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  )
}
