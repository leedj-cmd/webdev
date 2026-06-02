import axios from 'axios'

const isProd = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1'
const BASE_URL = isProd ? '/api' : 'http://127.0.0.1:8000'

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

// 요청 인터셉터 - 토큰 자동 첨부
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 응답 인터셉터(401) 처리
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const requestUrl = err.config?.url || ''
    const isAuthRequest = requestUrl.includes('/auth/login') || requestUrl.includes('/auth/signup')

    if (err.response?.status === 401 && !isAuthRequest) {
      localStorage.removeItem('access_token')
      if (window.location.pathname !== '/login') {
        window.location.assign('/login')
      }
    }
    return Promise.reject(err)
  }
)


export default api
