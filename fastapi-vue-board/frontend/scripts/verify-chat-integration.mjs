import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const scriptDir = dirname(fileURLToPath(import.meta.url))
const srcDir = resolve(scriptDir, '..', 'src')

const files = {
  communityDetail: readFileSync(resolve(srcDir, 'views', 'CommunityDetailView.vue'), 'utf8'),
  chatView: readFileSync(resolve(srcDir, 'views', 'ChatView.vue'), 'utf8'),
  router: readFileSync(resolve(srcDir, 'router', 'index.js'), 'utf8'),
  notificationStore: readFileSync(resolve(srcDir, 'stores', 'NotificationStore.js'), 'utf8'),
  notificationApi: readFileSync(resolve(srcDir, 'api', 'NotificationApi.js'), 'utf8'),
  navbar: readFileSync(resolve(srcDir, 'components', 'Navbar.vue'), 'utf8'),
}

function assertContains(source, pattern, description) {
  const matched = pattern instanceof RegExp ? pattern.test(source) : source.includes(pattern)
  if (!matched) {
    throw new Error(description)
  }
}

assertContains(
  files.communityDetail,
  /v-if="[^"]*!post\.is_anonymous[^"]*post\.owner_id[^"]*post\.owner_id !== currentUserId[^"]*"/,
  'Community detail must show the chat button only for non-anonymous posts by another user.',
)

assertContains(
  files.communityDetail,
  /api\.post\(['"]\/chat\/rooms['"]/,
  'Community detail must create or reuse a direct chat room through /chat/rooms.',
)

assertContains(
  files.communityDetail,
  /this\.\$router\.push\(\{\s*path:\s*['"]\/chat['"],\s*query:\s*\{\s*room:/s,
  'Community detail must navigate to /chat with the selected room id.',
)

assertContains(
  files.router,
  /path:\s*['"]\/chat\/:roomId['"]/,
  'Router must support direct navigation to /chat/:roomId from notifications.',
)

assertContains(
  files.chatView,
  /useRoute/,
  'ChatView must read route state to select a room from the URL.',
)

assertContains(
  files.chatView,
  /route\.query\.room|route\.params\.roomId/,
  'ChatView must support a room id from either query string or route params.',
)

assertContains(
  files.chatView,
  /selectRoom\(initialRoomId\)/,
  'ChatView must select the initial room after rooms are loaded.',
)

assertContains(
  files.chatView,
  /@keydown\.enter="handleMessageKeydown"/,
  'ChatView must route Enter through a keydown handler instead of sending directly.',
)

assertContains(
  files.chatView,
  /@compositionstart="isComposingMessage = true"/,
  'ChatView must track IME composition start for Korean input.',
)

assertContains(
  files.chatView,
  /@compositionend="isComposingMessage = false"/,
  'ChatView must track IME composition end for Korean input.',
)

assertContains(
  files.chatView,
  /event\.isComposing[\s\S]*isComposingMessage\.value[\s\S]*event\.keyCode === 229/,
  'ChatView Enter handler must ignore IME composition events.',
)

assertContains(
  files.chatView,
  /type="file"/,
  'ChatView must include a hidden file input for attachments.',
)

assertContains(
  files.chatView,
  /@click="openAttachmentPicker"/,
  'ChatView attach button must open the attachment file picker.',
)

assertContains(
  files.chatView,
  /\/chat\/rooms\/\$\{activeRoomId\.value\}\/attachments/,
  'ChatView must upload selected attachments to the chat attachment API.',
)

assertContains(
  files.chatView,
  /msg\.message_type === 'image'/,
  'ChatView must render image attachment messages differently from plain text.',
)

assertContains(
  files.chatView,
  /msg\.message_type === 'file'/,
  'ChatView must render generic file attachment messages differently from plain text.',
)

assertContains(
  files.chatView,
  /onlineUserIds = ref\(\[\]\)/,
  'ChatView must keep online user ids in reactive state.',
)

assertContains(
  files.chatView,
  /data\.event === 'presence'/,
  'ChatView must handle presence websocket events separately from chat messages.',
)

assertContains(
  files.chatView,
  /onlineUserIds\.value = data\.online_user_ids/,
  'ChatView must update online user ids from presence events.',
)

assertContains(
  files.chatView,
  /onlineUserIds\.value\.includes\(otherMember\?\.user_id\)/,
  'ChatView must mark the other direct-chat member as online when their id is present.',
)

assertContains(
  files.notificationApi,
  /import api from '@\/api\/axios'/,
  'Notification API must use the shared axios instance so backend baseURL and auth headers apply.',
)

assertContains(
  files.notificationStore,
  /const popupNotifications = ref\(\[\]\)/,
  'NotificationStore must keep popup notifications in reactive state.',
)

assertContains(
  files.notificationStore,
  /let _connectedToken = null/,
  'NotificationStore must track which account token owns the websocket connection.',
)

assertContains(
  files.notificationStore,
  /if \(_ws && _connectedToken === token\) return/,
  'NotificationStore must reuse only websocket connections for the same token.',
)

assertContains(
  files.notificationStore,
  /if \(_ws && _connectedToken !== token\) disconnectWs\(\)/,
  'NotificationStore must reconnect when the account token changes.',
)

assertContains(
  files.notificationStore,
  /notifications\.value = \[\]/,
  'NotificationStore must clear stale notifications when disconnecting or switching accounts.',
)

assertContains(
  files.notificationStore,
  /const url = `\$\{protocol\}:\/\/127\.0\.0\.1:8000\/notifications\/ws\?token=\$\{token\}`/,
  'NotificationStore WebSocket must connect to the backend notification endpoint.',
)

assertContains(
  files.notificationStore,
  /if \(notif\.type === 'chat'\) showPopup\(notif\)/,
  'NotificationStore must create popup notifications for chat notifications.',
)

assertContains(
  files.notificationStore,
  /function dismissPopup/,
  'NotificationStore must expose a way to dismiss popup notifications.',
)

assertContains(
  files.navbar,
  /watch\(\s*\(\) => authStore\.token/,
  'Navbar must watch auth token changes so notification websocket follows account switches.',
)

assertContains(
  files.navbar,
  /notifStore\.fetchNotifications\(\)/,
  'Navbar must fetch notifications when opening the notification panel.',
)

assertContains(
  files.navbar,
  /popupNotifications/,
  'Navbar must render notification popup toasts.',
)

assertContains(
  files.navbar,
  /openPopupNotification/,
  'Navbar popup toast must navigate to the notification target when clicked.',
)

console.log('Chat integration checks passed.')
