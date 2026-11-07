export const UnauthorizedPage = (): React.ReactNode => (
  <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
    <div className="max-w-md w-full bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
      <h2 className="text-xl font-bold text-gray-900 mb-2">Not authorized</h2>
      <p className="text-gray-600 mb-6">You do not have permission to view this page.</p>
      <a href="/dashboard" className="text-indigo-600 hover:text-indigo-500 font-medium">Back to dashboard</a>
    </div>
  </div>
)

export const NotFoundPage = (): React.ReactNode => (
  <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
    <div className="max-w-md w-full bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
      <h2 className="text-xl font-bold text-gray-900 mb-2">Page not found</h2>
      <p className="text-gray-600 mb-6">The requested page does not exist.</p>
      <a href="/dashboard" className="text-indigo-600 hover:text-indigo-500 font-medium">Back to dashboard</a>
    </div>
  </div>
)
