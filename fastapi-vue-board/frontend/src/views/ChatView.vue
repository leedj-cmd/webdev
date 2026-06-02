<template>
  <div class="chat-page-container">
    <div class="chat-shell">
      <aside class="rooms-sidebar" :class="{ 'mobile-hidden': activeRoomId && isMobile }">
        <div class="sidebar-header">
          <div class="header-title-row">
            <div class="header-dot"></div>
            <h2>메시지</h2>
          </div>
          <button class="icon-btn-ghost" title="새 채팅" @click="focusSearch">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
            </svg>
          </button>
        </div>

        <div class="search-rooms">
          <div class="search-input-wrap">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.35-4.35" />
            </svg>
            <input type="text" v-model="roomSearchQuery" placeholder="검색..." />
          </div>
        </div>

        <div class="section-label">최근 대화</div>

        <transition-group v-if="rooms.length > 0" name="room-list" tag="div" class="rooms-list">
          <div v-for="room in filteredRooms" :key="room.id" class="room-item"
            :class="{ active: activeRoomId === room.id, unread: hasUnread(room) }" @click="selectRoom(room.id)">
            <div class="room-avatar">
              <div class="avatar-circle" :style="{ background: getAvatarColor(room) }">
                {{ getRoomInitial(room) }}
              </div>
              <span v-if="isOnline(room)" class="online-dot"></span>
            </div>
            <div class="room-info">
              <div class="room-top">
                <span class="room-name">{{ getRoomName(room) }}</span>
                <time class="last-time">{{ formatTime(room.last_message_time) }}</time>
              </div>
              <div class="room-bottom">
                <p class="last-msg">{{ room.last_message || '대화 내용이 없습니다.' }}</p>
                <span v-if="room.unread_count" class="unread-badge">{{ room.unread_count }}</span>
              </div>
            </div>
          </div>
        </transition-group>

        <div v-else-if="loadingRooms" class="rooms-state">
          <div class="loader-spinner"></div>
          <p>불러오는 중...</p>
        </div>

        <div v-else class="rooms-state">
          <div class="empty-icon-wrap">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
          </div>
          <p>진행 중인 대화가 없습니다.</p>
        </div>
      </aside>

      <main class="chat-window" :class="{ 'mobile-hidden': !activeRoomId && isMobile }">
        <template v-if="activeRoomId">
          <header class="chat-header">
            <button v-if="isMobile" class="back-btn" @click="activeRoomId = null">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="m15 18-6-6 6-6" />
              </svg>
            </button>
            <div class="active-user-info">
              <div class="avatar-circle small" :style="{ background: getAvatarColor(activeRoom) }">
                {{ getRoomInitial(activeRoom) }}
              </div>
              <div>
                <h3>{{ getRoomName(activeRoom) }}</h3>
                <span class="status">{{ isOnline(activeRoom) ? '현재 활동 중' : '오프라인' }}</span>
              </div>
            </div>
            <div class="header-actions">
              <button class="icon-btn-small">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="1" />
                  <circle cx="12" cy="5" r="1" />
                  <circle cx="12" cy="19" r="1" />
                </svg>
              </button>
            </div>
          </header>

          <div class="messages-area" ref="messageContainer">
            <div v-if="loadingMessages" class="messages-state">
              <div class="loader-spinner"></div>
            </div>

            <transition-group v-else name="msg" tag="div" class="messages-inner">
              <div v-for="(msg, idx) in messages" :key="msg.id" class="message-row"
                :class="{ mine: msg.sender_id === currentUserId }">
                <div v-if="shouldShowDate(msg, idx)" class="date-divider">
                  <span>{{ formatDateDivider(msg.created_at) }}</span>
                </div>

                <div class="message-bubble-wrap">
                  <div v-if="msg.sender_id !== currentUserId" class="msg-avatar">
                    {{ getRoomInitial(activeRoom) }}
                  </div>
                  <div class="message-content">
                    <div v-if="msg.message_type === 'image'" class="bubble attachment-bubble image-message">
                      <a :href="getFileUrl(msg.file_url)" target="_blank" rel="noopener">
                        <img :src="getFileUrl(msg.file_url)" :alt="msg.file_name || '첨부 이미지'" />
                      </a>
                      <span class="attachment-name">{{ msg.file_name }}</span>
                    </div>
                    <a v-else-if="msg.message_type === 'file'" class="bubble attachment-bubble file-message"
                      :href="getFileUrl(msg.file_url)" target="_blank" rel="noopener">
                      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                        stroke-width="1.8">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                        <path d="M14 2v6h6" />
                      </svg>
                      <span>
                        <strong>{{ msg.file_name || msg.content }}</strong>
                        <small>{{ formatFileSize(msg.file_size) }}</small>
                      </span>
                    </a>
                    <div v-else class="bubble">
                      <p>{{ msg.content }}</p>
                    </div>
                    <time class="msg-time">{{ formatMsgTime(msg.created_at) }}</time>
                  </div>
                </div>
              </div>
            </transition-group>
          </div>

          <footer class="chat-input-area">
            <div class="input-shell">
              <button type="button" class="attach-btn" :disabled="uploadingAttachment" @click="openAttachmentPicker">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path
                    d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
                </svg>
              </button>
              <input ref="attachmentInputRef" class="attachment-input" type="file"
                accept=".jpg,.jpeg,.png,.gif,.webp,.pdf,.txt,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.zip"
                @change="handleAttachmentSelected" />
              <textarea ref="inputRef" v-model="newMessage" placeholder="메시지를 입력하세요..." rows="1"
                @keydown.enter="handleMessageKeydown" @compositionstart="isComposingMessage = true"
                @compositionend="isComposingMessage = false"></textarea>
              <button class="send-btn" :disabled="!newMessage.trim()" @click="sendMessage">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <path d="M22 2 11 13" />
                  <path d="m22 2-7 20-4-9-9-4 20-7z" />
                </svg>
              </button>
            </div>
          </footer>
        </template>

        <transition v-else name="fade">
          <div class="empty-chat-state">
            <div class="empty-illustration">
              <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M21 15a2 2 0 0 1-2 2H8l-5 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
            </div>
            <h2>내 메시지</h2>
            <p>동료 개발자와 대화를 시작해보세요</p>
            <button class="primary-cta" @click="focusSearch">
              <span>새 대화 시작하기</span>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </transition>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/axios'

const authStore = useAuthStore()
const route = useRoute()
const currentUserId = computed(() => authStore.user?.id)

const rooms = ref([])
const activeRoomId = ref(null)
const messages = ref([])
const newMessage = ref('')
const roomSearchQuery = ref('')
const loadingRooms = ref(false)
const loadingMessages = ref(false)
const isComposingMessage = ref(false)
const uploadingAttachment = ref(false)
const onlineUserIds = ref([])
const isMobile = ref(window.innerWidth <= 768)

const messageContainer = ref(null)
const inputRef = ref(null)
const attachmentInputRef = ref(null)
const ws = ref(null)

const activeRoom = computed(() => rooms.value.find(r => r.id === activeRoomId.value))
const filteredRooms = computed(() => {
  if (!roomSearchQuery.value) return rooms.value
  const q = roomSearchQuery.value.toLowerCase()
  return rooms.value.filter(r => getRoomName(r).toLowerCase().includes(q))
})

const fetchRooms = async () => {
  loadingRooms.value = true
  try {
    const res = await api.get('/chat/rooms')
    rooms.value = res.data
  } catch (err) {
    console.error('Rooms load failed:', err)
  } finally {
    loadingRooms.value = false
  }
}

const getRouteRoomId = () => {
  const rawRoomId = route.query.room || route.params.roomId
  const initialRoomId = Number(rawRoomId)
  return Number.isInteger(initialRoomId) && initialRoomId > 0 ? initialRoomId : null
}

const selectRouteRoom = async () => {
  const initialRoomId = getRouteRoomId()
  if (initialRoomId) await selectRoom(initialRoomId)
}

const selectRoom = async (roomId) => {
  if (activeRoomId.value === roomId) return
  if (ws.value) ws.value.close()
  activeRoomId.value = roomId
  onlineUserIds.value = []
  loadingMessages.value = true
  try {
    const res = await api.get(`/chat/rooms/${roomId}/messages`)
    messages.value = res.data
    await api.patch(`/chat/rooms/${roomId}/read`)
    const rIdx = rooms.value.findIndex(r => r.id === roomId)
    if (rIdx !== -1) rooms.value[rIdx].unread_count = 0
    await nextTick()
    scrollToBottom()
    connectWebSocket(roomId)
  } catch (err) {
    console.error('Messages load failed:', err)
  } finally {
    loadingMessages.value = false
  }
}

const connectWebSocket = (roomId) => {
  const token = localStorage.getItem('access_token')
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  ws.value = new WebSocket(`${protocol}//127.0.0.1:8000/chat/ws/${roomId}?token=${token}`)

  ws.value.onmessage = (event) => {
    try {
      // 백엔드에서 JSON으로 보낼 경우를 대비
      const data = JSON.parse(event.data)
      if (data.event === 'presence') {
        onlineUserIds.value = data.online_user_ids
        return
      }
      messages.value.push(data)
    } catch {
      // 문자열일 경우 임시 처리
      const raw = event.data
      const colonIdx = raw.indexOf(':')
      const senderId = parseInt(raw.substring(0, colonIdx))
      const text = raw.substring(colonIdx + 2)

      messages.value.push({
        id: Date.now(),
        sender_id: senderId,
        content: text,
        message_type: 'text',
        created_at: new Date().toISOString()
      })
    }
    nextTick(scrollToBottom)
  }

  ws.value.onerror = (err) => console.error('WS Error:', err)
  ws.value.onclose = () => console.log('WS Closed')
}

const sendMessage = () => {
  if (!newMessage.value.trim() || !ws.value) return
  ws.value.send(newMessage.value.trim())
  newMessage.value = ''
  if (inputRef.value) inputRef.value.style.height = 'auto'
}

const handleMessageKeydown = (event) => {
  if (event.isComposing || isComposingMessage.value || event.keyCode === 229) return
  event.preventDefault()
  sendMessage()
}

const openAttachmentPicker = () => {
  if (uploadingAttachment.value || !activeRoomId.value) return
  attachmentInputRef.value?.click()
}

const handleAttachmentSelected = async (event) => {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file || !activeRoomId.value) return

  const maxBytes = 10 * 1024 * 1024
  if (file.size > maxBytes) {
    alert('첨부파일은 10MB 이하만 업로드할 수 있습니다.')
    return
  }

  const formData = new FormData()
  formData.append('file', file)
  uploadingAttachment.value = true

  try {
    const res = await api.post(`/chat/rooms/${activeRoomId.value}/attachments`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    if (ws.value?.readyState !== WebSocket.OPEN) {
      messages.value.push(res.data)
      await nextTick()
      scrollToBottom()
    }
  } catch (err) {
    console.error('Attachment upload failed:', err)
    alert(err.response?.data?.detail || '첨부파일 전송에 실패했습니다.')
  } finally {
    uploadingAttachment.value = false
  }
}

// 유틸리티
const scrollToBottom = () => {
  if (messageContainer.value) messageContainer.value.scrollTop = messageContainer.value.scrollHeight
}

const getFileUrl = (fileUrl) => {
  if (!fileUrl) return '#'
  if (/^https?:\/\//.test(fileUrl)) return fileUrl
  return `http://127.0.0.1:8000${fileUrl}`
}

const formatFileSize = (size) => {
  if (!size) return ''
  if (size < 1024) return `${size}B`
  if (size < 1024 * 1024) return `${Math.round(size / 1024)}KB`
  return `${(size / 1024 / 1024).toFixed(1)}MB`
}

const getRoomName = (room) => {
  if (!room) return '대화'
  if (room.type === 'group') return room.name || '그룹 채팅'
  const otherMember = room.members?.find(m => m.user_id !== currentUserId.value)
  return otherMember?.user?.username || `사용자 ${room.id}`
}

const getRoomInitial = (room) => getRoomName(room).charAt(0)

const getAvatarColor = (room) => {
  const colors = ['#7c5c42', '#3d2e22', '#9e7a58', '#c4956a', '#5a4132']
  const otherMember = room?.members?.find(m => m.user_id !== currentUserId.value)
  return colors[(otherMember?.user_id || 0) % colors.length]
}

const formatTime = (isoStr) => {
  if (!isoStr) return ''
  const date = new Date(isoStr)
  const now = new Date()
  if (date.toDateString() === now.toDateString()) {
    return `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
  }
  return `${date.getMonth() + 1}/${date.getDate()}`
}

const formatMsgTime = (isoStr) => {
  const date = new Date(isoStr)
  const ampm = date.getHours() >= 12 ? '오후' : '오전'
  const hours = date.getHours() % 12 || 12
  return `${ampm} ${hours}:${String(date.getMinutes()).padStart(2, '0')}`
}

const formatDateDivider = (isoStr) => {
  const date = new Date(isoStr)
  return `${date.getFullYear()}년 ${date.getMonth() + 1}월 ${date.getDate()}일`
}

const shouldShowDate = (msg, idx) => {
  if (idx === 0) return true
  const prevMsg = messages.value[idx - 1]
  return new Date(msg.created_at).toDateString() !== new Date(prevMsg.created_at).toDateString()
}

const hasUnread = (room) => room.unread_count > 0
const isOnline = (room) => {
  const otherMember = room?.members?.find(m => m.user_id !== currentUserId.value)
  return onlineUserIds.value.includes(otherMember?.user_id)
}

const focusSearch = () => {
  alert("게시글 상세 페이지의 '메시지 보내기' 버튼을 통해 새로운 대화를 시작할 수 있습니다.")
}

const handleResize = () => { isMobile.value = window.innerWidth <= 768 }

onMounted(async () => {
  await fetchRooms()
  await selectRouteRoom()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (ws.value) ws.value.close()
  window.removeEventListener('resize', handleResize)
})

watch(newMessage, () => {
  if (!inputRef.value) return
  inputRef.value.style.height = 'auto'
  inputRef.value.style.height = inputRef.value.scrollHeight + 'px'
})

watch(
  () => [route.query.room, route.params.roomId],
  async () => {
    await selectRouteRoom()
  },
)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap');

/* ── CSS 변수 ── */
.chat-page-container {
  --color-bg: #f7f4f1;
  --color-sidebar: #ffffff;
  --color-window: #faf8f6;
  --color-primary: #5a3e2b;
  --color-primary-light: #7c5c42;
  --color-accent: #c4895a;
  --color-border: #ece8e3;
  --color-border-soft: #f2eeea;
  --color-text-main: #2a1f16;
  --color-text-muted: #9e8472;
  --color-text-light: #bba898;
  --color-bubble-mine: #3d2e22;
  --color-bubble-other: #ffffff;
  --color-hover: #f9f6f3;
  --color-active: #f3ede7;
  --color-unread: #e8ddd5;
  --radius-card: 28px;
  --radius-bubble: 20px;
  --radius-avatar: 14px;
  --shadow-card: 0 24px 64px -16px rgba(58, 38, 22, 0.14), 0 4px 16px -4px rgba(58, 38, 22, 0.06);
  --font: 'Pretendard', -apple-system, sans-serif;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.chat-page-container {
  font-family: var(--font);
  max-width: 1100px;
  height: calc(100vh - 112px);
  margin: 24px auto;
  padding: 0 20px;
}

/* ── 쉘 ── */
.chat-shell {
  display: flex;
  height: 100%;
  background: var(--color-window);
  border-radius: var(--radius-card);
  overflow: hidden;
  box-shadow: var(--shadow-card);
  border: 1px solid var(--color-border);
}

/* ════════════════════════════
   사이드바
════════════════════════════ */
.rooms-sidebar {
  width: 320px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background: var(--color-sidebar);
  border-right: 1px solid var(--color-border);
}

.sidebar-header {
  padding: 28px 20px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-accent);
}

.sidebar-header h2 {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--color-text-main);
  letter-spacing: -0.04em;
}

.icon-btn-ghost {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: none;
  background: transparent;
  color: var(--color-text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, color 0.15s;
}

.icon-btn-ghost:hover {
  background: var(--color-hover);
  color: var(--color-text-main);
}

/* 검색 */
.search-rooms {
  padding: 0 16px 4px;
}

.search-input-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: var(--color-hover);
  border-radius: 12px;
  color: var(--color-text-light);
  border: 1px solid transparent;
  transition: border-color 0.2s;
}

.search-input-wrap:focus-within {
  border-color: var(--color-border);
  background: #fff;
}

.search-input-wrap input {
  border: none;
  background: transparent;
  outline: none;
  font-size: 0.88rem;
  width: 100%;
  color: var(--color-text-main);
  font-family: var(--font);
}

.search-input-wrap input::placeholder {
  color: var(--color-text-light);
}

/* 섹션 레이블 */
.section-label {
  padding: 16px 20px 8px;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-text-light);
}

/* 방 목록 */
.rooms-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 8px 12px;
}

.rooms-list::-webkit-scrollbar {
  width: 4px;
}

.rooms-list::-webkit-scrollbar-track {
  background: transparent;
}

.rooms-list::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 4px;
}

.room-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 12px;
  cursor: pointer;
  transition: background 0.15s;
  border-radius: 14px;
  position: relative;
  margin-bottom: 2px;
}

.room-item:hover {
  background: var(--color-hover);
}

.room-item.active {
  background: var(--color-active);
}

.room-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 20%;
  bottom: 20%;
  width: 3px;
  border-radius: 0 3px 3px 0;
  background: var(--color-accent);
}

/* 아바타 */
.room-avatar {
  position: relative;
  flex-shrink: 0;
}

.avatar-circle {
  width: 46px;
  height: 46px;
  border-radius: var(--radius-avatar);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.95);
  font-weight: 800;
  font-size: 1.05rem;
  letter-spacing: -0.02em;
}

.header-avatar {
  width: 38px;
  height: 38px;
  border-radius: 11px;
  font-size: 0.95rem;
}

.online-dot {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 12px;
  height: 12px;
  background: #3dba6e;
  border: 2.5px solid #fff;
  border-radius: 50%;
}

/* 방 정보 */
.room-info {
  flex: 1;
  min-width: 0;
}

.room-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 3px;
}

.room-name {
  font-weight: 700;
  font-size: 0.92rem;
  color: var(--color-text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.last-time {
  font-size: 0.7rem;
  color: var(--color-text-light);
  white-space: nowrap;
  flex-shrink: 0;
  margin-left: 8px;
}

.room-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.last-msg {
  font-size: 0.82rem;
  color: var(--color-text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.unread-badge {
  background: var(--color-accent);
  color: white;
  font-size: 0.67rem;
  font-weight: 700;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.room-item.unread .room-name {
  font-weight: 800;
}

.room-item.unread .last-msg {
  color: var(--color-text-main);
  font-weight: 600;
}

/* 빈 상태 */
.rooms-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: var(--color-text-light);
  font-size: 0.85rem;
  padding: 40px 0;
}

.empty-icon-wrap {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  background: var(--color-hover);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 4px;
}

/* ════════════════════════════
   채팅창
════════════════════════════ */
.chat-window {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--color-window);
  min-width: 0;
}

/* 헤더 */
.chat-header {
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--color-sidebar);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.active-user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 채팅 헤더 우측 더보기 버튼 */
.icon-btn-small {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: none;
  background: transparent;
  color: var(--color-text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, color 0.15s, transform 0.15s;
}

.icon-btn-small:hover {
  background: var(--color-hover);
  color: var(--color-text-main);
  transform: scale(1.08);
}

.icon-btn-small:active {
  background: var(--color-active);
  transform: scale(0.95);
}

.user-meta h3 {
  font-size: 0.98rem;
  font-weight: 800;
  color: var(--color-text-main);
  letter-spacing: -0.02em;
}

.status-row {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-top: 2px;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--color-border);
}

.status-dot.online {
  background: #3dba6e;
}

.status-text {
  font-size: 0.72rem;
  color: var(--color-text-muted);
  font-weight: 500;
}

/* 메시지 영역 */
.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 28px 28px 12px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.messages-area::-webkit-scrollbar {
  width: 4px;
}

.messages-area::-webkit-scrollbar-track {
  background: transparent;
}

.messages-area::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 4px;
}

.messages-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 날짜 구분선 */
.date-divider {
  text-align: center;
  margin: 24px 0 12px;
  position: relative;
}

.date-divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: var(--color-border-soft);
}

.date-divider span {
  position: relative;
  background: var(--color-window);
  padding: 0 14px;
  font-size: 0.72rem;
  color: var(--color-text-light);
  font-weight: 600;
  letter-spacing: 0.02em;
}

/* 메시지 버블 */
.message-row {
  display: flex;
  flex-direction: column;
  margin-bottom: 2px;
}

.message-bubble-wrap {
  display: flex;
  gap: 9px;
  max-width: 72%;
  align-items: flex-start;
}

.mine .message-bubble-wrap {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.msg-avatar {
  width: 30px;
  height: 30px;
  border-radius: 10px;
  background: var(--color-unread);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 800;
  color: var(--color-primary-light);
  flex-shrink: 0;
  margin-bottom: 1px;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.bubble {
  padding: 11px 16px;
  border-radius: var(--radius-bubble);
  font-size: 0.92rem;
  line-height: 1.55;
}

.attachment-bubble {
  display: flex;
  gap: 10px;
  text-decoration: none;
}

.image-message {
  flex-direction: column;
  padding: 8px;
  max-width: 280px;
}

.image-message img {
  display: block;
  width: 100%;
  max-height: 260px;
  object-fit: cover;
  border-radius: 12px;
}

.attachment-name {
  padding: 0 4px 2px;
  font-size: 0.8rem;
  font-weight: 600;
  word-break: break-all;
}

.file-message {
  align-items: center;
  min-width: 220px;
  max-width: 320px;
}

.file-message svg {
  flex-shrink: 0;
}

.file-message span {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.file-message strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.9rem;
}

.file-message small {
  opacity: 0.72;
  font-size: 0.75rem;
}

.mine .bubble {
  background: var(--color-bubble-mine);
  color: rgba(255, 255, 255, 0.95);
  border-bottom-right-radius: 6px;
}

.message-row:not(.mine) .bubble {
  background: var(--color-bubble-other);
  color: var(--color-text-main);
  border-bottom-left-radius: 6px;
  border: 1px solid var(--color-border-soft);
  box-shadow: 0 1px 4px rgba(58, 38, 22, 0.05);
}

.msg-time {
  font-size: 0.68rem;
  color: var(--color-text-light);
  display: block;
  padding: 0 4px;
}

.mine .msg-time {
  text-align: right;
}

/* ── 입력창 ── */
.chat-input-area {
  padding: 16px 24px 24px;
  background: var(--color-sidebar);
  border-top: 1px solid var(--color-border-soft);
  flex-shrink: 0;
}

.input-shell {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  background: var(--color-window);
  padding: 6px 6px 6px 14px;
  border-radius: 18px;
  border: 1.5px solid var(--color-border);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input-shell:focus-within {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px rgba(196, 137, 90, 0.1);
}

.input-shell textarea {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  padding: 8px 0;
  font-family: var(--font);
  font-size: 0.92rem;
  color: var(--color-text-main);
  max-height: 120px;
  resize: none;
  line-height: 1.5;
}

.input-shell textarea::placeholder {
  color: var(--color-text-light);
}

.attach-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: none;
  background: transparent;
  color: var(--color-text-light);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, color 0.15s;
  flex-shrink: 0;
  align-self: flex-end;
  margin-bottom: 2px;
}

.attach-btn {
  background: transparent;
  color: #a68b6a;
}

.attach-btn:hover:not(:disabled) {
  background: #eee;
}

.attach-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.attachment-input {
  display: none;
}

.send-btn {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: none;
  background: var(--color-border);
  color: var(--color-text-light);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, color 0.2s, transform 0.15s;
  flex-shrink: 0;
  align-self: flex-end;
}

.send-btn.active {
  background: var(--color-bubble-mine);
  color: white;
}

.send-btn:disabled {
  cursor: not-allowed;
}

.send-btn.active:hover {
  background: var(--color-primary);
  transform: scale(1.06);
}

/* ── 빈 채팅 상태 ── */
.empty-chat-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 40px;
}

.empty-art {
  position: relative;
  width: 110px;
  height: 110px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 32px;
}

.art-ring {
  position: absolute;
  border-radius: 50%;
  border: 1.5px solid var(--color-border);
}

.art-ring.outer {
  width: 110px;
  height: 110px;
}

.art-ring.inner {
  width: 78px;
  height: 78px;
}

.art-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  background: var(--color-sidebar);
  border: 1.5px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-light);
  box-shadow: 0 4px 16px rgba(58, 38, 22, 0.08);
  position: relative;
  z-index: 1;
}

.empty-chat-state h2 {
  font-size: 1.3rem;
  font-weight: 800;
  color: var(--color-text-main);
  margin-bottom: 10px;
  letter-spacing: -0.03em;
}

.empty-chat-state p {
  font-size: 0.9rem;
  color: var(--color-text-muted);
  margin-bottom: 28px;
  line-height: 1.6;
}

.primary-cta {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 22px;
  background: var(--color-bubble-mine);
  color: rgba(255, 255, 255, 0.95);
  border: none;
  border-radius: 14px;
  font-family: var(--font);
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s, transform 0.15s;
  letter-spacing: -0.01em;
}

.primary-cta:hover {
  background: var(--color-primary);
  transform: translateY(-1px);
}

/* 로더 */
.loader-spinner {
  width: 22px;
  height: 22px;
  border: 2.5px solid var(--color-border);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

/* ════════════════════════════
   애니메이션
════════════════════════════ */

/* 채팅 쉘 진입 */
.chat-shell {
  animation: shell-in 0.45s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes shell-in {
  from {
    opacity: 0;
    transform: translateY(16px) scale(0.98);
  }

  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 사이드바 헤더 요소 순차 진입 */
.sidebar-header {
  animation: fade-down 0.4s cubic-bezier(0.22, 1, 0.36, 1) 0.1s both;
}

.search-rooms {
  animation: fade-down 0.4s cubic-bezier(0.22, 1, 0.36, 1) 0.18s both;
}

.section-label {
  animation: fade-down 0.4s cubic-bezier(0.22, 1, 0.36, 1) 0.24s both;
}

@keyframes fade-down {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 채팅방 목록 아이템 진입 */
.room-list-enter-active {
  animation: room-slide-in 0.3s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.room-list-leave-active {
  animation: room-slide-in 0.2s cubic-bezier(0.22, 1, 0.36, 1) reverse both;
}

.room-list-move {
  transition: transform 0.3s cubic-bezier(0.22, 1, 0.36, 1);
}

@keyframes room-slide-in {
  from {
    opacity: 0;
    transform: translateX(-12px);
  }

  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 채팅창 전환 (방 선택 시) */
.chat-switch-enter-active {
  animation: chat-fade-in 0.25s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.chat-switch-leave-active {
  animation: chat-fade-in 0.15s ease-in reverse both;
  position: absolute;
  width: 100%;
}

@keyframes chat-fade-in {
  from {
    opacity: 0;
    transform: translateX(10px);
  }

  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* chat-inner이 flex column을 채우도록 */
.chat-inner {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* messages-inner: transition-group wrapper */
.messages-inner {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

/* 메시지 버블 진입 */
.msg-enter-active {
  animation: msg-pop 0.28s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.msg-leave-active {
  animation: msg-pop 0.15s ease-in reverse both;
}

.msg-move {
  transition: transform 0.25s cubic-bezier(0.22, 1, 0.36, 1);
}

@keyframes msg-pop {
  from {
    opacity: 0;
    transform: translateY(10px) scale(0.97);
  }

  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 내 메시지는 오른쪽에서 진입 */
.mine .message-bubble-wrap {
  animation: msg-mine-in 0.28s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes msg-mine-in {
  from {
    opacity: 0;
    transform: translateX(12px) scale(0.97);
  }

  to {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
}

/* 빈 채팅 상태 진입 */
.empty-chat-state {
  animation: empty-in 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes empty-in {
  from {
    opacity: 0;
    transform: translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 아트 링 회전 */
.art-ring.outer {
  animation: spin-slow 12s linear infinite;
}

.art-ring.inner {
  animation: spin-slow 8s linear infinite reverse;
}

@keyframes spin-slow {
  to {
    transform: rotate(360deg);
  }
}

/* 아이콘 버튼 hover scale */
.icon-btn-ghost {
  transition: background 0.15s, color 0.15s, transform 0.15s;
}

.icon-btn-ghost:hover {
  transform: scale(1.08);
}

.icon-btn-ghost:active {
  transform: scale(0.95);
}

/* room-item hover 개선 */
.room-item {
  transition: background 0.15s, transform 0.15s;
}

.room-item:hover {
  transform: translateX(2px);
}

.room-item:active {
  transform: translateX(2px) scale(0.98);
}

/* 전송 버튼 전환 */
.send-btn {
  transition: background 0.2s, color 0.2s, transform 0.15s, box-shadow 0.2s;
}

.send-btn.active {
  box-shadow: 0 4px 14px rgba(58, 38, 22, 0.25);
}

.send-btn.active:hover {
  box-shadow: 0 6px 20px rgba(58, 38, 22, 0.3);
}

/* unread-badge 펄스 */
.unread-badge {
  animation: badge-pulse 2.4s ease-in-out infinite;
}

@keyframes badge-pulse {

  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }

  50% {
    opacity: 0.8;
    transform: scale(0.9);
  }
}

/* 헤더 avatar 진입 */
.header-avatar {
  animation: avatar-pop 0.35s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}

@keyframes avatar-pop {
  from {
    opacity: 0;
    transform: scale(0.6);
  }

  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* 로더 스피너 */
.loader-spinner {
  animation: spin 0.7s linear infinite;
}

/* 온라인 dot 펄스 */
.status-dot.online {
  animation: online-pulse 2s ease-in-out infinite;
}

@keyframes online-pulse {

  0%,
  100% {
    box-shadow: 0 0 0 0 rgba(61, 186, 110, 0.4);
  }

  50% {
    box-shadow: 0 0 0 5px rgba(61, 186, 110, 0);
  }
}

/* primary-cta 화살표 이동 */
.primary-cta svg {
  transition: transform 0.2s cubic-bezier(0.22, 1, 0.36, 1);
}

.primary-cta:hover svg {
  transform: translateX(4px);
}

/* 날짜 구분선 fade */
.date-divider {
  animation: fade-in 0.3s ease both;
}

@keyframes fade-in {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}


/* ── 반응형 ── */
@media (max-width: 768px) {
  .chat-page-container {
    padding: 0;
    margin: 0;
    height: calc(100vh - 60px);
  }

  .chat-shell {
    border-radius: 0;
    border: none;
  }

  .mobile-hidden {
    display: none !important;
  }

  .rooms-sidebar {
    width: 100%;
  }

  .messages-area {
    padding: 20px 16px 8px;
  }

  .chat-input-area {
    padding: 12px 16px 20px;
  }

  .message-bubble-wrap {
    max-width: 85%;
  }
}
</style>
