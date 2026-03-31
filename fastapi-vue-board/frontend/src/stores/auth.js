import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/axios'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('access_token'))

  // 로그인 상태 확인
  const isLoggedIn = computed(() => !!token.value)

  // 회원가입
  async function register(email, username, password) {
    const { data } = await api.post('/auth/signup', {  // ← 여기만 변경
      email,
      username,
      password
    })
    return data
  }

  // 로그인
  async function login(email, password) {
    const { data } = await api.post('/auth/login', {
      email,
      password
    })
    token.value = data.access_token
    user.value = data.user
    localStorage.setItem('access_token', data.access_token)
  }

  // 로그아웃
  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('access_token')
  }

  return { user, token, isLoggedIn, register, login, logout }
})