export interface BadgeProps {
  children: React.ReactNode
  variant?: string
  className?: string
}

export const Badge = ({ children, variant = 'default', className }: BadgeProps): React.ReactNode => {
  const variants: Record<string, string> = {
    default: 'bg-gray-100 text-gray-800',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-amber-100 text-amber-800',
    danger: 'bg-red-100 text-red-800',
    info: 'bg-blue-100 text-blue-800',
  }
  const style = variants[variant as keyof typeof variants] ?? variants.default
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${style} ${className ?? ''}`}>
      {children}
    </span>
  )
}
