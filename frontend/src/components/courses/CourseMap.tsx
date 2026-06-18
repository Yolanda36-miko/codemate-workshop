import { motion } from 'framer-motion'
import type { Course } from '../../types'

interface CourseMapProps {
  courses: Course[]
  selectedId: string | null
  onSelect: (id: string) => void
}

interface MapNode {
  id: string
  x: number
  y: number
  w: number
  h: number
  cx: number
  cy: number
}

interface MapEdge {
  from: string
  to: string
  highlight?: boolean
}

const NODES: MapNode[] = [
  { id: 'programming-basics', x: 8, y: 16, w: 156, h: 82, cx: 86, cy: 57 },
  { id: 'data-structures', x: 300, y: 16, w: 156, h: 82, cx: 378, cy: 57 },
  { id: 'database-system', x: 592, y: 16, w: 150, h: 82, cx: 667, cy: 57 },
  { id: 'computer-organization', x: 8, y: 188, w: 156, h: 82, cx: 86, cy: 229 },
  { id: 'operating-system', x: 280, y: 188, w: 156, h: 82, cx: 358, cy: 229 },
  { id: 'computer-network', x: 560, y: 188, w: 156, h: 82, cx: 638, cy: 229 },
]

const EDGES: MapEdge[] = [
  { from: 'programming-basics', to: 'data-structures', highlight: true },
  { from: 'programming-basics', to: 'computer-organization' },
  { from: 'data-structures', to: 'operating-system' },
  { from: 'data-structures', to: 'database-system' },
  { from: 'computer-organization', to: 'operating-system' },
  { from: 'operating-system', to: 'computer-network' },
]

function findNode(id: string): MapNode {
  return NODES.find((n) => n.id === id)!
}

export default function CourseMap({ courses, selectedId, onSelect }: CourseMapProps) {
  const courseMap = new Map(courses.map((c) => [c.id, c]))

  return (
    <div className="relative w-full" style={{ height: 280 }}>
      {/* SVG connection lines */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 0 }}>
        <defs>
          <marker id="arrow-normal" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 10 5 L 0 9 z" fill="#c4b5fd" />
          </marker>
          <marker id="arrow-highlight" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
            <path d="M 0 1 L 10 5 L 0 9 z" fill="#7c3aed" />
          </marker>
        </defs>
        {EDGES.map((edge) => {
          const fn = findNode(edge.from)
          const tn = findNode(edge.to)
          if (!fn || !tn) return null
          return (
            <line
              key={`${edge.from}-${edge.to}`}
              x1={fn.cx}
              y1={fn.cy}
              x2={tn.cx}
              y2={tn.cy}
              stroke={edge.highlight ? '#7c3aed' : '#c4b5fd'}
              strokeWidth={edge.highlight ? 2.5 : 1.5}
              strokeDasharray={edge.highlight ? 'none' : '6,3'}
              markerEnd={edge.highlight ? 'url(#arrow-highlight)' : 'url(#arrow-normal)'}
              opacity={edge.highlight ? 1 : 0.7}
            />
          )
        })}
      </svg>

      {/* Node cards */}
      {NODES.map((node) => {
        const course = courseMap.get(node.id)
        if (!course) return null
        const isSelected = node.id === selectedId

        return (
          <motion.button
            key={node.id}
            onClick={() => onSelect(node.id)}
            className={`absolute text-left rounded-2xl px-3.5 py-2.5 border transition-all duration-200 ${
              isSelected
                ? 'bg-primary-50 border-primary-300 shadow-md ring-1 ring-primary-200'
                : 'bg-white border-gray-200 shadow-card hover:shadow-card-hover hover:-translate-y-0.5'
            }`}
            style={{
              left: node.x,
              top: node.y,
              width: node.w,
              height: node.h,
              zIndex: isSelected ? 2 : 1,
            }}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.05 * NODES.indexOf(node), duration: 0.35 }}
            whileHover={{ y: -2 }}
          >
            <div className="flex items-center gap-1.5 mb-0.5">
              <h3 className="text-xs font-semibold text-gray-800 truncate">{course.name}</h3>
            </div>
            <p className="text-[10px] text-gray-400 mb-1.5">{course.stage}</p>
            <div className="flex flex-wrap gap-1">
              {course.knowledge_points.slice(0, 2).map((kp) => (
                <span
                  key={kp}
                  className="px-1.5 py-0.5 bg-gray-50 rounded-full text-[9px] text-gray-500 border border-gray-100"
                >
                  {kp}
                </span>
              ))}
              {course.knowledge_points.length > 2 && (
                <span className="text-[9px] text-gray-400">+{course.knowledge_points.length - 2}</span>
              )}
            </div>
          </motion.button>
        )
      })}

      {/* Highlight label */}
      <div
        className="absolute flex items-center gap-1"
        style={{ left: 175, top: 72 }}
      >
        <span className="text-[9px] text-primary-500 font-medium bg-primary-50 px-1.5 py-0.5 rounded whitespace-nowrap">
          核心先修
        </span>
      </div>
    </div>
  )
}
