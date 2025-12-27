interface InsightCardProps {
  insight: {
    icon: string
    title: string
    explanation: string
    concern_level: string
    confidence: string
  }
}

export default function InsightCard({ insight }: InsightCardProps) {
  // Color scheme based on concern level
  const colorSchemes = {
    positive: {
      bg: 'bg-green-50',
      border: 'border-green-200',
      iconBg: 'bg-green-100',
      titleColor: 'text-green-900',
      textColor: 'text-green-800'
    },
    neutral: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      iconBg: 'bg-blue-100',
      titleColor: 'text-blue-900',
      textColor: 'text-blue-800'
    },
    negative: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      iconBg: 'bg-red-100',
      titleColor: 'text-red-900',
      textColor: 'text-red-800'
    }
  }

  const colors = colorSchemes[insight.concern_level as keyof typeof colorSchemes] || colorSchemes.neutral

  // Confidence badge
  const confidenceBadges = {
    high: { text: 'High Confidence', color: 'bg-green-100 text-green-800' },
    medium: { text: 'Medium Confidence', color: 'bg-yellow-100 text-yellow-800' },
    low: { text: 'Low Confidence', color: 'bg-gray-100 text-gray-800' }
  }

  const confidenceBadge = confidenceBadges[insight.confidence as keyof typeof confidenceBadges] || confidenceBadges.medium

  return (
    <div className={`${colors.bg} ${colors.border} border-l-4 p-5 rounded-lg shadow-md hover:shadow-lg transition-shadow animate-slide-up`}>
      <div className="flex items-start">
        {/* Icon */}
        <div className={`${colors.iconBg} rounded-full w-12 h-12 flex items-center justify-center flex-shrink-0 mr-4`}>
          <span className="text-2xl">{insight.icon}</span>
        </div>

        {/* Content */}
        <div className="flex-1">
          <div className="flex items-start justify-between mb-2">
            <h3 className={`font-semibold text-lg ${colors.titleColor}`}>
              {insight.title}
            </h3>
            <span className={`text-xs px-2 py-1 rounded-full ${confidenceBadge.color} ml-2 whitespace-nowrap`}>
              {confidenceBadge.text}
            </span>
          </div>
          
          <p className={`${colors.textColor} text-sm leading-relaxed`}>
            {insight.explanation}
          </p>
        </div>
      </div>
    </div>
  )
}
