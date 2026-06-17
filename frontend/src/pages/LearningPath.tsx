import { useState, useMemo, useCallback, useEffect } from 'react'
import { GitBranch, BookOpen } from 'lucide-react'
import { Link } from 'react-router-dom'
import { getUserProfile, getCourses } from '../services/api'
import { hasUsableProfile, buildPersonalizedPath } from '../services/personalizedPath'
import { mockLearningPath } from '../mock/path'
import type { PathNode, PathResourceItem, PathNodeResource, BackendProfile, Course } from '../types'
import {
  loadPathResources,
  savePathResources,
  addPathResource,
  removePathResource,
} from '../utils/pathResources'
import {
  loadPathNodeStatuses,
  updatePathNodeStatus,
  mapResourcesToPathNodes,
  getCompletedCount,
} from '../utils/pathUtils'
import PathOverview from '../components/path/PathOverview'
import PathTimeline from '../components/path/PathTimeline'
import PathNodeDetail from '../components/path/PathNodeDetail'
import PathResourcePanel from '../components/path/PathResourcePanel'
import PathResourceDetailModal from '../components/path/PathResourceDetailModal'
import AnimatedSection from '../components/common/AnimatedSection'

const CURRENT_USER_ID = 1
let resourceIdCounter = 9000

export default function LearningPath() {
  const [pathItems, setPathItems] = useState<PathResourceItem[]>(() => loadPathResources())
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [detailResource, setDetailResource] = useState<PathResourceItem | PathNodeResource | null>(null)
  const [toast, setToast] = useState<string | null>(null)
  const [profile, setProfile] = useState<BackendProfile | null>(null)
  const [profileLoading, setProfileLoading] = useState(true)
  const [courses, setCourses] = useState<Course[]>([])

  const showToast = useCallback((msg: string) => {
    setToast(msg)
    setTimeout(() => setToast(null), 2000)
  }, [])

  // Load profile and courses on mount
  useEffect(() => {
    getUserProfile(CURRENT_USER_ID)
      .then((p) => setProfile(p))
      .catch(() => setProfile(null))
      .finally(() => setProfileLoading(false))

    getCourses()
      .then((res) => setCourses(res.courses))
      .catch(() => setCourses([]))
  }, [])

  // Generate path: personalized if profile usable, fallback to generic reference path
  const learningPath = useMemo(() => {
    if (!profileLoading && hasUsableProfile(profile) && courses.length > 0) {
      const personalized = buildPersonalizedPath(profile!, courses)
      if (personalized) return personalized
    }
    // Fallback: generic reference path
    return { ...mockLearningPath, name: '通用参考路径' }
  }, [profile, profileLoading, courses])

  const usable = !profileLoading && hasUsableProfile(profile)

  // Compute nodes with statuses and matched resources
  const nodes = useMemo(() => {
    const savedStatuses = loadPathNodeStatuses()
    const withStatuses = learningPath.nodes.map((n) => ({
      ...n,
      status: savedStatuses[n.id] || n.status,
    }))
    return mapResourcesToPathNodes(withStatuses)
  }, [learningPath, pathItems])

  const selectedNode = useMemo(() => nodes.find((n) => n.id === selectedId) ?? null, [nodes, selectedId])
  const completedCount = useMemo(() => getCompletedCount(nodes), [nodes])

  // Track which system resources have been added to package (for "已加入" state)
  const addedResourceIds = useMemo(() => {
    const ids = new Set<string>()
    for (const item of pathItems) {
      ids.add(item.resourceId)
    }
    return ids
  }, [pathItems])

  const handleStatusChange = useCallback((nodeId: string, status: 'pending' | 'in_progress' | 'completed') => {
    updatePathNodeStatus(nodeId, status)
    setPathItems((prev) => [...prev]) // trigger re-render to refresh nodes
  }, [])

  const handleStartLearning = useCallback(() => {
    const firstPending = nodes.find((n) => n.status !== 'completed')
    if (firstPending) {
      setSelectedId(firstPending.id)
      if (firstPending.status === 'pending') {
        handleStatusChange(firstPending.id, 'in_progress')
      }
    }
  }, [nodes, handleStatusChange])

  const handleAddToPackage = useCallback((resource: PathNodeResource) => {
    const item: PathResourceItem = {
      resourceId: `pkg-${resourceIdCounter++}`,
      title: resource.title,
      type: resource.type,
      estimatedTime: resource.estimatedTime,
      topic: '',
      course: '',
      language: '',
      note: '',
      purpose: '',
      priority: '',
    }
    const updated = addPathResource(item)
    setPathItems(updated)
    showToast('已加入学习路径资源包')
  }, [showToast])

  const handleRemoveFromPackage = useCallback((resourceId: string) => {
    const updated = removePathResource(resourceId)
    setPathItems(updated)
    showToast('已从资源包移除')
  }, [])

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6 pb-12">
      {/* Toast */}
      {toast && (
        <div className="fixed top-4 right-4 z-[100] px-4 py-2 rounded-xl bg-gray-900 text-white text-xs shadow-lg animate-fade-in">
          {toast}
        </div>
      )}

      {/* Header */}
      <AnimatedSection>
        <div className="flex items-center gap-2">
          <GitBranch className="w-6 h-6 text-primary-600" />
          <h1 className="text-2xl font-bold text-gray-900">
            {usable ? 'CodeBuddy 为你定制的学习路径' : '学习路径规划'}
          </h1>
          {!profileLoading && !usable && (
            <span className="text-[10px] text-gray-400 ml-2">— 画像不足，显示通用参考路径</span>
          )}
        </div>
      </AnimatedSection>

      {/* Profile insufficient banner */}
      {!profileLoading && !usable && (
        <AnimatedSection delay={0.03}>
          <div className="bg-gradient-to-r from-gray-50 to-blue-50 rounded-2xl border border-gray-100 px-5 py-5 text-center">
            <BookOpen className="w-8 h-8 text-gray-300 mx-auto mb-3" />
            <p className="text-sm font-semibold text-gray-700 mb-1">请先完成学习画像，以生成个性化学习路径。</p>
            <p className="text-xs text-gray-500 mb-4">CodeBuddy 将根据你的学习画像，为你生成专属的阶段性学习路线。</p>
            <Link
              to="/profile"
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-primary-500 text-white text-sm font-medium hover:bg-primary-600 transition-colors"
            >
              去完善学习画像
            </Link>
          </div>
        </AnimatedSection>
      )}

      {profileLoading ? (
        <AnimatedSection delay={0.05}>
          <div className="bg-white rounded-2xl shadow-card border border-gray-100 p-8 animate-pulse">
            <div className="h-5 bg-gray-200 rounded w-64 mx-auto mb-3" />
            <div className="h-4 bg-gray-200 rounded w-96 mx-auto" />
          </div>
        </AnimatedSection>
      ) : (
        <>
          {/* Overview — full width */}
          <AnimatedSection delay={0.05}>
            <PathOverview
              pathName={learningPath.name}
              nodes={nodes}
              onStartLearning={handleStartLearning}
            />
          </AnimatedSection>

          {/* Two-column layout: Timeline (left) + Detail & Resources (right) */}
          <div className="grid grid-cols-12 gap-6">
            {/* Left: Timeline */}
            <div className="col-span-7">
              <AnimatedSection delay={0.1}>
                <div className="bg-white rounded-2xl shadow-card border border-gray-100 p-5">
                  <h3 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
                    <GitBranch className="w-4 h-4 text-primary-500" />
                    学习路径时间轴
                    <span className="text-[10px] text-gray-400 font-normal">
                      ({completedCount}/{nodes.length} 已完成)
                    </span>
                  </h3>
                  <PathTimeline
                    nodes={nodes}
                    selectedId={selectedId}
                    onSelect={(node) => setSelectedId(node.id)}
                    onStatusChange={handleStatusChange}
                  />
                </div>
              </AnimatedSection>
            </div>

            {/* Right: Node Detail + Resource Panel */}
            <div className="col-span-5">
              <div className="sticky top-4 space-y-3" style={{ maxHeight: 'calc(100vh - 100px)', overflowY: 'auto' }}>
                <AnimatedSection delay={0.15} direction="right">
                  <PathNodeDetail
                    node={selectedNode}
                    addedResourceIds={addedResourceIds}
                    onStatusChange={handleStatusChange}
                    onViewResource={setDetailResource}
                    onAddToPackage={handleAddToPackage}
                  />
                </AnimatedSection>

                <AnimatedSection delay={0.2} direction="right">
                  <PathResourcePanel
                    items={pathItems}
                    onViewResource={setDetailResource}
                    onRemove={handleRemoveFromPackage}
                  />
                </AnimatedSection>

                {/* Compact status overview */}
                <AnimatedSection delay={0.25} direction="right">
                  <div className="bg-white rounded-2xl p-3 shadow-card border border-gray-100">
                    <div className="grid grid-cols-3 gap-2">
                      {[
                        { label: '未开始', count: nodes.filter((n) => n.status === 'pending').length, color: 'text-gray-400' },
                        { label: '学习中', count: nodes.filter((n) => n.status === 'in_progress').length, color: 'text-primary-500' },
                        { label: '已完成', count: nodes.filter((n) => n.status === 'completed').length, color: 'text-green-500' },
                      ].map((s) => (
                        <div key={s.label} className="text-center py-1.5 rounded-xl bg-gray-50">
                          <p className={`text-base font-bold ${s.color}`}>{s.count}</p>
                          <p className="text-[9px] text-gray-400">{s.label}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </AnimatedSection>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Resource Detail Modal */}
      <PathResourceDetailModal
        resource={detailResource}
        onClose={() => setDetailResource(null)}
      />
    </div>
  )
}
