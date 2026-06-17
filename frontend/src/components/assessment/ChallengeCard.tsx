import { motion } from 'framer-motion'
import { CheckCircle, XCircle, ChevronRight, ShieldQuestion } from 'lucide-react'
import type { ChallengeQuestion } from '../../mock/assessment'

interface ChallengeCardProps {
  question: ChallengeQuestion
  selectedAnswer: string | undefined
  submitted: boolean
  isCorrect: boolean
  isCurrent: boolean
  onSelectAnswer: (questionId: string, answer: string) => void
  onSubmit: () => void
}

const answerLabels = ['A', 'B', 'C', 'D']

export default function ChallengeCard({
  question,
  selectedAnswer,
  submitted,
  isCorrect,
  isCurrent,
  onSelectAnswer,
  onSubmit,
}: ChallengeCardProps) {
  return (
    <div
      className={`rounded-xl border transition-all ${
        submitted
          ? isCorrect
            ? 'bg-green-50/60 border-green-200'
            : 'bg-red-50/60 border-red-200'
          : isCurrent
            ? 'bg-white border-primary-300 shadow-sm ring-1 ring-primary-100'
            : 'bg-gray-50/60 border-gray-100'
      }`}
    >
      {/* Card header */}
      <div className="px-3 py-2.5 flex items-center gap-2">
        <span
          className={`w-6 h-6 rounded-lg flex items-center justify-center text-[10px] font-bold shrink-0 ${
            submitted
              ? isCorrect
                ? 'bg-green-500 text-white'
                : 'bg-red-500 text-white'
              : isCurrent
                ? 'bg-amber-500 text-white'
                : 'bg-gray-200 text-gray-400'
          }`}
        >
          {submitted ? (isCorrect ? <CheckCircle className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />) : question.level}
        </span>
        <div className="flex-1 min-w-0">
          <span className="text-[11px] font-semibold text-gray-700">第 {question.level} 关：{question.levelName}</span>
          {submitted && (
            <p className="text-[10px] text-gray-500 mt-0.5 leading-relaxed">{question.explanation}</p>
          )}
        </div>
        {submitted && (
          <span className={`text-[10px] font-medium shrink-0 ${isCorrect ? 'text-green-600' : 'text-red-500'}`}>
            {isCorrect ? '通过' : '需回顾'}
          </span>
        )}
        {!submitted && isCurrent && !selectedAnswer && (
          <ShieldQuestion className="w-4 h-4 text-amber-400 shrink-0" />
        )}
      </div>

      {/* Question + Options (only shown for current unsubmitted card) */}
      {!submitted && isCurrent && (
        <div className="px-3 pb-3">
          <p className="text-xs text-gray-700 mb-2 leading-relaxed whitespace-pre-line">{question.question}</p>
          <div className="space-y-1">
            {question.options.map((opt) => {
              const letter = opt[0]
              const isSelected = selectedAnswer === letter
              return (
                <button
                  key={opt}
                  onClick={() => onSelectAnswer(question.id, letter)}
                  className={`w-full text-left flex items-center gap-2 px-3 py-1.5 rounded-lg text-[11px] border transition-colors ${
                    isSelected
                      ? 'bg-amber-50 border-amber-300 text-amber-700 font-medium'
                      : 'bg-white border-gray-100 text-gray-600 hover:border-gray-200'
                  }`}
                >
                  <span
                    className={`w-5 h-5 rounded-md flex items-center justify-center text-[10px] font-bold shrink-0 ${
                      isSelected ? 'bg-amber-500 text-white' : 'bg-gray-100 text-gray-400'
                    }`}
                  >
                    {letter}
                  </span>
                  {opt.slice(3)}
                </button>
              )
            })}
          </div>

          {/* Submit button */}
          <button
            onClick={onSubmit}
            disabled={!selectedAnswer}
            className={`mt-2 w-full py-2 rounded-lg text-xs font-medium transition-all flex items-center justify-center gap-1.5 ${
              selectedAnswer
                ? 'bg-amber-500 text-white hover:bg-amber-600'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            }`}
          >
            提交本关
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      )}
    </div>
  )
}
