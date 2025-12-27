interface ConfidenceBarProps {
  confidence: string
}

export default function ConfidenceBar({ confidence }: ConfidenceBarProps) {
  const confidenceConfig = {
    high: {
      percentage: 90,
      color: 'bg-green-600',
      label: 'High',
      description: 'Strong research consensus'
    },
    medium: {
      percentage: 60,
      color: 'bg-yellow-500',
      label: 'Medium',
      description: 'Research still evolving'
    },
    low: {
      percentage: 30,
      color: 'bg-gray-500',
      label: 'Low',
      description: 'Limited long-term studies'
    }
  }

  const config = confidenceConfig[confidence as keyof typeof confidenceConfig] || confidenceConfig.medium

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-gray-700">
          Confidence Level
        </span>
        <span className="text-sm font-semibold text-gray-900">
          {config.label}
        </span>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-3 mb-2 overflow-hidden">
        <div
          className={`${config.color} h-full rounded-full transition-all duration-500 ease-out`}
          style={{ width: `${config.percentage}%` }}
        ></div>
      </div>

      <p className="text-xs text-gray-600">
        {config.description}
      </p>
    </div>
  )
}
