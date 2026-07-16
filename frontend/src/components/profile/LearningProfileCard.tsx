import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Star, ArrowRight, FileText, GitBranch } from 'lucide-react'
import DsAvatar from '../common/DsAvatar'
import type { StudentProfile, ProfileDimension } from '../../types'

interface LearningProfileCardProps {
  profile: StudentProfile
}

export default function LearningProfileCard({ profile }: LearningProfileCardProps) {
  const { student, profile: dims } = profile

  return (
    <div className="space-y-4">
      {/* Student header */}
      <motion.div
        className="bg-white rounded-2xl p-5 shadow-card border border-gray-100"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className="flex items-center gap-3 mb-3">
          <DsAvatar size="lg" />
          <div>
            <h3 className="font-semibold text-gray-800">
              {student.display_name || student.name || '小栈'}
            </h3>
          </div>
        </div>
        <p className="text-sm text-gray-500 leading-relaxed">{student.background}</p>
      </motion.div>

      {/* Six dimensions grid */}
      <div className="grid grid-cols-2 gap-4">
        {Object.entries(dims).map(([key, dim], i) => (
          <DimensionCard key={key} dim={dim} index={i} />
        ))}
      </div>

      {/* CTA buttons */}
      <motion.div
        className="flex items-center gap-3 pt-2"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <Link
          to="/resources"
          className="flex-1 flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-primary-500 to-primary-700 text-white text-sm font-medium shadow-md hover:shadow-glow hover:-translate-y-0.5 transition-all"
        >
          <FileText className="w-4 h-4" />
          生成个性化资源
          <ArrowRight className="w-4 h-4" />
        </Link>
        <Link
          to="/path"
          className="flex-1 flex items-center justify-center gap-2 px-5 py-3 rounded-xl border border-primary-200 text-primary-700 text-sm font-medium bg-white hover:shadow-card hover:-translate-y-0.5 transition-all"
        >
          <GitBranch className="w-4 h-4" />
          规划学习路径
          <ArrowRight className="w-4 h-4" />
        </Link>
      </motion.div>
    </div>
  )
}

function DimensionCard({ dim, index }: { dim: ProfileDimension; index: number }) {
  const hasScore = dim.score !== undefined && dim.score !== null

  return (
    <motion.div
      className="bg-white rounded-2xl p-4 shadow-card border border-gray-100 hover:shadow-card-hover transition-shadow"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.15 + index * 0.08, duration: 0.4 }}
    >
      <h4 className="text-sm font-semibold text-gray-800 mb-3">{dim.label}</h4>

      {/* Stars + Score for quantifiable dimensions */}
      {dim.stars !== undefined && dim.stars !== null ? (
        <div className="flex items-center gap-1 mb-2">
          {[1, 2, 3, 4, 5].map((s) => (
            <Star
              key={s}
              className={`w-4 h-4 ${s <= dim.stars! ? 'text-amber-400 fill-amber-400' : 'text-gray-200'}`}
            />
          ))}
          {hasScore && (
            <span className="ml-2 text-sm font-semibold text-gray-700">
              {dim.score}<span className="text-xs text-gray-400 font-normal">/{dim.max_score}</span>
            </span>
          )}
        </div>
      ) : hasScore ? (
        /* Score without stars */
        <div className="mb-2">
          <span className="text-sm font-semibold text-gray-700">
            {dim.score}<span className="text-xs text-gray-400 font-normal">/{dim.max_score}</span>
          </span>
        </div>
      ) : null}

      {/* Progress bar for scored dimensions */}
      {hasScore && dim.max_score !== undefined && (
        <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden mb-2">
          <div
            className="h-full rounded-full transition-all duration-700"
            style={{
              width: `${(dim.score! / dim.max_score) * 100}%`,
              background: dim.stars && dim.stars >= 4
                ? 'linear-gradient(90deg, #8b5cf6, #7c3aed)'
                : 'linear-gradient(90deg, #a78bfa, #8b5cf6)',
            }}
          />
        </div>
      )}

      {/* Note */}
      {dim.note && (
        <p className="text-xs text-primary-500 mb-2 bg-primary-50 px-2 py-0.5 rounded-full inline-block">
          {dim.note}
        </p>
      )}

      {/* Tags */}
      {dim.tags && dim.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {dim.tags.map((tag) => (
            <span
              key={tag}
              className="px-2 py-0.5 bg-gray-50 rounded-full text-[11px] text-gray-600 border border-gray-100"
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Empty state hint: only show when no score, no tags, no stars */}
      {!hasScore && dim.stars === undefined && (!dim.tags || dim.tags.length === 0) && (
        <p className="text-xs text-gray-400">完成更多对话后将补充此项信息</p>
      )}
    </motion.div>
  )
}
