import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Sparkles, CheckCircle2, Loader2, Brain, GitBranch, FileText, Code, ClipboardCheck } from 'lucide-react'
import { getStudentDisplayName } from '../../config/appConfig'

interface AgentStep {
  key: string
  label: string
  agent: string
  icon: typeof Brain
  color: string
  description: string
}

function getAgentSteps(): AgentStep[] {
  const student = getStudentDisplayName()
  return [
    {
      key: 'diagnosis', label: '诊断分析', agent: 'Diagnosis Agent',
      icon: Brain,
      color: 'text-blue-500',
      description: `分析${student}的学习画像与薄弱点...`,
    },
    {
      key: 'course-map', label: '课程映射', agent: 'Course Map Agent',
      icon: GitBranch,
      color: 'text-purple-500',
      description: '匹配课程知识图谱与先修关系...',
    },
    {
      key: 'resource', label: '资源生成', agent: 'Resource Agent',
      icon: FileText,
      color: 'text-primary-500',
      description: `根据${student}的画像与风格定制学习资源...`,
    },
    {
      key: 'code-practice', label: '代码练习', agent: 'Code Practice Agent',
      icon: Code,
      color: 'text-emerald-500',
      description: '生成配套代码示例与注释...',
    },
    {
      key: 'assessment', label: '评估校验', agent: 'Assessment Agent',
      icon: ClipboardCheck,
      color: 'text-amber-500',
      description: '校验资源难度匹配与知识点覆盖...',
    },
  ]
}

interface AgentGenerationStatusProps {
  active: boolean
  onComplete: () => void
}

export default function AgentGenerationStatus({ active, onComplete }: AgentGenerationStatusProps) {
  const [currentStep, setCurrentStep] = useState(-1)
  const [completedSteps, setCompletedSteps] = useState<Set<string>>(new Set())

  useEffect(() => {
    if (!active) {
      setCurrentStep(-1)
      setCompletedSteps(new Set())
      return
    }

    const steps = getAgentSteps()
    let step = 0
    setCurrentStep(0)

    const interval = setInterval(() => {
      setCompletedSteps((prev) => {
        const next = new Set(prev)
        if (step < steps.length) {
          next.add(steps[step].key)
        }
        return next
      })

      step++
      if (step < steps.length) {
        setCurrentStep(step)
      } else {
        clearInterval(interval)
        setCurrentStep(-1)
        setTimeout(() => onComplete(), 300)
      }
    }, 800)

    return () => clearInterval(interval)
  }, [active])

  if (!active) return null

  return (
    <div className="bg-white rounded-2xl p-5 shadow-card border border-gray-100">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="w-5 h-5 text-primary-500" />
        <h2 className="font-semibold text-gray-800">智能体协同生成</h2>
        <span className="ml-auto text-[10px] text-gray-400 bg-gray-50 px-2 py-0.5 rounded-full">
          5 个智能体
        </span>
      </div>

      <div className="space-y-0.5">
        {getAgentSteps().map((step, i) => {
          const Icon = step.icon
          const isCompleted = completedSteps.has(step.key)
          const isCurrent = i === currentStep

          return (
            <div
              key={step.key}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-colors ${
                isCurrent ? 'bg-primary-50/50' : ''
              }`}
            >
              {/* Icon */}
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 transition-colors ${
                isCompleted ? 'bg-green-50' : isCurrent ? 'bg-primary-100' : 'bg-gray-50'
              }`}>
                {isCompleted ? (
                  <CheckCircle2 className="w-4 h-4 text-green-500" />
                ) : isCurrent ? (
                  <Loader2 className={`w-4 h-4 ${step.color} animate-spin`} />
                ) : (
                  <Icon className={`w-4 h-4 text-gray-300`} />
                )}
              </div>

              {/* Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className={`text-xs font-semibold ${
                    isCompleted ? 'text-green-600' : isCurrent ? 'text-primary-700' : 'text-gray-400'
                  }`}>
                    {step.label}
                  </span>
                  <span className="text-[10px] text-gray-400">{step.agent}</span>
                </div>
                {(isCurrent || isCompleted) && (
                  <motion.p
                    className={`text-[10px] mt-0.5 ${
                      isCompleted ? 'text-green-600' : 'text-primary-500'
                    }`}
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                  >
                    {isCompleted ? '完成' : step.description}
                  </motion.p>
                )}
              </div>

              {/* Status dot */}
              <div className="shrink-0">
                {isCompleted ? (
                  <div className="w-2 h-2 rounded-full bg-green-400" />
                ) : isCurrent ? (
                  <motion.div
                    className="w-2 h-2 rounded-full bg-primary-400"
                    animate={{ scale: [1, 1.5, 1] }}
                    transition={{ duration: 1, repeat: Infinity }}
                  />
                ) : (
                  <div className="w-2 h-2 rounded-full bg-gray-200" />
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
