import React, { useState, useRef, useCallback } from 'react'
import { Mic, MicOff, Loader } from 'lucide-react'

interface MicButtonProps {
  isListening: boolean
  onToggle: () => void
  onTranscript: (transcript: string) => void
  disabled?: boolean
  transcribeAudio: (blob: Blob) => Promise<string>
}

function pickMime(): string | undefined {
  for (const t of ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4']) {
    if (typeof MediaRecorder !== 'undefined' && MediaRecorder.isTypeSupported(t)) return t
  }
  return undefined
}

const MicButton: React.FC<MicButtonProps> = ({
  isListening,
  onToggle,
  onTranscript,
  disabled = false,
  transcribeAudio,
}) => {
  const [isTranscribing, setIsTranscribing] = useState(false)
  const mediaStreamRef = useRef<MediaStream | null>(null)
  const recorderRef = useRef<MediaRecorder | null>(null)
  const transcribeFnRef = useRef(transcribeAudio)
  transcribeFnRef.current = transcribeAudio

  const isSupported =
    typeof MediaRecorder !== 'undefined' && !!navigator.mediaDevices?.getUserMedia

  const stopStream = useCallback(() => {
    mediaStreamRef.current?.getTracks().forEach((t) => t.stop())
    mediaStreamRef.current = null
  }, [])

  const handleClick = async () => {
    if (disabled || isTranscribing) return

    if (isListening) {
      const rec = recorderRef.current
      if (rec && rec.state === 'recording') {
        setIsTranscribing(true)
        if (typeof rec.requestData === 'function') {
          try {
            rec.requestData()
          } catch {
            /* ignore */
          }
        }
        rec.stop()
      } else {
        stopStream()
      }
      onToggle()
      return
    }

    if (!isSupported) {
      onTranscript('Recording is not supported in this browser. Use Chrome or Edge.')
      return
    }

    let stream: MediaStream
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true },
      })
    } catch (err: unknown) {
      const name = err instanceof DOMException ? err.name : ''
      if (name === 'NotAllowedError' || name === 'PermissionDeniedError') {
        onTranscript('Microphone permission denied. Allow the mic and try again.')
      } else if (name === 'NotFoundError') {
        onTranscript('No microphone found. Connect one or use text input.')
      } else {
        onTranscript(`Could not open microphone (${name || 'unknown error'}).`)
      }
      return
    }

    mediaStreamRef.current = stream
    const mime = pickMime()
    const rec = mime ? new MediaRecorder(stream, { mimeType: mime }) : new MediaRecorder(stream)
    const chunks: Blob[] = []

    rec.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.push(e.data)
    }

    rec.onstop = async () => {
      recorderRef.current = null
      stopStream()
      const blob = new Blob(chunks, { type: rec.mimeType || 'audio/webm' })
      if (blob.size < 100) {
        setIsTranscribing(false)
        onTranscript("Recording was too short. Hold the mic button and speak, then click again to stop.")
        return
      }
      try {
        const text = await transcribeFnRef.current(blob)
        if (text.trim()) {
          onTranscript(text.trim())
        } else {
          onTranscript("Didn't catch anything. Try speaking louder or closer to the mic.")
        }
      } catch (e) {
        const detail = e instanceof Error ? e.message : 'Unknown error'
        onTranscript(
          detail.startsWith('Could not') || detail.includes('ffmpeg')
            ? detail
            : `Transcription failed: ${detail}`
        )
      } finally {
        setIsTranscribing(false)
      }
    }

    recorderRef.current = rec
    rec.start(250)
    onToggle()
  }

  const busy = disabled || isTranscribing
  const getButtonClass = () => {
    if (busy) return 'mic-button bg-gray-400 cursor-not-allowed'
    if (isTranscribing) return 'mic-button bg-yellow-500 text-white animate-pulse'
    if (isListening) return 'mic-button-listening'
    return 'mic-button-idle'
  }

  const getIcon = () => {
    if (isTranscribing) return <Loader size={24} className="animate-spin" />
    if (busy) return <MicOff size={24} />
    return isListening ? <MicOff size={24} /> : <Mic size={24} />
  }

  const getStatusText = () => {
    if (!isSupported) return 'Not Supported'
    if (isTranscribing) return 'Transcribing...'
    if (disabled) return 'Processing...'
    if (isListening) return 'Click to Stop & Send'
    return 'Click to Record'
  }

  return (
    <div className="flex flex-col items-center space-y-3">
      <button
        onClick={handleClick}
        disabled={busy}
        className={getButtonClass()}
        title={getStatusText()}
      >
        {getIcon()}
      </button>

      <div className="text-center">
        <p className="text-sm font-medium text-gray-700">{getStatusText()}</p>
        {!isSupported && (
          <p className="text-xs text-red-600 mt-1">Use Chrome or Edge for voice support</p>
        )}
      </div>

      {isListening && (
        <div className="flex space-x-1">
          <div className="w-1 h-8 bg-red-500 rounded-full animate-pulse" />
          <div className="w-1 h-6 bg-red-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }} />
          <div className="w-1 h-10 bg-red-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }} />
          <div className="w-1 h-6 bg-red-500 rounded-full animate-pulse" style={{ animationDelay: '0.6s' }} />
          <div className="w-1 h-8 bg-red-500 rounded-full animate-pulse" style={{ animationDelay: '0.8s' }} />
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
