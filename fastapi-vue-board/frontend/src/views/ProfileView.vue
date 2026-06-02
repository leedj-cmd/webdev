<template>
  <main class="profile-page">
    <section class="profile-hero page-shell">
      <div class="section-head">
        <div>
          <span class="eyebrow">My Dashboard</span>
          <h1 class="page-title">내 프로필</h1>
        </div>
        <p>메인 보드와 동일한 무드로 프로필 정보와 보안 설정을 한 화면에서 관리할 수 있습니다.</p>
      </div>

      <div class="profile-layout">
        <aside class="double-shell profile-card">
          <div class="double-core card-core">
            <div class="avatar-section">
              <div class="avatar-wrapper">
                <img v-if="avatarPreview || user?.profile_image"
                  :src="avatarPreview || `http://localhost:8000/${user.profile_image}`" alt="프로필 사진"
                  class="avatar-img" />
                <div v-else class="avatar-placeholder">
                  {{ user?.username?.[0] ?? '유' }}
                </div>
                <label class="avatar-edit-btn" title="사진 변경">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
                    <circle cx="12" cy="13" r="4" />
                  </svg>
                  <input type="file" accept="image/*" class="hidden-input" @change="onFileChange" />
                </label>
              </div>

              <div v-if="avatarFile" class="avatar-actions">
                <button class="btn-sm-primary" :disabled="avatarUploading" @click="uploadAvatar">
                  <span v-if="avatarUploading" class="spinner-sm"></span>
                  <span v-else>저장</span>
                </button>
                <button class="btn-sm-ghost" @click="cancelAvatar">취소</button>
              </div>
            </div>

            <div class="profile-info">
              <p class="profile-username">{{ user?.username }}</p>
              <p class="profile-email">{{ user?.email }}</p>
              <p v-if="user?.bio" class="profile-bio">{{ user?.bio }}</p>
              <p v-else class="profile-bio empty">소개가 없어요</p>
              <span class="profile-role" :class="user?.role">{{ user?.role === 'admin' ? '관리자' : '일반 회원' }}</span>
            </div>
          </div>
        </aside>

        <div class="settings-col">
          <section class="double-shell settings-section">
            <div class="double-core section-core">
              <h2 class="section-title">기본 정보</h2>
              <form @submit.prevent="handleUpdateProfile" class="settings-form">
                <div class="form-group">
                  <label>닉네임</label>
                  <input v-model="profileForm.username" type="text" placeholder="닉네임을 입력하세요"
                    :class="{ error: profileErrors.username }" />
                  <span v-if="profileErrors.username" class="error-msg">{{ profileErrors.username }}</span>
                </div>
                <div class="form-group">
                  <label>소개</label>
                  <textarea v-model="profileForm.bio" placeholder="간단한 소개를 작성해보세요 (최대 200자)" maxlength="200"
                    rows="3"></textarea>
                  <span class="char-count">{{ profileForm.bio?.length ?? 0 }} / 200</span>
                </div>
                <p v-if="profileSuccess" class="success-msg">{{ profileSuccess }}</p>
                <p v-if="profileError" class="error-msg">{{ profileError }}</p>
                <button type="submit" class="btn-save" :disabled="profileLoading">
                  <span v-if="profileLoading" class="spinner-sm"></span>
                  <span v-else>저장하기</span>
                </button>
              </form>
            </div>
          </section>

          <section class="double-shell settings-section">
            <div class="double-core section-core">
              <h2 class="section-title">비밀번호 변경</h2>
              <form @submit.prevent="handleChangePassword" class="settings-form">
                <div class="form-group">
                  <label>현재 비밀번호</label>
                  <div class="input-wrapper">
                    <input v-model="pwForm.current" :type="showPw.current ? 'text' : 'password'"
                      placeholder="현재 비밀번호를 입력하세요" :class="{ error: pwErrors.current }"
                      autocomplete="current-password" />
                    <button type="button" class="toggle-pw" @click="showPw.current = !showPw.current">
                      <EyeIcon :open="showPw.current" />
                    </button>
                  </div>
                  <span v-if="pwErrors.current" class="error-msg">{{ pwErrors.current }}</span>
                </div>
                <div class="form-group">
                  <label>새 비밀번호</label>
                  <div class="input-wrapper">
                    <input v-model="pwForm.newPw" :type="showPw.newPw ? 'text' : 'password'" placeholder="8자 이상 입력하세요"
                      :class="{ error: pwErrors.newPw }" autocomplete="new-password" />
                    <button type="button" class="toggle-pw" @click="showPw.newPw = !showPw.newPw">
                      <EyeIcon :open="showPw.newPw" />
                    </button>
                  </div>
                  <span v-if="pwErrors.newPw" class="error-msg">{{ pwErrors.newPw }}</span>
                </div>
                <div class="form-group">
                  <label>새 비밀번호 확인</label>
                  <div class="input-wrapper">
                    <input v-model="pwForm.confirm" :type="showPw.confirm ? 'text' : 'password'"
                      placeholder="새 비밀번호를 다시 입력하세요" :class="{ error: pwErrors.confirm }" autocomplete="new-password" />
                    <button type="button" class="toggle-pw" @click="showPw.confirm = !showPw.confirm">
                      <EyeIcon :open="showPw.confirm" />
                    </button>
                  </div>
                  <span v-if="pwErrors.confirm" class="error-msg">{{ pwErrors.confirm }}</span>
                </div>
                <p v-if="pwSuccess" class="success-msg">{{ pwSuccess }}</p>
                <p v-if="pwError" class="error-msg">{{ pwError }}</p>
                <button type="submit" class="btn-save" :disabled="pwLoading">
                  <span v-if="pwLoading" class="spinner-sm"></span>
                  <span v-else>비밀번호 변경</span>
                </button>
              </form>
            </div>
          </section>

          <section v-if="user?.role !== 'admin'" class="double-shell settings-section promote-section">
            <div class="double-core section-core">
              <h2 class="section-title">관리자 승격</h2>
              <p class="promote-desc">관리자 코드를 입력하면 현재 계정을 관리자로 승격할 수 있습니다.</p>
              <form @submit.prevent="handlePromote" class="settings-form">
                <div class="form-group">
                  <label>관리자 코드</label>
                  <div class="input-wrapper">
                    <input
                      v-model="promoteSecret"
                      :type="showPromoteSecret ? 'text' : 'password'"
                      placeholder="관리자 코드를 입력하세요"
                      :class="{ error: promoteError }"
                    />
                    <button type="button" class="toggle-pw" @click="showPromoteSecret = !showPromoteSecret">
                      <EyeIcon :open="showPromoteSecret" />
                    </button>
                  </div>
                  <p class="field-hint">⚠️ .env 파일의 ADMIN_SECRET 값을 입력하세요.</p>
                </div>
                <p v-if="promoteError" class="error-msg">{{ promoteError }}</p>
                <p v-if="promoteSuccess" class="success-msg">{{ promoteSuccess }}</p>
                <button type="submit" class="btn-save btn-promote" :disabled="promoteLoading">
                  <span v-if="promoteLoading" class="spinner-sm"></span>
                  <span v-else>관리자로 승격하기</span>
                </button>
              </form>
            </div>
          </section>

          <section class="double-shell settings-section">
            <div class="double-core section-core">
              <div class="scrap-head">
                <h2 class="section-title no-border">내 스크랩</h2>
                <button class="btn-sm-ghost" type="button" :disabled="scrapsLoading" @click="fetchMyScraps">
                  새로고침
                </button>
              </div>

              <p v-if="scrapsError" class="error-msg">{{ scrapsError }}</p>
              <div v-if="scrapsLoading" class="scrap-status">스크랩한 항목을 불러오는 중입니다.</div>
              <div v-else-if="myScraps.length === 0" class="scrap-status">아직 스크랩한 채용 공고나 공모전이 없습니다.</div>
              <div v-else class="scrap-list">
                <article v-for="scrap in myScraps" :key="scrap.id" class="scrap-item">
                  <div class="scrap-main">
                    <span class="scrap-type">{{ scrap.scrap_type === 'job' ? '채용 공고' : '공모전' }}</span>
                    <h3>{{ scrapTitle(scrap) }}</h3>
                    <p>{{ scrapMeta(scrap) }}</p>
                    <span class="scrap-date">스크랩 {{ formatScrapDate(scrap.created_at) }}</span>
                  </div>
                  <div class="scrap-actions">
                    <a v-if="scrapUrl(scrap)" class="scrap-link" :href="scrapUrl(scrap)" target="_blank"
                      rel="noopener noreferrer">
                      상세보기
                    </a>
                    <button class="scrap-remove" type="button" @click="removeScrap(scrap.id)">삭제</button>
                  </div>
                </article>
              </div>
            </div>
          </section>

          <section class="double-shell settings-section">
            <div class="double-core section-core">
              <div class="scrap-head">
                <h2 class="section-title no-border">내 게시글</h2>
                <button class="btn-sm-ghost" type="button" :disabled="postsLoading" @click="fetchMyPosts">
                  새로고침
                </button>
              </div>

              <p v-if="postsError" class="error-msg">{{ postsError }}</p>
              <div v-if="postsLoading" class="scrap-status">작성한 게시글을 불러오는 중입니다.</div>
              <div v-else-if="myPosts.length === 0" class="scrap-status">아직 작성한 게시글이 없습니다.</div>
              <div v-else class="scrap-list">
                <article v-for="post in myPosts" :key="post.id" class="scrap-item">
                  <div class="scrap-main">
                    <span class="scrap-type post-badge">게시글</span>
                    <h3>{{ post.title }}</h3>
                    <p>{{ postMeta(post) }}</p>
                    <span class="scrap-date">{{ formatScrapDate(post.created_at) }}</span>
                  </div>
                  <div class="scrap-actions">
                    <router-link :to="`/posts/${post.id}`" class="scrap-link">
                      보러가기
                    </router-link>
                  </div>
                </article>
              </div>
            </div>
          </section>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/axios'

const router = useRouter()
const authStore = useAuthStore()
const user = computed(() => authStore.user)

// 로그인 안 된 경우 리다이렉트
onMounted(() => {
  if (!authStore.isLoggedIn) { router.push('/login'); return }
  profileForm.username = user.value?.username ?? ''
  profileForm.bio = user.value?.bio ?? ''
  fetchMyScraps()
  fetchMyPosts()
  window.addEventListener('focus', fetchMyScraps)
  window.addEventListener('scraps-updated', fetchMyScraps)
})

onBeforeUnmount(() => {
  window.removeEventListener('focus', fetchMyScraps)
  window.removeEventListener('scraps-updated', fetchMyScraps)
})

// ── 아바타
const avatarFile = ref(null)
const avatarPreview = ref(null)
const avatarUploading = ref(false)

function onFileChange(e) {
  const file = e.target.files[0]
  if (!file) return
  avatarFile.value = file
  avatarPreview.value = URL.createObjectURL(file)
}

function cancelAvatar() {
  avatarFile.value = null
  avatarPreview.value = null
}

async function uploadAvatar() {
  if (!avatarFile.value) return
  avatarUploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', avatarFile.value)
    const token = authStore.token
    const { data } = await api.post(`/auth/profile/image?token=${token}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    authStore.user = data
    avatarFile.value = null
    avatarPreview.value = null
  } catch (err) {
    alert(err.response?.data?.detail || '이미지 업로드에 실패했습니다')
  } finally {
    avatarUploading.value = false
  }
}

// ── 기본 정보 수정
const profileForm = reactive({ username: '', bio: '' })
const profileErrors = reactive({ username: '' })
const profileLoading = ref(false)
const profileSuccess = ref('')
const profileError = ref('')

async function handleUpdateProfile() {
  profileErrors.username = ''
  profileSuccess.value = ''
  profileError.value = ''

  if (!profileForm.username.trim()) {
    profileErrors.username = '닉네임을 입력해주세요'
    return
  }
  if (profileForm.username.length < 2) {
    profileErrors.username = '닉네임은 2자 이상이어야 합니다'
    return
  }

  profileLoading.value = true
  try {
    const token = authStore.token
    const { data } = await api.patch(`/auth/profile?token=${token}`, {
      username: profileForm.username,
      bio: profileForm.bio,
    })
    authStore.user = data
    profileSuccess.value = '프로필이 저장되었습니다'
  } catch (err) {
    profileError.value = err.response?.data?.detail || '저장에 실패했습니다'
  } finally {
    profileLoading.value = false
  }
}

// ── 비밀번호 변경
const pwForm = reactive({ current: '', newPw: '', confirm: '' })
const pwErrors = reactive({ current: '', newPw: '', confirm: '' })
const showPw = reactive({ current: false, newPw: false, confirm: false })
const pwLoading = ref(false)
const pwSuccess = ref('')
const pwError = ref('')

async function handleChangePassword() {
  pwErrors.current = ''
  pwErrors.newPw = ''
  pwErrors.confirm = ''
  pwSuccess.value = ''
  pwError.value = ''

  let valid = true
  if (!pwForm.current) { pwErrors.current = '현재 비밀번호를 입력해주세요'; valid = false }
  if (!pwForm.newPw || pwForm.newPw.length < 8) { pwErrors.newPw = '새 비밀번호는 8자 이상이어야 합니다'; valid = false }
  if (pwForm.newPw !== pwForm.confirm) { pwErrors.confirm = '비밀번호가 일치하지 않습니다'; valid = false }
  if (!valid) return

  pwLoading.value = true
  try {
    const token = authStore.token
    await api.patch(`/auth/change-password?token=${token}`, {
      current_password: pwForm.current,
      new_password: pwForm.newPw,
    })
    pwSuccess.value = '비밀번호가 성공적으로 변경되었습니다'
    pwForm.current = ''
    pwForm.newPw = ''
    pwForm.confirm = ''
  } catch (err) {
    pwError.value = err.response?.data?.detail || '비밀번호 변경에 실패했습니다'
  } finally {
    pwLoading.value = false
  }
}

// ── 관리자 승격
const promoteSecret = ref('')
const showPromoteSecret = ref(false)
const promoteLoading = ref(false)
const promoteSuccess = ref('')
const promoteError = ref('')

async function handlePromote() {
  promoteSuccess.value = ''
  promoteError.value = ''
  if (!promoteSecret.value) {
    promoteError.value = '관리자 코드를 입력해주세요'
    return
  }
  promoteLoading.value = true
  try {
    await authStore.promoteToAdmin(user.value.email, promoteSecret.value)
    await authStore.fetchMe()
    promoteSuccess.value = '관리자로 승격되었습니다!'
    promoteSecret.value = ''
  } catch (e) {
    promoteError.value = e.response?.data?.detail || '승격에 실패했습니다. 관리자 코드를 확인해주세요.'
  } finally {
    promoteLoading.value = false
  }
}

// ── 스크랩 목록
const myScraps = ref([])
const scrapsLoading = ref(false)
const scrapsError = ref('')

async function fetchMyScraps() {
  scrapsLoading.value = true
  scrapsError.value = ''
  try {
    const { data } = await api.get('/scraps/')
    myScraps.value = Array.isArray(data) ? data.filter((scrap) => scrap.job || scrap.contest || scrap.title) : []
  } catch (err) {
    scrapsError.value = err.response?.data?.detail || '스크랩 목록을 불러오지 못했습니다'
    myScraps.value = []
  } finally {
    scrapsLoading.value = false
  }
}

async function removeScrap(scrapId) {
  try {
    await api.delete(`/scraps/${scrapId}`)
    myScraps.value = myScraps.value.filter((scrap) => scrap.id !== scrapId)
  } catch (err) {
    scrapsError.value = err.response?.data?.detail || '스크랩 삭제에 실패했습니다'
  }
}

function scrapTitle(scrap) {
  return scrap.job?.title || scrap.contest?.title || scrap.title || '제목 없음'
}

function scrapMeta(scrap) {
  if (scrap.job) {
    return [scrap.job.company, scrap.job.region, scrap.job.experience].filter(Boolean).join(' · ') || '채용 정보'
  }
  if (scrap.contest) {
    return [scrap.contest.organizer, scrap.contest.category, scrap.contest.target].filter(Boolean).join(' · ') || '공모전 정보'
  }
  return scrap.subtitle || (scrap.scrap_type === 'job' ? '채용 정보' : '공모전 정보')
}

function scrapUrl(scrap) {
  return scrap.job?.external_url || scrap.contest?.external_url || scrap.external_url || ''
}

function formatScrapDate(value) {
  if (!value) return ''
  return new Date(value).toLocaleDateString('ko-KR', { year: 'numeric', month: 'short', day: 'numeric' })
}

// ── 내 게시글
const myPosts = ref([])
const postsLoading = ref(false)
const postsError = ref('')

async function fetchMyPosts() {
  postsLoading.value = true
  postsError.value = ''
  try {
    const { data } = await api.get('/auth/activity')
    myPosts.value = Array.isArray(data?.posts) ? data.posts : []
  } catch (err) {
    postsError.value = err.response?.data?.detail || '게시글 목록을 불러오지 못했습니다'
    myPosts.value = []
  } finally {
    postsLoading.value = false
  }
}

function postMeta(post) {
  const parts = []
  if (post.job_category) parts.push(post.job_category)
  if (post.region) parts.push(post.region)
  if (post.view_count != null) parts.push(`조회 ${post.view_count}`)
  return parts.join(' · ') || '게시글'
}
</script>

<!-- EyeIcon 인라인 컴포넌트 -->
<script>
const EyeIcon = {
  props: ['open'],
  template: `
    <svg v-if="!open" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>
    </svg>
    <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/><line x1="2" x2="22" y1="2" y2="22"/>
    </svg>
  `
}
export default { components: { EyeIcon } }
</script>

<style scoped>
.profile-page {
  padding: 8.5rem 0 6rem;
}

.page-shell {
  width: min(1200px, calc(100% - 32px));
  margin: 0 auto;
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 0.9rem;
  border-radius: 999px;
  background: rgba(196, 142, 102, 0.12);
  border: 1px solid rgba(196, 142, 102, 0.18);
  color: var(--color-accent);
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.section-head {
  display: grid;
  grid-template-columns: minmax(0, 0.9fr) minmax(0, 1fr);
  gap: 1.5rem;
  align-items: end;
  margin-bottom: 1.5rem;
}

.page-title,
.section-title {
  text-wrap: balance;
  word-break: keep-all;
}

.page-title {
  margin-top: 1rem;
  font-family: var(--font-display);
  font-size: clamp(2.2rem, 5vw, 3.8rem);
  line-height: 1.02;
  letter-spacing: -0.05em;
  color: var(--color-ink);
}

.section-head p,
.profile-bio,
.profile-email,
.char-count {
  color: var(--color-muted);
}

.section-head p {
  max-width: 36rem;
  line-height: 1.7;
}

.profile-layout {
  display: grid;
  grid-template-columns: minmax(260px, 0.36fr) minmax(0, 0.64fr);
  gap: 1rem;
  align-items: start;
}

.double-shell {
  padding: 1px;
  border-radius: 2rem;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.78), rgba(255, 255, 255, 0.32)),
    rgba(17, 24, 39, 0.05);
  box-shadow:
    0 30px 80px -42px rgba(43, 31, 18, 0.26),
    inset 0 1px 0 rgba(255, 255, 255, 0.68);
}

.double-core {
  border-radius: calc(2rem - 1px);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(253, 249, 243, 0.86));
  box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.55);
}

.profile-card {
  position: sticky;
  top: 88px;
}

.card-core {
  padding: 1.4rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.avatar-wrapper {
  position: relative;
  width: 96px;
  height: 96px;
}

.avatar-img {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid rgba(88, 70, 53, 0.12);
}

.avatar-placeholder {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f2e7da, #f7f4ed);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  font-weight: 700;
  color: #5d4a38;
  border: 3px solid rgba(88, 70, 53, 0.12);
}

.avatar-edit-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2f2722, #7e5a41);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: 2px solid #fff;
  transition: transform 0.25s ease;
}

.avatar-edit-btn:hover {
  transform: translateY(-1px);
}

.hidden-input {
  display: none;
}

.avatar-actions {
  display: flex;
  gap: 8px;
}

.btn-sm-primary {
  padding: 6px 14px;
  background: linear-gradient(135deg, #2f2722, #7e5a41);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: transform 0.25s ease;
}

.btn-sm-primary:hover:not(:disabled) {
  transform: translateY(-1px);
}

.btn-sm-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-sm-ghost {
  padding: 6px 14px;
  background: transparent;
  color: #6b7280;
  border: 1.5px solid rgba(88, 70, 53, 0.16);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s ease;
}

.btn-sm-ghost:hover {
  border-color: rgba(126, 90, 65, 0.36);
  color: var(--color-ink);
}

.profile-info {
  text-align: center;
  width: 100%;
}

.profile-username {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--color-ink);
  margin-bottom: 4px;
}

.profile-email {
  font-size: 0.82rem;
  margin-bottom: 10px;
}

.profile-bio {
  font-size: 0.9rem;
  line-height: 1.5;
  margin-bottom: 12px;
}

.profile-bio.empty {
  color: #b8b1a6;
}

.profile-role {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
  background: rgba(196, 142, 102, 0.12);
  color: var(--color-accent);
}

.profile-role.admin {
  background: rgba(180, 138, 95, 0.2);
  color: #7b552f;
}

.settings-col {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.settings-section {
  border-radius: 2rem;
}

.section-core {
  padding: 1.4rem;
}

.section-title {
  font-size: 1.3rem;
  font-family: var(--font-display);
  font-weight: 700;
  color: var(--color-ink);
  margin-bottom: 20px;
  padding-bottom: 14px;
  border-bottom: 1px solid rgba(88, 70, 53, 0.08);
}

.section-title.no-border {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: 0;
}

.settings-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-ink);
}

.form-group input {
  height: 44px;
  padding: 0 14px;
  border: 1.5px solid rgba(88, 70, 53, 0.12);
  border-radius: 10px;
  font-size: 15px;
  color: var(--color-ink);
  outline: none;
  transition: border-color 0.25s ease;
}

.form-group input:focus {
  border-color: rgba(126, 90, 65, 0.42);
  box-shadow: 0 0 0 3px rgba(126, 90, 65, 0.12);
}

.form-group input.error {
  border-color: #ef4444;
}

.form-group textarea {
  padding: 12px 14px;
  border: 1.5px solid rgba(88, 70, 53, 0.12);
  border-radius: 10px;
  font-size: 14px;
  color: var(--color-ink);
  outline: none;
  resize: vertical;
  font-family: inherit;
  transition: border-color 0.25s ease;
  line-height: 1.5;
}

.form-group textarea:focus {
  border-color: rgba(126, 90, 65, 0.42);
  box-shadow: 0 0 0 3px rgba(126, 90, 65, 0.12);
}

.char-count {
  font-size: 11px;
  text-align: right;
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
  color: #9f9a90;
  display: flex;
  align-items: center;
  padding: 0;
  transition: color 0.2s ease;
}

.toggle-pw:hover {
  color: var(--color-accent);
}

.error-msg {
  font-size: 12px;
  color: #ef4444;
}

.success-msg {
  font-size: 13px;
  color: #14532d;
  background: #eefbf2;
  border: 1px solid #c7eed5;
  border-radius: 8px;
  padding: 10px 14px;
  text-align: center;
}

.scrap-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}

.scrap-status {
  padding: 18px;
  border: 1px solid rgba(88, 70, 53, 0.1);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.52);
  color: var(--color-muted);
  font-size: 14px;
}

.scrap-list {
  display: grid;
  gap: 12px;
}

.scrap-item {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 14px;
  align-items: center;
  padding: 16px;
  border: 1px solid rgba(88, 70, 53, 0.1);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.68);
}

.scrap-main {
  min-width: 0;
}

.scrap-type {
  display: inline-flex;
  margin-bottom: 8px;
  padding: 3px 9px;
  border-radius: 999px;
  background: rgba(196, 142, 102, 0.12);
  color: var(--color-accent);
  font-size: 11px;
  font-weight: 700;
}

.post-badge {
  background: rgba(99, 130, 196, 0.12);
  color: #3b5a9e;
}

.scrap-main h3 {
  margin: 0 0 6px;
  color: var(--color-ink);
  font-size: 1rem;
  line-height: 1.35;
  word-break: keep-all;
}

.scrap-main p {
  margin: 0 0 8px;
  color: var(--color-muted);
  font-size: 0.86rem;
  line-height: 1.45;
}

.scrap-date {
  color: #9f9a90;
  font-size: 12px;
}

.scrap-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.scrap-link,
.scrap-remove {
  height: 34px;
  padding: 0 12px;
  border-radius: 9px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.scrap-link {
  background: #2f2722;
  color: #ffffff;
  border: 1px solid #2f2722;
}

.scrap-remove {
  background: transparent;
  color: #8a4b35;
  border: 1px solid rgba(138, 75, 53, 0.22);
}

.btn-save {
  height: 46px;
  background: linear-gradient(135deg, #2f2722, #7e5a41);
  color: #ffffff;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.25s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  align-self: flex-start;
  padding: 0 24px;
}

.btn-save:hover:not(:disabled) {
  transform: translateY(-1px);
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.promote-section .double-core {
  border: 1px solid rgba(230, 143, 0, 0.2);
  background: linear-gradient(180deg, rgba(255, 252, 245, 0.95), rgba(255, 248, 235, 0.88));
}

.promote-desc {
  font-size: 0.9rem;
  color: var(--color-muted);
  margin-bottom: 16px;
  line-height: 1.6;
}

.field-hint {
  font-size: 0.78rem;
  color: #c47a00;
  margin-top: 2px;
}

.btn-promote {
  background: linear-gradient(135deg, #7b3f00, #c47a00);
  box-shadow: 0 8px 24px -12px rgba(196, 122, 0, 0.6);
}

.spinner-sm {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1024px) {

  .section-head,
  .profile-layout {
    grid-template-columns: 1fr;
  }

  .profile-card {
    position: static;
  }
}

@media (max-width: 768px) {
  .profile-page {
    padding-top: 7rem;
  }

  .page-shell {
    width: min(100% - 24px, 1200px);
  }

  .scrap-item {
    grid-template-columns: 1fr;
  }

  .scrap-actions {
    justify-content: flex-start;
    flex-wrap: wrap;
  }
}
</style>