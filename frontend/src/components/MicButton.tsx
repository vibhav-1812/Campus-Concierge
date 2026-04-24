import React, { useState, useEffect, useRef } from 'react'
import { Mic, MicOff, Loader } from 'lucide-react'

interface MicButtonProps {
  isListening: boolean
  onToggle: () => void
  onTranscript: (transcript: string) => void
  disabled?: boolean
}

const MAX_NETWORK_RETRIES = 3

const MicButton: React.FC<MicButtonProps> = ({
  isListening,
  onToggle,
  onTranscript,
  disabled = false
}) => {
  const [isSupported, setIsSupported] = useState(false)
  const [isInitializing, setIsInitializing] = useState(false)
  const recognitionRef = useRef<any>(null)
  const timeoutRef = useRef<number | null>(null)
  const isRecognitionActive = useRef(false)
  const manualStop = useRef(false)

  // Refs to avoid stale closures in event handlers
  const isListeningRef = useRef(isListening)
  const onTranscriptRef = useRef(onTranscript)
  const onToggleRef = useRef(onToggle)
  const networkRetryCount = useRef(0)

  // Keep refs in sync with latest props
  useEffect(() => { isListeningRef.current = isListening }, [isListening])
  useEffect(() => { onTranscriptRef.current = onTranscript }, [onTranscript])
  useEffect(() => { onToggleRef.current = onToggle }, [onToggle])

  // One-time setup of the recognition instance
  useEffect(() => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      setIsSupported(false)
      return
    }

    setIsSupported(true)

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    const instance = new SpeechRecognition()

    instance.continuous = true
    instance.interimResults = true
    instance.lang = 'en-US'
    instance.maxAlternatives = 1

    instance.onstart = () => {
      console.log('Speech recognition started')
      setIsInitializing(false)
      isRecognitionActive.current = true
      networkRetryCount.current = 0
    }

    instance.onresult = (event: any) => {
      let finalTranscript = ''
      for (let i = 0; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript + ' '
        }
      }
      if (finalTranscript.trim()) {
        ;(recognitionRef.current as any).accumulatedTranscript = finalTranscript.trim()
      }
    }

    instance.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error)
      setIsInitializing(false)
      isRecognitionActive.current = false

      if (event.error === 'aborted') return

      if (event.error === 'network') {
        if (isListeningRef.current && networkRetryCount.current < MAX_NETWORK_RETRIES) {
          networkRetryCount.current++
          const delay = networkRetryCount.current * 1500
          console.log(`Network error — retrying in ${delay}ms (attempt ${networkRetryCount.current}/${MAX_NETWORK_RETRIES})`)
          setTimeout(() => {
            if (isListeningRef.current && recognitionRef.current && !isRecognitionActive.current) {
              try {
                setIsInitializing(true)
                recognitionRef.current.start()
              } catch (e) {
                console.error('Retry failed:', e)
                setIsInitializing(false)
                onToggleRef.current()
                onTranscriptRef.current('Network error. Please check your internet connection and try again.')
              }
            }
          }, delay)
          return
        }

        networkRetryCount.current = 0
        onToggleRef.current()
        onTranscriptRef.current('Network error: voice recognition requires an internet connection. Please check your connection and try again.')
        return
      }

      onToggleRef.current()

      if (event.error === 'no-speech') {
        onTranscriptRef.current("I didn't hear anything. Please try speaking louder or closer to your microphone.")
      } else if (event.error === 'audio-capture') {
        onTranscriptRef.current('Microphone access denied. Please check your microphone permissions in your browser settings.')
      } else if (event.error === 'not-allowed') {
        onTranscriptRef.current('Microphone access blocked. Please allow microphone access and try again.')
      } else {
        onTranscriptRef.current(`Speech recognition error: ${event.error}. Please try the text input option instead.`)
      }
    }

    instance.onend = () => {
      console.log('Speech recognition ended')
      setIsInitializing(false)
      isRecognitionActive.current = false

      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
        timeoutRef.current = null
      }

      if (manualStop.current) {
        const accumulatedText = (recognitionRef.current as any)?.accumulatedTranscript || ''
        if (accumulatedText.trim()) {
          console.log('Sending transcript:', accumulatedText)
          onTranscriptRef.current(accumulatedText.trim())
          ;(recognitionRef.current as any).accumulatedTranscript = ''
        } else {
          onTranscriptRef.current("I didn't hear anything. Please try speaking again.")
        }
        manualStop.current = false
      } else if (isListeningRef.current) {
        // Browser timed out naturally — restart for continuous recording
        console.log('Restarting recognition for continuous recording')
        setTimeout(() => {
          if (isListeningRef.current && recognitionRef.current && !isRecognitionActive.current && !manualStop.current) {
            try {
              recognitionRef.current.start()
            } catch (e) {
              console.log('Could not restart recognition:', e)
            }
          }
        }, 100)
      }
    }

    instance.onnomatch = () => {
      console.log('No speech recognized')
      isRecognitionActive.current = false
      onTranscriptRef.current("I couldn't understand what you said. Please try speaking more clearly.")
      onToggleRef.current()
    }

    recognitionRef.current = instance

    return () => {
      try { instance.abort() } catch (_) {}
      isRecognitionActive.current = false
    }
  }, []) // Run once on mount only

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
    }
  }, [])

  // Start/stop recognition in response to isListening changes
  useEffect(() => {
    if (isListening && isSupported && !isInitializing && !isRecognitionActive.current) {
      console.log('Starting speech recognition...')
      setIsInitializing(true)
      try {
        recognitionRef.current?.start()
      } catch (error) {
        console.error('Error starting speech recognition:', error)
        setIsInitializing(false)
        onToggle()
      }
    } else if (!isListening && isSupported && isRecognitionActive.current) {
      console.log('Stopping speech recognition...')
      try {
        recognitionRef.current?.stop()
      } catch (error) {
        console.error('Error stopping speech recognition:', error)
      }
    }
  }, [isListening, isSupported, isInitializing, onToggle])

  const handleClick = () => {
    if (!isSupported) {
      onTranscript('Speech recognition is not supported in your browser. Please try Chrome or Edge.')
      return
    }
    if (disabled) return

    if (isListening) {
      console.log('Manually stopping speech recognition...')
      manualStop.current = true

      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
        timeoutRef.current = null
      }

      if (recognitionRef.current && isRecognitionActive.current) {
        recognitionRef.current.stop()
      }

      setIsInitializing(false)
      isRecognitionActive.current = false
      networkRetryCount.current = 0
      onToggle()
    } else {
      console.log('Starting speech recognition...')
      manualStop.current = false
      networkRetryCount.current = 0
      setIsInitializing(false)
      isRecognitionActive.current = false

      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
        timeoutRef.current = null
      }

      if (recognitionRef.current) {
        ;(recognitionRef.current as any).accumulatedTranscript = ''
      }

      onToggle()
    }
  }

  const getButtonClass = () => {
    if (disabled) return 'mic-button bg-gray-400 cursor-not-allowed'
    if (isInitializing) return 'mic-button bg-yellow-500 hover:bg-yellow-600 text-white animate-pulse'
    if (isListening) return 'mic-button-listening'
    return 'mic-button-idle'
  }

  const getIcon = () => {
    if (disabled) return <MicOff size={24} />
    if (isInitializing) return <Loader size={24} className="animate-spin" />
    return isListening ? <MicOff size={24} /> : <Mic size={24} />
  }

  const getStatusText = () => {
    if (!isSupported) return 'Not Supported'
    if (disabled) return 'Processing...'
    if (isInitializing) return 'Starting...'
    if (isListening) return 'Click to Stop Recording'
    return 'Click to Start Recording'
  }

  return (
    <div className="flex flex-col items-center space-y-3">
      <button
        onClick={handleClick}
        disabled={disabled}
        className={getButtonClass()}
        title={getStatusText()}
      >
        {getIcon()}
      </button>

      <div className="text-center">
        <p className="text-sm font-medium text-gray-700">
          {getStatusText()}
        </p>
        {!isSupported && (
          <p className="text-xs text-red-600 mt-1">
            Use Chrome or Edge for voice support
          </p>
        )}
      </div>

      {isListening && (
        <div className="flex space-x-1">
          <div className="w-1 h-8 bg-red-500 rounded-full animate-pulse"></div>
          <div className="w-1 h-6 bg-red-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
          <div className="w-1 h-10 bg-red-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
          <div className="w-1 h-6 bg-red-500 rounded-full animate-pulse" style={{ animationDelay: '0.6s' }}></div>
          <div className="w-1 h-8 bg-red-500 rounded-full animate-pulse" style={{ animationDelay: '0.8s' }}></div>
        </div>
      )}
    </div>
  )
}

declare global {
  interface Window {
    SpeechRecognition: any
    webkitSpeechRecognition: any
  }
}

export default MicButton
