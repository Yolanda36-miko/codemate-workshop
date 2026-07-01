import { useState } from 'react'
import { Sparkles, BookOpen, Edit3, Clock, Code } from 'lucide-react'

const DIFFICULTIES = ['基础', '进阶', '综合']
const LANGUAGES = ['Python', 'C', 'C++', 'Java']

const RESOURCE_TYPES = [
  { key: '个性化讲解文档', icon: BookOpen, label: '讲解文档', desc: '个性化知识点讲解' },
  { key: '知识点思维导图', icon: Edit3, label: '思维导图', desc: '知识体系结构化' },
  { key: '代码示例与注释', icon: Code, label: '代码示例', desc: '逐行注释的范例' },
  { key: '分层练习题', icon: Edit3, label: '分层练习', desc: '基础到进阶练习' },
  { key: '拓展阅读资料', icon: BookOpen, label: '拓展阅读', desc: '深度话题与延伸' },
  { key: '项目式学习案例', icon: Code, label: '项目案例', desc: '综合实战项目' },
]

const RECOMMENDED_TOPICS = [
  '递归调用栈', '二叉树遍历', '图的 BFS 与 DFS', '快速排序', '动态规划入门',
]

export interface WorkbenchParams {
  courseId: string
  learningTopic: string
  difficulty: string
  language: string
  selectedTypes: string[]
}

interface ResourceWorkbenchProps {
  onGenerate: (params: WorkbenchParams) => void
  generating: boolean
}

export default function ResourceWorkbench({ onGenerate, generating }: ResourceWorkbenchProps) {
  const [courseId, setCourseId] = useState('data-structures')
  const [learningTopic, setLearningTopic] = useState('递归调用栈')
  const [difficulty, setDifficulty] = useState('基础')
  const [language, setLanguage] = useState('Python')
  const [selectedTypes, setSelectedTypes] = useState<string[]>(
    RESOURCE_TYPES.map((t) => t.key),
  )

  const toggleType = (key: string) => {
    setSelectedTypes((prev) =>
      prev.includes(key) ? prev.filter((x) => x !== key) : [...prev, key],
    )
  }

  const handleChipClick = (topic: string) => {
    setLearningTopic(topic)
  }

  const handleGenerate = () => {
    if (!learningTopic.trim()) return
    onGenerate({ courseId, learningTopic: learningTopic.trim(), difficulty, language, selectedTypes })
  }

  return (
    <div className="bg-white rounded-2xl p-5 shadow-card border border-gray-100 space-y-4">
      {/* Step 1: Course + Learning Topic */}
      <div className="grid grid-cols-5 gap-3">
        <div className="col-span-2">
          <label className="block text-xs font-medium text-gray-500 mb-1.5">
            <span className="inline-flex items-center gap-1">
              <BookOpen className="w-3 h-3 text-primary-400" />
              选择课程
            </span>
          </label>
          <select
            value={courseId}
            onChange={(e) => setCourseId(e.target.value)}
            className="w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-200 bg-white"
          >
            <option value="data-structures">数据结构与算法</option>
          </select>
        </div>
        <div className="col-span-3">
          <label className="block text-xs font-medium text-gray-500 mb-1.5">
            <span className="inline-flex items-center gap-1">
              <Edit3 className="w-3 h-3 text-primary-400" />
              学习主题
            </span>
          </label>
          <input
            type="text"
            value={learningTopic}
            onChange={(e) => setLearningTopic(e.target.value)}
            placeholder="输入你想学习的数据结构知识点，例如：递归调用栈、二叉树遍历、图的最短路径、快速排序、动态规划入门"
            className="w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-200 bg-white placeholder:text-gray-300"
          />
          <p className="text-[10px] text-gray-400 mt-1">
            可以输入具体问题或知识点，后续将由大模型自动识别学习需求
          </p>
        </div>
      </div>

      {/* Recommended topic chips */}
      <div>
        <span className="text-[10px] text-gray-400 mr-2">推荐主题：</span>
        <div className="inline-flex flex-wrap gap-1.5">
          {RECOMMENDED_TOPICS.map((topic) => (
            <button
              key={topic}
              onClick={() => handleChipClick(topic)}
              className={`px-2.5 py-1 rounded-full text-[11px] border transition-all ${
                learningTopic === topic
                  ? 'bg-primary-100 border-primary-300 text-primary-700 font-medium'
                  : 'bg-gray-50 border-gray-100 text-gray-500 hover:border-primary-200 hover:text-primary-600'
              }`}
            >
              {topic}
            </button>
          ))}
        </div>
      </div>

      {/* Step 2: Difficulty + Language */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1.5">
            <span className="inline-flex items-center gap-1">
              <Clock className="w-3 h-3 text-primary-400" />
              难度
            </span>
          </label>
          <div className="flex gap-2">
            {DIFFICULTIES.map((d) => (
              <button
                key={d}
                onClick={() => setDifficulty(d)}
                className={`flex-1 py-2 rounded-xl text-sm border transition-all ${
                  difficulty === d
                    ? 'bg-primary-50 border-primary-300 text-primary-700 font-medium'
                    : 'bg-white border-gray-200 text-gray-500 hover:border-gray-300'
                }`}
              >
                {d}
              </button>
            ))}
          </div>
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1.5">
            <span className="inline-flex items-center gap-1">
              <Code className="w-3 h-3 text-primary-400" />
              编程语言
            </span>
          </label>
          <div className="flex gap-2">
            {LANGUAGES.map((l) => (
              <button
                key={l}
                onClick={() => setLanguage(l)}
                className={`flex-1 py-2 rounded-xl text-sm border transition-all ${
                  language === l
                    ? 'bg-primary-50 border-primary-300 text-primary-700 font-medium'
                    : 'bg-white border-gray-200 text-gray-500 hover:border-gray-300'
                }`}
              >
                {l}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Step 3: Resource Types */}
      <div>
        <label className="block text-xs font-medium text-gray-500 mb-2">
          资源类型选择
        </label>
        <div className="grid grid-cols-3 gap-2">
          {RESOURCE_TYPES.map((rt) => {
            const selected = selectedTypes.includes(rt.key)
            const Icon = rt.icon
            return (
              <button
                key={rt.key}
                onClick={() => toggleType(rt.key)}
                className={`flex items-center gap-2 px-3 py-2 rounded-xl text-left border transition-all ${
                  selected
                    ? 'bg-primary-50 border-primary-300'
                    : 'bg-white border-gray-100 hover:border-gray-200'
                }`}
              >
                <Icon className={`w-4 h-4 shrink-0 ${selected ? 'text-primary-500' : 'text-gray-300'}`} />
                <span className={`text-[11px] font-medium truncate ${selected ? 'text-primary-700' : 'text-gray-600'}`}>
                  {rt.key}
                </span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Generate Button */}
      <button
        onClick={handleGenerate}
        disabled={generating || !learningTopic.trim() || selectedTypes.length === 0}
        className={`w-full flex items-center justify-center gap-2 py-3 rounded-xl font-semibold text-sm transition-all ${
          generating || !learningTopic.trim() || selectedTypes.length === 0
            ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
            : 'bg-gradient-to-r from-primary-500 to-purple-600 text-white hover:from-primary-600 hover:to-purple-700 shadow-md hover:shadow-glow hover:-translate-y-0.5'
        }`}
      >
        <Sparkles className={`w-4 h-4 ${generating ? 'animate-pulse' : ''}`} />
        {generating ? '智能体生成中...' : '生成个性化资源'}
      </button>
    </div>
  )
}
