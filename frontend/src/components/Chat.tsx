import React, { useEffect, useRef } from 'react'
import { User, Bot } from 'lucide-react'

interface Message {
  id: string
  text: string
  sender: 'user' | 'assistant'
  timestamp: Date
}

interface ChatProps {
  messages: Message[]
  isProcessing: boolean
}

const Chat: React.FC<ChatProps> = ({ messages, isProcessing }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isProcessing])

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const formatMessage = (text: string) => {
    // Simple formatting for better readability
    return text
      .split('\n')
      .map((line, index) => (
        <span key={index}>
          {line}
          {index < text.split('\n').length - 1 && <br />}
        </span>
      ))
  }

  return (
    <div className="space-y-4">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div className={`flex items-start space-x-2 max-w-xs lg:max-w-md ${message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
            {/* Avatar */}
            <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
              message.sender === 'user' 
                ? 'bg-vt-orange text-white' 
                : 'bg-vt-maroon text-white'
            }`}>
              {message.sender === 'user' ? (
                <User size={16} />
              ) : (
                <Bot size={16} />
              )}
            </div>

            {/* Message Bubble */}
            <div className={`px-4 py-2 rounded-lg shadow-sm ${
              message.sender === 'user'
                ? 'bg-vt-orange text-white'
                : 'bg-white text-gray-800 border border-gray-200'
            }`}>
              <div className="text-sm leading-relaxed">
                {formatMessage(message.text)}
              </div>
              <div className={`text-xs mt-1 ${
                message.sender === 'user' ? 'text-orange-100' : 'text-gray-500'
              }`}>
                {formatTime(message.timestamp)}
              </div>
            </div>
          </div>
        </div>
      ))}

      {/* Processing Indicator */}
      {isProcessing && (
        <div className="flex justify-start">
          <div className="flex items-start space-x-2 max-w-xs lg:max-w-md">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-vt-maroon text-white flex items-center justify-center">
              <Bot size={16} />
            </div>
            <div className="px-4 py-2 rounded-lg shadow-sm bg-white border border-gray-200">
              <div className="flex items-center space-x-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
                <span className="text-sm text-gray-600">Thinking...</span>
              </div>
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  )
}

export default Chat
