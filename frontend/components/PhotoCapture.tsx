/**
 * Photo Capture Component with Vision AI
 * 
 * Uses Vision LLMs (Gemini, Qwen-VL, LLaVA) to extract ingredients from images
 */
import React, { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import { Camera, X, Upload, Loader2 } from 'lucide-react'
import { getSelectedLanguage } from '../utils/languageSupport'

interface PhotoCaptureProps {
  onIngredientsExtracted: (ingredients: string) => void
  customButton?: React.ReactNode  // Allow custom trigger button
}

export default function PhotoCapture({ onIngredientsExtracted, customButton }: PhotoCaptureProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [isCameraActive, setIsCameraActive] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [capturedImage, setCapturedImage] = useState<string | null>(null)
  const [progress, setProgress] = useState(0)
  const [cameraError, setCameraError] = useState<string | null>(null)
  const [currentLanguage, setCurrentLanguage] = useState(getSelectedLanguage())
  
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    // Listen for language changes
    const handleLanguageChange = (e: any) => {
      setCurrentLanguage(e.detail)
    }
    window.addEventListener('languageChange', handleLanguageChange)
    
    // Cleanup camera when component unmounts or modal closes
    return () => {
      window.removeEventListener('languageChange', handleLanguageChange)
      stopCamera()
    }
  }, [])

  const startCamera = async () => {
    try {
      setCameraError(null)
      console.log('Attempting to start camera...')
      
      // Check if getUserMedia is supported
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Camera not supported in this browser')
      }
      
      // Request camera access
      console.log('Requesting camera stream...')
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { 
          facingMode: 'environment', // Use back camera on mobile
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        }
      })
      
      console.log('Camera stream obtained:', stream)
      streamRef.current = stream
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        await videoRef.current.play()
        setIsCameraActive(true)
        console.log('Camera active!')
      } else {
        console.error('Video element not found')
        throw new Error('Video element not ready')
      }
    } catch (error: any) {
      console.error('Camera error:', error)
      
      if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
        setCameraError('Camera permission denied.\n\n📷 To enable camera:\n1. Click the camera icon 🎥 in your browser address bar\n2. Select "Always allow" or "Allow"\n3. Refresh this page and try again\n\nOr try manual entry or barcode scanning instead.')
      } else if (error.name === 'NotFoundError') {
        setCameraError('No camera found on this device.\n\nPlease use:\n• Manual entry to type ingredients\n• Barcode scanner if product has a barcode')
      } else if (error.name === 'NotReadableError') {
        setCameraError('Camera is already in use by another application.\n\nPlease:\n• Close other apps using the camera\n• Try again')
      } else if (error.message === 'Camera not supported in this browser') {
        setCameraError('Your browser does not support camera access.\n\nTry:\n• Using Chrome, Edge, or Firefox\n• Manual entry instead')
      } else {
        setCameraError(`Camera error: ${error.message}\n\nTry:\n• Refreshing the page\n• Using a different browser\n• Manual entry or barcode scanning`)
      }
    }
  }

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
    setIsCameraActive(false)
  }

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return

    const video = videoRef.current
    const canvas = canvasRef.current
    
    // Set canvas size to match video
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    
    // Draw current video frame to canvas
    const context = canvas.getContext('2d')
    if (context) {
      context.drawImage(video, 0, 0, canvas.width, canvas.height)
      
      // Convert canvas to image
      const imageDataUrl = canvas.toDataURL('image/jpeg', 0.95)
      setCapturedImage(imageDataUrl)
      
      // Stop camera
      stopCamera()
      
      // Process the captured image
      processImage(imageDataUrl)
    }
  }

  const preprocessImage = (imageDataUrl: string): Promise<string> => {
    return new Promise((resolve) => {
      const img = new Image()
      img.onload = () => {
        const canvas = document.createElement('canvas')
        const ctx = canvas.getContext('2d')!
        
        // Increase resolution for better OCR
        const scale = 2
        canvas.width = img.width * scale
        canvas.height = img.height * scale
        
        ctx.scale(scale, scale)
        ctx.drawImage(img, 0, 0)
        ctx.setTransform(1, 0, 0, 1, 0, 0)
        
        // Get image data for processing
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
        const data = imageData.data
        
        // Convert to grayscale and enhance contrast
        for (let i = 0; i < data.length; i += 4) {
          const gray = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2]
          const contrast = 1.5
          const factor = (259 * (contrast + 255)) / (255 * (259 - contrast))
          const adjusted = factor * (gray - 128) + 128
          const threshold = adjusted > 140 ? 255 : 0
          
          data[i] = threshold
          data[i + 1] = threshold
          data[i + 2] = threshold
        }
        
        ctx.putImageData(imageData, 0, 0)
        resolve(canvas.toDataURL('image/png'))
      }
      img.src = imageDataUrl
    })
  }

  const processImage = async (imageDataUrl: string) => {
    setIsProcessing(true)
    setProgress(0)

    try {
      console.log('🤖 Processing image...')
      setProgress(10)
      
      // Try to extract text from the image using Vision API
      try {
        // Convert base64 to blob
        const blob = await (await fetch(imageDataUrl)).blob()
        
        // Create FormData
        const formData = new FormData()
        formData.append('image', blob, 'ingredient-photo.jpg')
        formData.append('language', currentLanguage.code)
        
        setProgress(30)
        console.log('🔍 Extracting text from image...')
        
        // Call vision extraction API
        const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/vision-extract`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        setProgress(80)
        
        if (response.data.success && response.data.ingredients) {
          console.log('✅ Text extracted:', response.data.ingredients)
          setProgress(100)
          onIngredientsExtracted(response.data.ingredients)
          handleClose()
          return
        } else if (response.data.error) {
          // Show specific error message
          console.log('⚠️ Vision API error:', response.data.error)
          setCameraError(response.data.error)
          setIsProcessing(false)
          setProgress(0)
          return
        }
      } catch (visionError: any) {
        console.log('⚠️ Vision extraction failed:', visionError)
        
        // Check if it's a quota error
        if (visionError?.response?.data?.error) {
          setCameraError(visionError.response.data.error)
          setIsProcessing(false)
          setProgress(0)
          return
        }
        
        // General error handling
        setCameraError('Failed to extract ingredients. Please try again.')
        setIsProcessing(false)
        setProgress(0)
      }
    } catch (error) {
      console.error('Error processing image:', error)
      setCameraError('Failed to process image. Please try again.')
      setIsProcessing(false)
      setProgress(0)
    }
  }

  const retakePhoto = () => {
    setCapturedImage(null)
    setIsProcessing(false)
    setCameraError(null)
    startCamera()
  }

  const handleClose = () => {
    stopCamera()
    setIsOpen(false)
    setCapturedImage(null)
    setIsProcessing(false)
    setCameraError(null)
  }

  const handleOpen = () => {
    setIsOpen(true)
    // Give the modal time to render before starting camera
    setTimeout(() => {
      console.log('Modal opened, starting camera...')
      startCamera()
    }, 500)
  }

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // Open modal for processing
    setIsOpen(true)
    
    // Stop camera if running
    stopCamera()

    // Read file and process
    const reader = new FileReader()
    reader.onload = (e) => {
      const imageDataUrl = e.target?.result as string
      setCapturedImage(imageDataUrl)
      processImage(imageDataUrl)
    }
    reader.readAsDataURL(file)
  }

  const openFileUpload = () => {
    fileInputRef.current?.click()
  }

  return (
    <>
      {customButton ? (
        <div onClick={handleOpen}>
          {customButton}
        </div>
      ) : (
        <>
          <button
            onClick={handleOpen}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center gap-2"
          >
            <Camera className="w-4 h-4" />
            📸 Capture ingredients photo
          </button>

          <button
            onClick={openFileUpload}
            className="text-sm text-green-600 hover:text-green-700 font-medium flex items-center gap-2"
          >
            <Upload className="w-4 h-4" />
            📁 Upload ingredients photo
          </button>
        </>
      )}

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleFileUpload}
        aria-label="Upload ingredient photo file"
      />

      {/* Camera Modal */}
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-4xl w-full p-6 relative">
            <button
              onClick={handleClose}
              className="absolute top-4 right-4 text-gray-500 hover:text-gray-700 z-10"
              aria-label="Close camera modal"
            >
              <X className="w-6 h-6" />
            </button>

            <h3 className="text-2xl font-bold mb-4">
              {isProcessing ? 'Reading Ingredients...' : isCameraActive ? 'Point Camera at Ingredients' : 'Camera Photo Capture'}
            </h3>

            {/* Loading/Permission State */}
            {!isCameraActive && !capturedImage && !cameraError && !isProcessing && (
              <div className="space-y-4 py-8">
                <div className="flex flex-col items-center justify-center">
                  <Loader2 className="w-12 h-12 animate-spin text-blue-600 mb-4" />
                  <p className="text-gray-700 font-medium">Requesting camera access...</p>
                  <p className="text-sm text-gray-500 mt-2">Please allow camera permission when prompted</p>
                </div>
                
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4">
                  <p className="text-sm text-blue-800 text-center">
                    📷 <strong>Camera permission needed</strong>
                    <br />Your browser will ask to access your camera.
                    <br />Click "Allow" to continue.
                  </p>
                </div>

                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <p className="text-sm text-yellow-800 text-center mb-3">
                    ⚠️ <strong>Don't see the permission prompt?</strong>
                    <br />Look for a camera icon 🎥 in your browser's address bar (top-left)
                  </p>
                  <button
                    onClick={handleClose}
                    className="w-full px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-medium transition"
                  >
                    Cancel & Use Manual Entry
                  </button>
                </div>
              </div>
            )}

            {/* Camera View (Always render video, hide when not needed) */}
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className={`w-full max-h-96 object-contain rounded-lg ${
                isCameraActive && !capturedImage ? 'block' : 'hidden'
              }`}
            />
            <canvas ref={canvasRef} className="hidden" />

            {isCameraActive && !capturedImage && (
              <div className="space-y-4">
                <div className="relative">
                  <div className="absolute inset-0 border-4 border-blue-500 border-dashed m-8 pointer-events-none flex items-center justify-center rounded-lg">
                    <p className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm">
                      Position ingredients list inside this frame
                    </p>
                  </div>
                </div>

                <button
                  onClick={capturePhoto}
                  className="w-full px-6 py-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-lg transition flex items-center justify-center gap-2"
                >
                  <Camera className="w-5 h-5" />
                  Capture Photo
                </button>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-blue-800">
                    💡 <strong>Tips for best results:</strong>
                    <br />• Hold phone steady
                    <br />• Good lighting (no shadows)
                    <br />• Focus only on ingredients section
                    <br />• Keep text clear and readable
                  </p>
                </div>
              </div>
            )}

            {/* Captured Image Preview */}
            {capturedImage && !isProcessing && (
              <div className="space-y-4">
                <img
                  src={capturedImage}
                  alt="Captured ingredients"
                  className="w-full max-h-96 object-contain rounded-lg"
                />
                
                <button
                  onClick={retakePhoto}
                  className="w-full px-4 py-3 bg-gray-600 hover:bg-gray-700 text-white font-semibold rounded-lg transition flex items-center justify-center gap-2"
                >
                  <RotateCcw className="w-5 h-5" />
                  Retake Photo
                </button>
              </div>
            )}

            {/* Processing State */}
            {isProcessing && capturedImage && (
              <div className="space-y-4">
                <img
                  src={capturedImage}
                  alt="Processing"
                  className="w-full max-h-64 object-contain rounded-lg opacity-50"
                />

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
                  {progress}% - Processing may take 10-30 seconds
                </p>
              </div>
            )}

            {/* Camera Error */}
            {cameraError && !isCameraActive && !isProcessing && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="font-medium text-red-800 mb-2">Camera Error</p>
                <p className="text-sm text-red-700 whitespace-pre-line">{cameraError}</p>
                
                {cameraError.includes('permission') && (
                  <div className="mt-3 bg-white rounded p-3 text-sm">
                    <p className="font-medium text-gray-800 mb-2">📱 How to enable camera:</p>
                    <ul className="list-disc list-inside space-y-1 text-gray-700">
                      <li>Look for camera icon 📷 in browser address bar</li>
                      <li>Click it and select "Allow" for this site</li>
                      <li>Refresh the page and try again</li>
                    </ul>
                  </div>
                )}
                
                <button
                  onClick={startCamera}
                  className="mt-3 w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition"
                >
                  Try Again
                </button>
              </div>
            )}
          </div>
        </div>
      )}

    </>
  )
}

