<template>
  <header class="navbar-wrap">
    <div class="navbar-shell">
      <div class="navbar-left">
        <RouterLink to="/" class="logo">
          <span class="logo-mark">TB</span>
          <span class="logo-copy">
            <strong>TechBridge</strong>
            <small>개발자 메인 허브</small>
          </span>
        </RouterLink>

        <nav class="nav-links" aria-label="주요 메뉴">
          <RouterLink to="/posts" class="nav-link">게시판</RouterLink>
          <RouterLink to="/jobs" class="nav-link">채용 공고</RouterLink>
          <RouterLink to="/contests" class="nav-link">공모전</RouterLink>
          <RouterLink to="/community" class="nav-link">커뮤니티</RouterLink>
        </nav>
      </div>

      <div class="navbar-right">
        <button class="icon-btn search-toggle" @click.stop="openSearch" aria-label="검색 열기">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
        </button>

        <template v-if="!authStore.isLoggedIn">
          <RouterLink to="/login" class="btn-ghost">로그인</RouterLink>
          <RouterLink to="/register" class="btn-primary">
            회원가입
            <span class="btn-icon">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                <path d="M5 12h14" />
                <path d="m13 5 7 7-7 7" />
              </svg>
            </span>
          </RouterLink>
        </template>

        <template v-else>

          <!-- ★ 실시간 채팅 아이콘 추가 -->
          <RouterLink to="/chat" class="icon-btn" aria-label="메시지">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
          </RouterLink>

          <!-- ★ 알림 벨 (검색 버튼과 프로필 사이) -->
          <div class="notif-wrap" ref="notifRef">
            <button class="icon-btn notif-btn" @click="toggleNotif" aria-label="알림">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                   stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
                <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
              </svg>
              <span v-if="notifStore.hasUnread" class="notif-badge">
                {{ notifStore.unreadCount > 99 ? '99+' : notifStore.unreadCount }}
              </span>
            </button>

            <Transition name="dropdown-fade">
              <div v-if="notifOpen" class="dropdown notif-panel">

                <!-- 헤더 -->
                <div class="notif-header">
                  <span class="notif-title">알림</span>
                  <button v-if="notifStore.hasUnread" class="notif-read-all" @click="notifStore.markAllAsRead()">
                    모두 읽음
                  </button>
                </div>

                <!-- 로딩 -->
                <div v-if="notifStore.loading" class="notif-state">
                  <span class="dot"/><span class="dot"/><span class="dot"/>
                </div>

                <!-- 비어 있음 -->
                <div v-else-if="!notifStore.notifications.length" class="notif-state">
                  <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                       stroke-width="1.5" stroke-linecap="round">
                    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
                    <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
                  </svg>
                  <p>새 알림이 없습니다</p>
                </div>

                <!-- 알림 목록 -->
                <!-- shape: { id, actor_name, type, message, related_type, related_id, is_read, created_at } -->
                <ul v-else class="notif-list">
                  <li
                    v-for="n in notifStore.notifications"
                    :key="n.id"
                    class="notif-item"
                    :class="{ 'notif-unread': !n.is_read }"
                    @click="handleNotifClick(n)"
                  >
                    <!-- 타입 아이콘 (model의 5종 타입 모두 처리) -->
                    <div class="notif-icon" :class="`ntype-${n.type}`">
                      <svg v-if="n.type === 'post_like' || n.type === 'community_like'"
                           width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                      </svg>
                      <svg v-else-if="n.type === 'post_comment' || n.type === 'community_comment'"
                           width="13" height="13" viewBox="0 0 24 24" fill="none"
                           stroke="currentColor" stroke-width="2" stroke-linecap="round">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                      </svg>
                      <svg v-else-if="n.type === 'chat'"
                           width="13" height="13" viewBox="0 0 24 24" fill="none"
                           stroke="currentColor" stroke-width="2" stroke-linecap="round">
                        <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
                      </svg>
                      <svg v-else width="13" height="13" viewBox="0 0 24 24" fill="none"
                           stroke="currentColor" stroke-width="2" stroke-linecap="round">
                        <circle cx="12" cy="12" r="10"/>
                        <line x1="12" y1="8" x2="12" y2="12"/>
                        <line x1="12" y1="16" x2="12.01" y2="16"/>
                      </svg>
                    </div>

                    <!-- 내용 -->
                    <div class="notif-body">
                      <p class="notif-msg">{{ n.message }}</p>
                      <span class="notif-time">{{ timeAgo(n.created_at) }}</span>
                    </div>

                    <!-- 읽지 않음 점 -->
                    <span v-if="!n.is_read" class="unread-dot" />
                  </li>
                </ul>

              </div>
            </Transition>
          </div>
          <!-- ★ 알림 벨 끝 -->

          <div class="user-menu" @click="toggleDropdown" ref="menuRef">
            <div class="user-avatar">
              {{ authStore.user?.username?.[0] ?? '유' }}
            </div>
            <div class="user-copy">
              <strong>{{ authStore.user?.username }}</strong>
              <small>내 보드</small>
            </div>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="m6 9 6 6 6-6" />
            </svg>

            <div v-if="dropdownOpen" class="dropdown">
              <RouterLink to="/profile" class="dropdown-item">내 프로필</RouterLink>
              <RouterLink v-if="authStore.isAdmin" to="/admin" class="dropdown-item admin-item">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" style="flex-shrink:0">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01z"/>
                </svg>
                관리자 대시보드
              </RouterLink>
              <RouterLink v-if="authStore.isAdmin" to="/admin/register" class="dropdown-item admin-item">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" style="flex-shrink:0">
                  <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>
                  <line x1="19" y1="8" x2="19" y2="14"/><line x1="22" y1="11" x2="16" y2="11"/>
                </svg>
                관리자 계정 만들기
              </RouterLink>
              <button class="dropdown-item danger" @click="handleLogout">로그아웃</button>
            </div>
          </div>

        </template>
      </div>
    </div>

    <Transition name="search-overlay">
      <div v-if="isSearchOpen" class="search-overlay" @keydown.esc="closeSearch">
        <button class="search-backdrop" type="button" aria-label="검색 닫기" @click="closeSearch"></button>
        <section ref="searchPanelRef" class="search-panel" role="dialog" aria-modal="true" aria-label="통합 검색">
          <div class="search-panel-inner">
            <form class="search-form" @submit.prevent="handleSearch">
              <svg class="search-panel-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.35-4.35" />
              </svg>
              <label for="global-search" class="sr-only">통합 검색</label>
              <input
                id="global-search"
                ref="searchInputRef"
                v-model="searchQuery"
                class="search-panel-input"
                type="search"
                placeholder="키워드, 회사명, 공모전, 게시글 검색하기"
              />
              <button class="search-submit" type="submit">검색</button>
              <button class="search-close" type="button" aria-label="검색 닫기" @click="closeSearch">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                  <path d="M18 6 6 18" />
                  <path d="m6 6 12 12" />
                </svg>
              </button>
            </form>

            <div class="search-panel-content">
              <section class="recent-searches" aria-labelledby="recent-search-title">
                <h2 id="recent-search-title">최근 검색어</h2>
                <div v-if="recentSearches.length" class="recent-chip-list">
                  <button
                    v-for="term in recentSearches"
                    :key="term"
                    type="button"
                    class="recent-chip"
                    @click="useSearchTerm(term)"
                  >
                    {{ term }}
                  </button>
                </div>
                <p v-else class="empty-search">최근 검색어가 없어요.</p>
              </section>
            </div>
          </div>
        </section>
      </div>
    </Transition>

    <div v-if="notifStore.popupNotifications.length" class="popupNotifications">
      <button
        v-for="popup in notifStore.popupNotifications"
        :key="popup.id"
        class="notification-toast"
        type="button"
        @click="openPopupNotification(popup)"
      >
        <span class="toast-icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        </span>
        <span class="toast-body">
          <strong>새 채팅 알림</strong>
          <span>{{ popup.message }}</span>
        </span>
        <span class="toast-close" @click.stop="notifStore.dismissPopup(popup.id)">×</span>
      </button>
    </div>
  </header>
</template>

<script setup>
import { onMounted, onUnmounted, ref, nextTick, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/NotificationStore'  // ★ 추가

const authStore  = useAuthStore()
const notifStore = useNotificationStore()                           // ★ 추가
const router     = useRouter()

// ── 프로필 드롭다운 (기존)
const dropdownOpen = ref(false)
const menuRef      = ref(null)

function toggleDropdown() { dropdownOpen.value = !dropdownOpen.value }

function handleLogout() {
  notifStore.disconnectWs()   // ★ WebSocket 연결 종료
  authStore.logout()
  dropdownOpen.value = false
  router.push('/')
}

// ── 검색
const isSearchOpen   = ref(false)
const searchQuery    = ref('')
const searchInputRef = ref(null)
const searchPanelRef = ref(null)
const recentSearches = ref([])
const recentSearchKey = 'techbridge_recent_searches'

async function openSearch() {
  isSearchOpen.value = true
  await nextTick()
  searchInputRef.value?.focus()
}

function closeSearch() {
  isSearchOpen.value = false
}

function loadRecentSearches() {
  try {
    const stored = window.localStorage.getItem(recentSearchKey)
    recentSearches.value = stored ? JSON.parse(stored).slice(0, 5) : []
  } catch {
    recentSearches.value = []
  }
}

function saveRecentSearch(term) {
  const normalized = term.trim()
  if (!normalized) return
  recentSearches.value = [
    normalized,
    ...recentSearches.value.filter(item => item !== normalized),
  ].slice(0, 5)
  window.localStorage.setItem(recentSearchKey, JSON.stringify(recentSearches.value))
}

function handleSearch() {
  const query = searchQuery.value.trim()
  if (!query) return
  saveRecentSearch(query)
  router.push({ path: '/', query: { search: query } })
  closeSearch()
  searchQuery.value = ''
}

function useSearchTerm(term) {
  searchQuery.value = term
  handleSearch()
}

// ── 알림 (★ 신규)
const notifOpen = ref(false)
const notifRef  = ref(null)

function toggleNotif() {
  notifOpen.value = !notifOpen.value
  if (notifOpen.value) {
    notifStore.fetchNotifications()
  }
}

// related_type: 'post' | 'community' | 'chat_room'  (백엔드 모델 기준)
function handleNotifClick(n) {
  if (!n.is_read) notifStore.markAsRead(n.id)
  const pathMap = {
    post:      `/posts/${n.related_id}`,
    community: `/community/${n.related_id}`,
    chat_room: `/chat/${n.related_id}`,
  }
  const path = n.related_id && pathMap[n.related_type]
  if (path) { router.push(path); notifOpen.value = false }
}

function openPopupNotification(n) {
  notifStore.dismissPopup(n.id)
  handleNotifClick(n)
}

function timeAgo(isoStr) {
  if (!isoStr) return ''
  const diff = Date.now() - new Date(isoStr).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1)  return '방금 전'
  if (m < 60) return `${m}분 전`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}시간 전`
  return `${Math.floor(h / 24)}일 전`
}

// ── 바깥 클릭 닫기 (기존 + 알림 패널 추가)
function onClickOutside(event) {
  if (menuRef.value && !menuRef.value.contains(event.target)) {
    dropdownOpen.value = false
  }
  // ★ 알림 패널 닫기
  if (notifRef.value && !notifRef.value.contains(event.target)) {
    notifOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', onClickOutside)
  authStore.fetchMe()
  loadRecentSearches()

  // ★ 로그인 상태면 WebSocket 연결 (토큰 키 이름은 authStore에 맞게 수정)
  const token = authStore.Token
  if (token) notifStore.connectWs(token)
})

onUnmounted(() => {
  document.removeEventListener('click', onClickOutside)
})

watch(
  () => authStore.token,
  (token) => {
    if (token) {
      notifStore.connectWs(token)
      notifStore.fetchNotifications()
    } else {
      notifStore.disconnectWs()
    }
  },
  { immediate: true },
)
</script>

<style scoped>
/* ════════════════════════════════════
   기존 스타일 전체 유지
════════════════════════════════════ */
.navbar-wrap {
  position: sticky;
  top: 0;
  z-index: 40;
  padding: 1rem 0 0;
}

.navbar-shell {
  width: min(1200px, calc(100% - 32px));
  margin: 0 auto;
  padding: 0.8rem 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.58);
  background: rgba(255, 251, 246, 0.7);
  backdrop-filter: blur(22px);
  box-shadow:
    0 24px 60px -34px rgba(76, 56, 41, 0.34),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

.navbar-left,
.navbar-right,
.logo,
.nav-links,
.nav-link,
.btn-primary,
.btn-ghost,
.user-menu {
  display: flex;
  align-items: center;
}

.navbar-left, .logo { gap: 0.9rem; }
.nav-links { gap: 0.3rem; flex-wrap: wrap; }
.logo { text-decoration: none; color: var(--color-ink); }

.logo-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.85rem;
  height: 2.85rem;
  border-radius: 999px;
  background: linear-gradient(135deg, #312821, #835d43);
  color: #fff8f2;
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: -0.05em;
  box-shadow: 0 16px 30px -24px rgba(131, 93, 67, 0.85);
}

.logo-copy strong, .user-copy strong { display: block; font-size: 0.95rem; font-weight: 700; }
.logo-copy small,  .user-copy small  { color: var(--color-muted); font-size: 0.78rem; }

.nav-link,
.btn-ghost,
.btn-primary,
.icon-btn,
.user-menu { transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1); }

.nav-link {
  padding: 0.72rem 0.95rem;
  border-radius: 999px;
  color: #5d4a38;
  font-size: 0.92rem;
  font-weight: 600;
  text-decoration: none;
}
.nav-link:hover,
.nav-link.router-link-active {
  background: rgba(196, 142, 102, 0.12);
  color: var(--color-ink);
}

.navbar-right { gap: 0.55rem; }

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.icon-btn {
  justify-content: center;
  display: flex;
  align-items: center;
  width: 2.8rem;
  height: 2.8rem;
  border: 0;
  border-radius: 999px;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.48);
  color: #5d4a38;
  cursor: pointer;
}

.btn-ghost,
.btn-primary {
  justify-content: center;
  min-height: 2.9rem;
  padding: 0.75rem 1rem;
  border-radius: 999px;
  font-size: 0.92rem;
  font-weight: 600;
  text-decoration: none;
}
.btn-ghost { color: var(--color-ink); }
.btn-primary {
  gap: 0.6rem;
  color: #fff8f2;
  background: linear-gradient(135deg, #2f2722, #7e5a41);
  box-shadow: 0 18px 40px -24px rgba(126, 90, 65, 0.78);
}
.btn-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.7rem;
  height: 1.7rem;
  border-radius: 999px;
  background: rgba(255, 248, 242, 0.14);
}

.icon-btn:hover, .btn-ghost:hover,
.btn-primary:hover, .user-menu:hover { transform: translateY(-1px) scale(1.01); }
.icon-btn:active, .btn-primary:active { transform: scale(0.98); }

.user-menu {
  position: relative;
  gap: 0.7rem;
  padding: 0.42rem 0.75rem 0.42rem 0.42rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.48);
  cursor: pointer;
}

.user-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(196, 142, 102, 0.2), rgba(255, 255, 255, 0.85));
  color: #5d4a38;
  font-size: 0.88rem;
  font-weight: 700;
}

.search-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 80;
}

.search-backdrop {
  position: absolute;
  inset: 0;
  border: 0;
  background: rgba(18, 18, 17, 0.48);
  cursor: pointer;
}

.search-panel {
  position: relative;
  z-index: 1;
  min-height: 24rem;
  border: 0;
  border-bottom: 1px solid rgba(48, 42, 35, 0.08);
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 30px 70px -44px rgba(20, 18, 16, 0.55);
}

.search-panel-inner {
  width: min(980px, calc(100% - 32px));
  margin: 0 auto;
  padding: 1.5rem 0 3rem;
}

.search-form {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto auto;
  align-items: center;
  gap: 1rem;
  min-height: 4.7rem;
  border-bottom: 1px solid rgba(76, 56, 41, 0.12);
}

.search-panel-icon {
  color: #2f2722;
}

.search-panel-input {
  min-width: 0;
  border: 0;
  background: transparent;
  color: var(--color-ink);
  font-size: clamp(1.15rem, 2vw, 1.45rem);
  font-weight: 600;
  outline: none;
}

.search-panel-input::placeholder {
  color: #bbb4ab;
  font-weight: 500;
}

.search-submit,
.search-close {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 0;
  border-radius: 999px;
  cursor: pointer;
}

.search-submit {
  min-height: 2.75rem;
  padding: 0 1rem;
  background: #2f2722;
  color: #fff8f2;
  font-weight: 700;
}

.search-close {
  width: 2.75rem;
  height: 2.75rem;
  background: transparent;
  color: #2f2722;
}

.search-panel-content {
  display: grid;
  gap: 2rem;
  padding-top: 2.7rem;
}

.recent-searches h2 {
  margin: 0 0 2rem;
  color: #2f2722;
  font-size: 1rem;
  font-weight: 800;
}

.empty-search {
  margin: 0;
  color: #898179;
  text-align: center;
  font-size: 1rem;
  font-weight: 600;
}

.recent-chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.recent-chip {
  min-height: 2.65rem;
  padding: 0 1rem;
  border: 1px solid rgba(76, 56, 41, 0.1);
  border-radius: 999px;
  background: rgba(247, 241, 235, 0.72);
  color: #5d4a38;
  cursor: pointer;
  font-weight: 700;
}

.search-overlay-enter-active,
.search-overlay-leave-active {
  transition: opacity 0.28s ease;
}

.search-overlay-enter-active .search-panel,
.search-overlay-leave-active .search-panel {
  transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

.search-overlay-enter-from,
.search-overlay-leave-to {
  opacity: 0;
}

.search-overlay-enter-from .search-panel,
.search-overlay-leave-to .search-panel {
  transform: translateY(-100%);
}

.dropdown {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  min-width: 11rem;
  padding: 0.45rem;
  border-radius: 1.2rem;
  border: 1px solid rgba(255, 255, 255, 0.72);
  background: rgba(255, 251, 246, 0.94);
  box-shadow: 0 28px 60px -34px rgba(76, 56, 41, 0.34);
}
.dropdown-item {
  width: 100%;
  display: flex;
  align-items: center;
  padding: 0.8rem 0.9rem;
  border: 0;
  border-radius: 0.95rem;
  background: transparent;
  color: var(--color-ink);
  font-size: 0.92rem;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
}
.dropdown-item:hover { background: rgba(196, 142, 102, 0.12); }
.danger { color: #a8563f; }
.admin-item { color: #5d4037; display: flex; align-items: center; gap: 0.5rem; }

/* ════════════════════════════════════
   ★ 알림 (신규 추가)
════════════════════════════════════ */
.notif-wrap {
  position: relative;
  display: inline-flex;
}

/* 벨 버튼: 기존 .icon-btn에 배지 추가 */
.notif-btn { position: relative; }

.notif-badge {
  position: absolute;
  top: -3px; right: -3px;
  min-width: 15px; height: 15px;
  padding: 0 3px;
  border-radius: 999px;
  background: #c0392b;
  color: #fff;
  font-size: 9px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  border: 2px solid rgba(255, 251, 246, 0.9); /* navbar 배경색에 맞춤 */
  line-height: 1;
  pointer-events: none;
}

/* 알림 패널: 기존 .dropdown 스타일 계승, 폭만 확장 */
.notif-panel {
  min-width: 300px;
  max-height: 420px;
  padding: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.notif-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 0.9rem 0.65rem;
  border-bottom: 1px solid rgba(196, 142, 102, 0.15);
  flex-shrink: 0;
}
.notif-title { font-size: 0.92rem; font-weight: 700; color: var(--color-ink); }
.notif-read-all {
  font-size: 0.78rem; font-weight: 600;
  color: #835d43;
  background: none; border: none; cursor: pointer; padding: 0;
  transition: color 0.2s;
}
.notif-read-all:hover { color: #312821; }

.notif-state {
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: 8px; padding: 2rem 1rem;
  color: var(--color-muted); font-size: 0.85rem;
}
.notif-state svg { opacity: 0.4; }

.dot {
  display: inline-block;
  width: 6px; height: 6px; border-radius: 50%;
  background: rgba(196, 142, 102, 0.5);
  animation: blink 1.2s infinite;
}
.dot:nth-child(2) { animation-delay: .2s; }
.dot:nth-child(3) { animation-delay: .4s; }
@keyframes blink { 0%,80%,100%{opacity:.2} 40%{opacity:1} }

.notif-list {
  list-style: none; margin: 0; padding: 0.3rem;
  overflow-y: auto; flex: 1;
}
.notif-list::-webkit-scrollbar { width: 4px; }
.notif-list::-webkit-scrollbar-thumb {
  background: rgba(196, 142, 102, 0.2); border-radius: 2px;
}

.notif-item {
  position: relative;
  display: flex; align-items: flex-start; gap: 0.6rem;
  padding: 0.7rem 0.8rem;
  border-radius: 0.95rem;
  cursor: pointer;
  transition: background 0.2s;
}
.notif-item:hover { background: rgba(196, 142, 102, 0.1); }
.notif-item.notif-unread { background: rgba(196, 142, 102, 0.07); }
.notif-item.notif-unread:hover { background: rgba(196, 142, 102, 0.14); }

.notif-icon {
  width: 28px; height: 28px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; margin-top: 1px;
}
.ntype-post_like,
.ntype-community_like    { background: rgba(192, 57, 43, 0.12); color: #a83226; }
.ntype-post_comment,
.ntype-community_comment { background: rgba(131, 93, 67, 0.12); color: #5d4a38; }
.ntype-chat              { background: rgba(39, 174, 96, 0.12);  color: #1e8449; }

.notif-body { flex: 1; min-width: 0; }
.notif-msg {
  font-size: 0.85rem; font-weight: 600;
  color: var(--color-ink); line-height: 1.45;
  margin: 0 0 2px; word-break: keep-all;
}
.notif-time { font-size: 0.75rem; color: var(--color-muted); }

.unread-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: #835d43; flex-shrink: 0; align-self: center;
}

/* 드롭다운 트랜지션 */
.dropdown-fade-enter-active { transition: opacity .15s, transform .15s; }
.dropdown-fade-leave-active { transition: opacity .10s, transform .10s; }
.dropdown-fade-enter-from,
.dropdown-fade-leave-to { opacity: 0; transform: translateY(-6px); }

.popupNotifications {
  position: fixed;
  top: 88px;
  right: 24px;
  z-index: 80;
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: min(340px, calc(100vw - 32px));
}

.notification-toast {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  width: 100%;
  padding: 14px;
  border: 1px solid rgba(196, 142, 102, 0.2);
  border-radius: 16px;
  background: rgba(255, 251, 246, 0.98);
  color: #312821;
  box-shadow: 0 20px 50px -28px rgba(76, 56, 41, 0.45);
  cursor: pointer;
  text-align: left;
}

.toast-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: rgba(39, 174, 96, 0.12);
  color: #1e8449;
}

.toast-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.toast-body strong {
  font-size: 0.88rem;
  font-weight: 800;
}

.toast-body span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.84rem;
  font-weight: 600;
  color: #5d4a38;
}

.toast-close {
  flex-shrink: 0;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #a68b6a;
  font-size: 1rem;
  line-height: 1;
}

.toast-close:hover {
  background: rgba(196, 142, 102, 0.12);
}

/* ── 반응형 (기존 유지) */
@media (max-width: 900px) {
  .navbar-shell { flex-direction: column; align-items: stretch; border-radius: 2rem; }
  .navbar-left, .navbar-right { justify-content: space-between; }
  .nav-links { overflow-x: auto; flex-wrap: nowrap; padding-bottom: 0.15rem; }
}
@media (max-width: 640px) {
  .navbar-shell { width: min(100% - 24px, 1200px); padding: 0.85rem; }
  .logo-copy small, .user-copy small { display: none; }
  .icon-btn { display: none; }
  .search-toggle { display: flex; }
  .search-form { grid-template-columns: auto minmax(0, 1fr) auto; }
  .search-submit { display: none; }
  .search-panel { min-height: 22rem; }
}
</style>
