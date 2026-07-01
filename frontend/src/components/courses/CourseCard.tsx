import { motion } from 'framer-motion'
import { Star } from 'lucide-react'
import type { Course } from '../../types'

interface CourseCardProps {
  course: Course
  isSelected: boolean
  isHovered: boolean
  anyHovered: boolean
  onClick: () => void
  onHover: (id: string | null) => void
  index: number
  isPriority?: boolean
}

export default function CourseCard({
  course,
  isSelected,
  isHovered,
  anyHovered,
  onClick,
  onHover,
  index,
  isPriority = false,
}: CourseCardProps) {
  const isDimmed = anyHovered && !isHovered
  const keywords = course.knowledge_points.slice(0, 5)

  return (
    <motion.button
      onClick={onClick}
      onMouseEnter={() => onHover(course.id)}
      onMouseLeave={() => onHover(null)}
      className={`relative text-left rounded-2xl p-4 border bg-white
        ${isSelected
          ? 'border-primary-300 shadow-card ring-1 ring-primary-200 bg-primary-50/50'
          : 'border-gray-100 shadow-card'
        }
      `}
      initial={{ opacity: 0, y: 12 }}
      animate={{
        opacity: isDimmed ? 0.6 : 1,
        y: 0,
        scale: isHovered ? 1.05 : isDimmed ? 0.97 : 1,
        filter: isDimmed ? 'blur(1px)' : 'blur(0px)',
      }}
      transition={{
        duration: 0.25,
        ease: 'easeOut',
      }}
      style={{
        zIndex: isHovered ? 20 : isSelected ? 1 : 0,
        boxShadow: isHovered
          ? '0 12px 40px rgba(124, 58, 237, 0.18), 0 0 0 1px rgba(124, 58, 237, 0.3)'
          : undefined,
      }}
    >
      {/* Course name + priority star */}
      <div className="flex items-center gap-1.5 mb-2">
        <h3 className="text-sm font-semibold text-gray-800 truncate">{course.name}</h3>
        {isPriority && <Star className="w-3 h-3 text-amber-400 fill-amber-400 shrink-0" />}
      </div>

      {/* Priority badge — only shown when profile matches */}
      {isPriority && (
        <div className="flex items-center gap-1.5 mb-2.5">
          <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-amber-100 text-amber-700 font-medium">
            建议优先学习
          </span>
        </div>
      )}

      {/* Keyword chips */}
      <div className="flex flex-wrap gap-1 mb-2.5">
        {keywords.map((kp) => (
          <span
            key={kp}
            className="px-1.5 py-0.5 bg-gray-50 rounded-full text-[10px] text-gray-600 border border-gray-100"
          >
            {kp}
          </span>
        ))}
      </div>

      {/* One-line summary */}
      <p className="text-[11px] text-gray-400 leading-relaxed">
        {course.summary}
      </p>
    </motion.button>
  )
}
