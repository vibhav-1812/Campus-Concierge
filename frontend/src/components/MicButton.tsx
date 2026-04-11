import React, { useState, useEffect, useRef } from 'react'
import { Mic, MicOff, Loader } from 'lucide-react'

interface MicButtonProps {
  isListening: boolean
  onToggle: () => void
  onTranscript: (transcript: string) => void
  disabled?: boolean
}

const MicButton: React.FC<MicButtonProps> = ({ 
  isListening, 
  onToggle, 
  onTranscript, 
  disabled = false 
}) => {
  const [recognition, setRecognition] = useState<any>(null)
  const [isSupported, setIsSupported] = useState(false)
  const [isInitializing, setIsInitializing] = useState(false)
  const recognitionRef = useRef<any>(null)
  const timeoutRef = useRef<number | null>(null)
  const isRecognitionActive = useRef(false)
  const sessionId = useRef(0)
  const manualStop = useRef(false)

  useEffect(() => {
    // Check for Speech Recognition support
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      setIsSupported(true)
      
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      const recognitionInstance = new SpeechRecognition()
      
      // Configure recognition for continuous manual control
      recognitionInstance.continuous = true
      recognitionInstance.interimResults = true
      recognitionInstance.lang = 'en-US'
      recognitionInstance.maxAlternatives = 1

      // Event handlers
      recognitionInstance.onstart = () => {
        console.log('🎤 Speech recognition started successfully!')
        console.log('📢 Speak continuously - click stop when finished...')
        setIsInitializing(false)
        isRecognitionActive.current = true
        
        // Increment session ID for this recording session
        sessionId.current += 1
        const currentSessionId = sessionId.current
        console.log(`🆔 Starting session ${currentSessionId} - NO AUTO-TIMEOUT`)
        
        // NO AUTO-TIMEOUT - only manual stop allowed
      }

      recognitionInstance.onresult = (event: any) => {
        console.log('Speech recognition results:', event.results)
        
        // Collect all final results into one transcript
        let finalTranscript = ''
        for (let i = 0; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript + ' '
          }
        }
        
        // Store the accumulated transcript but DON'T send it yet
        // We'll only send when user manually stops
        if (finalTranscript.trim()) {
          console.log('Accumulated transcript:', finalTranscript.trim())
          // Store in a ref for when user manually stops
          if (recognitionRef.current) {
            (recognitionRef.current as any).accumulatedTranscript = finalTranscript.trim()
          }
        }
      }

      recognitionInstance.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error)
        setIsInitializing(false)
        isRecognitionActive.current = false
        
        // Don't auto-stop on certain errors that might be recoverable
        if (event.error === 'aborted') {
          // Aborted usually means we stopped it ourselves, don't show error
          return
        }
        
        onToggle() // Stop listening on error
        
        // Show more helpful error messages
        if (event.error === 'no-speech') {
          onTranscript('I didn\'t hear anything. Please try speaking louder and closer to your microphone.')
        } else if (event.error === 'audio-capture') {
          onTranscript('Microphone access denied. Please check your microphone permissions in your browser settings.')
        } else if (event.error === 'not-allowed') {
          onTranscript('Microphone access blocked. Please allow microphone access and try again.')
        } else if (event.error === 'network') {
          onTranscript('Network error. Please check your internet connection.')
        } else if (event.error === 'aborted') {
          // This shouldn't reach here due to early return, but just in case
          return
        } else {
          onTranscript(`Speech recognition error: ${event.error}. Please try the text input option instead.`)
        }
      }

      recognitionInstance.onend = () => {
        console.log('Speech recognition ended')
        setIsInitializing(false)
        isRecognitionActive.current = false
        
        // Clear the timeout when recognition ends
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current)
          timeoutRef.current = null
        }
        
        // If this was a manual stop, send the accumulated transcript
        if (manualStop.current && recognitionRef.current) {
          const accumulatedText = (recognitionRef.current as any).accumulatedTranscript || ''
          if (accumulatedText.trim()) {
            console.log('📤 Sending accumulated transcript on manual stop:', accumulatedText)
            onTranscript(accumulatedText.trim())
            // Clear the accumulated transcript
            ;(recognitionRef.current as any).accumulatedTranscript = ''
          } else {
            console.log('⚠️ No speech captured during recording session')
            onTranscript('I didn\'t hear anything. Please try speaking again.')
          }
          manualStop.current = false
        }
        
        // If recognition ended naturally (browser timeout) and we're still listening,
        // restart it for continuous recording
        else if (isListening && !manualStop.current) {
          console.log('🔄 Recognition ended naturally - restarting for continuous recording')
          setTimeout(() => {
            if (isListening && recognitionRef.current && !manualStop.current) {
              try {
                recognitionRef.current.start()
              } catch (e) {
                console.log('Could not restart recognition:', e)
              }
            }
          }, 100)
        }
      }

      recognitionInstance.onnomatch = () => {
        console.log('No speech was recognized')
        isRecognitionActive.current = false
        onTranscript('I couldn\'t understand what you said. Please try speaking more clearly and make sure your microphone is working.')
        onToggle()
      }

      setRecognition(recognitionInstance)
      recognitionRef.current = recognitionInstance
    } else {
      setIsSupported(false)
    }
  }, [onTranscript, onToggle])

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  useEffect(() => {
    if (isListening && recognition && isSupported && !isInitializing && !isRecognitionActive.current) {
      console.log('Starting speech recognition...')
      setIsInitializing(true)
      
      try {
        if (recognitionRef.current && !isRecognitionActive.current) {
          recognitionRef.current.start()
        }
      } catch (error) {
        console.error('Error starting speech recognition:', error)
        setIsInitializing(false)
        onToggle()
      }
    } else if (!isListening && recognition && isSupported && isRecognitionActive.current) {
      console.log('Stopping speech recognition...')
      try {
        if (recognitionRef.current) {
          recognitionRef.current.stop()
        }
      } catch (error) {
        console.error('Error stopping speech recognition:', error)
      }
    }
  }, [isListening, recognition, isSupported, onToggle, isInitializing])

  const handleClick = () => {
    console.log('🖱️ Button clicked! Current isListening state:', isListening)
    
    if (!isSupported) {
      onTranscript('Speech recognition is not supported in your browser. Please try Chrome or Edge.')
      return
    }
    
    if (disabled) {
      console.log('❌ Button disabled, ignoring click')
      return
    }
    
    // Toggle listening state
    if (isListening) {
      // Stop listening immediately and clear any pending processing
      console.log('🛑 Manually stopping speech recognition...')
      
      // Set manual stop flag so onend knows this was intentional
      manualStop.current = true
      
      // Clear any pending timeouts
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
        timeoutRef.current = null
      }
      
      // Stop recognition if active
      if (recognitionRef.current && isRecognitionActive.current) {
        recognitionRef.current.stop()
      }
      
      // Reset states
      setIsInitializing(false)
      isRecognitionActive.current = false
      sessionId.current += 1 // Invalidate any pending results from previous session
      onToggle()
      
      console.log('✅ Speech recognition manually stopped - transcript will be sent in onend')
    } else {
      // Start listening with clean state
      console.log('🎤 Starting fresh speech recognition...')
      
      // Ensure clean state before starting
      setIsInitializing(false)
      isRecognitionActive.current = false
      manualStop.current = false
      
      // Clear any existing timeouts
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
        timeoutRef.current = null
      }
      
      // Clear any previous accumulated transcript
      if (recognitionRef.current) {
        (recognitionRef.current as any).accumulatedTranscript = ''
      }
      
      onToggle()
    }
  }

  const getButtonClass = () => {
    if (disabled) {
      return 'mic-button bg-gray-400 cursor-not-allowed'
    }
    
    if (isInitializing) {
      return 'mic-button bg-yellow-500 hover:bg-yellow-600 text-white animate-pulse'
    }
    
    if (isListening) {
      return 'mic-button-listening'
    }
    
    return 'mic-button-idle'
  }

  const getIcon = () => {
    if (disabled) {
      return <MicOff size={24} />
    }
    
    if (isInitializing) {
      return <Loader size={24} className="animate-spin" />
    }
    
    return isListening ? <MicOff size={24} /> : <Mic size={24} />
  }

  const getStatusText = () => {
    if (!isSupported) {
      return 'Not Supported'
    }
    
    if (disabled) {
      return 'Processing...'
    }
    
    if (isInitializing) {
      return 'Starting...'
    }
    
    if (isListening) {
      console.log('🔄 Button state: LISTENING - showing stop text')
      return 'Click to Stop Recording'
    }
    
    console.log('🔄 Button state: IDLE - showing start text')
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
      
      {/* Visual indicator when listening */}
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

// Extend Window interface for TypeScript
declare global {
  interface Window {
    SpeechRecognition: any
    webkitSpeechRecognition: any
  }
}

export default MicButton
