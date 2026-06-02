<template>
  <div class="form-container">
    <header class="form-header">
      <button class="back-btn" @click="$router.back()">← 뒤로</button>
      <p class="eyebrow">ADMIN</p>
      <h1>{{ isEditMode ? '공모전 수정' : '공모전 등록' }}</h1>
    </header>

    <div class="form-card card">
      <form @submit.prevent="handleSubmit">

        <div class="field-row">
          <div class="field-group">
            <label>공모전 제목 <span class="required">*</span></label>
            <input v-model="form.title" type="text" placeholder="예: 2026 AI 챌린지" />
          </div>
          <div class="field-group">
            <label>주최 기관 <span class="required">*</span></label>
            <input v-model="form.organizer" type="text" placeholder="예: 과학기술정보통신부" />
          </div>
        </div>

        <div class="field-group">
          <label>공모전 설명 <span class="required">*</span></label>
          <textarea v-model="form.description" rows="6" placeholder="공모전 내용을 상세히 작성해주세요."></textarea>
        </div>

        <div class="field-row">
          <div class="field-group">
            <label>분야 (카테고리)</label>
            <select v-model="form.category">
              <option value="">선택 안함</option>
              <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>
          <div class="field-group">
            <label>참가 대상</label>
            <select v-model="form.target">
              <option value="">선택 안함</option>
              <option v-for="t in targets" :key="t" :value="t">{{ t }}</option>
            </select>
          </div>
        </div>

        <div class="field-row">
          <div class="field-group">
            <label>시상금 / 혜택</label>
            <input v-model="form.prize" type="text" placeholder="예: 총 5,000만원" />
          </div>
          <div class="field-group">
            <label>접수 시작일</label>
            <input v-model="form.start_date" type="datetime-local" />
          </div>
          <div class="field-group">
            <label>마감일</label>
            <input v-model="form.deadline" type="datetime-local" />
          </div>
        </div>

        <div class="field-group">
          <label>외부 링크 (공모전 URL)</label>
          <input v-model="form.external_url" type="url" placeholder="https://..." />
        </div>

        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
        <p v-if="successMsg" class="success-msg">{{ successMsg }}</p>

        <div class="btn-row">
          <button type="button" class="cancel-btn" @click="$router.back()">취소</button>
          <button type="submit" class="submit-btn" :disabled="loading">
            {{ loading ? '처리 중...' : (isEditMode ? '수정 완료' : '등록하기') }}
          </button>
        </div>

      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api/axios'

const route = useRoute()
const router = useRouter()

const isEditMode = computed(() => !!route.params.id)

const form = ref({
  title: '',
  organizer: '',
  description: '',
  category: '',
  target: '',
  prize: '',
  start_date: '',
  deadline: '',
  external_url: '',
})

const loading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

const categories = ['기획', '아이디어', '디자인', '개발/SW', '논문/학술', '마케팅', '기타']
const targets = ['전국민', '대학(원)생', '고등학생', '일반인/학생', '직장인', '기타']

onMounted(async () => {
  if (isEditMode.value) {
    try {
      const { data } = await api.get(`/contests/${route.params.id}`)
      form.value = {
        title: data.title || '',
        organizer: data.organizer || '',
        description: data.description || '',
        category: data.category || '',
        target: data.target || '',
        prize: data.prize || '',
        start_date: data.start_date ? data.start_date.slice(0, 16) : '',
        deadline: data.deadline ? data.deadline.slice(0, 16) : '',
        external_url: data.external_url || '',
      }
    } catch (e) {
      errorMsg.value = '공모전 정보를 불러오지 못했습니다.'
    }
  }
})

async function handleSubmit() {
  errorMsg.value = ''
  successMsg.value = ''

  if (!form.value.title || !form.value.organizer || !form.value.description) {
    errorMsg.value = '제목, 주최 기관, 공모전 설명은 필수입니다.'
    return
  }

  loading.value = true

  const payload = {
    ...form.value,
    start_date: form.value.start_date ? new Date(form.value.start_date).toISOString() : null,
    deadline: form.value.deadline ? new Date(form.value.deadline).toISOString() : null,
    category: form.value.category || null,
    target: form.value.target || null,
    prize: form.value.prize || null,
    external_url: form.value.external_url || null,
  }

  try {
    if (isEditMode.value) {
      await api.patch(`/contests/${route.params.id}`, payload)
      successMsg.value = '공모전이 수정되었습니다!'
    } else {
      await api.post('/contests/', payload)
      successMsg.value = '공모전이 등록되었습니다!'
    }
    setTimeout(() => router.push('/contests'), 1200)
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || '처리에 실패했습니다.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.form-container {
  max-width: 860px;
  margin: 0 auto;
  padding: 60px 30px;
  font-family: 'Pretendard', sans-serif;
}

.form-header { margin-bottom: 36px; }

.back-btn {
  background: none;
  border: none;
  font-size: 14px;
  color: #a68b6a;
  font-weight: 700;
  cursor: pointer;
  padding: 0;
  margin-bottom: 16px;
}

.back-btn:hover { color: #5d4037; }

.eyebrow {
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 3px;
  color: #a68b6a;
  margin-bottom: 8px;
}

.form-header h1 {
  font-size: 30px;
  font-weight: 800;
  color: #1a1a1a;
}

.form-card {
  background: white;
  border-radius: 24px;
  padding: 48px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.04);
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
  flex: 1;
}

.field-row {
  display: flex;
  gap: 20px;
}

label {
  font-size: 14px;
  font-weight: 700;
  color: #444;
}

.required { color: #e53935; }

input, textarea, select {
  padding: 13px 16px;
  border: 1.5px solid #e0d8d0;
  border-radius: 12px;
  font-size: 15px;
  font-family: inherit;
  outline: none;
  background: #fdfaf7;
  transition: border-color 0.2s;
  width: 100%;
  box-sizing: border-box;
}

input:focus, textarea:focus, select:focus {
  border-color: #5d4037;
}

textarea { resize: vertical; }

.error-msg {
  background: #ffebee;
  color: #c62828;
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 14px;
  margin-bottom: 16px;
}

.success-msg {
  background: #e8f5e9;
  color: #2e7d32;
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 14px;
  margin-bottom: 16px;
}

.btn-row {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 8px;
}

.cancel-btn {
  padding: 14px 28px;
  border: 1.5px solid #e0d8d0;
  border-radius: 14px;
  background: white;
  font-size: 15px;
  font-weight: 700;
  color: #888;
  cursor: pointer;
}

.cancel-btn:hover { background: #f8f6f3; }

.submit-btn {
  padding: 14px 36px;
  background: #5d4037;
  color: white;
  border: none;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s;
}

.submit-btn:hover:not(:disabled) { background: #3e2723; }

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>