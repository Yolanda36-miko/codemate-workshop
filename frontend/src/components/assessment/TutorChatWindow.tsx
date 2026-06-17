import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Sparkles, Code, BookOpen, Lightbulb, MessageCircle } from 'lucide-react'
import type { TutorChatResponse, ConversationContext, PathNode } from '../../types'
import { getTutorResponse, getContextualExampleQuestions, inferConversationContextMock } from '../../mock/assessment'
import SuggestedQuestions from './SuggestedQuestions'

interface TutorChatWindowProps {
  onQuestionAsked: (question: string) => void
  onViewResource: (resource: { title: string; type: string; estimatedTime: string; topic: string }) => void
  pathNodes?: PathNode[]
}

interface ChatMessage {
  id: number
  role: 'user' | 'buddy'
  content: string
  tutorResponse?: TutorChatResponse
}

export default function TutorChatWindow({ onQuestionAsked, onViewResource, pathNodes }: TutorChatWindowProps) {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [context, setContext] = useState<ConversationContext>(() => inferConversationContextMock('', pathNodes))
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const msgIdRef = useRef(0)

  const exampleQuestions = getContextualExampleQuestions(context)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = (question?: string) => {
    const q = (question || input).trim()
    if (!q) return

    // Update context based on user question + learning path
    const newContext = inferConversationContextMock(q, pathNodes)
    setContext(newContext)
    onQuestionAsked(q)

    const id = ++msgIdRef.current
    const response = getTutorResponse(q)

    setMessages((prev) => [...prev, { id, role: 'user', content: q }])

    setTimeout(() => {
      setMessages((prev) => [...prev, { id: id + 0.5, role: 'buddy', content: '', tutorResponse: response }])
    }, 400)

    if (!question) setInput('')
  }

  const handleSuggestedQuestion = (q: string) => {
    setInput(q)
    handleSend(q)
  }

  return (
    <div className="bg-white rounded-2xl shadow-card border border-gray-100 overflow-hidden flex flex-col" style={{ height: 'calc(100vh - 160px)', minHeight: '520px' }}>
      {/* Top bar */}
      <div className="px-4 py-3 border-b border-gray-50 shrink-0 space-y-2">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary-400 to-purple-500 flex items-center justify-center ring-2 ring-primary-100">
            <Sparkles className="w-4.5 h-4.5 text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-gray-800">CodeBuddy 智能辅导</p>
            <p className="text-[10px] text-gray-400 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-green-400 inline-block" />
              在线 · 智能辅导中
            </p>
          </div>
        </div>

      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-50 to-purple-50 flex items-center justify-center mx-auto mb-3">
              <MessageCircle className="w-6 h-6 text-primary-400" />
            </div>
            <p className="text-xs text-gray-500 mb-4">开始向 CodeBuddy 提问吧！</p>
            <SuggestedQuestions questions={exampleQuestions} onSelect={handleSuggestedQuestion} />
          </div>
        )}

        <AnimatePresence>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 12, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
              className={`flex gap-2.5 ${msg.role === 'user' ? 'justify-end' : ''}`}
            >
              {msg.role === 'buddy' && (
                <div className="w-7 h-7 rounded-full bg-gradient-to-br from-primary-400 to-purple-500 flex items-center justify-center shrink-0 mt-0.5">
                  <Sparkles className="w-3.5 h-3.5 text-white" />
                </div>
              )}

              {msg.role === 'user' ? (
                <div className="max-w-[80%] px-4 py-2.5 rounded-2xl rounded-br-md bg-gradient-to-r from-primary-500 to-purple-600 text-white">
                  <p className="text-xs leading-relaxed">{msg.content}</p>
                </div>
              ) : msg.tutorResponse ? (
                <div className="flex-1 min-w-0 space-y-2.5">
                  <div className="bg-gray-50 rounded-2xl rounded-bl-md px-4 py-3 border border-gray-100">
                    <p className="text-xs text-gray-700 leading-relaxed">{msg.tutorResponse.greeting}</p>
                    <p className="text-[11px] text-primary-500 italic mt-1">{msg.tutorResponse.approach}</p>
                  </div>

                  <div className="bg-white rounded-xl px-4 py-3 border border-primary-100">
                    <div className="flex items-center gap-1.5 mb-2">
                      <Lightbulb className="w-3.5 h-3.5 text-amber-500" />
                      <span className="text-[11px] font-medium text-gray-700">分步讲解</span>
                    </div>
                    <ol className="space-y-2">
                      {msg.tutorResponse.steps.map((s, i) => (
                        <li key={i} className="text-[11px] text-gray-600 flex gap-1.5 leading-relaxed">
                          <span className="text-primary-500 font-medium shrink-0">{i + 1}.</span>
                          {s}
                        </li>
                      ))}
                    </ol>
                  </div>

                  {msg.tutorResponse.code_example && (
                    <div className="bg-gray-900 rounded-xl px-3 py-2.5 overflow-x-auto">
                      <div className="flex items-center gap-1.5 mb-1.5">
                        <Code className="w-3 h-3 text-gray-400" />
                        <span className="text-[10px] text-gray-400">Python</span>
                      </div>
                      <pre className="text-[10px] text-green-400 leading-relaxed whitespace-pre">{msg.tutorResponse.code_example}</pre>
                    </div>
                  )}

                  {msg.tutorResponse.recommended_resources.length > 0 && (
                    <div>
                      <div className="flex items-center gap-1.5 mb-1.5">
                        <BookOpen className="w-3 h-3 text-primary-500" />
                        <span className="text-[10px] text-gray-500">推荐资源</span>
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {msg.tutorResponse.recommended_resources.map((res) => (
                          <button
                            key={res.title}
                            onClick={() => onViewResource({
                              title: res.title,
                              type: res.title.includes('思维导图') ? '知识点思维导图' : res.title.includes('代码') ? '代码示例与注释' : res.title.includes('练习') ? '分层练习题' : '个性化讲解文档',
                              estimatedTime: '20 分钟',
                              topic: context.pathNode,
                            })}
                            className="px-2 py-1 rounded-lg text-[10px] bg-white border border-primary-200 text-primary-600 hover:bg-primary-50 transition-colors text-left"
                          >
                            {res.title}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {msg.tutorResponse.suggested_exercise && (
                    <div className="bg-amber-50 rounded-xl px-3 py-2.5 border border-amber-100">
                      <div className="flex items-center gap-1.5 mb-1">
                        <Lightbulb className="w-3.5 h-3.5 text-amber-500" />
                        <span className="text-[10px] font-medium text-amber-800">小练习</span>
                      </div>
                      <p className="text-[11px] text-amber-700 leading-relaxed">{msg.tutorResponse.suggested_exercise}</p>
                    </div>
                  )}
                </div>
              ) : null}

              {msg.role === 'user' && (
                <div className="w-7 h-7 rounded-full bg-gray-200 flex items-center justify-center shrink-0 mt-0.5">
                  <span className="text-[10px] text-gray-500 font-medium">你</span>
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {messages.length > 0 && (
          <div className="pt-2">
            <SuggestedQuestions questions={exampleQuestions} onSelect={handleSuggestedQuestion} />
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="px-4 py-3 border-t border-gray-50 flex gap-2 shrink-0">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="输入你的问题..."
          className="flex-1 rounded-xl border border-gray-200 px-3 py-2 text-xs focus:outline-none focus:ring-2 focus:ring-primary-200 bg-gray-50 placeholder:text-gray-300"
        />
        <button
          onClick={() => handleSend()}
          disabled={!input.trim()}
          className="px-3.5 py-2 rounded-xl bg-gradient-to-r from-primary-500 to-purple-600 text-white text-xs font-medium hover:from-primary-600 hover:to-purple-700 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1.5 shrink-0"
        >
          <Send className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  )
}
