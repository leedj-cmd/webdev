<template>
  <div class="verify-page">
    <section class="verify-card">
      <span class="page-badge">EMAIL VERIFICATION</span>
      <template v-if="status === 'loading'">
        <div class="spinner dark"></div>
        <h1>이메일을 인증하는 중입니다</h1>
        <p>잠시만 기다려주세요.</p>
      </template>
      <template v-else-if="status === 'success'">
        <div class="status-icon success">✓</div>
        <h1>이메일 인증이 완료되었습니다</h1>
        <p>이제 로그인해서 TechBridge를 이용할 수 있습니다.</p>
        <RouterLink to="/login?verified=1" class="btn-submit">로그인으로 이동</RouterLink>
      </template>
      <template v-else>
        <div class="status-icon error">!</div>
        <h1>인증 링크를 확인할 수 없습니다</h1>
        <p>{{ errorMessage }}</p>
        <RouterLink to="/register" class="btn-submit">회원가입으로 이동</RouterLink>
      </template>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import api from '@/api/axios'

const route = useRoute()
const status = ref('loading')
const errorMessage = ref('인증 링크가 만료되었거나 이미 사용되었습니다.')

onMounted(async () => {
  const token = route.query.token
  if (!token) {
    status.value = 'error'
    errorMessage.value = '인증 토큰이 없습니다.'
    return
  }

  try {
    await api.get('/auth/verify-email', { params: { token } })
    status.value = 'success'
  } catch (err) {
    status.value = 'error'
    errorMessage.value = err.response?.data?.detail || errorMessage.value
  }
})
</script>

<style scoped>
.verify-page {
  min-height: calc(100vh - 64px);
  background: #f5ede4;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
}

.verify-card {
  width: min(100%, 440px);
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 8px 48px rgba(100, 70, 40, 0.12);
  padding: 40px 36px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  text-align: center;
}

.page-badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: #7a5c42;
  border: 1.5px solid #c9a882;
  border-radius: 20px;
  padding: 3px 12px;
}

h1 {
  font-size: 26px;
  line-height: 1.35;
  color: #1a1209;
  margin: 0;
}

p {
  color: #6b4f38;
  font-size: 14px;
  line-height: 1.7;
  margin: 0;
}

.status-icon {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 24px;
}

.status-icon.success {
  color: #166534;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
}

.status-icon.error {
  color: #991b1b;
  background: #fef2f2;
  border: 1px solid #fecaca;
}

.btn-submit {
  height: 48px;
  background: linear-gradient(135deg, #6b4c38 0%, #3d2b1f 100%);
  color: #ffffff;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  text-decoration: none;
  margin-top: 8px;
}

.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid rgba(107, 76, 56, 0.2);
  border-top-color: #6b4c38;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
