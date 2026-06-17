// ========== Student & Profile ==========

export interface StudentInfo {
  name: string
  grade: string
  major: string
  background: string
}

export interface ProfileDimension {
  label: string
  stars?: number
  score?: number
  max_score?: number
  note?: string
  tags?: string[]
}

export interface StudentProfile {
  student: StudentInfo
  profile: Record<string, ProfileDimension>
}

export interface ProfileChatResponse {
  message: string
  extracted_fields: Record<string, unknown>
  missing_fields: string[]
}

// ========== Backend Profile (Phase 6A) ==========

export interface BackendProfile {
  id: number | null
  user_id: number
  knowledge_base_score: number | null
  practice_ability_score: number | null
  cognitive_styles: string | null   // JSON-encoded array of tags
  error_patterns: string | null     // JSON-encoded array of tags
  learning_goals: string | null     // JSON-encoded array of tags
  resource_preferences: string | null // JSON-encoded array of tags
  profile_summary: string | null
  diagnosis_status: string | null
  created_at: string | null
  updated_at: string | null
  source: string
}

export interface ProfileUpdatePayload {
  knowledge_base_score?: number
  practice_ability_score?: number
  cognitive_styles?: string
  error_patterns?: string
  learning_goals?: string
  resource_preferences?: string
  profile_summary?: string
  diagnosis_status?: string
}

export interface ConversationItem {
  id: number
  user_id: number
  role: string
  message: string
  extracted_fields: string | null
  missing_fields: string | null
  created_at: string | null
}

export interface ConversationCreateRequest {
  role: string
  message: string
  extracted_fields?: string
  missing_fields?: string
}

// ========== Courses ==========

export interface Course {
  id: string
  name: string
  description: string
  summary: string
  stage: string
  prerequisites: string[]
  related_courses: string[]
  knowledge_points: string[]
  resource_types: string[]
  positioning?: '重点演示' | '课程群支撑'
  typical_difficulties?: string[]
  learning_suggestion?: string
  color?: string
}

export interface CourseListResponse {
  courses: Course[]
}

// ========== Resources ==========

export interface ResourceSection {
  heading: string
  content: string
  codeBlock?: string
  language?: string
}

export interface ResourceCard {
  id: string
  title: string
  type: string
  course: string
  knowledge_point: string
  difficulty: string
  language: string
  teaching_style?: string
  summary: string
  match_reason?: string
  detailed_content?: string
  sections?: ResourceSection[]
  key_concepts?: string[]
  learning_tips?: string[]
  learning_objectives?: string
  recommended_usage?: string
  profile_dimension?: string
  next_steps?: string
  estimated_time?: string
  student_name?: string
  generated_at?: string
  added_to_path?: boolean
}

export interface ResourceGenerateResponse {
  resource_cards: ResourceCard[]
}

export interface ResourceGenerateParams {
  course_id: string
  learning_topic: string
  difficulty?: string
  language?: string
  teaching_style?: string
  resource_types?: string[]
}

export interface SaveResourcePayload {
  custom_title: string
  topic: string
  course_name: string
  resource_type: string
  estimated_time: string
  note: string
  purpose: string
  priority: string
}

export interface SavedPackageItem {
  id: number
  user_id: number
  custom_title: string
  topic: string
  course_name: string
  resource_type: string
  estimated_time: string
  purpose: string
  priority: string
  note: string
  status: string
  detail?: string
  created_at?: string
}

// ========== Learning Path ==========

export interface PathResourceItem {
  resourceId: string
  title: string
  type: string
  estimatedTime: string
  topic: string
  course: string
  language: string
  note: string
  purpose: '课前预习' | '课堂理解' | '课后练习' | '项目实践' | '错题复习' | ''
  priority: '必学' | '推荐' | '拓展' | ''
}

export interface PathNodeResource {
  resourceId: string
  title: string
  type: string
  estimatedTime: string
  source: 'resource_package' | 'default'
}

export interface PathNode {
  id: string
  name: string
  course: string
  goal: string
  duration: string
  status: 'pending' | 'in_progress' | 'completed'
  keywords: string[]
  learningObjectives: string[]
  defaultResources: PathNodeResource[]
  matchedResources: PathNodeResource[]
  growthDimensions: { label: string; value: number }[]
  taskDescription: string
  /** Phase 9: 路径阶段 (基础概念 | 核心理解 | 代码实现 | 练习巩固 | 项目应用) */
  stage: string
  /** Phase 9: 个性化推荐理由，画像不足时显示通用说明 */
  reason: string
}

export interface PersonalizedPathResult {
  name: string
  nodes: PathNode[]
  /** Phase 9: 个性化依据摘要，画像不足时为 null */
  personalizedBasis: string | null
  /** Phase 9: 使用了哪些画像字段 */
  profileFieldsUsed: string[]
}

export interface LearningPathResponse {
  name: string
  nodes: PathNode[]
}

// ========== Assessment ==========

export interface DiagnosisQuestion {
  id: string
  question: string
  options: string[]
  correct: string
  knowledge_point: string
  explanation: string
}

export interface AssessmentResult {
  score: number
  total: number
  growth: Record<string, number>
  badges: string[]
  remedial_resources: Array<{
    knowledge_point: string
    reason: string
  }>
}

export interface TutorChatResponse {
  greeting: string
  approach: string
  steps: string[]
  code_example: string | null
  recommended_resources: Array<{ title: string; url: string }>
  suggested_exercise: string
}

// ========== Assessment Context ==========

export interface ConversationContext {
  currentQuestion: string
  pathNode: string
  resourceCount: number
  weakPoints: string[]
  inferredTopics: string[]
  matchedPathNodeId?: string
  matchedPathNodeTitle?: string
  matchedPathNodeStage?: string
  pathNodeMatchNote?: string
}
