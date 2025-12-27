/**
 * Barcode Scanner Component
 * 
 * Scans product barcodes and fetches ingredient data from Open Food Facts API
 */

import { useState, useEffect, useRef } from 'react'
import { Html5Qrcode } from 'html5-qrcode'
import { Barcode, X, Loader2, AlertCircle } from 'lucide-react'

interface BarcodeScannerProps {
  onProductFound: (ingredients: string, productName: string) => void
}

export default function BarcodeScanner({ onProductFound }: BarcodeScannerProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [isScanning, setIsScanning] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showPermissionHelp, setShowPermissionHelp] = useState(true)
  const [manualBarcode, setManualBarcode] = useState('')
  const scannerRef = useRef<Html5Qrcode | null>(null)
  const qrCodeRegionId = 'barcode-reader'

  useEffect(() => {
    return () => {
      // Cleanup scanner on unmount
      if (scannerRef.current && isScanning) {
        scannerRef.current.stop().catch(console.error)
      }
    }
  }, [isScanning])

  const startScanning = async () => {
    try {
      setError(null)
      setIsScanning(true)

      // First, request camera permissions explicitly
      try {
        await navigator.mediaDevices.getUserMedia({ video: true })
      } catch (permErr) {
        throw new Error('CAMERA_PERMISSION_DENIED')
      }

      // Initialize scanner
      const html5QrCode = new Html5Qrcode(qrCodeRegionId)
      scannerRef.current = html5QrCode

      // Start scanning
      await html5QrCode.start(
        { facingMode: 'environment' }, // Use back camera
        {
          fps: 10,
          qrbox: { width: 250, height: 250 }
        },
        onScanSuccess,
        onScanFailure
      )
    } catch (err: any) {
      console.error('Scanner error:', err)
      
      if (err.message === 'CAMERA_PERMISSION_DENIED' || err.name === 'NotAllowedError') {
        setError('Camera permission denied. Click the camera icon in your browser\'s address bar and allow access.')
      } else if (err.name === 'NotFoundError') {
        setError('No camera found on this device.')
      } else if (err.name === 'NotReadableError') {
        setError('Camera is already in use by another app. Please close other apps using the camera.')
      } else {
        setError('Could not start camera. Try refreshing the page or using manual entry instead.')
      }
      
      setIsScanning(false)
    }
  }

  const stopScanning = async () => {
    if (scannerRef.current && isScanning) {
      try {
        await scannerRef.current.stop()
        scannerRef.current = null
      } catch (err) {
        console.error('Error stopping scanner:', err)
      }
    }
    setIsScanning(false)
  }

  const onScanSuccess = async (decodedText: string) => {
    console.log('Barcode detected:', decodedText)
    
    // Stop scanning and fetch product data
    await stopScanning()
    await fetchProductData(decodedText)
  }

  const onScanFailure = (error: string) => {
    // Ignore scan failures (normal when no barcode in view)
    // console.log('Scan failure:', error)
  }

  const fetchProductData = async (barcode: string) => {
    setIsLoading(true)
    setError(null)

    try {
      console.log('Fetching product for barcode:', barcode)
      
      // Use backend API (avoids CORS issues)
      const response = await fetch(
        `http://localhost:8000/api/barcode/${barcode}`,
        {
          method: 'GET',
        }
      )
      
      console.log('API Response status:', response.status)
      
      const data = await response.json()
      console.log('API Response data:', data)
      
      if (response.ok && data.found) {
        const productName = data.product_name
        const ingredients = data.ingredients

        console.log('Product found:', productName)
        console.log('Ingredients:', ingredients)

        onProductFound(ingredients, productName)
        setIsOpen(false)
      } else {
        // Handle error from backend
        const errorMsg = data.detail || 'Product not found'
        
        if (errorMsg.includes('not found')) {
          setError(`Barcode ${barcode} not found in database.\n\nThis product may not be registered yet.\n\n💡 Try:\n• Manual entry\n• Upload a photo\n• Scan a major brand product`)
        } else if (errorMsg.includes('no ingredient list')) {
          setError(`Found product but no ingredients available.\n\n${errorMsg}\n\nTry manual entry or photo upload instead.`)
        } else {
          setError(errorMsg)
        }
      }
    } catch (err: any) {
      console.error('Fetch error:', err)
      
      if (err.message === 'Failed to fetch' || err.name === 'TypeError') {
        setError('Cannot connect to backend server.\n\nMake sure backend is running:\ncd backend && uvicorn app:app --reload')
      } else {
        setError('Unexpected error. Try manual entry or photo upload instead.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleClose = () => {
    stopScanning()
    setIsOpen(false)
    setError(null)
    setShowPermissionHelp(true)
    setManualBarcode('')
  }

  const handleManualSubmit = () => {
    if (manualBarcode.trim().length >= 8) {
      fetchProductData(manualBarcode.trim())
    } else {
      setError('Please enter a valid barcode (at least 8 digits)')
    }
  }

  const testKnownProduct = () => {
    // Coca-Cola barcode - definitely in database
    fetchProductData('5449000000996')
  }

  return (
    <>
      <button
        onClick={() => {
          setIsOpen(true)
        }}
        className="text-sm text-purple-600 hover:text-purple-700 font-medium flex items-center gap-2"
      >
        <Barcode className="w-4 h-4" />
        🔍 Scan barcode
      </button>

      {/* Scanner Modal */}
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 relative">
            <button
              onClick={handleClose}
              className="absolute top-4 right-4 text-gray-500 hover:text-gray-700 z-10"
            >
              <X className="w-6 h-6" />
            </button>

            <h3 className="text-2xl font-bold mb-4">Scan Product Barcode</h3>

            {/* Permission Help - Show before scanning */}
            {showPermissionHelp && !isScanning && !error && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <div className="flex gap-3 mb-3">
                  <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-medium text-blue-800">Camera Permission Required</p>
                    <p className="text-sm text-blue-700 mt-1">
                      Your browser will ask to access your camera. Click "Allow" to scan barcodes.
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => {
                    setShowPermissionHelp(false)
                    startScanning()
                  }}
                  className="w-full px-4 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-semibold transition flex items-center justify-center gap-2"
                >
                  <Barcode className="w-5 h-5" />
                  Grant Camera Access & Start Scanning
                </button>
              </div>
            )}

            {/* Scanner View */}
            {isScanning && (
              <div className="space-y-4">
                <div 
                  id={qrCodeRegionId} 
                  className="w-full rounded-lg overflow-hidden"
                  style={{ minHeight: '300px' }}
                />
                
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <p className="text-sm text-purple-800">
                    💡 <strong>Instructions:</strong>
                    <br />• Point camera at product barcode
                    <br />• Keep barcode centered in the box
                    <br />• Hold steady for automatic detection
                  </p>
                </div>
              </div>
            )}

            {/* Loading State */}
            {isLoading && (
              <div className="flex flex-col items-center justify-center py-12 space-y-4">
                <Loader2 className="w-12 h-12 animate-spin text-purple-600" />
                <p className="text-gray-700 font-medium">Fetching product data...</p>
                <p className="text-sm text-gray-500">Looking up in Open Food Facts database</p>
              </div>
            )}

            {/* Error State */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex gap-3 mb-3">
                  <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-medium text-red-800">Scan Issue</p>
                    <p className="text-sm text-red-700 mt-1 whitespace-pre-line">{error}</p>
                  </div>
                </div>
                
                {error.includes('permission') && (
                  <div className="bg-white rounded p-3 text-sm space-y-2 mb-3">
                    <p className="font-medium text-gray-800">📱 How to enable camera:</p>
                    <ul className="list-disc list-inside space-y-1 text-gray-700">
                      <li>Look for camera icon 📷 in browser address bar</li>
                      <li>Click it and select "Allow" for this site</li>
                      <li>Or go to browser Settings → Privacy → Camera</li>
                      <li>Then click "Scan barcode" again</li>
                    </ul>
                  </div>
                )}
                
                {error.includes('not found') && (
                  <div className="bg-blue-50 rounded p-3 text-sm mt-3 mb-3">
                    <p className="font-medium text-blue-800">💡 What to try instead:</p>
                    <ul className="list-disc list-inside space-y-1 text-blue-700 mt-2">
                      <li>Upload a photo of the ingredient label</li>
                      <li>Type ingredients manually</li>
                      <li>Try scanning a different product</li>
                    </ul>
                  </div>
                )}
                
                <button
                  onClick={() => {
                    setError(null)
                    setShowPermissionHelp(true)
                  }}
                  className="mt-3 w-full px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition"
                >
                  Try Another Barcode
                </button>
              </div>
            )}

            {/* Manual Entry Option */}
            {!isScanning && !isLoading && (
              <div className="border-t pt-4 mt-4">
                <p className="text-sm font-medium text-gray-700 mb-3">
                  Or enter barcode manually:
                </p>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={manualBarcode}
                    onChange={(e) => setManualBarcode(e.target.value.replace(/\D/g, ''))}
                    onKeyPress={(e) => e.key === 'Enter' && handleManualSubmit()}
                    placeholder="Enter barcode number"
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
                  />
                  <button
                    onClick={handleManualSubmit}
                    className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition"
                  >
                    Lookup
                  </button>
                </div>
                
                <button
                  onClick={testKnownProduct}
                  className="mt-3 text-sm text-green-600 hover:text-green-700 font-medium"
                >
                  🧪 Test with Coca-Cola (known product)
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  )
}
