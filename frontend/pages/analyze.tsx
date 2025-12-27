import { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import axios from 'axios'
import { ArrowLeft, Lightbulb } from 'lucide-react'
import InsightCard from '../components/InsightCard'
import DetailedIngredientCard from '../components/DetailedIngredientCard'
import NutritionCard from '../components/NutritionCard'
import HealthSignal from '../components/HealthSignal'
import ConfidenceBar from '../components/ConfidenceBar'
import SurpriseScore from '../components/SurpriseScore'
import { getPersonalizedIntents, trackFollowUpClick } from '../utils/userPreferences'
import { getSelectedLanguage } from '../utils/languageSupport'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function AnalyzePage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [analysisData, setAnalysisData] = useState<any>(null)
  const [showELI5, setShowELI5] = useState(false)
  const [eli5Data, setEli5Data] = useState<string | null>(null)

  useEffect(() => {
    const performAnalysis = async () => {
      // Get data from sessionStorage
      const storedData = sessionStorage.getItem('analysis_data')
      
      if (!storedData) {
        router.push('/')
        return
      }

      const { ingredients, productName, analysisMode, nutritionImage } = JSON.parse(storedData)

      // PATENT FEATURE: Get personalized intent hints
      const userPreferences = getPersonalizedIntents()
      
      // Get selected language
      const selectedLanguage = getSelectedLanguage()

      try {
        // Determine analysis type and prepare request
        const requestData: any = {
          ingredients: ingredients || [],
          product_name: productName,
          include_eli5: false,
          user_preferences: userPreferences,
          language: selectedLanguage.code,
          analysis_type: analysisMode || 'ingredients'
        }

        // If nutrition mode, add the image
        if (analysisMode === 'nutrition' && nutritionImage) {
          requestData.nutrition_image = nutritionImage
        }

        // Call backend API
        const response = await axios.post(`${API_URL}/api/analyze`, requestData)

        setAnalysisData(response.data.data)
        setLoading(false)

        // Speak summary if voice is enabled
        if (typeof window !== 'undefined' && (window as any).foodSenseSpeak) {
          setTimeout(() => {
            const summary = response.data.data.nutrition_analysis?.health_summary || response.data.data.context?.summary
            if (summary) {
              (window as any).foodSenseSpeak(summary)
            }
          }, 1000)
        }
      } catch (error) {
        console.error('Analysis failed:', error)
        alert('Analysis failed. Please try again.')
        router.push('/')
      }
    }

    performAnalysis()
  }, [router])

  const handleELI5 = async () => {
    if (eli5Data) {
      setShowELI5(!showELI5)
      return
    }

    try {
      const storedData = sessionStorage.getItem('analysis_data')
      if (!storedData) return

      const { ingredients, productName } = JSON.parse(storedData)

      const response = await axios.post(`${API_URL}/api/analyze/eli5`, {
        ingredients,
        product_name: productName,
        include_eli5: true
      })

      setEli5Data(response.data.eli5_explanation)
      setShowELI5(true)
    } catch (error) {
      console.error('ELI5 generation failed:', error)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 flex items-center justify-center">
        <div className="text-center px-4">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-green-600 mx-auto mb-4"></div>
          <p className="text-xl font-semibold text-gray-800 mb-2">Analyzing ingredients with AI...</p>
          <p className="text-sm text-gray-600 mb-4">🧠 Comprehensive analysis in progress</p>
          <div className="bg-white rounded-lg p-4 shadow-md max-w-md mx-auto">
            <p className="text-xs text-gray-500">
              ⏱️ Analyzing all ingredients may take 30-60 seconds
              <br />
              🔍 Each ingredient gets detailed health, safety, and usage analysis
            </p>
          </div>
        </div>
      </div>
    )
  }

  if (!analysisData) {
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50">
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        {/* Back Button */}
        <button
          onClick={() => router.push('/')}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-6 transition"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          Analyze Another Product
        </button>

        {/* Context Summary */}
        {analysisData.context && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-6 animate-fade-in">
            <p className="text-gray-700 text-lg">
              {analysisData.context.summary}
            </p>
          </div>
        )}

        {/* PATENT FEATURE: Deception Detection / Surprise Score */}
        {analysisData.deception_analysis && (
          <SurpriseScore
            alerts={analysisData.deception_analysis.alerts}
            overallScore={analysisData.deception_analysis.overall_score}
          />
        )}

        {/* Health Signal */}
        {analysisData.health_signal && (
          <div className="mb-6 animate-slide-up">
            <HealthSignal
              level={analysisData.health_signal.level}
              icon={analysisData.health_signal.icon}
            />
            <div className="mt-3">
              <ConfidenceBar confidence={analysisData.health_signal.confidence} />
            </div>
          </div>
        )}

        {/* NEW: Nutrition Analysis Display */}
        {analysisData.nutrition_analysis && analysisData.nutrition_data && (
          <NutritionCard 
            analysis={analysisData.nutrition_analysis}
            nutritionData={analysisData.nutrition_data}
          />
        )}

        {/* Comprehensive Ingredient Analysis - ALL INGREDIENTS */}
        {analysisData.detailed_insights && analysisData.detailed_insights.length > 0 && (
          <div className="mb-8">
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl p-6 mb-6 shadow-lg">
              <h2 className="text-3xl font-bold mb-2 flex items-center">
                <span className="mr-3">📋</span>
                Complete Ingredient Analysis
              </h2>
              <p className="text-blue-100 text-lg">
                Detailed AI-powered breakdown of all {analysisData.detailed_insights.length} ingredients • 
                Each ingredient analyzed for health effects, safety, and usage
              </p>
            </div>
            <div className="space-y-4">
              {analysisData.detailed_insights.map((detail: string, idx: number) => (
                <DetailedIngredientCard key={idx} content={detail} index={idx} />
              ))}
            </div>
          </div>
        )}

        {/* Trade-Offs */}
        {analysisData.trade_offs && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
            <h3 className="text-xl font-semibold mb-4 text-gray-900">
              ⚖️ Trade-Offs
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Benefits */}
              <div>
                <h4 className="font-medium text-green-700 mb-2">👍 Benefits</h4>
                {analysisData.trade_offs.benefits.length > 0 ? (
                <ul className="space-y-1 text-sm text-gray-700">
                  {analysisData.trade_offs.benefits.map((benefit: string, idx: number) => (
                    <li key={idx} className="flex items-start">
                      <span className="text-green-500 mr-2">•</span>
                      {benefit}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500 text-sm">No significant benefits identified</p>
              )}
            </div>

            {/* Downsides */}
            <div>
              <h4 className="font-medium text-red-700 mb-2">⚠️ Downsides</h4>
              {analysisData.trade_offs.downsides.length > 0 ? (
                <ul className="space-y-1 text-sm text-gray-700">
                  {analysisData.trade_offs.downsides.map((downside: string, idx: number) => (
                    <li key={idx} className="flex items-start">
                      <span className="text-red-500 mr-2">•</span>
                      {downside}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500 text-sm">No significant concerns identified</p>
              )}
            </div>
          </div>
        </div>
        )}

        {/* Uncertainty Note */}
        {analysisData.uncertainty_note && (
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6 rounded-r-lg">
            <div className="flex items-start">
              <Lightbulb className="w-5 h-5 text-yellow-600 mr-3 mt-0.5 flex-shrink-0" />
              <div>
                <h4 className="font-semibold text-yellow-900 mb-1">
                  🤷 Honest Uncertainty
                </h4>
                <p className="text-yellow-800 text-sm">
                  {analysisData.uncertainty_note}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* ELI5 Toggle */}
        {analysisData.eli5_explanation !== undefined && (
          <div className="mb-6">
            <button
              onClick={handleELI5}
              className="w-full md:w-auto px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg shadow-lg transition flex items-center justify-center"
            >
              <Lightbulb className="w-5 h-5 mr-2" />
              {showELI5 ? 'Hide Simple Explanation' : 'Explain Like I\'m 10'}
            </button>

            {showELI5 && eli5Data && (
              <div className="mt-4 bg-purple-50 border border-purple-200 rounded-lg p-6 animate-slide-up">
                <h3 className="text-lg font-semibold text-purple-900 mb-3">
                  🎓 Simple Explanation
                </h3>
                <div className="text-gray-800 whitespace-pre-line">
                  {eli5Data}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Follow-Up Questions */}
        {analysisData.follow_up_questions && analysisData.follow_up_questions.length > 0 && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-semibold mb-4 text-gray-900">
              💬 Want to Know More?
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {analysisData.follow_up_questions.map((fq: any, idx: number) => (
              <button
                key={idx}
                className="px-4 py-3 bg-gray-100 hover:bg-gray-200 text-left rounded-lg transition text-sm"
                onClick={() => {
                  // PATENT FEATURE: Track follow-up click for personalization
                  trackFollowUpClick(fq.question)
                  alert(`This would trigger: "${fq.question}"\n\nContext: ${fq.context}\n\n✅ Preference saved! Future analyses will prioritize similar concerns.`)
                }}
              >
                <span className="font-medium text-gray-900">{fq.question}</span>
                <p className="text-xs text-gray-500 mt-1">{fq.context}</p>
              </button>
            ))}
          </div>
        </div>
        )}

        {/* Footer */}
        <div className="text-center mt-12 text-gray-500 text-sm">
          <p>AI-powered analysis • Research-backed insights • Honest uncertainty</p>
        </div>
      </div>
    </div>
  )
}
