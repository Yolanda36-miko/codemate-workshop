import { NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  UserRound,
  BookOpen,
  FileText,
  GitBranch,
  ClipboardCheck,
  Sparkles,
} from 'lucide-react'
import { getCurrentUserDisplay } from '../../config/appConfig'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: '首页' },
  { to: '/profile', icon: UserRound, label: '学习画像' },
  { to: '/courses', icon: BookOpen, label: '模块中心' },
  { to: '/resources', icon: FileText, label: '资源生成' },
  { to: '/path', icon: GitBranch, label: '学习路径' },
  { to: '/assessment', icon: ClipboardCheck, label: '辅导评估' },
]

export default function Sidebar() {
  const location = useLocation()
  const currentUser = getCurrentUserDisplay()

  return (
    <aside className="fixed left-0 top-0 h-screen w-[240px] bg-white border-r border-gray-200 flex flex-col z-40 shadow-sm">
      {/* Logo */}
      <div className="h-16 flex items-center gap-3 px-5 border-b border-gray-100">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-400 to-primary-700 flex items-center justify-center shadow-sm">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-sm font-bold text-gray-800 leading-tight">CodeMate</h1>
          <p className="text-[11px] text-gray-400 leading-tight">智学工坊</p>
        </div>
      </div>

      {/* Nav Links */}
      <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = item.to === '/'
            ? location.pathname === '/'
            : location.pathname.startsWith(item.to)
          const Icon = item.icon

          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'bg-primary-50 text-primary-700 shadow-sm'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <Icon className={`w-5 h-5 ${isActive ? 'text-primary-600' : 'text-gray-400'}`} />
              <span>{item.label}</span>
            </NavLink>
          )
        })}
      </nav>

      {/* Footer — Current User */}
      <div className="px-4 py-3 border-t border-gray-100">
        <div className="flex items-center gap-2.5 px-3 py-2.5 rounded-xl hover:bg-gray-50 transition-colors cursor-default">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center text-white text-xs font-semibold shadow-sm shrink-0">
            {currentUser.avatarText}
          </div>
          <div className="min-w-0">
            <p className="text-xs font-semibold text-gray-800">{currentUser.name}</p>
            <p className="text-[10px] text-gray-400">{currentUser.role}</p>
          </div>
        </div>
      </div>
    </aside>
  )
}
