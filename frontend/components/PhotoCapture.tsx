/**
 * Photo Capture Component with OCR
 * 
 * Captures photos of ingredient labels and extracts text using Tesseract.js
 */

import { useState, useRef } from 'react'
import { Camera, X, Loader2 } from 'lucide-react'
import Tesseract from 'tesseract.js'

interface PhotoCaptureProps {
  onIngredientsExtracted: (ingredients: string) => void
}

export default function PhotoCapture({ onIngredientsExtracted }: PhotoCaptureProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [capturedImage, setCapturedImage] = useState<string | null>(null)
  const [progress, setProgress] = useState(0)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setIsOpen(true) // Open modal when file is selected

    // Display preview
    const reader = new FileReader()
    reader.onload = (e) => {
      const imageDataUrl = e.target?.result as string
      setCapturedImage(imageDataUrl)
      processImage(imageDataUrl)
    }
    reader.readAsDataURL(file)
  }

  const processImage = async (imageDataUrl: string) => {
    setIsProcessing(true)
    setProgress(0)

    try {
      const result = await Tesseract.recognize(
        imageDataUrl,
        'eng',
        {
          logger: (m) => {
            if (m.status === 'recognizing text') {
              setProgress(Math.round(m.progress * 100))
            }
          }
        }
      )

      const text = result.data.text
      
      // Extract ingredients section
      const extractedIngredients = extractIngredients(text)
      
      if (extractedIngredients) {
        onIngredientsExtracted(extractedIngredients)
        setIsOpen(false)
        setCapturedImage(null)
      } else {
        alert('Could not find ingredients in the image. Please try:\n1. Better lighting\n2. Clear focus on ingredients text\n3. Typing manually')
      }
    } catch (error) {
      console.error('OCR Error:', error)
      alert('Failed to read text from image. Please try again or type manually.')
    } finally {
      setIsProcessing(false)
      setProgress(0)
    }
  }

  const extractIngredients = (text: string): string | null => {
    // Look for common ingredient label patterns
    const patterns = [
      /ingredients?:\s*(.+?)(?:\n\n|nutrition|allergen|contains|$)/is,
      /ingredientes?:\s*(.+?)(?:\n\n|nutrición|$)/is,
      /ingrédients?:\s*(.+?)(?:\n\n|valeur|$)/is,
    ]

    for (const pattern of patterns) {
      const match = text.match(pattern)
      if (match && match[1]) {
        return match[1].trim()
      }
    }

    // If no pattern match, check if the whole text looks like ingredients
    // (contains commas and common ingredient words)
    const lowerText = text.toLowerCase()
    if (
      (lowerText.includes('sugar') || lowerText.includes('flour') || 
       lowerText.includes('water') || lowerText.includes('salt')) &&
      text.includes(',')
    ) {
      return text.trim()
    }

    return null
  }

  return (
    <>
      <button
        onClick={() => fileInputRef.current?.click()}
        className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center gap-2"
      >
        <Camera className="w-4 h-4" />
        📸 Upload photo of label
      </button>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleFileSelect}
      />

      {/* Processing Modal */}
      {isOpen && (isProcessing || capturedImage) && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 relative">
            <button
              onClick={() => {
                setIsOpen(false)
                setCapturedImage(null)
                setIsProcessing(false)
              }}
              className="absolute top-4 right-4 text-gray-500 hover:text-gray-700"
            >
              <X className="w-6 h-6" />
            </button>

            <h3 className="text-2xl font-bold mb-4">
              {isProcessing ? 'Reading Ingredients...' : 'Image Uploaded'}
            </h3>

            {capturedImage && (
              <img
                src={capturedImage}
                alt="Uploaded label"
                className="w-full max-h-96 object-contain rounded-lg mb-4"
              />
            )}

            {isProcessing && (
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
                  <span className="text-gray-700">
                    Using AI to read text from image...
                  </span>
                </div>

                {/* Progress Bar */}
                <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                  <div
                    className="bg-blue-600 h-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  />
                </div>

                <p className="text-sm text-gray-500 text-center">
                  {progress}% - This may take 10-30 seconds
                </p>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-blue-800">
                    💡 <strong>Tip:</strong> For best results:
                    <br />• Ensure good lighting
                    <br />• Keep camera steady
                    <br />• Focus on ingredients section only
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  )
}
