import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Swords, ChevronRight } from 'lucide-react'
import type { ChallengeQuestion, ChallengeResult } from '../../mock/assessment'
import type { ConversationContext, PathNode } from '../../types'
import { generateChallengeByContextMock, generateChallengeResult, recommendResourcesByContextMock } from '../../mock/assessment'
import ChallengeCard from './ChallengeCard'

interface ChallengePanelProps {
  context: ConversationContext
  pathNodes?: PathNode[]
  onViewResource: (resource: { title: string; type: string; estimatedTime: string; topic: string }) => void
}

export default function ChallengePanel({ context, pathNodes, onViewResource }: ChallengePanelProps) {
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
  const recommendedResources = recommendResourcesByContextMock(context)

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
          className="px-4 pb-4 space-y-3"
        >
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-3 border border-green-100">
            <div className="flex items-center gap-2 mb-2">
              <Swords className="w-4 h-4 text-green-600" />
              <span className="text-xs font-semibold text-green-700">闯关完成！</span>
              <span className="text-[10px] text-green-500">
                {result.correctCount}/{result.totalLevels} 关通过
              </span>
            </div>
            <div className="flex items-center gap-4 text-xs">
              <span className="text-green-700">
                知识基础 <span className="font-bold text-green-600">+{result.growth.knowledge_base}</span>
              </span>
              <span className="text-green-700">
                实践能力 <span className="font-bold text-green-600">+{result.growth.practice_ability}</span>
              </span>
            </div>
            {result.badges.length > 0 && (
              <div className="flex items-center gap-1.5 mt-2">
                {result.badges.map((b) => (
                  <motion.span
                    key={b}
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: 'spring', stiffness: 300 }}
                    className="px-2 py-1 rounded-lg bg-amber-100 text-[10px] font-semibold text-amber-700 border border-amber-200"
                  >
                    {b}
                  </motion.span>
                ))}
              </div>
            )}
          </div>

          {result.wrongPoints.length > 0 && (
            <div>
              <span className="text-[10px] text-gray-500 block mb-1.5">需要回顾：</span>
              <div className="space-y-1">
                {result.wrongPoints.map((wp) => (
                  <div key={wp.knowledge_point} className="flex items-start gap-1.5 text-[10px] text-gray-500">
                    <ChevronRight className="w-3 h-3 text-orange-400 shrink-0 mt-0.5" />
                    <span><span className="text-gray-700 font-medium">{wp.knowledge_point}</span>：{wp.reason}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div>
            <span className="text-[10px] text-gray-500 block mb-1.5">推荐补救资源：</span>
            <div className="space-y-1">
              {recommendedResources.map((r) => (
                <button
                  key={r.title}
                  onClick={() => onViewResource({ ...r, topic: r.topic })}
                  className="w-full text-left px-3 py-2 rounded-xl bg-gray-50 border border-gray-100 text-[11px] text-gray-600 hover:border-primary-200 hover:text-primary-600 transition-colors"
                >
                  {r.title} · {r.estimatedTime}
                </button>
              ))}
            </div>
          </div>

          <div className="bg-primary-50 rounded-xl p-3 border border-primary-100">
            <span className="text-[10px] text-primary-600 block leading-relaxed">
              {result.correctCount === result.totalLevels
                ? '全部通关！继续提问或进入学习路径进行项目实践。'
                : '回顾上述推荐资源，重点关注薄弱知识点，然后再次挑战剩余关卡。'}
            </span>
          </div>
        </motion.div>
      )}
    </div>
  )
}
