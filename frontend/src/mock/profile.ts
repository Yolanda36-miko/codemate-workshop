import type { StudentProfile, ProfileChatResponse, DiagnosisQuestion, BackendProfile, ConversationItem } from '../types'

// ========== Original mock data (kept for backward compatibility) ==========

export const mockProfileChat: ProfileChatResponse = {
  message: '你好！我是你的学习伙伴 CodeBuddy 🎓 让我们从了解你开始吧～你目前在学哪几门课程呢？',
  extracted_fields: {},
  missing_fields: [
    'current_courses', 'completed_courses', 'knowledge_basis',
    'learning_difficulty', 'programming_languages', 'learning_style',
    'learning_goals', 'resource_preference',
  ],
}

// ========== Backend Profile API mocks (Phase 6A) ==========

export const mockBackendProfile: BackendProfile = {
  id: null,
  user_id: 1,
  knowledge_base_score: null,
  practice_ability_score: null,
  cognitive_styles: null,
  error_patterns: null,
  learning_goals: null,
  resource_preferences: null,
  profile_summary: null,
  diagnosis_status: null,
  created_at: null,
  updated_at: null,
  source: 'local_cache',
}

export const mockConversations: ConversationItem[] = []

export const mockStudentProfile: StudentProfile = {
  student: {
    name: '当前用户',
    grade: '待完善',
    major: '暂未绑定专业',
    background:
      '基于对话与诊断生成的综合学习画像。',
  },
  profile: {
    knowledge_base: {
      label: '知识基础',
      max_score: 100,
      note: '暂未评估',
    },
    practice_ability: {
      label: '实践能力',
      max_score: 100,
      note: '暂未评估',
    },
    cognitive_style: {
      label: '认知风格',
      tags: ['图示优先', '示例驱动', '分步骤解释'],
    },
    weak_points: {
      label: '易错点特征',
      tags: ['递归出口', '函数调用顺序', '数组边界', '遍历顺序'],
    },
    learning_goals: {
      label: '学习目标',
      tags: ['掌握递归', '掌握数组和二叉树遍历', '完成课程练习'],
    },
    resource_preferences: {
      label: '资源偏好',
      tags: ['代码案例', '思维导图', '分层练习题', '简洁讲义'],
    },
  },
}

// ========== Chat flow state machine data ==========

export interface ChatRound {
  id: number
  question: string
  fieldLabel: string
  collects: string[]
  hint?: string
}

export const chatRounds: ChatRound[] = [
  {
    id: 0,
    question: '嗨！我是你的学习伙伴 CodeBuddy 🎓 让我们从了解你开始吧～你最近主要在学习哪些计算机专业课程？有没有哪些知识点让你觉得不太顺手？',
    fieldLabel: '当前课程与学习困难',
    collects: ['current_courses', 'learning_difficulty'],
    hint: '比如：程序设计基础、数据结构等',
  },
  {
    id: 1,
    question: '你现在主要会哪些编程语言呢？写代码时，更容易卡在理解思路、语法实现，还是调试错误上？',
    fieldLabel: '编程基础与卡点',
    collects: ['programming_languages', 'coding_blockers'],
    hint: '比如：Python、C 语言等',
  },
  {
    id: 2,
    question: '学习新知识时，你更喜欢哪种方式？图示讲解、代码示例、分步骤推导，还是项目案例？',
    fieldLabel: '认知风格',
    collects: ['cognitive_style'],
    hint: '可以多选哦～',
  },
  {
    id: 3,
    question: '这次你希望先达成什么目标呢？另外，你更喜欢什么样的学习资源？',
    fieldLabel: '学习目标与资源偏好',
    collects: ['learning_goals', 'resource_preference'],
    hint: '比如：掌握递归，喜欢代码案例和思维导图',
  },
]

export const ALL_FIELDS = [
  { key: 'current_courses', label: '当前学习课程' },
  { key: 'learning_difficulty', label: '学习困难' },
  { key: 'programming_languages', label: '编程语言基础' },
  { key: 'coding_blockers', label: '写代码卡点' },
  { key: 'cognitive_style', label: '认知风格' },
  { key: 'learning_goals', label: '学习目标' },
  { key: 'resource_preference', label: '资源偏好' },
  { key: 'diagnosis_result', label: '诊断题结果' },
]

export const liDemoAnswers = [
  '我在学习程序设计基础和数据结构与算法，对递归、数组操作和二叉树遍历感觉不太顺手。',
  '我会 Python 和 C 语言基础，写代码时更容易卡在理解思路上，经常需要参考示例代码。',
  '我更喜欢图示讲解和代码示例，分步骤推导也很好。',
  '我想掌握递归、数组和二叉树遍历，完成课程练习。我偏好代码案例、思维导图、分层练习题和简洁讲义。',
]

// ========== Diagnosis questions ==========

export const mockDiagnosisQuestions: DiagnosisQuestion[] = [
  {
    id: 'd1',
    question: '以下递归函数 foo(4) 的返回值是多少？\n\nint foo(int n) {\n  if (n <= 1) return 1;\n  return n * foo(n - 1);\n}',
    options: ['4', '12', '24', '120'],
    correct: '24',
    knowledge_point: '递归',
    explanation: 'foo(4) = 4 × foo(3) = 4 × 3 × foo(2) = 4 × 3 × 2 × foo(1) = 4 × 3 × 2 × 1 = 24',
  },
  {
    id: 'd2',
    question: '对于长度为 n 的数组 arr，以下哪个索引访问会导致数组越界？',
    options: ['arr[0]', 'arr[n-1]', 'arr[n]', 'arr[1]'],
    correct: 'arr[n]',
    knowledge_point: '数组边界',
    explanation: '数组索引从 0 开始，有效范围是 [0, n-1]。arr[n] 访问了第 n+1 个元素，会越界。',
  },
  {
    id: 'd3',
    question: '二叉树的前序遍历顺序是？',
    options: ['左→根→右', '根→左→右', '左→右→根', '根→右→左'],
    correct: '根→左→右',
    knowledge_point: '二叉树遍历',
    explanation: '前序遍历（Pre-order）的顺序：先访问根节点，再遍历左子树，最后遍历右子树。',
  },
]
