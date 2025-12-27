/**
 * Multi-language Support for Indian Languages
 * 
 * Supports Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati, Kannada, Malayalam, Punjabi, and English
 */

export interface Language {
  code: string
  name: string
  nativeName: string
  voiceCode: string // For Web Speech API
  ocrCode: string   // For Tesseract.js
}

export const SUPPORTED_LANGUAGES: Language[] = [
  {
    code: 'en',
    name: 'English',
    nativeName: 'English',
    voiceCode: 'en-IN',
    ocrCode: 'eng'
  },
  {
    code: 'hi',
    name: 'Hindi',
    nativeName: 'हिन्दी',
    voiceCode: 'hi-IN',
    ocrCode: 'hin'
  },
  {
    code: 'bn',
    name: 'Bengali',
    nativeName: 'বাংলা',
    voiceCode: 'bn-IN',
    ocrCode: 'ben'
  },
  {
    code: 'ta',
    name: 'Tamil',
    nativeName: 'தமிழ்',
    voiceCode: 'ta-IN',
    ocrCode: 'tam'
  },
  {
    code: 'te',
    name: 'Telugu',
    nativeName: 'తెలుగు',
    voiceCode: 'te-IN',
    ocrCode: 'tel'
  },
  {
    code: 'mr',
    name: 'Marathi',
    nativeName: 'मराठी',
    voiceCode: 'mr-IN',
    ocrCode: 'mar'
  },
  {
    code: 'gu',
    name: 'Gujarati',
    nativeName: 'ગુજરાતી',
    voiceCode: 'gu-IN',
    ocrCode: 'guj'
  },
  {
    code: 'kn',
    name: 'Kannada',
    nativeName: 'ಕನ್ನಡ',
    voiceCode: 'kn-IN',
    ocrCode: 'kan'
  },
  {
    code: 'ml',
    name: 'Malayalam',
    nativeName: 'മലയാളം',
    voiceCode: 'ml-IN',
    ocrCode: 'mal'
  },
  {
    code: 'pa',
    name: 'Punjabi',
    nativeName: 'ਪੰਜਾਬੀ',
    voiceCode: 'pa-IN',
    ocrCode: 'pan'
  }
]

// Get/Set language from localStorage
export const getSelectedLanguage = (): Language => {
  if (typeof window === 'undefined') return SUPPORTED_LANGUAGES[0]
  
  const saved = localStorage.getItem('foodsense_language')
  if (saved) {
    const found = SUPPORTED_LANGUAGES.find(l => l.code === saved)
    if (found) return found
  }
  
  return SUPPORTED_LANGUAGES[0] // Default to English
}

export const setSelectedLanguage = (languageCode: string) => {
  if (typeof window === 'undefined') return
  localStorage.setItem('foodsense_language', languageCode)
}

export const getLanguageByCode = (code: string): Language => {
  return SUPPORTED_LANGUAGES.find(l => l.code === code) || SUPPORTED_LANGUAGES[0]
}
