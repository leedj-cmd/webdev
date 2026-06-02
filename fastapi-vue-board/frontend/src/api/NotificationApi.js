// src/api/notificationApi.js
import api from '@/api/axios'  // 공통 인스턴스 사용

const BASE = '/notifications'

export const notificationApi = {
  getAll:       () => api.get(BASE + '/'),
  markAllAsRead: () => api.patch(BASE + '/read-all'),
  markAsRead:   (id) => api.patch(`${BASE}/${id}/read`),
}
