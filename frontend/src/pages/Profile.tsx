import { useState, useCallback, useEffect, useRef } from 'react'
import { UserRound } from 'lucide-react'
import { AnimatePresence, motion } from 'framer-motion'
import CodeBuddyAvatar from '../components/profile/CodeBuddyAvatar'
import ChatPanel from '../components/profile/ChatPanel'
import ProfileDraftPanel from '../components/profile/ProfileDraftPanel'
import DiagnosisQuiz from '../components/profile/DiagnosisQuiz'
import LearningProfileCard from '../components/profile/LearningProfileCard'
import { isDemoMode } from '../config/appConfig'
import { profileChat, getUserProfile, updateUserProfile } from '../services/api'
import {
  createInitialState,
  processMessage,
  startDiagnosis,
  submitDiagnosis,
  generateProfile,
  applyDemoFill,
  ALL_FIELDS,
  isProfileComplete,
  mapBackendProfileToStudentProfile,
  mapStudentProfileToBackend,
  type InterviewState,
} from '../services/profileInterview'

const CURRENT_USER_ID = 1 // MVP: single-user mode

type BuddyState = 'welcome' | 'thinking' | 'generating'

export default function Profile() {
  const [state, setState] = useState<InterviewState>(createInitialState)
  const [buddyState, setBuddyState] = useState<BuddyState>('welcome')
  const [diagnosisAnswers, setDiagnosisAnswers] = useState<Record<string, string>>({})
  const [existingProfile, setExistingProfile] = useState<import('../types').StudentProfile | null>(null)
  const profileLoaded = useRef(false)

  const conversationFields = ALL_FIELDS.filter((f) => f.key !== 'diagnosis_result').map((f) => f.key)
  const collectedConvFields = conversationFields.filter((k) => k in state.collectedFields)
  const missingConvFields = conversationFields.filter((k) => !(k in state.collectedFields))

  const isChatActive = state.stage === 'collecting' || state.stage === 'greeting'
  const demoMode = isDemoMode()
  const showDemoBtn = demoMode && state.stage === 'collecting' && Object.keys(state.collectedFields).length === 0

  // ---- Load existing profile on mount ----

  useEffect(() => {
    if (profileLoaded.current) return
    profileLoaded.current = true

    const loadProfile = async () => {
      try {
        const backend = await getUserProfile(CURRENT_USER_ID)
        if (backend && isProfileComplete(backend)) {
          const mapped = mapBackendProfileToStudentProfile(backend)
          // Store for right-panel display — do NOT change stage
          setExistingProfile(mapped)
        }
      } catch {
        // Backend unavailable — stay on interview flow (local mock)
      }
    }
    loadProfile()
  }, [])

  // ---- Handlers ----

  const handleSend = useCallback(async (text: string) => {
    if (!isChatActive) return

    setBuddyState('thinking')

    try {
      // Build history from current messages
      const history = state.messages.map((m) => ({ role: m.role, content: m.content }))
      const response = await profileChat(text, history)

      // Strict field validation
      const msg = typeof response.message === 'string' ? response.message : ''
      const extracted = typeof response.extracted_fields === 'object' && response.extracted_fields !== null
        ? response.extracted_fields as Record<string, unknown>
        : {}
      const missing = Array.isArray(response.missing_fields) ? response.missing_fields : []

      if (!msg) {
        throw new Error('Empty message in chat response')
      }

      setState((prev) => {
        const newMessages = [
          ...prev.messages,
          { role: 'user' as const, content: text },
          { role: 'buddy' as const, content: msg },
        ]

        // Merge extracted fields
        const collected: Record<string, string> = { ...prev.collectedFields }
        for (const [key, value] of Object.entries(extracted)) {
          if (typeof value === 'string') {
            collected[key] = value
          }
        }

        const newMissing = missing.length > 0 ? missing : prev.missingFields.filter(
          (f) => !(f in collected)
        )
        const newStage = newMissing.length === 0 ? 'ready_for_diagnosis' : 'collecting'

        return {
          ...prev,
          messages: newMessages,
          collectedFields: collected,
          missingFields: newMissing,
          stage: newStage,
        }
      })
    } catch {
      // Fallback to local mock
      console.warn('Backend /api/profile/chat unavailable — using local mock')
      setTimeout(() => {
        setState((prev) => processMessage(prev, text))
      }, 800)
    }

    setBuddyState('welcome')
  }, [isChatActive, state.messages])

  const handleDemoFill = useCallback(() => {
    setBuddyState('thinking')
    setTimeout(() => {
      setState((prev) => applyDemoFill(prev))
      setBuddyState('welcome')
    }, 500)
  }, [])

  const handleStartDiagnosis = useCallback(() => {
    setState((prev) => startDiagnosis(prev))
  }, [])

  const handleDiagnosisSubmit = useCallback((answers: Record<string, string>) => {
    setDiagnosisAnswers(answers)
    setBuddyState('generating')
    setTimeout(() => {
      setState((prev) => submitDiagnosis(prev, answers))
      setBuddyState('welcome')
    }, 600)
  }, [])

  const handleGenerateProfile = useCallback(() => {
    setBuddyState('generating')
    setTimeout(() => {
      setState((prev) => {
        const newState = generateProfile(prev)

        // Save to backend (non-blocking, fire-and-forget)
        if (newState.finalProfile) {
          const payload = mapStudentProfileToBackend(newState.finalProfile)
          updateUserProfile(CURRENT_USER_ID, payload).catch(() => {
            console.warn('Failed to save profile to backend')
          })
        }

        return newState
      })
      setBuddyState('welcome')
    }, 1500)
  }, [])

  // ---- Render ----

  const buddyStateForAvatar: BuddyState =
    state.stage === 'generating' ? 'generating' : buddyState

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex items-center gap-2">
        <UserRound className="w-6 h-6 text-primary-600" />
        <h1 className="text-2xl font-bold text-gray-900">学习画像</h1>
      </div>

      <AnimatePresence mode="wait">
        {state.stage !== 'complete' ? (
          /* ===== Chat / Diagnosis Phase ===== */
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
                {showDemoBtn && (
                  <motion.button
                    onClick={handleDemoFill}
                    className="mt-3 w-full py-2 rounded-xl border border-dashed border-primary-300 text-primary-500 text-xs font-medium hover:bg-primary-50 transition-colors"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5 }}
                  >
                    使用示例数据快速填充 →
                  </motion.button>
                )}
              </div>

              {/* Chat or Diagnosis */}
              <div className="bg-white rounded-2xl shadow-card border border-gray-100 overflow-hidden">
                {state.stage === 'diagnosis' ? (
                  <div className="p-4">
                    <p className="text-sm font-semibold text-gray-800 mb-1">轻量诊断题</p>
                    <p className="text-xs text-gray-400 mb-4">
                      回答以下 {state.diagnosisQuestions.length} 道题，帮助 CodeBuddy 更准确地了解你的知识基础
                    </p>
                    <DiagnosisQuiz
                      questions={state.diagnosisQuestions}
                      onSubmit={handleDiagnosisSubmit}
                      submitted={state.diagnosisEvaluated}
                      userAnswers={diagnosisAnswers}
                    />
                  </div>
                ) : (
                  <ChatPanel
                    messages={state.messages}
                    onSend={handleSend}
                    disabled={!isChatActive}
                    hint={
                      state.stage === 'ready_for_diagnosis'
                        ? '点击右侧「进入诊断题」继续'
                        : state.stage === 'ready_for_profile'
                          ? '点击右侧「生成学习画像」查看完整画像'
                          : undefined
                    }
                    currentRound={collectedConvFields.length}
                    totalRounds={conversationFields.length}
                  />
                )}
              </div>
            </div>

            {/* Right: Profile Draft */}
            <div className="col-span-5 space-y-4">
              {/* Synced profile indicator */}
              {existingProfile && (
                <div className="bg-green-50 rounded-2xl border border-green-200 p-4 space-y-2">
                  <p className="text-xs font-semibold text-green-800">
                    画像信息已同步
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {existingProfile.profile.knowledge_base?.score != null && (
                      <span className="px-2 py-0.5 text-[10px] rounded-full bg-green-100 text-green-700">
                        知识基础: {existingProfile.profile.knowledge_base.score}
                      </span>
                    )}
                    {existingProfile.profile.practice_ability?.score != null && (
                      <span className="px-2 py-0.5 text-[10px] rounded-full bg-green-100 text-green-700">
                        实践能力: {existingProfile.profile.practice_ability.score}
                      </span>
                    )}
                  </div>
                  <p className="text-[10px] text-green-500">
                    你可以继续对话补充信息，或点击下方"生成学习画像"更新完整画像
                  </p>
                </div>
              )}
              <ProfileDraftPanel
                collectedFields={Object.keys(state.collectedFields)}
                missingFields={missingConvFields.concat(
                  state.diagnosisEvaluated ? [] : ['diagnosis_result']
                )}
                allFields={ALL_FIELDS}
                canStartDiagnosis={state.stage === 'ready_for_diagnosis'}
                canGenerateProfile={state.stage === 'ready_for_profile'}
                diagnosisSubmitted={state.diagnosisEvaluated}
                onStartDiagnosis={handleStartDiagnosis}
                onGenerateProfile={handleGenerateProfile}
              />
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
            {state.finalProfile && <LearningProfileCard profile={state.finalProfile} />}
            {/* Way back to chat for further updates */}
            <div className="flex justify-center">
              <button
                onClick={() => {
                  // Reset to collecting stage with existing data as starting point
                  setState((prev) => ({
                    ...prev,
                    stage: 'collecting',
                    messages: [
                      ...prev.messages,
                      { role: 'buddy' as const, content: '好的，我们继续聊聊你的学习情况吧～还有什么想补充的吗？' },
                    ],
                    nextQuestion: '还有什么想补充的吗？',
                  }))
                }}
                className="px-6 py-2.5 rounded-xl border border-primary-300 text-primary-600 text-sm font-medium hover:bg-primary-50 transition-colors"
              >
                继续补充信息 / 重新对话
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
