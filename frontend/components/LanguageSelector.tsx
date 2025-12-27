import { useState, useEffect } from 'react'
import { Globe } from 'lucide-react'
import { SUPPORTED_LANGUAGES, getSelectedLanguage, setSelectedLanguage, type Language } from '../utils/languageSupport'

export default function LanguageSelector() {
  const [selectedLang, setSelectedLang] = useState<Language>(getSelectedLanguage())
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    // Dispatch custom event when language changes so other components can react
    window.dispatchEvent(new CustomEvent('languageChange', { detail: selectedLang }))
  }, [selectedLang])

  const handleLanguageChange = (lang: Language) => {
    setSelectedLang(lang)
    setSelectedLanguage(lang.code)
    setIsOpen(false)
    
    // Show confirmation
    alert(`Language changed to ${lang.nativeName} / ${lang.name}`)
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-white border-2 border-purple-400 rounded-lg hover:bg-purple-50 transition-colors"
      >
        <Globe className="w-5 h-5 text-purple-600" />
        <span className="font-medium text-purple-900">{selectedLang.nativeName}</span>
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          
          {/* Dropdown */}
          <div className="absolute top-full mt-2 right-0 bg-white border-2 border-purple-400 rounded-lg shadow-xl z-50 min-w-[200px] max-h-[400px] overflow-y-auto">
            {SUPPORTED_LANGUAGES.map((lang) => (
              <button
                key={lang.code}
                onClick={() => handleLanguageChange(lang)}
                className={`w-full text-left px-4 py-3 hover:bg-purple-50 transition-colors border-b border-purple-100 last:border-b-0 ${
                  selectedLang.code === lang.code ? 'bg-purple-100 font-semibold' : ''
                }`}
              >
                <div className="text-lg">{lang.nativeName}</div>
                <div className="text-sm text-gray-600">{lang.name}</div>
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
