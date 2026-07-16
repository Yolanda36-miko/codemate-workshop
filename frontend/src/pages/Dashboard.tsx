import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Sparkles, BookOpen, GitBranch, Users, Zap, ArrowRight,
  MessageCircle, Search, FileText, ClipboardCheck,
  UserRound, Map, Terminal,
} from 'lucide-react'
import { dataStructureModules } from '../config/courseFocus'
import { isDemoMode } from '../config/appConfig'
import AnimatedSection from '../components/common/AnimatedSection'

const flowSteps = [
  { label: '多轮对话', icon: MessageCircle },
  { label: '画像生成', icon: Sparkles },
  { label: '模块诊断', icon: Search },
  { label: '资源生成', icon: FileText },
  { label: '路径规划', icon: GitBranch },
  { label: '辅导评估', icon: ClipboardCheck },
]

const agents = [
  { name: 'Profile Agent', role: '学习画像构建', icon: UserRound, bg: 'bg-primary-400/20', fg: 'text-primary-500' },
  { name: 'Course Map Agent', role: '模块依赖分析', icon: Map, bg: 'bg-primary-500/20', fg: 'text-primary-600' },
  { name: 'Diagnosis Agent', role: '学习困难诊断', icon: Search, bg: 'bg-purple-400/20', fg: 'text-purple-500' },
  { name: 'Resource Agent', role: '个性化资源生成', icon: FileText, bg: 'bg-primary-600/20', fg: 'text-primary-700' },
  { name: 'Code Practice Agent', role: '代码练习辅导', icon: Terminal, bg: 'bg-purple-500/20', fg: 'text-purple-600' },
  { name: 'Path Planning Agent', role: '学习路径规划', icon: GitBranch, bg: 'bg-primary-700/20', fg: 'text-primary-700' },
  { name: 'Assessment Agent', role: '学习效果评估', icon: ClipboardCheck, bg: 'bg-purple-600/20', fg: 'text-purple-700' },
]

const moduleAccents: Record<string, string> = {
  '复杂度分析': 'border-l-primary-400',
  '线性表': 'border-l-blue-400',
  '栈与队列': 'border-l-primary-500',
  '递归与调用栈': 'border-l-purple-400',
  '树与二叉树': 'border-l-primary-600',
  '图结构与图算法': 'border-l-purple-500',
  '排序与查找': 'border-l-blue-500',
  '散列表': 'border-l-primary-700',
  '动态规划入门': 'border-l-purple-600',
  '综合项目实践': 'border-l-amber-400',
}

export default function Dashboard() {
  return (
    <div className="p-8 max-w-5xl mx-auto space-y-10 pb-12">
      {/* ========== Section 1: Hero ========== */}
      <AnimatedSection className="relative text-center py-10">
        {/* Decorative blur blobs */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full bg-primary-400/10 blur-3xl pointer-events-none" />
        <div className="absolute top-0 right-10 w-72 h-72 rounded-full bg-purple-400/8 blur-3xl pointer-events-none" />

        <div className="relative">
          {/* Badge pill */}
          <motion.div
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary-50 text-primary-700 text-sm font-medium mb-5 border border-primary-100/50"
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.4 }}
          >
            <Sparkles className="w-4 h-4" />
            CodeBuddy 在线陪伴学习
          </motion.div>

          {/* Title */}
          <h1 className="text-4xl font-bold mb-3 tracking-tight">
            <span className="gradient-text">CodeMate 智学工坊</span>
          </h1>

          {/* Decorative underline */}
          <div className="flex items-center justify-center gap-1 mb-4">
            <div className="w-8 h-0.5 rounded-full bg-primary-400" />
            <div className="w-12 h-0.5 rounded-full bg-primary-500" />
            <div className="w-8 h-0.5 rounded-full bg-purple-400" />
          </div>

          {/* Subtitle */}
          <p className="text-gray-500 text-base max-w-2xl mx-auto mb-4 leading-relaxed">
            数据结构与算法个性化学习资源平台
          </p>
        </div>
      </AnimatedSection>

      {/* CTA Buttons — outside AnimatedSection to avoid Framer Motion event interception */}
      <div className="flex items-center justify-center gap-3 pb-4">
        <Link
          to="/profile"
          className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-primary-500 to-primary-700 text-white text-sm font-medium shadow-md hover:shadow-glow hover:-translate-y-0.5 transition-all duration-200"
        >
          开始构建画像
          <ArrowRight className="w-4 h-4" />
        </Link>
        <Link
          to="/courses"
          className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl border border-primary-200 text-primary-700 text-sm font-medium bg-white/80 hover:bg-white hover:shadow-card transition-all duration-200"
        >
          查看模块中心
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      {/* ========== Section 2: Module Overview ========== */}
      <AnimatedSection delay={0.1}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-primary-600" />
            <h2 className="text-lg font-semibold text-gray-800">数据结构与算法模块中心</h2>
          </div>
          <Link
            to="/courses"
            className="flex items-center gap-1 text-xs text-primary-500 hover:text-primary-700 transition-colors font-medium"
          >
            查看全部 <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
        <div className="grid grid-cols-3 gap-4">
          {dataStructureModules.slice(0, 6).map((c, i) => {
            const accent = moduleAccents[c.name] || 'border-l-primary-400'

            return (
              <motion.div
                key={c.id}
                className={`bg-white rounded-2xl p-5 shadow-card hover:shadow-card-hover border border-gray-100 border-l-4 ${accent} transition-colors`}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.1 + i * 0.08, duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
                whileHover={{ y: -3 }}
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-gray-800 text-sm">{c.name}</h3>
                </div>
                <p className="text-xs text-gray-500 leading-relaxed line-clamp-2 mb-3">
                  {c.description}
                </p>
                <div className="flex items-center justify-between">
                  <span className="text-[11px] text-gray-400">
                    {(c.knowledge_points ?? []).length} 个核心知识点
                  </span>
                </div>
              </motion.div>
            )
          })}
        </div>
      </AnimatedSection>

      {/* ========== Section 3: System Flow ========== */}
      <AnimatedSection delay={0.15}>
        <div className="flex items-center gap-2 mb-4">
          <GitBranch className="w-5 h-5 text-primary-600" />
          <h2 className="text-lg font-semibold text-gray-800">系统流程</h2>
        </div>
        <div className="bg-white rounded-2xl p-6 shadow-card border border-gray-100 overflow-x-auto">
          <div className="flex items-start justify-between min-w-[720px]">
            {flowSteps.flatMap((step, i) => {
              const stepEl = (
                <motion.div
                  key={step.label}
                  className="flex flex-col items-center gap-2 shrink-0"
                  initial={{ opacity: 0, y: 12 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.1 + i * 0.1, duration: 0.4 }}
                >
                  <div
                    className="w-11 h-11 rounded-full flex items-center justify-center shadow-sm"
                    style={{
                      background: `linear-gradient(135deg, hsl(${250 + i * 10}, 80%, ${75 - i * 5}%), hsl(${260 + i * 10}, 70%, ${65 - i * 4}%))`,
                    }}
                  >
                    <step.icon className="w-5 h-5 text-white" />
                  </div>
                  <span className="text-xs text-gray-600 font-medium whitespace-nowrap">{step.label}</span>
                </motion.div>
              )

              if (i === flowSteps.length - 1) return [stepEl]

              return [
                stepEl,
                <div key={`arrow-${i}`} className="pt-[6px] shrink-0">
                  <ArrowRight className="w-8 h-8 text-primary-300" strokeWidth={2.5} />
                </div>,
              ]
            })}
          </div>
        </div>
      </AnimatedSection>

      {/* ========== Section 4: Multi-Agent Collaboration ========== */}
      <AnimatedSection delay={0.2}>
        <div className="flex items-center gap-2 mb-4">
          <Users className="w-5 h-5 text-primary-600" />
          <h2 className="text-lg font-semibold text-gray-800">多智能体协作</h2>
        </div>
        <div className="grid grid-cols-4 gap-3">
          {agents.slice(0, 4).map((agent, i) => (
            <motion.div
              key={agent.name}
              className="bg-white rounded-2xl p-4 shadow-card border border-gray-100 hover:shadow-card-hover transition-colors cursor-default"
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 + i * 0.06, duration: 0.4 }}
              whileHover={{ y: -3 }}
            >
              <div className={`w-9 h-9 rounded-xl ${agent.bg} flex items-center justify-center mb-2.5`}>
                <agent.icon className={`w-4 h-4 ${agent.fg}`} />
              </div>
              <p className="text-sm font-semibold text-gray-800 mb-0.5">{agent.name}</p>
              <p className="text-[11px] text-gray-400">{agent.role}</p>
            </motion.div>
          ))}
        </div>
        <div className="grid grid-cols-3 gap-3 mt-3">
          {agents.slice(4).map((agent, i) => (
            <motion.div
              key={agent.name}
              className="bg-white rounded-2xl p-4 shadow-card border border-gray-100 hover:shadow-card-hover transition-colors cursor-default"
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.35 + i * 0.06, duration: 0.4 }}
              whileHover={{ y: -3 }}
            >
              <div className={`w-9 h-9 rounded-xl ${agent.bg} flex items-center justify-center mb-2.5`}>
                <agent.icon className={`w-4 h-4 ${agent.fg}`} />
              </div>
              <p className="text-sm font-semibold text-gray-800 mb-0.5">{agent.name}</p>
              <p className="text-[11px] text-gray-400">{agent.role}</p>
            </motion.div>
          ))}
        </div>
      </AnimatedSection>

      {/* ========== Section 5: Demo Scenario ========== */}
      <AnimatedSection delay={0.25}>
        <div className="flex items-center gap-2 mb-4">
          <Zap className="w-5 h-5 text-primary-600" />
          <h2 className="text-lg font-semibold text-gray-800">
            {isDemoMode() ? '默认演示场景' : '开始学习'}
          </h2>
        </div>

        {isDemoMode() ? (
          /* Demo Mode: generic DS scenario */
          <div className="bg-gradient-to-r from-primary-50 to-purple-50 rounded-2xl p-6 border border-primary-100/50">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-11 h-11 rounded-full bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm shadow-sm">
                学
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-800">
                  当前学习者
                </p>
                <p className="text-xs text-gray-400 mt-0.5">
                  数据结构与算法 · 个性化学习
                </p>
              </div>
            </div>
            <p className="text-sm text-gray-600 leading-relaxed mb-4">
              当前学习者正在学习<strong className="text-gray-800">数据结构与算法</strong>，
              对<strong className="text-primary-600">复杂度分析</strong>、
              <strong className="text-primary-600">递归调用栈</strong>、
              <strong className="text-primary-600">二叉树遍历</strong>和
              <strong className="text-primary-600">动态规划</strong>等模块需要加强，
              偏好图示讲解、代码案例和分层练习题。
            </p>
            <div className="space-y-2">
              <div className="flex items-center gap-1.5 flex-wrap">
                <span className="text-[10px] text-gray-400 font-medium">薄弱模块</span>
                {['复杂度分析', '递归调用栈', '二叉树遍历', '动态规划'].map((tag) => (
                  <span key={tag} className="px-2 py-0.5 rounded-full bg-white/80 text-primary-600 text-[11px] font-medium border border-primary-100">
                    {tag}
                  </span>
                ))}
              </div>
              <div className="flex items-center gap-1.5 flex-wrap">
                <span className="text-[10px] text-gray-400 font-medium">偏好方式</span>
                {['图示讲解', '代码案例', '分层练习'].map((tag) => (
                  <span key={tag} className="px-2 py-0.5 rounded-full bg-white/80 text-purple-600 text-[11px] font-medium border border-purple-100">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ) : (
          /* Real Mode: generic guide */
          <div className="bg-gradient-to-r from-primary-50 to-purple-50 rounded-2xl p-6 border border-primary-100/50 text-center">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-400 to-purple-500 flex items-center justify-center mx-auto mb-3">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <p className="text-sm font-semibold text-gray-800 mb-1">从数据结构与算法开始你的学习之旅</p>
            <p className="text-xs text-gray-500 leading-relaxed max-w-md mx-auto">
              先去<Link to="/profile" className="text-primary-500 font-medium hover:underline">学习画像</Link>告诉 CodeBuddy 你的基础和目标，
              系统将为你生成专属的数据结构与算法学习资源与路径规划。
            </p>
          </div>
        )}
      </AnimatedSection>
    </div>
  )
}
