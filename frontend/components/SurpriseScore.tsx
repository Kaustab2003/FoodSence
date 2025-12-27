/**
 * Surprise Score Component
 * 
 * Displays deception alerts for hidden ingredients
 * PATENT FEATURE: Visual representation of ingredient deception detection
 */

import { AlertTriangle, Info } from 'lucide-react'

interface DeceptionAlert {
  alert_type: string
  severity: string
  surprise_score: number
  title: string
  explanation: string
  disguised_ingredients: string[]
  cumulative_impact: string
}

interface SurpriseScoreProps {
  alerts: DeceptionAlert[]
  overallScore: number
}

export default function SurpriseScore({ alerts, overallScore }: SurpriseScoreProps) {
  if (!alerts || alerts.length === 0) {
    return (
      <div className="bg-green-50 border-2 border-green-200 rounded-xl p-6 mb-6">
        <div className="flex items-center">
          <div className="text-4xl mr-4">✅</div>
          <div>
            <h3 className="font-semibold text-lg text-green-800">No Deceptive Practices Detected</h3>
            <p className="text-sm text-green-600 mt-1">
              Ingredient list appears straightforward with no hidden duplicates or marketing tricks.
            </p>
          </div>
        </div>
      </div>
    )
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'border-red-300 bg-red-50'
      case 'medium': return 'border-yellow-300 bg-yellow-50'
      case 'low': return 'border-blue-300 bg-blue-50'
      default: return 'border-gray-300 bg-gray-50'
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'high': return '🚨'
      case 'medium': return '⚠️'
      case 'low': return 'ℹ️'
      default: return '💡'
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 70) return 'text-red-600'
    if (score >= 40) return 'text-yellow-600'
    return 'text-green-600'
  }

  return (
    <div className="mb-8">
      {/* Overall Deception Score */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 border-2 border-purple-200 rounded-xl p-6 mb-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold text-xl text-gray-800 mb-2">
              🔍 Ingredient Transparency Check
            </h3>
            <p className="text-sm text-gray-600">
              Our AI detected <strong>{alerts.length}</strong> potential marketing trick{alerts.length > 1 ? 's' : ''} in this product.
            </p>
          </div>
          <div className="text-center">
            <div className={`text-5xl font-bold ${getScoreColor(overallScore)}`}>
              {overallScore}
            </div>
            <div className="text-xs text-gray-500 mt-1">Surprise Score</div>
            <div className="text-xs text-gray-400">(0=clear, 100=very deceptive)</div>
          </div>
        </div>
      </div>

      {/* Individual Alerts */}
      <div className="space-y-4">
        {alerts.map((alert, index) => (
          <div
            key={index}
            className={`border-2 rounded-xl p-5 ${getSeverityColor(alert.severity)} transition-all hover:shadow-md`}
          >
            {/* Alert Header */}
            <div className="flex items-start mb-3">
              <div className="text-3xl mr-3">{getSeverityIcon(alert.severity)}</div>
              <div className="flex-1">
                <h4 className="font-semibold text-lg text-gray-800 mb-1">
                  {alert.title}
                </h4>
                <div className="flex items-center gap-2 mb-2">
                  <span className={`text-xs font-bold px-2 py-1 rounded ${
                    alert.severity === 'high' ? 'bg-red-200 text-red-800' :
                    alert.severity === 'medium' ? 'bg-yellow-200 text-yellow-800' :
                    'bg-blue-200 text-blue-800'
                  }`}>
                    {alert.severity.toUpperCase()} SEVERITY
                  </span>
                  <span className="text-xs bg-purple-200 text-purple-800 px-2 py-1 rounded font-semibold">
                    Surprise: {alert.surprise_score}/100
                  </span>
                </div>
              </div>
            </div>

            {/* Explanation */}
            <p className="text-sm text-gray-700 mb-3 leading-relaxed">
              {alert.explanation}
            </p>

            {/* Disguised Ingredients */}
            <div className="bg-white bg-opacity-60 rounded-lg p-3 mb-3">
              <div className="flex items-center mb-2">
                <Info className="w-4 h-4 mr-2 text-gray-600" />
                <span className="text-xs font-semibold text-gray-700">Found in ingredient list:</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {alert.disguised_ingredients.map((ing, idx) => (
                  <span
                    key={idx}
                    className="text-xs bg-gray-100 px-2 py-1 rounded border border-gray-300"
                  >
                    {ing}
                  </span>
                ))}
              </div>
            </div>

            {/* Cumulative Impact */}
            <div className="border-t pt-3">
              <p className="text-xs font-medium text-gray-600 mb-1">
                💥 <strong>Cumulative Impact:</strong>
              </p>
              <p className="text-sm text-gray-700">
                {alert.cumulative_impact}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Educational Footer */}
      <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-xs text-blue-800 leading-relaxed">
          <strong>💡 Why This Matters:</strong> Food manufacturers sometimes use multiple forms of the same 
          ingredient to make each appear lower on the ingredient list (which is ordered by weight). This 
          can create the illusion of a healthier product. Our AI aggregates these "hidden duplicates" to 
          show you the full picture.
        </p>
      </div>
    </div>
  )
}
