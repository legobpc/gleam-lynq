import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 10000 // 10 sec timeout
})

// Інтерцептор для логів:
apiClient.interceptors.request.use(config => {
  console.log(`[API] ${config.method.toUpperCase()} ${config.url}`, config)
  return config
})

apiClient.interceptors.response.use(
  response => response,
  error => {
    console.error('[API ERROR]', error)
    return Promise.reject(error)
  }
)

export default apiClient
