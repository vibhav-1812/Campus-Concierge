import axios from 'axios'

/**
 * Base URL for all backend calls.
 * - VITE_API_URL if set → direct to FastAPI (e.g. http://localhost:8000).
 * - Dev without env → "/api" so Vite proxies to port 8000 (vite.config.ts).
 * - Production build without env → http://localhost:8000 (set VITE_API_URL when deploying).
 */
function getApiBaseUrl(): string {
  const fromEnv = import.meta.env.VITE_API_URL?.trim()
  if (fromEnv) return fromEnv.replace(/\/$/, '')
  if (import.meta.env.DEV) return '/api'
  return 'http://localhost:8000'
}

export const API_BASE_URL = getApiBaseUrl()

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface QueryResponse {
  answer: string
  sources: string[]
}

export interface DiningResponse {
  dining_halls: string
  sources: string[]
}

export interface BusResponse {
  bus_times: string
  sources: string[]
}

export interface ClubsResponse {
  events: string
  sources: string[]
}

function formatAxiosDetail(data: unknown): string {
  if (data && typeof data === 'object' && 'detail' in data) {
    const d = (data as { detail: unknown }).detail
    if (typeof d === 'string') return d
    if (Array.isArray(d)) {
      return d
        .map((x) => (x && typeof x === 'object' && 'msg' in x ? String((x as { msg: string }).msg) : String(x)))
        .join('; ')
    }
  }
  return ''
}

function transcribeEndpoint(): string {
  const base = API_BASE_URL
  return base.endsWith('/') ? `${base}transcribe` : `${base}/transcribe`
}

/** Server-side speech-to-text (Whisper or free Google via SpeechRecognition lib). */
export const transcribeAudio = async (blob: Blob): Promise<string> => {
  const form = new FormData()
  form.append('file', blob, 'speech.webm')
  try {
    const { data } = await axios.post<{ text: string }>(transcribeEndpoint(), form)
    return (data.text || '').trim()
  } catch (err) {
    if (axios.isAxiosError(err) && err.response?.status === 404) {
      throw new Error(
        'Transcription endpoint not found (404). Use the same API base as /ask: in dev leave VITE_API_URL unset so requests go to /api, or set VITE_API_URL=http://localhost:8000. Restart the backend after git pull.'
      )
    }
    if (axios.isAxiosError(err) && err.response?.data) {
      const msg = formatAxiosDetail(err.response.data)
      if (msg && msg !== 'Not Found') throw new Error(msg)
      if (msg === 'Not Found') {
        throw new Error(
          'Server returned Not Found — the request likely hit the frontend (wrong URL). Set VITE_API_URL=http://localhost:8000 or use dev server without VITE_API_URL so /api proxy is used.'
        )
      }
    }
    if (axios.isAxiosError(err) && err.code === 'ERR_NETWORK') {
      throw new Error(
        `Cannot reach the API (${API_BASE_URL}). Start the backend: cd backend && python main.py`
      )
    }
    throw err instanceof Error ? err : new Error('Transcription request failed.')
  }
}

export const askQuestion = async (query: string): Promise<QueryResponse> => {
  try {
    const response = await api.post<QueryResponse>('/ask', { query })
    return response.data
  } catch (error) {
    console.error('Error asking question:', error)
    throw new Error('Failed to get response from AI assistant')
  }
}

export const getDiningStatus = async (): Promise<DiningResponse> => {
  try {
    const response = await api.get<DiningResponse>('/dining')
    return response.data
  } catch (error) {
    console.error('Error fetching dining status:', error)
    throw new Error('Failed to fetch dining information')
  }
}

export const getBusStatus = async (): Promise<BusResponse> => {
  try {
    const response = await api.get<BusResponse>('/bus')
    return response.data
  } catch (error) {
    console.error('Error fetching bus status:', error)
    throw new Error('Failed to fetch bus information')
  }
}

export const getClubsEvents = async (): Promise<ClubsResponse> => {
  try {
    const response = await api.get<ClubsResponse>('/clubs')
    return response.data
  } catch (error) {
    console.error('Error fetching club events:', error)
    throw new Error('Failed to fetch club events')
  }
}

// Health check function
export const checkApiHealth = async (): Promise<boolean> => {
  try {
    const response = await api.get('/')
    return response.status === 200
  } catch (error) {
    console.error('API health check failed:', error)
    return false
  }
}
