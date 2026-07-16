import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { MessageCircle, Sparkles, FileText, GitBranch, ClipboardCheck } from 'lucide-react'
import { generateProfile, getUserProfile, USE_MOCK } from '../../services/api'
import { mapBackendProfileToStudentProfile, isProfileComplete } from '../../services/profileInterview'
import DsAvatar from '../common/DsAvatar'
import type { StudentProfile } from '../../types'

const agents = [
  { name: 'Profile Agent', label: '画像诊断', icon: Sparkles },
  { name: 'Resource Agent', label: '资源生成', icon: FileText },
  { name: 'Path Planning Agent', label: '路径规划', icon: GitBranch },
  { name: 'Assessment Agent', label: '辅导评估', icon: ClipboardCheck },
]

export default function RightPanel() {
  const [profile, setProfile] = useState<StudentProfile | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!USE_MOCK) {
      // Real mode: load profile from backend, show neutral placeholder if empty
      getUserProfile(1)
        .then((backend) => {
          if (backend && isProfileComplete(backend)) {
            setProfile(mapBackendProfileToStudentProfile(backend))
          }
        })
        .catch(() => {})
        .finally(() => setLoading(false))
    } else {
      // Mock mode: use demo student
      generateProfile()
        .then((p) => setProfile(p))
        .catch(() => {})
        .finally(() => setLoading(false))
    }
  }, [])

  return (
    <aside className="fixed right-0 top-0 h-screen w-[--right-panel-width] bg-white border-l border-gray-100 overflow-y-auto z-30">
      <div className="p-4 space-y-4 pt-20">

        {/* Section 1: CodeBuddy Wizard Card */}
        <div className="rounded-2xl bg-gradient-to-br from-primary-50 to-purple-50 p-4 border border-primary-100/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center text-white text-sm font-bold shadow-sm shrink-0">
              CB
            </div>
            <div className="min-w-0">
              <p className="text-sm font-semibold text-gray-800">CodeBuddy</p>
              <p className="text-xs text-gray-500">你的 AI 学习向导</p>
            </div>
            <div className="ml-auto flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-green-400" />
              <span className="text-[10px] text-green-600 font-medium">在线</span>
            </div>
          </div>
          <Link
            to="/profile"
            className="mt-3 flex items-center justify-center gap-2 w-full py-2 rounded-xl bg-primary-500 text-white text-sm font-medium hover:bg-primary-600 transition-colors"
          >
            <MessageCircle className="w-4 h-4" />
            开始对话
          </Link>
        </div>

        {/* Section 2: Current Student Card */}
        {loading ? (
          <div className="rounded-2xl bg-white border border-gray-100 p-4 space-y-3 animate-pulse">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gray-200" />
              <div className="space-y-1.5 flex-1">
                <div className="h-4 bg-gray-200 rounded w-16" />
                <div className="h-3 bg-gray-100 rounded w-24" />
              </div>
            </div>
            <div className="h-3 bg-gray-100 rounded w-full" />
            <div className="h-3 bg-gray-100 rounded w-3/4" />
          </div>
        ) : profile ? (
          <div className="rounded-2xl bg-white border border-gray-100 p-4">
            <div className="flex items-center gap-3 mb-3">
              <DsAvatar size="md" />
              <div>
                <p className="text-sm font-semibold text-gray-800">
                  {profile.student.display_name || profile.student.name || '小栈'}
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="rounded-2xl bg-white border border-gray-100 p-4 text-center">
            <p className="text-xs text-gray-400">暂未绑定学生</p>
            <Link to="/profile" className="text-xs text-primary-500 hover:underline mt-1 inline-block">
              去画像页初始化 →
            </Link>
          </div>
        )}

        {/* Section 3: Profile Dimensions Summary */}
        {loading ? (
          <div className="rounded-2xl bg-white border border-gray-100 p-4 space-y-3 animate-pulse">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-3 bg-gray-100 rounded w-full" />
            ))}
          </div>
        ) : profile ? (
          <div className="rounded-2xl bg-white border border-gray-100 p-4">
            <h3 className="text-sm font-semibold text-gray-800 mb-3">学习画像摘要</h3>

            {/* Knowledge Base */}
            <div className="mb-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-gray-500">知识基础</span>
                {profile.profile.knowledge_base?.score != null && profile.profile.knowledge_base?.stars != null ? (
                  <span className="text-xs text-gray-400">
                    {'★'.repeat(profile.profile.knowledge_base.stars)}
                    {'☆'.repeat(5 - profile.profile.knowledge_base.stars)}
                    {' '}{profile.profile.knowledge_base.score}/{profile.profile.knowledge_base.max_score}
                  </span>
                ) : null}
              </div>
              {profile.profile.knowledge_base?.score != null ? (
                <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary-400 rounded-full transition-all"
                    style={{ width: `${((profile.profile.knowledge_base.score) / (profile.profile.knowledge_base.max_score || 100)) * 100}%` }}
                  />
                </div>
              ) : (
                <p className="text-[10px] text-gray-400">完成画像后将补充此信息</p>
              )}
            </div>

            {/* Practice Ability */}
            <div className="mb-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-gray-500">实践能力</span>
                {profile.profile.practice_ability?.score != null && profile.profile.practice_ability?.stars != null ? (
                  <span className="text-xs text-gray-400">
                    {'★'.repeat(profile.profile.practice_ability.stars)}
                    {'☆'.repeat(5 - profile.profile.practice_ability.stars)}
                    {' '}{profile.profile.practice_ability.score}/{profile.profile.practice_ability.max_score}
                  </span>
                ) : null}
              </div>
              {profile.profile.practice_ability?.score != null ? (
                <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-purple-400 rounded-full transition-all"
                    style={{ width: `${((profile.profile.practice_ability.score) / (profile.profile.practice_ability.max_score || 100)) * 100}%` }}
                  />
                </div>
              ) : (
                <p className="text-[10px] text-gray-400">完成画像后将补充此信息</p>
              )}
            </div>

            {/* Cognitive Style */}
            {profile.profile.cognitive_style?.tags && (
              <div className="mb-3">
                <span className="text-xs text-gray-500 block mb-1.5">认知风格</span>
                <div className="flex flex-wrap gap-1">
                  {profile.profile.cognitive_style.tags.map((tag) => (
                    <span key={tag} className="px-2 py-0.5 bg-primary-50 text-primary-600 text-[10px] rounded-full">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Resource Preferences */}
            {profile.profile.resource_preferences?.tags && (
              <div>
                <span className="text-xs text-gray-500 block mb-1.5">资源偏好</span>
                <div className="flex flex-wrap gap-1">
                  {profile.profile.resource_preferences.tags.map((tag) => (
                    <span key={tag} className="px-2 py-0.5 bg-purple-50 text-purple-600 text-[10px] rounded-full">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : null}

        {/* Section 4: Agent Status */}
        <div className="rounded-2xl bg-white border border-gray-100 p-4">
          <h3 className="text-sm font-semibold text-gray-800 mb-3">智能体状态</h3>
          <div className="space-y-2">
            {agents.map((agent) => {
              const Icon = agent.icon
              return (
                <div key={agent.name} className="flex items-center gap-2.5">
                  <div className="w-7 h-7 rounded-lg bg-primary-50 flex items-center justify-center shrink-0">
                    <Icon className="w-3.5 h-3.5 text-primary-500" />
                  </div>
                  <span className="text-xs text-gray-600 flex-1 truncate">{agent.label}</span>
                  <span className="w-1.5 h-1.5 rounded-full bg-green-400 shrink-0" />
                  <span className="text-[10px] text-green-600 font-medium">就绪</span>
                </div>
              )
            })}
          </div>
        </div>

        {/* Footer */}
        <div className="rounded-2xl bg-gradient-to-r from-primary-50 to-purple-50 border border-primary-100/50 p-3 text-center">
          <p className="text-xs text-primary-600 font-medium">智能体协同工作中</p>
        </div>

      </div>
    </aside>
  )
}
