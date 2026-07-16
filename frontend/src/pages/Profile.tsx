import { useState, useCallback, useEffect, useRef } from 'react'
import { UserRound } from 'lucide-react'
import { AnimatePresence, motion } from 'framer-motion'
import CodeBuddyAvatar from '../components/profile/CodeBuddyAvatar'
import ChatPanel from '../components/profile/ChatPanel'
import LearningProfileCard from '../components/profile/LearningProfileCard'
import { profileChat } from '../services/api'
import {
  createInitialState,
  processMessage,
  persistState,
  generateFinalProfileMock,
  PROFILE_STORAGE_VERSION,
  draftValueToText,
  hasDraftValue,
  draftValueToList,
  type InterviewState,
  type InterviewStage,
} from '../services/profileInterview'

const CURRENT_USER_ID = 1
const QUICK_PROFILE_KEY = 'codemate_resource_quick_profile'

type BuddyState = 'welcome' | 'thinking' | 'generating'

export default function Profile() {
  const [state, setState] = useState<InterviewState>(() => createInitialState())
  const [buddyState, setBuddyState] = useState<BuddyState>('welcome')
  const initializedRef = useRef(false)

  // Persist on every state change
  useEffect(() => {
    if (initializedRef.current) {
      persistState(state)
    } else {
      initializedRef.current = true
    }
  }, [state])

  // Chat is active for all stages except complete
  const isChatActive = state.stage !== 'complete'

  // ---- Handlers ----

  const handleSend = useCallback(async (text: string) => {
    if (!isChatActive) return

    setBuddyState('thinking')

    try {
      const history = state.messages.map((m) => ({
        role: m.role === 'buddy' ? 'assistant' : m.role,
        content: m.content,
      }))

      const response = await profileChat(
        text,
        history,
        { ...state.profileDraft },
        state.stage,
      )

      // Extract reply from either 'reply' or 'message' field
      const reply =
        (typeof response.reply === 'string' && response.reply) ||
        (typeof response.message === 'string' && response.message) ||
        ''

      // Extract profile from response
      const responseProfile =
        (response.profile && typeof response.profile === 'object' ? response.profile as Record<string, unknown> : null) ||
        (response.extracted_fields && typeof response.extracted_fields === 'object' ? response.extracted_fields as Record<string, unknown> : null) ||
        {}

      const responseStage = (typeof response.stage === 'string' ? response.stage : null) as InterviewStage | null
      const missing = Array.isArray(response.missing_fields) ? response.missing_fields : []

      if (!reply) {
        throw new Error('Empty reply in chat response')
      }

      setState((prev) => {
        // Merge profile
        const mergedProfile: Record<string, unknown> = { ...prev.profileDraft }
        for (const [key, value] of Object.entries(responseProfile)) {
          if (typeof value === 'string' && value.trim()) {
            mergedProfile[key] = value
          }
        }

        const newMessages = [
          ...prev.messages,
          { role: 'user' as const, content: text },
          { role: 'buddy' as const, content: reply },
        ]

        const newStage = responseStage || prev.stage

        return {
          messages: newMessages,
          profileDraft: mergedProfile,
          missingFields: missing.length > 0 ? missing : prev.missingFields,
          stage: newStage,
        }
      })
    } catch {
      console.warn('Backend /api/profile/chat unavailable — using local mock')
      // Use local state machine directly
      setState((prev) => {
        const newState = processMessage(prev, text)
        return newState
      })
    }

    setBuddyState('welcome')
  }, [isChatActive, state.messages, state.profileDraft, state.stage])

  const handleReset = useCallback(() => {
    // Clear localStorage cache and restart
    try {
      localStorage.removeItem('codemate_profile_messages')
      localStorage.removeItem('codemate_profile_draft')
      localStorage.removeItem('codemate_profile_stage')
      localStorage.removeItem('codemate_profile_version')
    } catch { /* ignore */ }
    setState(createInitialState())
  }, [])

  const handleGenerateProfile = useCallback(() => {
    setBuddyState('generating')
    setTimeout(() => {
      setState((prev) => {
        const finalProfile = generateFinalProfileMock(prev.profileDraft)

        // Save quick_profile to sessionStorage
        try {
          const qp = {
            programming_language: prev.profileDraft.programming_language || undefined,
            learning_goal: prev.profileDraft.learning_goal || undefined,
            foundation_level: prev.profileDraft.foundation_level || undefined,
            current_difficulties: draftValueToList(prev.profileDraft.current_difficulties),
            expression_preferences: draftValueToList(prev.profileDraft.expression_preferences),
          }
          sessionStorage.setItem(QUICK_PROFILE_KEY, JSON.stringify(qp))
        } catch { /* ignore */ }

        return {
          ...prev,
          stage: 'complete' as InterviewStage,
          messages: [
            ...prev.messages,
            { role: 'buddy' as const, content: '你的学习画像已经生成好啦！以下是基于我们对话的综合评估。你可以基于此画像生成个性化资源，或者规划专属学习路径。' },
          ],
        }
      })
      setBuddyState('welcome')
    }, 600)
  }, [])

  // ---- Render ----

  const buddyStateForAvatar: BuddyState =
    state.stage === 'complete' ? 'generating' : buddyState

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex items-center gap-2">
        <UserRound className="w-6 h-6 text-primary-600" />
        <div>
          <h1 className="text-2xl font-bold text-gray-900">数据结构与算法学习画像</h1>
        </div>
      </div>

      <AnimatePresence mode="wait">
        {state.stage !== 'complete' ? (
          /* ===== Chat Phase ===== */
          <motion.div
            key="build-phase"
            className="grid grid-cols-12 gap-6"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            {/* Left: CodeBuddy + Chat */}
            <div className="col-span-7 space-y-4">
              {/* CodeBuddy Avatar */}
              <div className="bg-white rounded-2xl shadow-card border border-gray-100 p-5">
                <CodeBuddyAvatar state={buddyStateForAvatar} />
              </div>

              {/* Chat */}
              <div className="bg-white rounded-2xl shadow-card border border-gray-100 overflow-hidden">
                <ChatPanel
                  messages={state.messages}
                  onSend={handleSend}
                  disabled={!isChatActive}
                  hint={
                    state.stage === 'summary'
                      ? '画像基本完成，可以继续补充或查看摘要'
                      : undefined
                  }
                  currentRound={Object.keys(state.profileDraft).filter(k => hasDraftValue(state.profileDraft[k])).length}
                  totalRounds={7}
                />
              </div>
            </div>

            {/* Right: Profile Draft */}
            <div className="col-span-5 space-y-4">
              <div className="rounded-2xl bg-white border border-gray-100 p-4">
                <h3 className="text-sm font-semibold text-gray-800 mb-3">学习画像草稿</h3>

                {Object.keys(state.profileDraft).length === 0 || !Object.values(state.profileDraft).some(hasDraftValue) ? (
                  <p className="text-xs text-gray-400">开始对话后，这里会逐步显示你的学习画像</p>
                ) : (
                  <div className="space-y-2">
                    {hasDraftValue(state.profileDraft.programming_language) && (
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-gray-500 w-20 shrink-0">编程语言</span>
                        <span className="px-1.5 py-0.5 bg-primary-50 text-primary-600 text-[10px] rounded-full">{draftValueToText(state.profileDraft.programming_language)}</span>
                      </div>
                    )}
                    {hasDraftValue(state.profileDraft.learning_goal) && (
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-gray-500 w-20 shrink-0">学习目标</span>
                        <span className="text-xs text-gray-700">{draftValueToText(state.profileDraft.learning_goal)}</span>
                      </div>
                    )}
                    {hasDraftValue(state.profileDraft.foundation_level) && (
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-gray-500 w-20 shrink-0">基础水平</span>
                        <span className="text-xs text-gray-700">{draftValueToText(state.profileDraft.foundation_level)}</span>
                      </div>
                    )}
                    {hasDraftValue(state.profileDraft.current_difficulties) && (
                      <div className="flex items-start gap-2">
                        <span className="text-xs text-gray-500 w-20 shrink-0 mt-0.5">薄弱模块</span>
                        <div className="flex flex-wrap gap-1">
                          {draftValueToList(state.profileDraft.current_difficulties).map(t => (
                            <span key={t} className="px-1.5 py-0.5 bg-purple-50 text-purple-600 text-[10px] rounded-full">{t}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    {hasDraftValue(state.profileDraft.expression_preferences) && (
                      <div className="flex items-start gap-2">
                        <span className="text-xs text-gray-500 w-20 shrink-0 mt-0.5">资源偏好</span>
                        <div className="flex flex-wrap gap-1">
                          {draftValueToList(state.profileDraft.expression_preferences).map(t => (
                            <span key={t} className="px-1.5 py-0.5 bg-blue-50 text-blue-600 text-[10px] rounded-full">{t}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    {hasDraftValue(state.profileDraft.error_prone_points) && (
                      <div className="flex items-start gap-2">
                        <span className="text-xs text-gray-500 w-20 shrink-0 mt-0.5">易错点</span>
                        <div className="flex flex-wrap gap-1">
                          {draftValueToList(state.profileDraft.error_prone_points).map(t => (
                            <span key={t} className="px-1.5 py-0.5 bg-orange-50 text-orange-600 text-[10px] rounded-full">{t}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    {hasDraftValue(state.profileDraft.learned_courses) && (
                      <div className="flex items-start gap-2">
                        <span className="text-xs text-gray-500 w-20 shrink-0 mt-0.5">先修课程</span>
                        <div className="flex flex-wrap gap-1">
                          {draftValueToList(state.profileDraft.learned_courses).map(t => (
                            <span key={t} className="px-1.5 py-0.5 bg-green-50 text-green-600 text-[10px] rounded-full">{t}</span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Generate profile button when summary stage */}
                    {state.stage === 'summary' && (
                      <button
                        onClick={handleGenerateProfile}
                        className="mt-3 w-full py-2 rounded-xl bg-primary-500 text-white text-sm font-medium hover:bg-primary-600 transition-colors"
                      >
                        生成完整学习画像
                      </button>
                    )}
                  </div>
                )}
              </div>

              {/* Missing fields hint */}
              {state.missingFields.length > 0 && (
                <div className="rounded-2xl bg-white border border-gray-100 p-4">
                  <h3 className="text-xs font-semibold text-gray-500 mb-2">待收集信息</h3>
                  <div className="flex flex-wrap gap-1">
                    {state.missingFields.map(f => {
                      const labelMap: Record<string, string> = {
                        programming_language: '编程语言',
                        learning_goal: '学习目标',
                        foundation_level: '基础水平',
                        current_difficulties: '薄弱模块',
                        expression_preferences: '资源偏好',
                        learned_courses: '先修课程',
                        error_prone_points: '易错点',
                      }
                      return (
                        <span key={f} className="px-2 py-0.5 bg-gray-100 text-gray-500 text-[10px] rounded-full">
                          {labelMap[f] || f}
                        </span>
                      )
                    })}
                  </div>
                </div>
              )}

              {/* Reset button */}
              <button
                onClick={handleReset}
                className="w-full py-2 text-xs text-gray-400 hover:text-gray-600 transition-colors"
              >
                重新开始对话
              </button>
            </div>
          </motion.div>
        ) : (
          /* ===== Profile Display Phase ===== */
          <motion.div
            key="profile-phase"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="space-y-4"
          >
            <LearningProfileCard
              profile={generateFinalProfileMock(state.profileDraft)}
            />
            <div className="flex justify-center gap-3">
              <button
                onClick={handleReset}
                className="px-6 py-2.5 rounded-xl border border-primary-300 text-primary-600 text-sm font-medium hover:bg-primary-50 transition-colors"
              >
                重新对话
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
