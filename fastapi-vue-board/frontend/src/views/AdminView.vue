<template>
  <div class="admin-container">
    <header class="admin-header">
      <p class="eyebrow">ADMIN DASHBOARD</p>
      <h1>관리자 대시보드</h1>
      <p class="sub">플랫폼을 관리하세요.</p>
    </header>

    <!-- 탭 메뉴 -->
    <div class="tab-bar">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        :class="['tab-btn', { active: activeTab === tab.key }]"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
        <span v-if="tab.key === 'reports' && pendingReportsCount > 0" class="badge">
          {{ pendingReportsCount }}
        </span>
      </button>
    </div>

    <!-- ① 유저 승격 탭 -->
    <section v-if="activeTab === 'promote'" class="tab-content card">
      <h2>일반 유저 → 관리자 승격</h2>
      <p class="desc">승격할 유저의 이메일과 관리자 코드를 입력하세요.</p>

      <div class="form-row">
        <div class="field-group">
          <label>승격할 유저 이메일</label>
          <input v-model="promote.email" type="email" placeholder="user@example.com" />
        </div>
        <div class="field-group">
          <label>관리자 코드</label>
          <input v-model="promote.secret" type="password" placeholder="ADMIN_SECRET" />
        </div>
        <button class="action-btn primary" @click="handlePromote" :disabled="promote.loading">
          {{ promote.loading ? '처리 중...' : '승격하기' }}
        </button>
      </div>
      <p v-if="promote.message" :class="['result-msg', promote.isError ? 'error' : 'success']">
        {{ promote.message }}
      </p>
    </section>

    <!-- ② 유저 목록 탭 -->
    <section v-if="activeTab === 'users'" class="tab-content card">
      <div class="section-header">
        <h2>유저 목록</h2>
        <button class="refresh-btn" @click="fetchUsers">새로고침</button>
      </div>

      <div v-if="users.length === 0" class="empty-state">유저가 없습니다.</div>

      <table v-else class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>이메일</th>
            <th>사용자명</th>
            <th>역할</th>
            <th>상태</th>
            <th>가입일</th>
            <th>액션</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id">
            <td>{{ u.id }}</td>
            <td>{{ u.email }}</td>
            <td>{{ u.username }}</td>
            <td>
              <span :class="['role-badge', u.role === 'admin' ? 'admin' : 'user']">
                {{ u.role === 'admin' ? '관리자' : '일반' }}
              </span>
            </td>
            <td>
              <span :class="['status-badge', u.is_suspended ? 'suspended' : 'active']">
                {{ u.is_suspended ? '정지됨' : '활성' }}
              </span>
            </td>
            <td>{{ formatDate(u.created_at) }}</td>
            <td>
              <button
                v-if="u.role !== 'admin'"
                :class="['small-btn', u.is_suspended ? 'unsuspend' : 'suspend']"
                @click="toggleSuspend(u)"
              >
                {{ u.is_suspended ? '정지 해제' : '정지' }}
              </button>
              <span v-else class="no-action">-</span>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <!-- ③ 신고 처리 탭 -->
    <section v-if="activeTab === 'reports'" class="tab-content card">
      <div class="section-header">
        <h2>신고 목록</h2>
        <div class="filter-row">
          <button
            :class="['filter-btn', !showResolved ? 'active' : '']"
            @click="showResolved = false; fetchReports()"
          >미처리</button>
          <button
            :class="['filter-btn', showResolved ? 'active' : '']"
            @click="showResolved = true; fetchReports()"
          >처리완료</button>
          <button class="refresh-btn" @click="fetchReports">새로고침</button>
        </div>
      </div>

      <div v-if="reports.length === 0" class="empty-state">
        {{ showResolved ? '처리된 신고가 없습니다.' : '처리할 신고가 없습니다. 👍' }}
      </div>

      <div v-else class="report-list">
        <div v-for="report in reports" :key="report.id" class="report-card">
          <div class="report-info">
            <div class="report-meta">
              <span class="report-id">#{{ report.id }}</span>
              <span class="report-date">{{ formatDate(report.created_at) }}</span>
            </div>
            <p class="report-reason">
              <strong>신고 사유:</strong> {{ report.reason }}
            </p>
            <p class="report-detail">
              게시글 ID: <strong>{{ report.post_id }}</strong> &nbsp;|&nbsp;
              신고자 ID: <strong>{{ report.reporter_id }}</strong>
            </p>
          </div>
          <div v-if="!report.is_resolved" class="report-actions">
            <button class="action-btn warn" @click="resolveReport(report.id)">
              신고만 처리
            </button>
            <button class="action-btn danger" @click="resolveAndDelete(report.id)">
              게시글 삭제 + 처리
            </button>
          </div>
          <div v-else class="resolved-badge">✅ 처리완료</div>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api/axios'

const activeTab = ref('promote')
const tabs = [
  { key: 'promote', label: '유저 승격' },
  { key: 'users',   label: '유저 목록' },
  { key: 'reports', label: '신고 처리' },
]

// ── 유저 승격
const promote = ref({ email: '', secret: '', loading: false, message: '', isError: false })

async function handlePromote() {
  if (!promote.value.email || !promote.value.secret) {
    promote.value.message = '이메일과 관리자 코드를 모두 입력해주세요.'
    promote.value.isError = true
    return
  }
  promote.value.loading = true
  promote.value.message = ''
  try {
    const res = await api.patch(
      `/auth/promote/admin?email=${encodeURIComponent(promote.value.email)}&admin_secret=${encodeURIComponent(promote.value.secret)}`
    )
    promote.value.message = res.data.message || '승격 완료!'
    promote.value.isError = false
    promote.value.email = ''
    promote.value.secret = ''
  } catch (e) {
    promote.value.message = e.response?.data?.detail || '승격에 실패했습니다.'
    promote.value.isError = true
  } finally {
    promote.value.loading = false
  }
}

// ── 유저 목록
const users = ref([])

async function fetchUsers() {
  try {
    const { data } = await api.get('/admin/users?limit=100')
    users.value = data
  } catch (e) {
    console.error('유저 목록 로드 실패', e)
  }
}

async function toggleSuspend(u) {
  const action = u.is_suspended ? 'unsuspend' : 'suspend'
  const confirmMsg = u.is_suspended
    ? `${u.username} 계정 정지를 해제할까요?`
    : `${u.username} 계정을 정지할까요?`
  if (!confirm(confirmMsg)) return
  try {
    await api.patch(`/admin/users/${u.id}/${action}`)
    u.is_suspended = !u.is_suspended
  } catch (e) {
    alert(e.response?.data?.detail || '처리에 실패했습니다.')
  }
}

// ── 신고 처리
const reports = ref([])
const showResolved = ref(false)
const pendingReportsCount = computed(() => reports.value.filter(r => !r.is_resolved).length)

async function fetchReports() {
  try {
    const { data } = await api.get(`/admin/reports?is_resolved=${showResolved.value}&limit=50`)
    reports.value = data
  } catch (e) {
    console.error('신고 목록 로드 실패', e)
  }
}

async function resolveReport(reportId) {
  if (!confirm('신고를 처리하시겠습니까? (게시글은 삭제되지 않습니다)')) return
  try {
    await api.patch(`/admin/reports/${reportId}/resolve`)
    reports.value = reports.value.filter(r => r.id !== reportId)
    alert('신고가 처리되었습니다.')
  } catch (e) {
    alert(e.response?.data?.detail || '처리에 실패했습니다.')
  }
}

async function resolveAndDelete(reportId) {
  if (!confirm('게시글을 삭제하고 신고를 처리하시겠습니까?\n이 작업은 되돌릴 수 없습니다.')) return
  try {
    await api.delete(`/admin/reports/${reportId}/resolve-and-delete`)
    reports.value = reports.value.filter(r => r.id !== reportId)
    alert('게시글이 삭제되고 신고가 처리되었습니다.')
  } catch (e) {
    alert(e.response?.data?.detail || '처리에 실패했습니다.')
  }
}

// 날짜 포맷
function formatDate(str) {
  if (!str) return '-'
  return new Date(str).toLocaleDateString('ko-KR')
}

onMounted(() => {
  fetchUsers()
  fetchReports()
})
</script>

<style scoped>
.admin-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 60px 30px;
  font-family: 'Pretendard', sans-serif;
}

.admin-header {
  margin-bottom: 40px;
}

.eyebrow {
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 3px;
  color: #a68b6a;
  margin-bottom: 8px;
}

.admin-header h1 {
  font-size: 34px;
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 6px;
}

.admin-header .sub {
  color: #888;
  font-size: 15px;
}

/* 탭 */
.tab-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  border-bottom: 2px solid #f0ede9;
  padding-bottom: 0;
}

.tab-btn {
  padding: 12px 24px;
  border: none;
  background: none;
  font-size: 15px;
  font-weight: 600;
  color: #aaa;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  margin-bottom: -2px;
  transition: all 0.2s;
  position: relative;
}

.tab-btn.active {
  color: #5d4037;
  border-bottom-color: #5d4037;
}

.badge {
  background: #e53935;
  color: white;
  font-size: 11px;
  font-weight: 800;
  padding: 2px 7px;
  border-radius: 20px;
  margin-left: 6px;
}

/* 탭 콘텐츠 */
.tab-content {
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.04);
}

.tab-content h2 {
  font-size: 20px;
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 8px;
}

.desc {
  color: #888;
  font-size: 14px;
  margin-bottom: 24px;
}

/* 유저 승격 폼 */
.form-row {
  display: flex;
  gap: 16px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
  min-width: 200px;
}

.field-group label {
  font-size: 13px;
  font-weight: 700;
  color: #555;
}

.field-group input {
  padding: 12px 16px;
  border: 1.5px solid #e0d8d0;
  border-radius: 12px;
  font-size: 15px;
  outline: none;
  background: #fdfaf7;
  transition: border-color 0.2s;
}

.field-group input:focus {
  border-color: #5d4037;
}

.result-msg {
  margin-top: 16px;
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
}

.result-msg.success {
  background: #e8f5e9;
  color: #2e7d32;
}

.result-msg.error {
  background: #ffebee;
  color: #c62828;
}

/* 버튼들 */
.action-btn {
  padding: 12px 22px;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.action-btn.primary {
  background: #5d4037;
  color: white;
}

.action-btn.primary:hover:not(:disabled) {
  background: #3e2723;
}

.action-btn.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.action-btn.warn {
  background: #fff3e0;
  color: #e65100;
  border: 1px solid #ffcc80;
}

.action-btn.warn:hover {
  background: #ffe0b2;
}

.action-btn.danger {
  background: #ffebee;
  color: #c62828;
  border: 1px solid #ef9a9a;
}

.action-btn.danger:hover {
  background: #ffcdd2;
}

/* 섹션 헤더 */
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}

.filter-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.filter-btn {
  padding: 8px 16px;
  border: 1.5px solid #e0d8d0;
  border-radius: 20px;
  background: white;
  font-size: 13px;
  font-weight: 600;
  color: #888;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn.active {
  background: #5d4037;
  color: white;
  border-color: #5d4037;
}

.refresh-btn {
  padding: 8px 16px;
  border: 1.5px solid #e0d8d0;
  border-radius: 20px;
  background: white;
  font-size: 13px;
  font-weight: 600;
  color: #5d4037;
  cursor: pointer;
}

.refresh-btn:hover {
  background: #f0ede9;
}

/* 테이블 */
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.data-table th {
  text-align: left;
  padding: 12px 16px;
  background: #fdfaf7;
  color: #888;
  font-weight: 700;
  font-size: 12px;
  letter-spacing: 0.5px;
  border-bottom: 1px solid #f0ede9;
}

.data-table td {
  padding: 14px 16px;
  border-bottom: 1px solid #f8f6f3;
  color: #333;
}

.data-table tr:hover td {
  background: #fdfaf7;
}

.role-badge {
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
}

.role-badge.admin {
  background: #fff3e0;
  color: #e65100;
}

.role-badge.user {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-badge {
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
}

.status-badge.active {
  background: #e3f2fd;
  color: #1565c0;
}

.status-badge.suspended {
  background: #ffebee;
  color: #c62828;
}

.small-btn {
  padding: 6px 14px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}

.small-btn.suspend {
  background: #ffebee;
  color: #c62828;
}

.small-btn.unsuspend {
  background: #e8f5e9;
  color: #2e7d32;
}

.no-action {
  color: #ccc;
  font-size: 13px;
}

/* 신고 목록 */
.report-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.report-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 20px 24px;
  background: #fdfaf7;
  border: 1px solid #f0ede9;
  border-radius: 16px;
  flex-wrap: wrap;
}

.report-info {
  flex: 1;
}

.report-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 8px;
}

.report-id {
  font-size: 12px;
  font-weight: 800;
  color: #a68b6a;
  background: #f0ede9;
  padding: 2px 8px;
  border-radius: 6px;
}

.report-date {
  font-size: 12px;
  color: #aaa;
}

.report-reason {
  font-size: 15px;
  color: #333;
  margin-bottom: 6px;
}

.report-detail {
  font-size: 13px;
  color: #888;
}

.report-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.resolved-badge {
  font-size: 14px;
  font-weight: 700;
  color: #2e7d32;
  white-space: nowrap;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #aaa;
  font-size: 16px;
}
</style>