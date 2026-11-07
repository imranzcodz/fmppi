export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  size?: 'sm' | 'default'
  loading?: boolean
}

export const Button = ({ variant = 'primary', size = 'default', loading, children, className, ...props }: ButtonProps): React.ReactNode => {
  const base =
    'inline-flex items-center justify-center rounded-md border border-transparent px-4 py-2 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none'
  const variants: Record<string, string> = {
    primary: 'bg-indigo-600 text-white focus:ring-indigo-500 hover:bg-indigo-700',
    secondary: 'bg-gray-100 text-gray-900 focus:ring-gray-500 hover:bg-gray-200',
    danger: 'bg-red-600 text-white focus:ring-red-500 hover:bg-red-700',
    ghost: 'bg-transparent text-gray-700 focus:ring-gray-500 hover:bg-gray-100',
  }
  const sizes: Record<string, string> = {
    sm: 'px-3 py-1 text-xs',
    default: 'px-4 py-2 text-sm',
  }
  return (
    <button className={[base, variants[variant], sizes[size], className].filter(Boolean).join(' ')} disabled={loading} {...props}>
      {loading && <span className="mr-2">Loading...</span>}
      {children}
    </button>
  )
}
