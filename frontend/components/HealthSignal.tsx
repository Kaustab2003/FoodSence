interface HealthSignalProps {
  level: string
  icon: string
}

export default function HealthSignal({ level, icon }: HealthSignalProps) {
  const signalConfig = {
    likely_safe: {
      label: 'Likely Safe',
      description: 'Research suggests this is relatively safe for moderate consumption',
      bg: 'bg-green-100',
      border: 'border-green-400',
      text: 'text-green-900',
      iconBg: 'bg-green-200'
    },
    moderate_concern: {
      label: 'Use in Moderation',
      description: 'Some ingredients warrant awareness - best consumed occasionally',
      bg: 'bg-yellow-100',
      border: 'border-yellow-400',
      text: 'text-yellow-900',
      iconBg: 'bg-yellow-200'
    },
    potential_risk: {
      label: 'Potential Concern',
      description: 'Contains ingredients that may warrant caution or avoidance',
      bg: 'bg-red-100',
      border: 'border-red-400',
      text: 'text-red-900',
      iconBg: 'bg-red-200'
    }
  }

  const config = signalConfig[level as keyof typeof signalConfig] || signalConfig.moderate_concern

  return (
    <div className={`${config.bg} ${config.border} border-l-4 p-6 rounded-lg shadow-lg animate-slide-up`}>
      <div className="flex items-center">
        {/* Signal Icon */}
        <div className={`${config.iconBg} rounded-full w-16 h-16 flex items-center justify-center mr-4`}>
          <span className="text-4xl">{icon}</span>
        </div>

        {/* Signal Info */}
        <div className="flex-1">
          <h2 className={`text-2xl font-bold ${config.text} mb-1`}>
            {config.label}
          </h2>
          <p className={`${config.text} text-sm opacity-90`}>
            {config.description}
          </p>
        </div>
      </div>
    </div>
  )
}
