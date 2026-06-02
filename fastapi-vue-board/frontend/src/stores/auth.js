import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/axios'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('access_token'))

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  // 앱 초기 로드 시 토큰으로 유저 정보 복원
  async function fetchMe() {
    if (!token.value) return
    try {
      const { data } = await api.get('/auth/me')
      user.value = data
    } catch {
      logout()
    }
  }

  // 일반 회원가입
  async function register(email, username, password) {
    const { data } = await api.post('/auth/signup', { email, username, password })
    return data
  }

  async function resendVerification(email) {
    const { data } = await api.post('/auth/resend-verification', { email })
    return data
  }

  // 관리자 회원가입 (admin_secret 필요)
  async function adminRegister(email, username, password, adminSecret) {
    const { data } = await api.post(
      `/auth/signup/admin?admin_secret=${encodeURIComponent(adminSecret)}`,
      { email, username, password }
    )
    return data
  }

  // 일반 유저 → 관리자 승격 (admin_secret 필요)
  async function promoteToAdmin(email, adminSecret) {
    const { data } = await api.patch(
      `/auth/promote/admin?email=${encodeURIComponent(email)}&admin_secret=${encodeURIComponent(adminSecret)}`
    )
    return data
  }

  // 로그인
  async function login(email, password) {
    const { data } = await api.post('/auth/login', { email, password })
    token.value = data.access_token
    localStorage.setItem('access_token', data.access_token)
    await fetchMe()
  }

  // 로그아웃
  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('access_token')
  }

  return {
    user, token,
    isLoggedIn, isAdmin,
    register, resendVerification, adminRegister, promoteToAdmin,
    login, logout, fetchMe
  }
})
