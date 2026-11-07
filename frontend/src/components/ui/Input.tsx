export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
}

export const Input = ({ label, error, className, id, ...props }: InputProps): React.ReactNode => {
  const inputId = id || label?.toLowerCase().replace(/\s+/g, '-')
  return (
    <div className="mb-4">
      {label && <label htmlFor={inputId} className="block text-sm font-medium text-gray-700 mb-1">{label}</label>}
      <input
        id={inputId}
        className={[
          'block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
          error ? 'border-red-500 focus:ring-red-500 focus:border-red-500' : 'border-gray-300',
          className,
        ].filter(Boolean).join(' ')}
        {...props}
        aria-invalid={error ? 'true' : 'false'}
      />
      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
    </div>
  )
}
