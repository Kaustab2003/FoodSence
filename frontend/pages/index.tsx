import { useState, useEffect } from 'react'
import { Camera, FileText, Sparkles } from 'lucide-react'
import { useRouter } from 'next/router'
import VoiceInput from '../components/VoiceInput'
import PhotoCapture from '../components/PhotoCapture'
import BarcodeScanner from '../components/BarcodeScanner'
import LanguageSelector from '../components/LanguageSelector'
import { trackAnalyzedProduct } from '../utils/userPreferences'
import { getSelectedLanguage } from '../utils/languageSupport'

export default function Home() {
  const router = useRouter()
  const [ingredients, setIngredients] = useState('')
  const [productName, setProductName] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [currentLanguage, setCurrentLanguage] = useState(getSelectedLanguage())
  const [analysisMode, setAnalysisMode] = useState<'ingredients' | 'nutrition'>('ingredients')
  const [nutritionImage, setNutritionImage] = useState<string | null>(null)
  
  useEffect(() => {
    // Listen for language changes
    const handleLanguageChange = (e: any) => {
      setCurrentLanguage(e.detail)
    }
    window.addEventListener('languageChange', handleLanguageChange)
    
    return () => {
      window.removeEventListener('languageChange', handleLanguageChange)
    }
  }, [])

  const handleAnalyze = async () => {
    // Validate based on mode
    if (analysisMode === 'ingredients' && !ingredients.trim()) {
      alert('Please enter at least one ingredient')
      return
    }
    
    if (analysisMode === 'nutrition' && !nutritionImage) {
      alert('Please capture a nutrition facts photo')
      return
    }

    setIsLoading(true)

    // Parse ingredients (comma or newline separated)
    const ingredientList = ingredients
      .split(/[,\n]/)
      .map(i => i.trim())
      .filter(i => i.length > 0)

    // Track analyzed product (PATENT FEATURE: Session-based learning)
    const category = detectCategory(ingredients)
    trackAnalyzedProduct(productName || 'Unknown Product', category)

    // Store in sessionStorage for analyze page
    sessionStorage.setItem('analysis_data', JSON.stringify({
      ingredients: ingredientList,
      productName: productName || null,
      analysisMode: analysisMode,
      nutritionImage: nutritionImage
    }))

    // Navigate to analyze page
    router.push('/analyze')
  }

  const handleVoiceTranscript = (transcript: string) => {
    // Add to ingredients field
    setIngredients(prev => prev ? `${prev}, ${transcript}` : transcript)
  }

  const handleVoiceCommand = (command: string) => {
    const lower = command.toLowerCase()
    if (lower.includes('analyze') || lower.includes('check this')) {
      handleAnalyze()
    }
  }

  const detectCategory = (ingredientText: string): string => {
    const lower = ingredientText.toLowerCase()
    if (lower.includes('protein') || lower.includes('whey')) return 'protein_supplement'
    if (lower.includes('cereal') || lower.includes('oats')) return 'breakfast'
    if (lower.includes('soda') || lower.includes('cola')) return 'beverage'
    if (lower.includes('candy') || lower.includes('chocolate')) return 'snack'
    return 'general'
  }

  const loadDemoProduct = (demo: number) => {
    const demos = [
      {
        name: 'Sugar Blast Cereal',
        ingredients: 'sugar, corn syrup, wheat flour, red 40, yellow 5, bht, salt'
      },
      {
        name: 'Energy Cola',
        ingredients: 'carbonated water, high fructose corn syrup, caffeine, sodium benzoate, aspartame, red 40'
      },
      {
        name: 'Protein Power Bar',
        ingredients: 'whey protein, oats, honey, almonds, dark chocolate, soy lecithin, salt'
      }
    ]

    const selected = demos[demo]
    setProductName(selected.name)
    setIngredients(selected.ingredients)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50">
      <div className="container mx-auto px-4 py-12">
        {/* Header with Language Selector */}
        <div className="flex justify-end mb-4">
          <LanguageSelector />
        </div>
        
        {/* Header */}
        <div className="text-center mb-12 animate-fade-in">
          <div className="flex items-center justify-center mb-4">
            <Sparkles className="w-12 h-12 text-green-600 mr-2" />
            <h1 className="text-5xl font-bold text-gray-900">
              FoodSense AI+
            </h1>
          </div>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            <strong>Just show the food. I'll explain what matters.</strong>
          </p>
          <p className="text-gray-500 mt-2">
            AI-native food understanding co-pilot
          </p>
        </div>

        {/* Mode Selection */}
        <div className="max-w-3xl mx-auto mb-6 animate-fade-in">
          <div className="bg-white rounded-xl shadow-md p-4">
            <p className="text-sm font-medium text-gray-700 mb-3 text-center">
              What would you like to analyze?
            </p>
            <div className="grid grid-cols-2 gap-4">
              <button
                onClick={() => {
                  setAnalysisMode('ingredients')
                  setNutritionImage(null)
                }}
                className={`p-4 rounded-lg border-2 transition-all ${
                  analysisMode === 'ingredients'
                    ? 'border-green-500 bg-green-50 shadow-md'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <FileText className={`w-8 h-8 mx-auto mb-2 ${
                  analysisMode === 'ingredients' ? 'text-green-600' : 'text-gray-400'
                }`} />
                <h3 className={`font-semibold ${
                  analysisMode === 'ingredients' ? 'text-green-700' : 'text-gray-700'
                }`}>
                  Ingredient List
                </h3>
                <p className="text-xs text-gray-500 mt-1">
                  Analyze what's inside
                </p>
              </button>
              
              <button
                onClick={() => {
                  setAnalysisMode('nutrition')
                  setIngredients('')
                }}
                className={`p-4 rounded-lg border-2 transition-all ${
                  analysisMode === 'nutrition'
                    ? 'border-blue-500 bg-blue-50 shadow-md'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <Camera className={`w-8 h-8 mx-auto mb-2 ${
                  analysisMode === 'nutrition' ? 'text-blue-600' : 'text-gray-400'
                }`} />
                <h3 className={`font-semibold ${
                  analysisMode === 'nutrition' ? 'text-blue-700' : 'text-gray-700'
                }`}>
                  Nutrition Facts
                </h3>
                <p className="text-xs text-gray-500 mt-1">
                  Scan the label
                </p>
              </button>
            </div>
          </div>
        </div>

        {/* Main Input Card */}
        <div className="max-w-3xl mx-auto bg-white rounded-2xl shadow-xl p-8 mb-8 animate-slide-up">
          <h2 className="text-2xl font-semibold mb-6 text-gray-800">
            {analysisMode === 'ingredients' ? 'Enter Ingredients' : 'Capture Nutrition Facts'}
          </h2>

          {/* Product Name (Optional) */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Product Name <span className="text-gray-400">(optional)</span>
            </label>
            <input
              type="text"
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              placeholder="e.g., Chocolate Chip Cookies"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
            />
          </div>

          {/* Conditional Input based on mode */}
          {analysisMode === 'ingredients' ? (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ingredients <span className="text-red-500">*</span>
              </label>
              <textarea
                value={ingredients}
                onChange={(e) => setIngredients(e.target.value)}
                placeholder="Enter ingredients (comma or line separated)&#10;Example: sugar, wheat flour, palm oil, salt, vanilla extract"
                rows={6}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition resize-none"
              />
              <p className="text-sm text-gray-500 mt-2">
                💡 Tip: Just paste from the food label or type them out
              </p>
            </div>
          ) : (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nutrition Facts Photo <span className="text-red-500">*</span>
              </label>
              
              {nutritionImage ? (
                <div className="space-y-4">
                  <div className="border-2 border-blue-300 rounded-lg p-4 bg-blue-50">
                    <img 
                      src={nutritionImage} 
                      alt="Nutrition facts" 
                      className="max-h-96 mx-auto rounded-lg shadow-md"
                    />
                  </div>
                  <button
                    onClick={() => setNutritionImage(null)}
                    className="w-full px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition"
                  >
                    📷 Retake Photo
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  <PhotoCapture 
                    onIngredientsExtracted={(base64Image) => {
                      setNutritionImage(base64Image)
                    }}
                    customButton={
                      <button className="w-full px-6 py-12 border-2 border-dashed border-blue-300 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-all">
                        <Camera className="w-16 h-16 mx-auto mb-4 text-blue-500" />
                        <p className="text-lg font-semibold text-gray-700">Capture Nutrition Label</p>
                        <p className="text-sm text-gray-500 mt-2">Click to take or upload photo</p>
                      </button>
                    }
                  />
                  
                  <div className="relative">
                    <div className="absolute inset-0 flex items-center">
                      <div className="w-full border-t border-gray-300"></div>
                    </div>
                    <div className="relative flex justify-center text-sm">
                      <span className="px-2 bg-white text-gray-500">or</span>
                    </div>
                  </div>

                  <label className="block">
                    <input
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onChange={(e) => {
                        const file = e.target.files?.[0]
                        if (file) {
                          const reader = new FileReader()
                          reader.onloadend = () => {
                            setNutritionImage(reader.result as string)
                          }
                          reader.readAsDataURL(file)
                        }
                      }}
                    />
                    <div className="w-full px-6 py-8 border-2 border-dashed border-gray-300 rounded-lg hover:border-gray-400 hover:bg-gray-50 transition-all cursor-pointer">
                      <FileText className="w-12 h-12 mx-auto mb-3 text-gray-500" />
                      <p className="text-base font-semibold text-gray-700 text-center">Upload from Device</p>
                      <p className="text-sm text-gray-500 mt-1 text-center">Click to browse files</p>
                    </div>
                  </label>
                </div>
              )}
              
              <p className="text-sm text-gray-500 mt-2">
                📊 Tip: Make sure the nutrition facts table is clearly visible and well-lit
              </p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="grid grid-cols-1 gap-4 mb-6">
            <button
              onClick={handleAnalyze}
              disabled={isLoading}
              className="flex items-center justify-center px-6 py-4 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Analyzing...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5 mr-2" />
                  Analyze with AI
                </>
              )}
            </button>

            {/* PATENT FEATURE: Voice-First Interaction */}
            <VoiceInput 
              onTranscript={handleVoiceTranscript}
              onVoiceCommand={handleVoiceCommand}
              enableTTS={false}
            />
          </div>

          {/* Quick Input Options */}
          <div className="text-center space-y-2 mb-6">
            <p className="text-sm text-gray-600">Quick options:</p>
            <div className="flex items-center justify-center gap-4 flex-wrap">
              <PhotoCapture 
                onIngredientsExtracted={(extractedText) => {
                  setIngredients(extractedText)
                  alert('✅ Ingredients extracted! Review and click Analyze.')
                }}
              />
              
              <BarcodeScanner 
                onProductFound={(extractedIngredients, productName) => {
                  setProductName(productName)
                  setIngredients(extractedIngredients)
                  alert(`✅ Found: ${productName}\nReview ingredients and click Analyze.`)
                }}
              />
            </div>
          </div>

          {/* Demo Products */}
          <div className="border-t pt-6">
            <p className="text-sm font-medium text-gray-700 mb-3">
              Or try a demo product:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <button
                onClick={() => loadDemoProduct(0)}
                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded-lg text-sm transition"
              >
                🥣 Sugar Cereal
              </button>
              <button
                onClick={() => loadDemoProduct(1)}
                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded-lg text-sm transition"
              >
                🥤 Energy Drink
              </button>
              <button
                onClick={() => loadDemoProduct(2)}
                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded-lg text-sm transition"
              >
                🍫 Protein Bar
              </button>
            </div>
          </div>
        </div>

        {/* Features */}
        <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          <div className="bg-white p-6 rounded-xl shadow-md text-center">
            <div className="text-4xl mb-3">🧠</div>
            <h3 className="font-semibold text-lg mb-2">Intent-First</h3>
            <p className="text-gray-600 text-sm">
              AI infers what you care about automatically. No forms or questionnaires.
            </p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-md text-center">
            <div className="text-4xl mb-3">⚖️</div>
            <h3 className="font-semibold text-lg mb-2">Honest Trade-Offs</h3>
            <p className="text-gray-600 text-sm">
              Clear benefits and downsides. Uncertainty communicated openly.
            </p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-md text-center">
            <div className="text-4xl mb-3">🎓</div>
            <h3 className="font-semibold text-lg mb-2">ELI5 Mode</h3>
            <p className="text-gray-600 text-sm">
              One-tap simplification to 10-year-old comprehension level.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-16 text-gray-500 text-sm">
          <p>Built for <strong>ENCODE: Code to Innovate</strong> Hackathon 2026</p>
          <p className="mt-1">AI-Native Food Understanding • Patent-Pending Technology</p>
        </div>
      </div>
    </div>
  )
}
