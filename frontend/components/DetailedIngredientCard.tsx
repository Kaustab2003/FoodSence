/**
 * DetailedIngredientCard Component
 * 
 * Displays comprehensive AI-generated analysis for individual ingredients.
 * Parses markdown-formatted strings with ingredient details.
 */

interface DetailedIngredientCardProps {
  content: string
  index: number
}

export default function DetailedIngredientCard({ content, index }: DetailedIngredientCardProps) {
  // Parse the content
  const lines = content.split('\n')
  
  // Extract ingredient name (first line with ###)
  const nameMatch = lines[0]?.match(/###\s*(.+)/)
  const ingredientName = nameMatch ? nameMatch[1].trim() : `Ingredient ${index + 1}`
  
  // Helper function to extract section content
  const extractSection = (sectionHeader: string): string => {
    const regex = new RegExp(`${sectionHeader.replace(/\*/g, '\\*')}\\s*(.+?)(?=\\*\\*|$)`, 's')
    const match = content.match(regex)
    return match ? match[1].trim() : ''
  }
  
  // Extract sections
  const whatItIs = extractSection('**What it is**:')
  const healthEffects = extractSection('**Health Effects**:')
  const safety = extractSection('**Safety**:')
  const usage = extractSection('**Usage in Food**:')
  const verdict = extractSection('**Final Verdict**:')
  
  // Determine color scheme based on verdict
  const isGenerallySafe = verdict.includes('✅ Generally Safe') || verdict.includes('✅')
  const isAvoid = verdict.includes('❌ Limit') || verdict.includes('❌ Avoid') || verdict.includes('❌')
  
  const colorScheme = isGenerallySafe
    ? { 
        bg: 'bg-green-50', 
        border: 'border-green-300', 
        header: 'bg-green-100', 
        text: 'text-green-900', 
        badge: 'bg-green-600',
        icon: '✅'
      }
    : isAvoid
    ? { 
        bg: 'bg-red-50', 
        border: 'border-red-300', 
        header: 'bg-red-100', 
        text: 'text-red-900', 
        badge: 'bg-red-600',
        icon: '❌'
      }
    : { 
        bg: 'bg-yellow-50', 
        border: 'border-yellow-300', 
        header: 'bg-yellow-100', 
        text: 'text-yellow-900', 
        badge: 'bg-yellow-600',
        icon: '⚠️'
      }
  
  return (
    <div className={`${colorScheme.bg} border-l-4 ${colorScheme.border} rounded-lg shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden animate-slide-up`}>
      {/* Header */}
      <div className={`${colorScheme.header} px-6 py-4 border-b ${colorScheme.border}`}>
        <div className="flex items-center justify-between">
          <h3 className={`text-xl font-bold ${colorScheme.text} flex items-center`}>
            <span className={`${colorScheme.badge} w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm mr-3`}>
              {index + 1}
            </span>
            {ingredientName}
          </h3>
          <span className={`${colorScheme.badge} px-3 py-1 rounded-full text-sm font-semibold text-white`}>
            {colorScheme.icon}
          </span>
        </div>
      </div>
      
      {/* Content */}
      <div className="px-6 py-5 space-y-4">
        {/* What it is */}
        {whatItIs && (
          <div>
            <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
              <span className="mr-2">🔍</span> What it is
            </h4>
            <p className="text-gray-700 leading-relaxed">{whatItIs}</p>
          </div>
        )}
        
        {/* Health Effects */}
        {healthEffects && (
          <div>
            <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
              <span className="mr-2">💊</span> Health Effects
            </h4>
            <div className="bg-white rounded-lg p-4 space-y-3">
              {healthEffects.split('\n').map((line, idx) => {
                const trimmed = line.trim()
                if (!trimmed) return null
                
                if (trimmed.includes('✅') || trimmed.toLowerCase().includes('benefits:')) {
                  const text = trimmed.replace(/✅\s*Benefits:\s*/i, '').replace(/Benefits:\s*/i, '').replace('-', '').trim()
                  return (
                    <div key={idx} className="flex items-start">
                      <span className="text-green-600 font-bold mr-2 flex-shrink-0">✅</span>
                      <div>
                        <span className="font-semibold text-green-900">Benefits: </span>
                        <span className="text-gray-700">{text}</span>
                      </div>
                    </div>
                  )
                } else if (trimmed.includes('⚠️') || trimmed.toLowerCase().includes('concerns:')) {
                  const text = trimmed.replace(/⚠️\s*Concerns:\s*/i, '').replace(/Concerns:\s*/i, '').replace('-', '').trim()
                  return (
                    <div key={idx} className="flex items-start">
                      <span className="text-orange-600 font-bold mr-2 flex-shrink-0">⚠️</span>
                      <div>
                        <span className="font-semibold text-orange-900">Concerns: </span>
                        <span className="text-gray-700">{text}</span>
                      </div>
                    </div>
                  )
                } else if (trimmed.startsWith('-')) {
                  return <p key={idx} className="text-gray-700 ml-6">{trimmed.substring(1).trim()}</p>
                }
                return <p key={idx} className="text-gray-700">{trimmed}</p>
              })}
            </div>
          </div>
        )}
        
        {/* Safety */}
        {safety && (
          <div>
            <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
              <span className="mr-2">🛡️</span> Safety Information
            </h4>
            <p className="text-gray-700 leading-relaxed bg-white rounded-lg p-4">{safety}</p>
          </div>
        )}
        
        {/* Usage */}
        {usage && (
          <div>
            <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
              <span className="mr-2">🏭</span> Usage in Food
            </h4>
            <p className="text-gray-700 leading-relaxed bg-white rounded-lg p-4">{usage}</p>
          </div>
        )}
        
        {/* Final Verdict */}
        {verdict && (
          <div className={`${colorScheme.header} rounded-lg p-4 border ${colorScheme.border}`}>
            <h4 className="font-semibold text-gray-900 mb-2">📋 Final Verdict</h4>
            <p className={`${colorScheme.text} font-medium leading-relaxed`}>{verdict}</p>
          </div>
        )}
      </div>
    </div>
  )
}
