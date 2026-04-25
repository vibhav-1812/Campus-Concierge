/* HokieAssist main UI — generative AI tools assisted with layout/speech wiring; see docs/AI_USAGE_LOG.md */
import { useState, useEffect, useCallback } from 'react'
import Chat from './components/Chat'
import MicButton from './components/MicButton'
import { askQuestion } from './api'

interface Message {
  id: string
  text: string
  sender: 'user' | 'assistant'
  timestamp: Date
}

function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hello! I\'m HokieAssist, your AI assistant for Virginia Tech. I can help you with dining, transportation, and club events. Try asking me something like "Which dining halls are open?" or "What bus routes are available?"',
      sender: 'assistant',
      timestamp: new Date()
    }
  ])
  const [isListening, setIsListening] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [showTextInput, setShowTextInput] = useState(false)
  const [textInput, setTextInput] = useState('')

  // Cleanup speech synthesis on unmount
  useEffect(() => {
    return () => {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel()
      }
    }
  }, [])

  const addMessage = useCallback((text: string, sender: 'user' | 'assistant') => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text,
      sender,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, newMessage])
  }, [])

  const [isSpeaking, setIsSpeaking] = useState(false)

  const speakText = useCallback((text: string) => {
    if ('speechSynthesis' in window) {
      // Stop any current speech
      window.speechSynthesis.cancel()
      
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.rate = 0.9
      utterance.pitch = 1
      utterance.volume = 0.8
      
      utterance.onstart = () => {
        console.log('AI started speaking')
        setIsSpeaking(true)
      }
      
      utterance.onend = () => {
        console.log('AI finished speaking')
        setIsSpeaking(false)
      }
      
      utterance.onerror = () => {
        console.log('Speech synthesis error')
        setIsSpeaking(false)
      }
      
      window.speechSynthesis.speak(utterance)
    }
  }, [])

  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      console.log('Manually stopping AI speech')
      window.speechSynthesis.cancel()
      setIsSpeaking(false)
    }
  }

  const handleVoiceInput = useCallback(async (transcript: string) => {
    if (!transcript.trim()) return

    // Don't process error messages or system messages
    if (transcript.includes("I didn't hear anything") ||
        transcript.includes("Microphone access") ||
        transcript.includes("Speech recognition error") ||
        transcript.includes("Network error") ||
        transcript.includes("I can help you with")) {
      return
    }

    // Add user message
    addMessage(transcript, 'user')
    setIsProcessing(true)

    try {
      // Send to backend
      const response = await askQuestion(transcript)

      // Add assistant response
      addMessage(response.answer, 'assistant')

      // Speak the response
      speakText(response.answer)

    } catch (error) {
      console.error('Error processing question:', error)
      const errorMessage = 'Sorry, I encountered an error processing your request. Please try again.'
      addMessage(errorMessage, 'assistant')
      speakText(errorMessage)
    } finally {
      setIsProcessing(false)
    }
  }, [addMessage, speakText])

  const toggleListening = useCallback(() => {
    setIsListening(prev => !prev)
  }, [])

  const sendQuery = useCallback(async (query: string) => {
    const q = query.trim()
    if (!q) return

    addMessage(q, 'user')
    setIsProcessing(true)
    setShowTextInput(false)
    setTextInput('')

    try {
      const response = await askQuestion(q)
      addMessage(response.answer, 'assistant')
      speakText(response.answer)
    } catch (error) {
      console.error('Error processing question:', error)
      const errorMessage = 'Sorry, I encountered an error processing your request. Please try again.'
      addMessage(errorMessage, 'assistant')
      speakText(errorMessage)
    } finally {
      setIsProcessing(false)
    }
  }, [addMessage, speakText])

  const handleTextSubmit = () => sendQuery(textInput)

  return (
    <div className="min-h-screen bg-gradient-to-br from-vt-maroon via-gray-900 to-vt-orange">
      {/* Header */}
      <header className="bg-white/10 backdrop-blur-md border-b border-white/20">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">
                HokieAssist
              </h1>
              <p className="text-white/80 mt-1">
                Your AI voice assistant for Virginia Tech
              </p>
            </div>
            <div className="flex items-center space-x-4">
              {/* Status pill — colored dot + label so the current state is glanceable */}
              <div
                className={`flex items-center space-x-2 px-3 py-1.5 rounded-full border text-xs font-medium ${
                  isSpeaking
                    ? 'bg-blue-500/20 border-blue-300/40 text-blue-100'
                    : isListening
                    ? 'bg-red-500/20 border-red-300/40 text-red-100'
                    : isProcessing
                    ? 'bg-yellow-500/20 border-yellow-300/40 text-yellow-100'
                    : 'bg-green-500/20 border-green-300/40 text-green-100'
                }`}
              >
                <span
                  className={`inline-block w-2 h-2 rounded-full ${
                    isSpeaking
                      ? 'bg-blue-300 animate-pulse'
                      : isListening
                      ? 'bg-red-400 animate-pulse'
                      : isProcessing
                      ? 'bg-yellow-300 animate-pulse'
                      : 'bg-green-400'
                  }`}
                ></span>
                <span>
                  {isSpeaking
                    ? 'AI Speaking'
                    : isListening
                    ? 'Listening'
                    : isProcessing
                    ? 'Thinking'
                    : 'Ready'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-2xl overflow-hidden">
          {/* Chat Area */}
          <div className="h-96 overflow-y-auto p-6">
            <Chat 
              messages={messages}
              isProcessing={isProcessing}
            />
          </div>

          {/* Voice Input Area */}
          <div className="border-t border-gray-200 p-6 bg-gray-50">
            <div className="flex flex-col items-center space-y-4">
              <div className="text-center">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">
                  Voice Assistant
                </h3>
                <p className="text-sm text-gray-600">
                  Click to start recording, speak your question, then click again to stop
                </p>
              </div>
              
              <MicButton
                isListening={isListening}
                onToggle={toggleListening}
                onTranscript={handleVoiceInput}
                disabled={isProcessing}
              />

              {/* Stop Speaking Button - Only show when AI is speaking */}
              {isSpeaking && (
                <div className="flex flex-col items-center space-y-2">
                  <button
                    onClick={stopSpeaking}
                    className="mic-button bg-red-500 hover:bg-red-600 text-white"
                    title="Stop AI Speech"
                  >
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                      <rect x="6" y="6" width="4" height="12" />
                      <rect x="14" y="6" width="4" height="12" />
                    </svg>
                  </button>
                  <p className="text-sm font-medium text-red-600">
                    AI is speaking... Click to stop
                  </p>
                </div>
              )}
              
              <div className="text-xs text-gray-500 text-center max-w-sm mb-4">
                Try asking: "Which dining halls are open?" or "What bus routes are available?"
                <br />
                <span className="text-red-500">If voice doesn't work, check browser console (F12) for errors</span>
              </div>

              {/* Text Input Fallback */}
              <div className="flex flex-col items-center space-y-2">
                {!showTextInput ? (
                  <button
                    onClick={() => setShowTextInput(true)}
                    className="text-sm text-vt-orange hover:text-orange-700 underline"
                  >
                    Or type your question instead
                  </button>
                ) : (
                  <div className="flex flex-col items-center space-y-2 w-full max-w-md">
                    <input
                      type="text"
                      value={textInput}
                      onChange={(e) => setTextInput(e.target.value)}
                      placeholder="Type your question here..."
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-vt-orange focus:border-transparent"
                      onKeyPress={(e) => e.key === 'Enter' && handleTextSubmit()}
                      autoFocus
                    />
                    <div className="flex space-x-2">
                      <button
                        onClick={handleTextSubmit}
                        disabled={!textInput.trim() || isProcessing}
                        className="btn-primary text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Ask
                      </button>
                      <button
                        onClick={() => {
                          setShowTextInput(false)
                          setTextInput('')
                        }}
                        className="btn-secondary text-sm"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions — clicking a card sends the question right away */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            {
              icon: '🍽️',
              title: 'Dining',
              desc: 'Find open dining halls and meal options',
              query: 'Which dining halls are open?',
            },
            {
              icon: '🚌',
              title: 'Transportation',
              desc: 'Check bus schedules and routes',
              query: 'What bus routes are available?',
            },
            {
              icon: '🎉',
              title: 'Events',
              desc: 'Discover club events and activities',
              query: 'What club events are coming up?',
            },
          ].map((card) => (
            <button
              key={card.title}
              type="button"
              onClick={() => sendQuery(card.query)}
              disabled={isProcessing}
              className="text-left bg-white/90 backdrop-blur-sm rounded-xl p-6 shadow-lg
                         transition-all duration-200 hover:-translate-y-1 hover:shadow-2xl
                         focus:outline-none focus:ring-2 focus:ring-vt-orange
                         disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:translate-y-0"
            >
              <div className="text-2xl mb-2">{card.icon}</div>
              <h3 className="font-semibold text-gray-800 mb-1">{card.title}</h3>
              <p className="text-sm text-gray-600 mb-3">{card.desc}</p>
              <span className="text-sm font-medium text-vt-orange">
                Ask now →
              </span>
            </button>
          ))}
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-12 bg-white/10 backdrop-blur-md border-t border-white/20">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="text-center text-white/80">
            <p className="text-sm">
              Powered by AI • Built for Virginia Tech students
            </p>
            <p className="text-xs mt-2">
              Data sourced from UDC, Blacksburg Transit, and Gobbler Connect
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App