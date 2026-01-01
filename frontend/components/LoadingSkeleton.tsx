export default function LoadingSkeleton() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 py-12 px-4">
      <div className="container mx-auto max-w-4xl">
        {/* Header Skeleton */}
        <div className="flex items-center justify-between mb-8 animate-pulse">
          <div className="h-8 w-32 bg-gray-200 rounded"></div>
          <div className="h-10 w-10 bg-gray-200 rounded-full"></div>
        </div>

        {/* Main Card Skeleton */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-6 animate-pulse">
          <div className="flex items-center justify-center mb-6">
            <div className="h-16 w-16 bg-gray-200 rounded-full mr-4"></div>
            <div className="h-10 w-64 bg-gray-200 rounded"></div>
          </div>
          
          <div className="space-y-4">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-full"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          </div>
        </div>

        {/* Cards Grid Skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white rounded-xl shadow-lg p-6 animate-pulse">
              <div className="h-6 w-24 bg-gray-200 rounded mb-4"></div>
              <div className="space-y-3">
                <div className="h-4 bg-gray-200 rounded w-full"></div>
                <div className="h-4 bg-gray-200 rounded w-4/5"></div>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              </div>
            </div>
          ))}
        </div>

        {/* Progress Text */}
        <div className="text-center">
          <div className="inline-flex items-center gap-3 bg-blue-50 px-6 py-3 rounded-full">
            <div className="w-5 h-5 border-3 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-blue-600 font-medium">
              Analyzing with AI...
            </p>
          </div>
          <p className="text-gray-500 text-sm mt-4">
            This may take 10-20 seconds for nutrition label OCR
          </p>
        </div>
      </div>
    </div>
  )
}
