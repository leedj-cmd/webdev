<template>
  <div class="auth-page">
    <div class="bg-blob bg-blob--1"></div>
    <div class="bg-blob bg-blob--2"></div>

    <div class="auth-wrapper">

      <!-- ── 왼쪽: 플랫폼 소개 카드 ── -->
      <div class="side-card">
        <div class="side-brand">
          <RouterLink to="/" class="brand-logo">
            <span class="brand-icon">MiQ</span>
          </RouterLink>
          <div class="brand-info">
            <span class="brand-name">TechBridge</span>
            <span class="brand-sub">관리자 전용</span>
          </div>
        </div>

        <span class="side-badge">ADMIN ONLY</span>

        <p class="side-headline">관리자 계정으로<br>플랫폼 전체를 관리하세요</p>

        <div class="side-divider"></div>

        <p class="side-feature-label">관리자 전용 기능</p>
        <div class="benefit-list">
          <div v-for="item in benefits" :key="item.title" class="benefit-item">
            <div class="benefit-icon-wrap">{{ item.icon }}</div>
            <div>
              <p class="benefit-title">{{ item.title }}</p>
              <p class="benefit-desc">{{ item.description }}</p>
            </div>
          </div>
        </div>

        <div class="side-divider"></div>

        <div class="side-quote">
          <span class="quote-mark">"</span>
          <p class="quote-text">관리자 코드가 있어야 가입할 수 있습니다.<br>채용공고·신고 처리까지 모든 운영 기능을 사용할 수 있습니다.</p>
        </div>
      </div>

      <!-- ── 오른쪽: 관리자 회원가입 폼 ── -->
      <div class="auth-card">
        <span class="page-badge">ADMIN REGISTER</span>
        <h1 class="auth-title">관리자 회원가입</h1>

        <form @submit.prevent="handleRegister" class="auth-form">
          <div class="form-group">
            <label for="email">이메일</label>
            <input id="email" v-model="form.email" type="email" placeholder="admin@example.com"
              :class="{ error: errors.email }" autocomplete="email" />
            <span v-if="errors.email" class="error-msg">{{ errors.email }}</span>
          </div>

          <div class="form-group">
            <label for="username">닉네임</label>
            <input id="username" v-model="form.username" type="text" placeholder="관리자 닉네임을 입력하세요"
              :class="{ error: errors.username }" autocomplete="nickname" />
            <span v-if="errors.username" class="error-msg">{{ errors.username }}</span>
          </div>

          <div class="form-group">
            <label for="password">비밀번호</label>
            <div class="input-wrapper">
              <input id="password" v-model="form.password" :type="showPassword ? 'text' : 'password'"
                placeholder="8자 이상 입력하세요" :class="{ error: errors.password }" autocomplete="new-password" />
              <button type="button" class="toggle-pw" @click="showPassword = !showPassword">
                <svg v-if="!showPassword" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                  stroke-width="2">
                  <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
                  <circle cx="12" cy="12" r="3" />
                </svg>
                <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                  stroke-width="2">
                  <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24" />
                  <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68" />
                  <path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61" />
                  <line x1="2" x2="22" y1="2" y2="22" />
                </svg>
              </button>
            </div>
            <span v-if="errors.password" class="error-msg">{{ errors.password }}</span>
          </div>

          <div class="form-group">
            <label for="adminSecret">관리자 코드</label>
            <div class="input-wrapper">
              <input id="adminSecret" v-model="form.adminSecret" :type="showSecret ? 'text' : 'password'"
                placeholder="관리자 코드를 입력하세요" :class="{ error: errors.adminSecret, 'admin-code': true }" />
              <button type="button" class="toggle-pw" @click="showSecret = !showSecret">
                <svg v-if="!showSecret" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                  stroke-width="2">
                  <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
                  <circle cx="12" cy="12" r="3" />
                </svg>
                <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                  stroke-width="2">
                  <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24" />
                  <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68" />
                  <path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61" />
                  <line x1="2" x2="22" y1="2" y2="22" />
                </svg>
              </button>
            </div>
            <span v-if="errors.adminSecret" class="error-msg">{{ errors.adminSecret }}</span>
            <p class="field-hint">⚠️ .env 파일의 ADMIN_SECRET 값을 입력하세요.</p>
          </div>

          <p v-if="serverError" class="server-error">{{ serverError }}</p>
          <p v-if="successMsg" class="success-msg">{{ successMsg }}</p>

          <button type="submit" class="btn-submit" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            <span v-else>관리자 계정 만들기 →</span>
          </button>
        </form>

        <p class="auth-switch">
          이미 계정이 있으신가요?
          <RouterLink to="/login" class="switch-link">로그인으로 이동</RouterLink>
        </p>
        <p class="auth-switch normal-register-link">
          일반 회원가입을 원하시나요?
          <RouterLink to="/register" class="switch-link">일반 회원가입 →</RouterLink>
        </p>
      </div>

    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const benefits = [
  {
    icon: '📋',
    title: '채용공고 · 공모전 관리',
    description: '새 채용공고와 공모전을 등록하고 수정·삭제할 수 있습니다.',
  },
  {
    icon: '🚨',
    title: '신고 처리',
    description: '사용자가 접수한 게시글·댓글 신고를 검토하고 처리할 수 있습니다.',
  },
  {
    icon: '👥',
    title: '사용자 관리',
    description: '전체 회원 목록을 확인하고 플랫폼 운영에 필요한 조치를 취할 수 있습니다.',
  },
]

const form = reactive({
  email: '',
  username: '',
  password: '',
  adminSecret: '',
})

const errors = reactive({
  email: '',
  username: '',
  password: '',
  adminSecret: '',
})

const showPassword = ref(false)
const showSecret = ref(false)
const loading = ref(false)
const serverError = ref('')
const successMsg = ref('')

function validate() {
  let valid = true
  errors.email = ''
  errors.username = ''
  errors.password = ''
  errors.adminSecret = ''

  if (!form.email) {
    errors.email = '이메일을 입력해주세요'
    valid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.email = '올바른 이메일 형식이 아닙니다'
    valid = false
  }

  if (!form.username) {
    errors.username = '닉네임을 입력해주세요'
    valid = false
  } else if (form.username.length < 2) {
    errors.username = '닉네임은 2자 이상이어야 합니다'
    valid = false
  }

  if (!form.password) {
    errors.password = '비밀번호를 입력해주세요'
    valid = false
  } else if (form.password.length < 8) {
    errors.password = '비밀번호는 8자 이상이어야 합니다'
    valid = false
  }

  if (!form.adminSecret) {
    errors.adminSecret = '관리자 코드를 입력해주세요'
    valid = false
  }

  return valid
}

async function handleRegister() {
  if (!validate()) return
  loading.value = true
  serverError.value = ''
  successMsg.value = ''

  try {
    await authStore.adminRegister(
      form.email,
      form.username,
      form.password,
      form.adminSecret,
    )
    successMsg.value = '관리자 계정이 생성되었습니다! 로그인 페이지로 이동합니다.'
    setTimeout(() => router.push('/login'), 1500)
  } catch (e) {
    serverError.value = e.response?.data?.detail || '회원가입에 실패했습니다. 관리자 코드를 확인해주세요.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ── 배경 ── */
.auth-page {
  min-height: calc(100vh - 64px);
  background: linear-gradient(135deg, #f5ede4 0%, #ede8e0 40%, #e8ddd4 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  position: relative;
  overflow: hidden;
}

.bg-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.35;
  pointer-events: none;
}

.bg-blob--1 {
  width: 500px;
  height: 500px;
  background: #d4b89a;
  top: -120px;
  left: -120px;
}

.bg-blob--2 {
  width: 400px;
  height: 400px;
  background: #c9a882;
  bottom: -100px;
  right: -80px;
}

/* ── 2단 래퍼 ── */
.auth-wrapper {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: stretch;
  gap: 24px;
  width: 100%;
  max-width: 960px;
}

/* ── 왼쪽 소개 카드 ── */
.side-card {
  flex: 1;
  background: #ffffff;
  border-radius: 24px;
  padding: 40px 36px;
  box-shadow: 0 8px 48px rgba(100, 70, 40, 0.12);
  display: flex;
  flex-direction: column;
}

.side-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 28px;
}

.brand-logo {
  text-decoration: none;
  display: flex;
}

.brand-icon {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #3d2b1f 0%, #6b4c38 100%);
  color: #fff;
  border-radius: 50%;
  font-size: 13px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  letter-spacing: -0.5px;
}

.brand-info {
  display: flex;
  flex-direction: column;
}

.brand-name {
  font-size: 14px;
  font-weight: 700;
  color: #1a1209;
  line-height: 1.2;
}

.brand-sub {
  font-size: 11px;
  color: #9a8070;
}

.side-badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: #7a5c42;
  border: 1.5px solid #c9a882;
  border-radius: 20px;
  padding: 3px 12px;
  margin-bottom: 16px;
  align-self: flex-start;
}

.side-headline {
  font-size: 21px;
  font-weight: 800;
  color: #1a1209;
  line-height: 1.45;
  margin: 0 0 12px;
  letter-spacing: -0.3px;
}

.side-divider {
  height: 1px;
  background: #ede5dc;
  margin: 22px 0;
}

.side-feature-label {
  font-size: 16px;
  font-weight: 700;
  color: #7a5c42;
  margin: 0 0 30px;
  letter-spacing: 0.04em;
}

.benefit-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.benefit-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding-bottom: 15px;
}

.benefit-icon-wrap {
  width: 34px;
  height: 34px;
  background: linear-gradient(135deg, #faf6f2 0%, #f0e6d8 100%);
  border: 1.5px solid #e8ddd4;
  border-radius: 9px;
  font-size: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.benefit-title {
  font-size: 13px;
  font-weight: 700;
  color: #2a1e15;
  margin: 0 0 2px;
}

.benefit-desc {
  font-size: 11.5px;
  color: #9a8070;
  line-height: 1.5;
  margin: 0;
}

.side-quote {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  background: linear-gradient(135deg, #faf6f2 0%, #f3ece4 100%);
  border-left: 3px solid #c9a882;
  border-radius: 0 10px 10px 0;
  padding: 14px 16px;
}

.quote-mark {
  font-size: 28px;
  font-weight: 900;
  color: #c9a882;
  line-height: 1;
  flex-shrink: 0;
  margin-top: -4px;
}

.quote-text {
  font-size: 13px;
  font-weight: 600;
  color: #5a4030;
  line-height: 1.7;
  margin: 0;
}

/* ── 오른쪽 회원가입 카드 ── */
.auth-card {
  flex: 1;
  background: #ffffff;
  border-radius: 24px;
  padding: 40px 44px 44px;
  box-shadow: 0 8px 48px rgba(100, 70, 40, 0.12);
  display: flex;
  flex-direction: column;
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
  margin-bottom: 12px;
  align-self: flex-start;
}

.auth-title {
  font-size: 30px;
  font-weight: 800;
  color: #1a1209;
  margin: 0 0 30px;
  letter-spacing: -0.5px;
}

/* ── 폼 ── */
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
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
  transition: border-color 0.15s, box-shadow 0.15s;
  width: 100%;
  background: #faf8f6;
  box-sizing: border-box;
}

.form-group input::placeholder {
  color: #b5a49a;
}

.form-group input:focus {
  border-color: #a0785a;
  box-shadow: 0 0 0 3px rgba(160, 120, 90, 0.12);
  background: #fff;
}

.form-group input.error {
  border-color: #ef4444;
}

.form-group input.admin-code {
  border-color: rgba(230, 143, 0, 0.45);
  background: rgba(255, 248, 235, 0.7);
}

.form-group input.admin-code:focus {
  border-color: rgba(200, 110, 0, 0.65);
  box-shadow: 0 0 0 3px rgba(230, 143, 0, 0.1);
}

.input-wrapper {
  position: relative;
}

.input-wrapper input {
  padding-right: 44px;
}

.toggle-pw {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  border: none;
  background: transparent;
  cursor: pointer;
  color: #b5a49a;
  display: flex;
  align-items: center;
  padding: 0;
  transition: color 0.15s;
}

.toggle-pw:hover {
  color: #a0785a;
}

.field-hint {
  font-size: 12px;
  color: #c47a00;
  margin-top: 0;
  margin-bottom: -10px;
}

.error-msg {
  font-size: 12px;
  color: #ef4444;
}

.server-error {
  font-size: 13px;
  color: #a34d3b;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 10px 14px;
  text-align: center;
}

.success-msg {
  font-size: 13px;
  color: #2e7d32;
  background: rgba(46, 125, 50, 0.08);
  border: 1px solid rgba(46, 125, 50, 0.2);
  border-radius: 8px;
  padding: 10px 14px;
  text-align: center;
}

/* ── 버튼 ── */
.btn-submit {
  height: 54px;
  background: linear-gradient(135deg, #6b4c38 0%, #3d2b1f 100%);
  color: #ffffff;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: filter 0.15s, transform 0.1s;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  margin-top: 4px;
  letter-spacing: -0.2px;
}

.btn-submit:hover:not(:disabled) {
  filter: brightness(1.12);
  transform: translateY(-1px);
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

/* ── 하단 텍스트 ── */
.auth-switch {
  text-align: center;
  margin-top: 20px;
  font-size: 13.5px;
  color: #9a8070;
}

.normal-register-link {
  margin-top: 8px;
  font-size: 12.5px;
  opacity: 0.8;
}

.switch-link {
  color: #a0785a;
  font-weight: 700;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.switch-link:hover {
  opacity: 0.75;
}

/* ── 반응형 ── */
@media (max-width: 768px) {
  .auth-wrapper {
    flex-direction: column;
  }

  .auth-page {
    padding: 24px 16px;
  }

  .auth-card {
    padding: 32px 24px 36px;
  }

  .side-card {
    padding: 32px 24px;
  }
}
</style>
