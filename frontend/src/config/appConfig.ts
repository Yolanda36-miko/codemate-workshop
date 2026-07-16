/**
 * Application configuration — reads from Vite env variables.
 *
 * VITE_DEMO_MODE:
 *   "true"  → Demo Mode: Li classmate example data and demo entry points are visible
 *   other   → Real Mode: no default demo data, student starts from scratch
 */

const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true'

export function isDemoMode(): boolean {
  return DEMO_MODE
}

/** Demo student — used only in Demo Mode */
export const demoCurrentUser = {
  name: '小栈',
  role: '学习者',
  avatarText: '学',
}

/** Get current user display info. Uses default values — no longer synced from Profile. */
export function getCurrentUserDisplay(): {
  name: string
  role: string
  avatarText: string
} {
  if (isDemoMode()) return demoCurrentUser
  return { name: '小栈', role: '数据结构学习者', avatarText: '栈' }
}

/** Get the student name for display in resource/agent copy. */
export function getStudentDisplayName(): string {
  return '小栈'
}
