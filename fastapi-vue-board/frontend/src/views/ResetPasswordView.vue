<template>
  <div class="reset-page">
    <section class="reset-card">
      <span class="page-badge">PASSWORD RESET</span>
      <h1>새 비밀번호 설정</h1>

      <template v-if="done">
        <div class="status-icon success">✓</div>
        <p>비밀번호가 변경되었습니다. 새 비밀번호로 로그인해주세요.</p>
        <RouterLink to="/login" class="btn-submit">로그인으로 이동</RouterLink>
      </template>

      <template v-else>
        <p>메일로 받은 링크를 확인했습니다. 새 비밀번호를 입력해주세요.</p>
        <div class="form-group">
          <label>새 비밀번호</label>
          <input v-model="form.newPassword" type="password" placeholder="8자 이상 입력하세요" autocomplete="new-password" />
        </div>
        <div class="form-group">
          <label>새 비밀번호 확인</label>
          <input v-model="form.confirmPassword" type="password" placeholder="비밀번호를 다시 입력하세요" autocomplete="new-password" @keyup.enter="handleResetPassword" />
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <button class="btn-submit" :disabled="loading" @click="handleResetPassword">
          <span v-if="loading" class="spinner"></span>
          <span v-else>비밀번호 변경</span>
        </button>
      </template>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import api from '@/api/axios'

const route = useRoute()
const form = reactive({ newPassword: '', confirmPassword: '' })
const loading = ref(false)
const done = ref(false)
const error = ref('')

async function handleResetPassword() {
  error.value = ''
  const token = route.query.token
  if (!token) {
    error.value = '비밀번호 재설정 토큰이 없습니다'
    return
  }
  if (!form.newPassword || form.newPassword.length < 8) {
    error.value = '비밀번호는 8자 이상이어야 합니다'
    return
  }
  if (form.newPassword !== form.confirmPassword) {
    error.value = '비밀번호가 일치하지 않습니다'
    return
  }

  loading.value = true
  try {
    await api.patch('/auth/reset-password', {
      token,
      new_password: form.newPassword,
    })
    done.value = true
  } catch (err) {
    error.value = err.response?.data?.detail || '비밀번호 변경에 실패했습니다'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.reset-page {
  min-height: calc(100vh - 64px);
  background: #f5ede4;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
}

.reset-card {
  width: min(100%, 440px);
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 8px 48px rgba(100, 70, 40, 0.12);
  padding: 40px 36px;
  display: flex;
  flex-direction: column;
  gap: 16px;
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
  align-self: flex-start;
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

.form-group {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.form-group label {
  font-size: 14px;
  font-weight: 600;
  color: #6b4f38;
}

.form-group input {
  height: 50px;
  padding: 0 16px;
  border: 1.5px solid #e8ddd4;
  border-radius: 10px;
  font-size: 15px;
  color: #1a1209;
  outline: none;
  width: 100%;
  background: #faf8f6;
  box-sizing: border-box;
}

.form-group input:focus {
  border-color: #a0785a;
  box-shadow: 0 0 0 3px rgba(160, 120, 90, 0.12);
  background: #fff;
}

.error-msg {
  font-size: 13px;
  color: #ef4444;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 10px 14px;
  text-align: center;
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
  color: #166534;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
}

.btn-submit {
  height: 50px;
  background: linear-gradient(135deg, #6b4c38 0%, #3d2b1f 100%);
  color: #ffffff;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  text-decoration: none;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2.5px solid rgba(255, 255, 255, 0.4);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
