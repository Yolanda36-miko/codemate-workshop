import { useState, useMemo, useCallback, useEffect } from 'react'
import { ClipboardCheck } from 'lucide-react'
import TutorChatWindow from '../components/assessment/TutorChatWindow'
import ChallengePanel from '../components/assessment/ChallengePanel'
import AssessmentResourceDetailModal from '../components/assessment/AssessmentResourceDetailModal'
import type { AssessmentResource } from '../components/assessment/AssessmentResourceDetailModal'
import { inferConversationContextMock } from '../mock/assessment'
import { getUserProfile, getCourses } from '../services/api'
import { hasUsableProfile, buildPersonalizedPath } from '../services/personalizedPath'
import { mockLearningPath } from '../mock/path'
import type { PathNode } from '../types'
import {
  loadPathResources,
} from '../utils/pathResources'
import {
  loadPathNodeStatuses,
  mapResourcesToPathNodes,
} from '../utils/pathUtils'
import AnimatedSection from '../components/common/AnimatedSection'

const CURRENT_USER_ID = 1

export default function Assessment() {
  const [lastQuestion, setLastQuestion] = useState('')
  const [detailResource, setDetailResource] = useState<AssessmentResource | null>(null)
  const [profileLoading, setProfileLoading] = useState(true)

  // ---- Load profile and courses to build learning path ----
  const [pathNodes, setPathNodes] = useState<PathNode[]>([])

  useEffect(() => {
    async function loadPath() {
      try {
        const [profile, coursesRes] = await Promise.all([
          getUserProfile(CURRENT_USER_ID).catch(() => null),
          getCourses().catch(() => ({ courses: [] })),
        ])

        let nodes: PathNode[]
        if (hasUsableProfile(profile) && coursesRes.courses.length > 0) {
          const result = buildPersonalizedPath(profile!, coursesRes.courses)
          nodes = result?.nodes ?? mockLearningPath.nodes
        } else {
          nodes = mockLearningPath.nodes
        }

        // Apply saved node statuses and matched resources
        const savedStatuses = loadPathNodeStatuses()
        const pathItems = loadPathResources()
        const withStatuses = nodes.map((n) => ({
          ...n,
          status: (savedStatuses[n.id] || n.status) as 'pending' | 'in_progress' | 'completed',
        }))
        const mapped = mapResourcesToPathNodes(withStatuses)
        setPathNodes(mapped)
      } catch {
        // Use mock path as fallback
        const savedStatuses = loadPathNodeStatuses()
        const pathItems = loadPathResources()
        const withStatuses = mockLearningPath.nodes.map((n) => ({
          ...n,
          status: (savedStatuses[n.id] || n.status) as 'pending' | 'in_progress' | 'completed',
        }))
        const mapped = mapResourcesToPathNodes(withStatuses)
        setPathNodes(mapped)
      } finally {
        setProfileLoading(false)
      }
    }
    loadPath()
  }, [])

  // ---- Compute context from question + path nodes ----
  const context = useMemo(
    () => inferConversationContextMock(lastQuestion, pathNodes),
    [lastQuestion, pathNodes],
  )

  const handleViewResource = useCallback((resource: AssessmentResource) => {
    setDetailResource(resource)
  }, [])

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6 pb-12">
      {/* Header */}
      <AnimatedSection>
        <div className="flex items-center gap-2">
          <ClipboardCheck className="w-6 h-6 text-primary-600" />
          <h1 className="text-2xl font-bold text-gray-900">智能辅导与学习评估</h1>
        </div>
      </AnimatedSection>

      {/* Main layout */}
      <div className="grid grid-cols-12 gap-6">
        {/* Left: Chat Window (7 cols) */}
        <div className="col-span-7">
          <AnimatedSection delay={0.05}>
            <TutorChatWindow
              onQuestionAsked={setLastQuestion}
              onViewResource={handleViewResource}
              pathNodes={pathNodes.length > 0 ? pathNodes : undefined}
            />
          </AnimatedSection>
        </div>

        {/* Right: Challenge Panel (5 cols) */}
        <div className="col-span-5">
          <AnimatedSection delay={0.1} direction="right">
            <ChallengePanel
              context={context}
              pathNodes={pathNodes.length > 0 ? pathNodes : undefined}
              onViewResource={handleViewResource}
            />
          </AnimatedSection>
        </div>
      </div>

      {/* Resource Detail Modal */}
      <AssessmentResourceDetailModal
        resource={detailResource}
        onClose={() => setDetailResource(null)}
      />
    </div>
  )
}
