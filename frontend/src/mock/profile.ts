import type { StudentProfile, ProfileChatResponse, DiagnosisQuestion, BackendProfile, ConversationItem } from '../types'

// ========== Original mock data (kept for backward compatibility) ==========

export const mockProfileChat: ProfileChatResponse = {
  message: '你好！我是你的学习伙伴 CodeBuddy 🎓 你现在正在学习数据结构与算法吧？感觉最吃力的模块是哪一个呢——复杂度分析、递归、树、还是图？先跟我聊聊你的学习情况吧～',
  extracted_fields: {},
  missing_fields: [
    'current_courses', 'completed_courses', 'learning_difficulty',
    'programming_languages', 'coding_blockers', 'cognitive_style',
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
