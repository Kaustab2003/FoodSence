import { useState } from 'react'
import { Camera, FileText, Sparkles } from 'lucide-react'
import { useRouter } from 'next/router'
import VoiceInput from '../components/VoiceInput'
import PhotoCapture from '../components/PhotoCapture'
import BarcodeScanner from '../components/BarcodeScanner'
import { trackAnalyzedProduct } from '../utils/userPreferences'

export default function Home() {
  const router = useRouter()
  const [ingredients, setIngredients] = useState('')
  const [productName, setProductName] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleAnalyze = async () => {
    if (!ingredients.trim()) {
      alert('Please enter at least one ingredient')
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
      productName: productName || null
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

        {/* Main Input Card */}
        <div className="max-w-3xl mx-auto bg-white rounded-2xl shadow-xl p-8 mb-8 animate-slide-up">
          <h2 className="text-2xl font-semibold mb-6 text-gray-800">
            What are you considering?
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

          {/* Ingredients Input */}
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
