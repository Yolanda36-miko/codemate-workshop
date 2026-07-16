import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Swords } from 'lucide-react'
import type { ChallengeQuestion, ChallengeResult } from '../../mock/assessment'
import type { ConversationContext, PathNode } from '../../types'
import { generateChallengeByContextMock, generateChallengeResult } from '../../mock/assessment'
import ChallengeCard from './ChallengeCard'

interface ChallengePanelProps {
  context: ConversationContext
  pathNodes?: PathNode[]
}

export default function ChallengePanel({ context, pathNodes }: ChallengePanelProps) {
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [submittedIds, setSubmittedIds] = useState<Set<string>>(new Set())
  const [result, setResult] = useState<ChallengeResult | null>(null)
  const [allDone, setAllDone] = useState(false)
  const [currentLevel, setCurrentLevel] = useState(1)
  const [questions, setQuestions] = useState<ChallengeQuestion[]>(() =>
    generateChallengeByContextMock(context, pathNodes),
  )

  // Reset when context changes (new question asked)
  useEffect(() => {
    const newQuestions = generateChallengeByContextMock(context)
    setQuestions(newQuestions)
    setAnswers({})
    setSubmittedIds(new Set())
    setResult(null)
    setAllDone(false)
    setCurrentLevel(1)
  }, [context])

  const handleSelectAnswer = (questionId: string, answer: string) => {
    if (submittedIds.has(questionId)) return
    setAnswers((prev) => ({ ...prev, [questionId]: answer }))
  }

  const handleSubmitLevel = (questionId: string) => {
    if (!answers[questionId]) return
    const newSubmitted = new Set(submittedIds)
    newSubmitted.add(questionId)
    setSubmittedIds(newSubmitted)

    const q = questions.find((cq) => cq.id === questionId)
    if (q && q.level < questions.length) {
      setCurrentLevel(q.level + 1)
    }

    if (newSubmitted.size >= questions.length) {
      const res = generateChallengeResult(answers, questions)
      setResult(res)
      setAllDone(true)
    }
  }

  const handleViewAllResults = () => {
    const res = generateChallengeResult(answers, questions)
    setResult(res)
    setAllDone(true)
  }

  const completedCount = submittedIds.size
  const totalCount = questions.length

  return (
    <div className="bg-white rounded-2xl shadow-card border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center">
            <Swords className="w-3.5 h-3.5 text-white" />
          </div>
          <div>
            <span className="text-sm font-semibold text-gray-800">闯关评估</span>
            {!allDone && (
              <span className="text-[10px] text-gray-400 ml-1.5">
                第 {currentLevel}/{totalCount} 关
              </span>
            )}
          </div>
        </div>
        {!allDone && (
          <span className="text-[10px] text-amber-600 font-medium bg-amber-50 px-2 py-0.5 rounded-full">
            {completedCount}/{totalCount} 已完成
          </span>
        )}
        {allDone && result && (
          <motion.span
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="text-[10px] text-green-600 font-medium bg-green-50 px-2 py-0.5 rounded-full"
          >
            {result.score} 分
          </motion.span>
        )}
      </div>

      {/* Progress bar */}
      {!allDone && (
        <div className="px-4 pt-3">
          <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-amber-400 to-orange-500 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${(completedCount / totalCount) * 100}%` }}
              transition={{ duration: 0.4 }}
            />
          </div>
        </div>
      )}

      {/* Challenge cards */}
      <div className="p-4 space-y-2.5">
        <AnimatePresence mode="popLayout">
          {questions.map((q) => {
            const isCurrent = q.level === currentLevel && !allDone
            const isSubmitted = submittedIds.has(q.id)
            const isCorrect = answers[q.id] === q.correct

            return (
              <motion.div
                key={q.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{
                  opacity: allDone || isCurrent || isSubmitted ? 1 : 0.5,
                  y: 0,
                  scale: isCurrent ? 1.02 : 1,
                }}
                transition={{ delay: (q.level - 1) * 0.04, duration: 0.25 }}
              >
                <ChallengeCard
                  question={q}
                  selectedAnswer={answers[q.id]}
                  submitted={isSubmitted}
                  isCorrect={isCorrect}
                  isCurrent={isCurrent}
                  onSelectAnswer={handleSelectAnswer}
                  onSubmit={() => handleSubmitLevel(q.id)}
                />
              </motion.div>
            )
          })}
        </AnimatePresence>

        {completedCount > 0 && completedCount < totalCount && !allDone && (
          <button
            onClick={handleViewAllResults}
            className="w-full py-2 rounded-xl text-xs text-gray-400 hover:text-primary-500 transition-colors"
          >
            查看已完成结果
          </button>
        )}
      </div>

      {/* All Done — Summary */}
      {allDone && result && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35 }}
          className="px-4 pb-4 space-y-2"
        >
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-3 border border-green-100">
            <div className="flex items-center gap-2">
              <Swords className="w-4 h-4 text-green-600" />
              <span className="text-xs font-semibold text-green-700">闯关完成</span>
              <span className="text-[10px] text-green-500">
                {result.correctCount}/{result.totalLevels} 通过 · {result.score} 分
              </span>
            </div>
          </div>

          {result.wrongPoints.length > 0 && (
            <div>
              <span className="text-[10px] text-gray-500 block mb-1">需回顾的知识点：</span>
              {result.wrongPoints.map((wp) => (
                <p key={wp.knowledge_point} className="text-[10px] text-gray-500 leading-relaxed">
                  <span className="text-gray-700 font-medium">{wp.knowledge_point}</span>：{wp.reason}
                </p>
              ))}
            </div>
          )}
        </motion.div>
      )}
    </div>
  )
}
