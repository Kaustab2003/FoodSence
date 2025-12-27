import { useState, useEffect } from 'react'
import { Mic, MicOff, Volume2 } from 'lucide-react'

interface VoiceInputProps {
  onTranscript: (text: string) => void
  enableTTS?: boolean  // Enable text-to-speech responses
  onVoiceCommand?: (command: string) => void  // Handle voice commands
}

export default function VoiceInput({ onTranscript, enableTTS = false, onVoiceCommand }: VoiceInputProps) {
  const [isListening, setIsListening] = useState(false)
  const [isSupported, setIsSupported] = useState(false)
  const [recognition, setRecognition] = useState<any>(null)
  const [isSpeaking, setIsSpeaking] = useState(false)

  useEffect(() => {
    // Check if Web Speech API is supported
    if (typeof window !== 'undefined') {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
      
      if (SpeechRecognition) {
        const recognitionInstance = new SpeechRecognition()
        recognitionInstance.continuous = true
        recognitionInstance.interimResults = true
        recognitionInstance.lang = 'en-US'

        recognitionInstance.onresult = (event: any) => {
          const transcript = Array.from(event.results)
            .map((result: any) => result[0])
            .map((result: any) => result.transcript)
            .join('')

          // Check for voice commands
          if (onVoiceCommand && detectVoiceCommand(transcript)) {
            onVoiceCommand(transcript)
          } else {
            onTranscript(transcript)
          }
        }

        recognitionInstance.onerror = (event: any) => {
          console.error('Speech recognition error:', event.error)
          setIsListening(false)
        }

        recognitionInstance.onend = () => {
          setIsListening(false)
        }

        setRecognition(recognitionInstance)
        setIsSupported(true)
      }
    }
  }, [onTranscript])

  const toggleListening = () => {
    if (!recognition) return

    if (isListening) {
      recognition.stop()
      setIsListening(false)
    } else {
      recognition.start()
      setIsListening(true)
    }
  }

  // Text-to-Speech function
  const speak = (text: string) => {
    if (!enableTTS || typeof window === 'undefined') return

    // Stop any ongoing speech
    window.speechSynthesis.cancel()

    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'en-US'
    utterance.rate = 0.9  // Slightly slower for clarity
    utterance.pitch = 1.0
    utterance.volume = 1.0

    utterance.onstart = () => setIsSpeaking(true)
    utterance.onend = () => setIsSpeaking(false)
    utterance.onerror = () => setIsSpeaking(false)

    window.speechSynthesis.speak(utterance)
  }

  // Detect voice commands
  const detectVoiceCommand = (transcript: string): boolean => {
    const lower = transcript.toLowerCase()
    return lower.includes('analyze') || 
           lower.includes('check this') ||
           lower.includes('what about') ||
           lower.includes('tell me about')
  }

  // Expose speak function to parent (via ref would be better, but keeping it simple)
  useEffect(() => {
    if (enableTTS && typeof window !== 'undefined') {
      (window as any).foodSenseSpeak = speak
    }
  }, [enableTTS])

  if (!isSupported) {
    return (
      <div className="text-sm text-gray-500 text-center py-2">
        Voice input not supported in this browser
      </div>
    )
  }

  return (
    <div className="flex items-center justify-center gap-3">
      <button
        onClick={toggleListening}
        className={`flex items-center px-6 py-3 rounded-lg font-semibold shadow-lg transition-all ${
          isListening
            ? 'bg-red-600 hover:bg-red-700 text-white animate-pulse'
            : 'bg-blue-600 hover:bg-blue-700 text-white'
        }`}
      >
        {isListening ? (
          <>
            <MicOff className="w-5 h-5 mr-2" />
            Stop Listening
          </>
        ) : (
          <>
            <Mic className="w-5 h-5 mr-2" />
            Speak Ingredients
          </>
        )}
      </button>
      
      {isSpeaking && enableTTS && (
        <div className="flex items-center text-green-600 animate-fade-in">
          <Volume2 className="w-5 h-5 mr-2 animate-pulse" />
          <span className="text-sm font-medium">AI Speaking...</span>
        </div>
      )}
      
      {isListening && (
        <span className="text-sm text-gray-600 animate-fade-in">
          🎤 Listening... Try saying "analyze this"
        </span>
      )}
    </div>
  )
}
