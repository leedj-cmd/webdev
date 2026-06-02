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
            <span class="brand-sub">개발자 메인 허브</span>
          </div>
        </div>

        <span class="side-badge">ABOUT</span>

        <p class="side-headline">가입 하나로 커리어 준비의<br>중심을 잡아보세요</p>

        <div class="side-divider"></div>

        <p class="side-feature-label">가입하면 달라지는 것들</p>
        <div class="benefit-list">
          <div class="benefit-item">
            <div class="benefit-icon-wrap">📌</div>
            <div>
              <p class="benefit-title">관심 공고 북마크 저장</p>
              <p class="benefit-desc">채용 공고와 공모전을 저장하고 언제든 이어보세요</p>
            </div>
          </div>
          <div class="benefit-item">
            <div class="benefit-icon-wrap">🗂️</div>
            <div>
              <p class="benefit-title">기술 스택 기반 개인 보드</p>
              <p class="benefit-desc">관심 스택 중심으로 메인 보드가 자동 구성돼요</p>
            </div>
          </div>
          <div class="benefit-item">
            <div class="benefit-icon-wrap">💬</div>
            <div>
              <p class="benefit-title">커뮤니티 참여</p>
              <p class="benefit-desc">게시글 작성과 댓글로 다른 개발자들과 소통해요</p>
            </div>
          </div>
          <div class="benefit-item">
            <div class="benefit-icon-wrap">🔔</div>
            <div>
              <p class="benefit-title">마감 임박 우선 노출</p>
              <p class="benefit-desc">관심 공고 마감이 다가오면 상단에 먼저 표시돼요</p>
            </div>
          </div>
        </div>

        <div class="side-divider"></div>

        <div class="side-quote">
          <span class="quote-mark">"</span>
          <p class="quote-text">처음 들어와도 바로 감이 오도록,<br>가입 경험부터 같은 톤으로 맞췄습니다.</p>
        </div>
      </div>

      <!-- ── 오른쪽: 회원가입 폼 ── -->
      <div class="auth-card">
        <span class="page-badge">CREATE ACCOUNT</span>
        <h1 class="auth-title">회원가입</h1>

        <div v-if="verificationSent" class="verification-panel">
          <div class="verification-icon">✓</div>
          <h2>인증 메일을 보냈습니다</h2>
          <p>
            <strong>{{ registeredEmail }}</strong> 주소로 보낸 링크를 열면 가입이 완료됩니다.
            인증 전에는 로그인할 수 없습니다.
          </p>
          <p v-if="resendMessage" class="success-msg">{{ resendMessage }}</p>
          <p v-if="resendError" class="server-error">{{ resendError }}</p>
          <button type="button" class="btn-submit" :disabled="resendLoading" @click="handleResendVerification">
            <span v-if="resendLoading" class="spinner"></span>
            <span v-else>인증 메일 다시 보내기</span>
          </button>
          <RouterLink to="/login" class="secondary-link">로그인 화면으로 이동</RouterLink>
        </div>

        <form v-else @submit.prevent="handleRegister" class="auth-form">
          <div class="form-group">
            <label for="email">이메일</label>
            <input id="email" v-model="form.email" type="email" placeholder="example@email.com"
              :class="{ error: errors.email }" autocomplete="email" />
            <span v-if="errors.email" class="error-msg">{{ errors.email }}</span>
          </div>

          <div class="form-group">
            <label for="username">닉네임</label>
            <input id="username" v-model="form.username" type="text" placeholder="사용할 닉네임을 입력하세요"
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
            <label for="passwordConfirm">비밀번호 확인</label>
            <div class="input-wrapper">
              <input id="passwordConfirm" v-model="form.passwordConfirm"
                :type="showPasswordConfirm ? 'text' : 'password'" placeholder="비밀번호를 다시 입력하세요"
                :class="{ error: errors.passwordConfirm }" autocomplete="new-password" />
              <button type="button" class="toggle-pw" @click="showPasswordConfirm = !showPasswordConfirm">
                <svg v-if="!showPasswordConfirm" width="18" height="18" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" stroke-width="2">
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
            <span v-if="errors.passwordConfirm" class="error-msg">{{ errors.passwordConfirm }}</span>
          </div>

          <p v-if="serverError" class="server-error">{{ serverError }}</p>

          <button type="submit" class="btn-submit" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            <span v-else>회원가입하고 이메일 인증하기 →</span>
          </button>
        </form>

        <p class="auth-switch">
          이미 계정이 있으신가요?
          <RouterLink to="/login" class="switch-link">로그인으로 이동</RouterLink>
        </p>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const form = reactive({
  email: '',
  username: '',
  password: '',
  passwordConfirm: '',
})

const errors = reactive({
  email: '',
  username: '',
  password: '',
  passwordConfirm: '',
})

const showPassword = ref(false)
const showPasswordConfirm = ref(false)
const loading = ref(false)
const serverError = ref('')
const verificationSent = ref(false)
const registeredEmail = ref('')
const resendLoading = ref(false)
const resendMessage = ref('')
const resendError = ref('')

function validate() {
  let valid = true
  errors.email = ''
  errors.username = ''
  errors.password = ''
  errors.passwordConfirm = ''

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

  if (!form.passwordConfirm) {
    errors.passwordConfirm = '비밀번호 확인을 입력해주세요'
    valid = false
  } else if (form.password !== form.passwordConfirm) {
    errors.passwordConfirm = '비밀번호가 일치하지 않습니다'
    valid = false
  }

  return valid
}

async function handleRegister() {
  if (!validate()) return
  loading.value = true
  serverError.value = ''
  try {
    await authStore.register(form.email, form.username, form.password)
    registeredEmail.value = form.email
    verificationSent.value = true
  } catch (err) {
    serverError.value = err.response?.data?.detail || '회원가입에 실패했습니다. 다시 시도해주세요.'
  } finally {
    loading.value = false
  }
}

async function handleResendVerification() {
  resendLoading.value = true
  resendMessage.value = ''
  resendError.value = ''
  try {
    const { message } = await authStore.resendVerification(registeredEmail.value)
    resendMessage.value = message || '인증 메일을 다시 발송했습니다'
  } catch (err) {
    resendError.value = err.response?.data?.detail || '인증 메일 재발송에 실패했습니다'
  } finally {
    resendLoading.value = false
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

.error-msg {
  font-size: 12px;
  color: #ef4444;
}

.server-error {
  font-size: 13px;
  color: #ef4444;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 10px 14px;
  text-align: center;
}

.success-msg {
  font-size: 13px;
  color: #166534;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  padding: 10px 14px;
  text-align: center;
}

.verification-panel {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 16px;
}

.verification-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #166534;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 22px;
}

.verification-panel h2 {
  color: #1a1209;
  font-size: 23px;
  line-height: 1.35;
  margin: 0;
}

.verification-panel p {
  color: #6b4f38;
  font-size: 14px;
  line-height: 1.7;
  margin: 0;
}

.secondary-link {
  color: #a0785a;
  font-weight: 700;
  text-align: center;
  text-decoration: underline;
  text-underline-offset: 2px;
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
