// src/stores/notificationStore.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { notificationApi } from '@/api/NotificationApi'

export const useNotificationStore = defineStore('notification', () => {
    // ── state
    const notifications = ref([])   // 알림 목록 (백엔드 반환 shape 그대로)
    const popupNotifications = ref([])
    const loading = ref(false)
    const wsConnected = ref(false)
    let _ws = null       // WebSocket 인스턴스 (내부용)
    let _connectedToken = null

    // ── getters
    const unreadCount = computed(() => notifications.value.filter((n) => !n.is_read).length)
    const hasUnread = computed(() => unreadCount.value > 0)

    // ── REST: 알림 목록 불러오기
    async function fetchNotifications() {
        loading.value = true
        try {
            const { data } = await notificationApi.getAll()
            notifications.value = data          // [{ id, actor_name, type, message, related_type, related_id, is_read, created_at }]
        } catch (e) {
            console.error('[notification] fetch error', e)
        } finally {
            loading.value = false
        }
    }

    // ── REST: 단일 읽음 처리
    async function markAsRead(id) {
        try {
            await notificationApi.markAsRead(id)
            const t = notifications.value.find((n) => n.id === id)
            if (t) t.is_read = true
        } catch (e) {
            console.error('[notification] markAsRead error', e)
        }
    }

    // ── REST: 전체 읽음 처리
    async function markAllAsRead() {
        try {
            await notificationApi.markAllAsRead()
            notifications.value.forEach((n) => (n.is_read = true))
        } catch (e) {
            console.error('[notification] markAllAsRead error', e)
        }
    }

    // ── WebSocket: 연결
    // token: localStorage 등에서 꺼낸 access token 문자열
    function connectWs(token) {
        if (!token) return
        if (_ws && _connectedToken === token) return
        if (_ws && _connectedToken !== token) disconnectWs()

        const protocol = location.protocol === 'https:' ? 'wss' : 'ws'
        const isProd = location.hostname !== 'localhost' && location.hostname !== '127.0.0.1'
        const wsHost = isProd ? location.host : '127.0.0.1:8000'
        const url = `${protocol}://${wsHost}/notifications/ws?token=${token}`

        _ws = new WebSocket(url)
        _connectedToken = token

        _ws.onopen = () => {
            wsConnected.value = true
            console.info('[notification ws] 연결됨')
        }

        _ws.onmessage = (event) => {
            try {
                const notif = JSON.parse(event.data)
                // 서버가 push한 알림을 목록 맨 앞에 추가
                notifications.value.unshift(notif)
                if (notif.type === 'chat') showPopup(notif)
            } catch {
                // ping/pong 텍스트 무시
            }
        }

        _ws.onclose = () => {
            wsConnected.value = false
            _ws = null
            _connectedToken = null
            console.info('[notification ws] 연결 종료')
        }

        _ws.onerror = (e) => {
            console.error('[notification ws] 오류', e)
        }
    }

    function showPopup(notification) {
        popupNotifications.value.unshift(notification)
        window.setTimeout(() => dismissPopup(notification.id), 5000)
    }

    function dismissPopup(id) {
        popupNotifications.value = popupNotifications.value.filter((n) => n.id !== id)
    }

    // ── WebSocket: 연결 해제 (로그아웃 시 호출)
    function disconnectWs() {
        _ws?.close()
        _ws = null
        _connectedToken = null
        wsConnected.value = false
        notifications.value = []
        popupNotifications.value = []
    }

    return {
        notifications,
        popupNotifications,
        loading,
        wsConnected,
        unreadCount,
        hasUnread,
        fetchNotifications,
        markAsRead,
        markAllAsRead,
        connectWs,
        disconnectWs,
        dismissPopup,
    }
})
