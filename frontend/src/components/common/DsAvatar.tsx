import type { HTMLAttributes } from 'react'

type DsAvatarSize = 'sm' | 'md' | 'lg' | number

interface DsAvatarProps extends HTMLAttributes<HTMLDivElement> {
  size?: DsAvatarSize
  label?: string
  showLabel?: boolean
  active?: boolean
  [key: string]: unknown
}

const sizeClassMap: Record<'sm' | 'md' | 'lg', string> = {
  sm: 'h-8 w-8 text-sm',
  md: 'h-10 w-10 text-base',
  lg: 'h-12 w-12 text-lg',
}

export default function DsAvatar({
  size = 'md',
  label = '小栈',
  showLabel = false,
  active = false,
  className = '',
  ...rest
}: DsAvatarProps) {
  const numericSize = typeof size === 'number'
  const sizeClass = numericSize ? '' : sizeClassMap[size] ?? sizeClassMap.md

  return (
    <div className="flex items-center gap-2">
      <div
        className={[
          'inline-flex shrink-0 items-center justify-center rounded-full border bg-white font-semibold text-slate-700 shadow-sm',
          active ? 'border-indigo-300 ring-2 ring-indigo-100' : 'border-slate-200',
          sizeClass,
          className,
        ]
          .filter(Boolean)
          .join(' ')}
        style={
          numericSize
            ? {
                width: size,
                height: size,
              }
            : undefined
        }
        aria-label={label}
        {...rest}
      >
        <span aria-hidden="true">栈</span>
      </div>

      {showLabel && <span className="text-sm font-medium text-slate-700">{label}</span>}
    </div>
  )
}
