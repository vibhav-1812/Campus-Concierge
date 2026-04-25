import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/** Turn axios / unknown errors into a short user-facing string */
export function formatApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
      return 'Cannot reach the server. Start the backend (port 8000) or check your network.'
    }
    const data = error.response?.data as { detail?: unknown } | undefined
    const detail = data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      const parts = detail
        .map((d: { msg?: string }) => (typeof d?.msg === 'string' ? d.msg : null))
        .filter(Boolean) as string[]
      if (parts.length) return parts.join(' ')
    }
    const status = error.response?.status
    if (status === 404) return 'That service was not found.'
    if (status === 429) return 'Too many requests. Please wait a moment and try again.'
    if (status != null && status >= 500) {
      return 'The server had a problem. Please try again in a moment.'
    }
    if (status != null) return `Request failed (${status}). Please try again.`
  }
  if (error instanceof Error && error.message) return error.message
  return 'Something went wrong. Please try again.'
}

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

export const askQuestion = async (query: string): Promise<QueryResponse> => {
  try {
    const response = await api.post<QueryResponse>('/ask', { query })
    return response.data
  } catch (error) {
    console.error('Error asking question:', error)
    throw new Error(formatApiError(error))
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
