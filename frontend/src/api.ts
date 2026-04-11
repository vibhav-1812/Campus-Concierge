import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

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
