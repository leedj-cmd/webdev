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

        <p class="side-headline">IT 취준생을 위한<br>올인원 커리어 플랫폼</p>

        <div class="side-divider"></div>

        <p class="side-for-label">이런 분들을 위한 곳이에요</p>
        <div class="persona-list">
          <div class="persona-item">
            <div class="persona-icon-wrap">👨‍💻</div>
            <div>
              <p class="persona-title">IT 전공 재학생</p>
              <p class="persona-desc">관심 기술 스택 맞춤 공고와 공모전을 한눈에</p>
            </div>
          </div>
          <div class="persona-item">
            <div class="persona-icon-wrap">🎯</div>
            <div>
              <p class="persona-title">취업 준비 중인 졸업생</p>
              <p class="persona-desc">마감 임박 공고와 실무 후기를 빠르게 파악</p>
            </div>
          </div>
          <div class="persona-item">
            <div class="persona-icon-wrap">🔁</div>
            <div>
              <p class="persona-title">이직을 고민하는 개발자</p>
              <p class="persona-desc">커뮤니티에서 현직자 경험과 정보를 교류</p>
            </div>
          </div>
        </div>

        <div class="side-divider"></div>

        <div class="side-quote">
          <span class="quote-mark">"</span>
          <p class="quote-text">지원 준비 흐름을 끊지 않도록,<br>바로 이어서 시작하세요.</p>
        </div>
      </div>

      <!-- ── 오른쪽: 로그인 폼 ── -->
      <div class="auth-card">
        <span class="login-badge">LOGIN</span>
        <h1 class="auth-title">로그인</h1>
        <p v-if="verifiedMessage" class="success-msg">{{ verifiedMessage }}</p>

        <form @submit.prevent="handleLogin" class="auth-form">
          <div class="form-group">
            <label for="email">이메일</label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              placeholder="example@email.com"
              :class="{ error: errors.email }"
              autocomplete="email"
            />
            <span v-if="errors.email" class="error-msg">{{ errors.email }}</span>
          </div>

          <div class="form-group">
            <div class="label-row">
              <label for="password">비밀번호</label>
              <button type="button" class="find-inline-btn" @click="openModal('findPassword')">비밀번호 찾기</button>
            </div>
            <div class="input-wrapper">
              <input
                id="password"
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="비밀번호를 입력하세요"
                :class="{ error: errors.password }"
                autocomplete="current-password"
              />
              <button type="button" class="toggle-pw" @click="showPassword = !showPassword">
                <svg v-if="!showPassword" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" /><circle cx="12" cy="12" r="3" />
                </svg>
                <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24" /><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68" /><path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61" /><line x1="2" x2="22" y1="2" y2="22" />
                </svg>
              </button>
            </div>
            <span v-if="errors.password" class="error-msg">{{ errors.password }}</span>
          </div>

          <p v-if="serverError" class="server-error">{{ serverError }}</p>

          <button type="submit" class="btn-submit" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            <span v-else>로그인하고 보드 이어보기 →</span>
          </button>
        </form>

        <div class="bottom-links">
          <button class="find-btn" @click="openModal('findId')">아이디 찾기</button>
          <span class="dot">·</span>
          <button class="find-btn" @click="openModal('resetWithCurrentPassword')">비밀번호 재설정</button>
          <span class="dot">·</span>
          <RouterLink to="/admin/register" class="find-btn">관리자 회원가입</RouterLink>
        </div>

        <p class="auth-switch">
          계정이 아직 없으신가요?
          <RouterLink to="/register" class="switch-link">회원가입으로 이동</RouterLink>
        </p>
      </div>

    </div>

    <!-- ── 모달 ── -->
    <Teleport to="body">
      <div v-if="modal" class="modal-backdrop" @click.self="closeModal">
        <div class="modal">
          <template v-if="modal === 'findId'">
            <div class="modal-header">
              <h2>아이디(이메일) 찾기</h2>
              <button class="modal-close" @click="closeModal">✕</button>
            </div>
            <p class="modal-desc">가입 시 사용한 닉네임을 입력하면 이메일을 알려드려요.</p>
            <div class="form-group">
              <label>닉네임</label>
              <input v-model="findIdForm.username" type="text" placeholder="닉네임을 입력하세요" @keyup.enter="handleFindId" />
            </div>
            <p v-if="findIdResult" class="result-box">{{ findIdResult }}</p>
            <p v-if="findIdError" class="error-msg">{{ findIdError }}</p>
            <button class="btn-submit" :disabled="findIdLoading" @click="handleFindId">
              <span v-if="findIdLoading" class="spinner"></span>
              <span v-else>찾기</span>
            </button>
          </template>

          <template v-else-if="modal === 'findPassword'">
            <div class="modal-header">
              <h2>비밀번호 찾기</h2>
              <button class="modal-close" @click="closeModal">✕</button>
            </div>
            <p class="modal-desc">비밀번호를 잊으셨나요? 가입한 이메일로 본인 확인 링크를 보내드립니다.</p>
            <div class="form-group">
              <label>이메일</label>
              <input v-model="resetForm.email" type="email" placeholder="example@email.com" @keyup.enter="handleFindPassword" />
            </div>
            <p v-if="findPwMessage" class="success-msg">{{ findPwMessage }}</p>
            <p v-if="findPwError" class="error-msg">{{ findPwError }}</p>
            <button class="btn-submit" :disabled="findPwLoading" @click="handleFindPassword">
              <span v-if="findPwLoading" class="spinner"></span>
              <span v-else>확인 메일 받기</span>
            </button>
          </template>

          <template v-else-if="modal === 'resetWithCurrentPassword'">
            <div class="modal-header">
              <h2>비밀번호 재설정</h2>
              <button class="modal-close" @click="closeModal">✕</button>
            </div>
            <p class="modal-desc">현재 비밀번호를 알고 있다면 이메일과 현재 비밀번호 확인 후 새 비밀번호로 변경할 수 있습니다.</p>
            <div class="form-group">
              <label>이메일</label>
              <input v-model="currentResetForm.email" type="email" placeholder="example@email.com" autocomplete="email" />
            </div>
            <div class="form-group">
              <label>현재 비밀번호</label>
              <input v-model="currentResetForm.currentPassword" type="password" placeholder="현재 비밀번호를 입력하세요" autocomplete="current-password" />
            </div>
            <div class="form-group">
              <label>새 비밀번호</label>
              <input v-model="currentResetForm.newPassword" type="password" placeholder="8자 이상 입력하세요" autocomplete="new-password" />
            </div>
            <div class="form-group">
              <label>새 비밀번호 확인</label>
              <input v-model="currentResetForm.confirmPassword" type="password" placeholder="비밀번호를 다시 입력하세요" autocomplete="new-password" @keyup.enter="handleResetWithCurrentPassword" />
            </div>
            <p v-if="currentResetError" class="error-msg">{{ currentResetError }}</p>
            <button class="btn-submit" :disabled="currentResetLoading" @click="handleResetWithCurrentPassword">
              <span v-if="currentResetLoading" class="spinner"></span>
              <span v-else>비밀번호 변경</span>
            </button>
          </template>

          <template v-else-if="modal === 'done'">
            <div class="done-wrap">
              <div class="done-icon">✓</div>
              <h2>{{ doneMessage }}</h2>
              <button class="btn-submit" @click="closeModal">확인</button>
            </div>
          </template>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, ref, reactive } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/axios'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const verifiedMessage = computed(() => (
  route.query.verified === '1' ? '이메일 인증이 완료되었습니다. 로그인해주세요.' : ''
))

const form = reactive({ email: '', password: '' })
const errors = reactive({ email: '', password: '' })
const showPassword = ref(false)
const loading = ref(false)
const serverError = ref('')

function validate() {
  let valid = true
  errors.email = ''
  errors.password = ''
  if (!form.email) { errors.email = '이메일을 입력해주세요'; valid = false }
  if (!form.password) { errors.password = '비밀번호를 입력해주세요'; valid = false }
  return valid
}

async function handleLogin() {
  if (!validate()) return
  loading.value = true
  serverError.value = ''
  try {
    await authStore.login(form.email, form.password)
    router.push('/')
  } catch (err) {
    serverError.value = err.response?.data?.detail || '로그인에 실패했습니다. 다시 시도해주세요.'
  } finally {
    loading.value = false
  }
}

const modal = ref(null)
const doneMessage = ref('')

function openModal(type) {
  modal.value = type
  findIdForm.username = ''
  findIdResult.value = ''
  findIdError.value = ''
  resetForm.email = ''
  findPwError.value = ''
  findPwMessage.value = ''
  currentResetForm.email = form.email
  currentResetForm.currentPassword = ''
  currentResetForm.newPassword = ''
  currentResetForm.confirmPassword = ''
  currentResetError.value = ''
}

function closeModal() { modal.value = null }

const findIdForm = reactive({ username: '' })
const findIdResult = ref('')
const findIdError = ref('')
const findIdLoading = ref(false)

async function handleFindId() {
  if (!findIdForm.username) { findIdError.value = '닉네임을 입력해주세요'; return }
  findIdLoading.value = true
  findIdError.value = ''
  findIdResult.value = ''
  try {
    const { data } = await api.post('/auth/find-id', { username: findIdForm.username })
    findIdResult.value = `가입하신 이메일은 ${data.email} 입니다`
  } catch (err) {
    findIdError.value = err.response?.data?.detail || '해당 닉네임을 찾을 수 없습니다'
  } finally {
    findIdLoading.value = false
  }
}

const resetForm = reactive({ email: '' })
const findPwMessage = ref('')
const findPwError = ref('')
const findPwLoading = ref(false)
const currentResetForm = reactive({
  email: '',
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
})
const currentResetError = ref('')
const currentResetLoading = ref(false)

async function handleFindPassword() {
  if (!resetForm.email) { findPwError.value = '이메일을 입력해주세요'; return }
  findPwLoading.value = true
  findPwError.value = ''
  findPwMessage.value = ''
  try {
    const { data } = await api.post('/auth/find-password', { email: resetForm.email })
    findPwMessage.value = data.message || '가입한 이메일이라면 비밀번호 찾기 안내를 발송했습니다'
  } catch (err) {
    findPwError.value = err.response?.data?.detail || '비밀번호 찾기 메일 발송에 실패했습니다'
  } finally {
    findPwLoading.value = false
  }
}

async function handleResetWithCurrentPassword() {
  currentResetError.value = ''
  if (!currentResetForm.email) {
    currentResetError.value = '이메일을 입력해주세요'
    return
  }
  if (!currentResetForm.currentPassword) {
    currentResetError.value = '현재 비밀번호를 입력해주세요'
    return
  }
  if (!currentResetForm.newPassword || currentResetForm.newPassword.length < 8) {
    currentResetError.value = '새 비밀번호는 8자 이상이어야 합니다'
    return
  }
  if (currentResetForm.newPassword !== currentResetForm.confirmPassword) {
    currentResetError.value = '새 비밀번호가 일치하지 않습니다'
    return
  }

  currentResetLoading.value = true
  try {
    await api.patch('/auth/reset-password/current', {
      email: currentResetForm.email,
      current_password: currentResetForm.currentPassword,
      new_password: currentResetForm.newPassword,
    })
    doneMessage.value = '비밀번호가 성공적으로 변경되었습니다'
    modal.value = 'done'
  } catch (err) {
    currentResetError.value = err.response?.data?.detail || '비밀번호 변경에 실패했습니다'
  } finally {
    currentResetLoading.value = false
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
  width: 500px; height: 500px;
  background: #d4b89a;
  top: -120px; left: -120px;
}

.bg-blob--2 {
  width: 400px; height: 400px;
  background: #c9a882;
  bottom: -100px; right: -80px;
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

/* ── 왼쪽 카드 ── */
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
  margin-bottom: 32px;
}

.brand-logo { text-decoration: none; display: flex; }

.brand-icon {
  width: 44px; height: 44px;
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

.brand-info { display: flex; flex-direction: column; }

.brand-name { font-size: 14px; font-weight: 700; color: #1a1209; line-height: 1.2; }
.brand-sub { font-size: 11px; color: #9a8070; }

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
  font-size: 22px;
  font-weight: 800;
  color: #1a1209;
  line-height: 1.4;
  margin: 0 0 12px;
  letter-spacing: -0.3px;
}


.side-divider {
  height: 1px;
  background: #ede5dc;
  margin: 24px 0;
}

.side-for-label {
  font-size: 12px;
  font-weight: 700;
  color: #7a5c42;
  margin: 0 0 16px;
  letter-spacing: 0.04em;
}

.persona-list { display: flex; flex-direction: column; gap: 16px; }

.persona-item { display: flex; align-items: flex-start; gap: 12px; }

.persona-icon-wrap {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #faf6f2 0%, #f0e6d8 100%);
  border: 1.5px solid #e8ddd4;
  border-radius: 10px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.persona-title {
  font-size: 13.5px;
  font-weight: 700;
  color: #2a1e15;
  margin: 0 0 2px;
}

.persona-desc { font-size: 12px; color: #9a8070; line-height: 1.5; margin: 0; }

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

/* ── 오른쪽 로그인 카드 ── */
.auth-card {
  flex: 1;
  background: #ffffff;
  border-radius: 24px;
  padding: 40px 44px 44px;
  box-shadow: 0 8px 48px rgba(100, 70, 40, 0.12);
  display: flex;
  flex-direction: column;
}

.login-badge {
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
  margin: 0 0 15px;
  letter-spacing: -0.5px;
}

.auth-form { display: flex; flex-direction: column; gap: 20px; }

.form-group { display: flex; flex-direction: column; gap: 7px; }

.label-row { display: flex; align-items: center; justify-content: space-between; }

.form-group label,
.label-row label {
  font-size: 14px;
  font-weight: 600;
  color: #6b4f38;
}

.find-inline-btn {
  background: none;
  border: none;
  font-size: 12px;
  color: #9a8070;
  cursor: pointer;
  padding: 0;
  transition: color 0.15s;
}

.find-inline-btn:hover { color: #a0785a; }

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
}

.form-group input::placeholder { color: #b5a49a; }

.form-group input:focus {
  border-color: #a0785a;
  box-shadow: 0 0 0 3px rgba(160, 120, 90, 0.12);
  background: #fff;
}

.form-group input.error { border-color: #ef4444; }

.input-wrapper { position: relative; }
.input-wrapper input { padding-right: 44px; }

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

.toggle-pw:hover { color: #a0785a; }

.error-msg { font-size: 12px; color: #ef4444; }

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
  margin: 0 0 16px;
}

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

.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }

.spinner {
  width: 20px; height: 20px;
  border: 2.5px solid rgba(255, 255, 255, 0.4);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.bottom-links {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 20px;
}

.find-btn {
  background: none;
  border: none;
  font-size: 12.5px;
  color: #9a8070;
  cursor: pointer;
  padding: 0;
  transition: color 0.15s;
  text-decoration: none;
}

.find-btn:hover { color: #a0785a; }

.dot { color: #c9bab0; font-size: 12px; }

.auth-switch {
  text-align: center;
  margin-top: 14px;
  font-size: 13.5px;
  color: #9a8070;
}

.switch-link {
  color: #a0785a;
  font-weight: 700;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.switch-link:hover { opacity: 0.75; }

/* ── 모달 ── */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(30, 20, 10, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}

.modal {
  background: #ffffff;
  border-radius: 20px;
  padding: 32px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(60, 40, 20, 0.15);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.modal-header { display: flex; align-items: center; justify-content: space-between; }
.modal-header h2 { font-size: 18px; font-weight: 700; color: #1a1209; }

.modal-close {
  background: none;
  border: none;
  font-size: 16px;
  color: #9a8070;
  cursor: pointer;
  padding: 4px;
  line-height: 1;
  transition: color 0.15s;
}

.modal-close:hover { color: #a0785a; }

.modal-desc { font-size: 14px; color: #7a6a5a; line-height: 1.5; }

.result-box {
  font-size: 14px;
  color: #059669;
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  border-radius: 8px;
  padding: 10px 14px;
  text-align: center;
}

.done-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 8px 0;
}

.done-icon {
  width: 56px; height: 56px;
  border-radius: 50%;
  background: #ecfdf5;
  color: #059669;
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.done-wrap h2 { font-size: 16px; font-weight: 600; color: #1a1209; text-align: center; }
</style>
