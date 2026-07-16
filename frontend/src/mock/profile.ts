import type { StudentProfile, ProfileChatResponse, DiagnosisQuestion, BackendProfile, ConversationItem } from '../types'

// ========== Profile chat mock ==========

export const mockProfileChat: ProfileChatResponse = {
  message: '嗨！我是你的学习伙伴 CodeBuddy 🎓 你在学习数据结构与算法时，感觉最吃力的模块是哪一个？递归调用栈、二叉树遍历、图算法（BFS/DFS）、排序算法，还是动态规划？',
  extracted_fields: {},
  missing_fields: [
    'learning_difficulties', 'current_difficulties', 'programming_language',
    'learned_courses', 'expression_preferences', 'learning_goal', 'error_prone_points',
  ],
}

// ========== Backend Profile API mocks ==========

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
    name: '',
    display_name: '',
    grade: '',
    major: '',
    background: '',
  },
  profile: {
    knowledge_base: {
      label: '知识基础',
      max_score: 100,
    },
    practice_ability: {
      label: '实践能力',
      max_score: 100,
    },
    programming_language: {
      label: '编程语言',
      tags: [],
    },
    learning_goal: {
      label: '学习目标',
      tags: [],
    },
    learning_difficulties: {
      label: '学习困难',
      tags: [],
    },
    expression_preferences: {
      label: '资源偏好',
      tags: [],
    },
  },
}

// ========== Diagnosis questions (DS-specific) ==========

export const mockDiagnosisQuestions: DiagnosisQuestion[] = [
  {
    id: 'd1',
    question: '以下递归函数 foo(4) 的返回值是多少？\n\nint foo(int n) {\n  if (n <= 1) return 1;\n  return n * foo(n - 1);\n}',
    options: ['4', '12', '24', '120'],
    correct: '24',
    knowledge_point: '递归',
    explanation: 'foo(4) = 4 × foo(3) = 4 × 3 × foo(2) = 4 × 3 × 2 × 1 = 24。递归终止条件是 n <= 1 时返回 1。',
  },
  {
    id: 'd2',
    question: '对于长度为 n 的数组 arr，以下哪个索引访问会导致数组越界？',
    options: ['arr[0]', 'arr[n-1]', 'arr[n]', 'arr[1]'],
    correct: 'arr[n]',
    knowledge_point: '数组边界',
    explanation: '数组索引从 0 开始，有效范围是 [0, n-1]。arr[n] 访问了第 n+1 个元素，会触发 IndexOutOfBounds 或越界错误。',
  },
  {
    id: 'd3',
    question: '二叉树的前序遍历顺序是？',
    options: ['左→根→右', '根→左→右', '左→右→根', '根→右→左'],
    correct: '根→左→右',
    knowledge_point: '二叉树遍历',
    explanation: '前序遍历（Pre-order）：先访问根节点，再递归遍历左子树，最后递归遍历右子树。中序是左→根→右，后序是左→右→根。',
  },
]
