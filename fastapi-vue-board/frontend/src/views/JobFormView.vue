<template>
  <div class="form-container">
    <header class="form-header">
      <button class="back-btn" @click="$router.back()">← 뒤로</button>
      <p class="eyebrow">ADMIN</p>
      <h1>{{ isEditMode ? '채용공고 수정' : '채용공고 등록' }}</h1>
    </header>

    <div class="form-card card">
      <form @submit.prevent="handleSubmit">

        <div class="field-row">
          <div class="field-group">
            <label>공고 제목 <span class="required">*</span></label>
            <input v-model="form.title" type="text" placeholder="예: 백엔드 개발자 채용" />
          </div>
          <div class="field-group">
            <label>회사명 <span class="required">*</span></label>
            <input v-model="form.company" type="text" placeholder="예: 네이버" />
          </div>
        </div>

        <div class="field-group">
          <label>공고 설명 <span class="required">*</span></label>
          <textarea v-model="form.description" rows="6" placeholder="공고 내용을 상세히 작성해주세요."></textarea>
        </div>

        <div class="field-row">
          <div class="field-group">
            <label>직무 카테고리</label>
            <select v-model="form.job_category">
              <option value="">선택 안함</option>
              <option v-for="c in jobCategories" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>
          <div class="field-group">
            <label>지역</label>
            <select v-model="form.region">
              <option value="">선택 안함</option>
              <option v-for="r in regions" :key="r" :value="r">{{ r }}</option>
            </select>
          </div>
          <div class="field-group">
            <label>경력</label>
            <select v-model="form.experience">
              <option value="">선택 안함</option>
              <option v-for="e in experiences" :key="e" :value="e">{{ e }}</option>
            </select>
          </div>
        </div>

        <div class="field-row">
          <div class="field-group">
            <label>학력</label>
            <input v-model="form.education" type="text" placeholder="예: 학력 무관" />
          </div>
          <div class="field-group">
            <label>마감일</label>
            <input v-model="form.deadline" type="datetime-local" />
          </div>
        </div>

        <div class="field-group">
          <label>외부 링크 (채용 URL)</label>
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
  company: '',
  description: '',
  job_category: '',
  region: '',
  experience: '',
  education: '',
  deadline: '',
  external_url: '',
})

const loading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

const jobCategories = ['프론트엔드', '백엔드', '풀스택', '모바일', 'AI/ML', 'DevOps', '데이터', '보안', '기획', 'QA']
const regions = ['서울', '경기', '인천', '부산', '대구', '대전', '광주', '울산', '세종', '제주', '기타']
const experiences = ['신입', '1~3년', '3~5년', '5년↑', '경력 무관']

onMounted(async () => {
  if (isEditMode.value) {
    try {
      const { data } = await api.get(`/jobs/${route.params.id}`)
      form.value = {
        title: data.title || '',
        company: data.company || '',
        description: data.description || '',
        job_category: data.job_category || '',
        region: data.region || '',
        experience: data.experience || '',
        education: data.education || '',
        deadline: data.deadline ? data.deadline.slice(0, 16) : '',
        external_url: data.external_url || '',
      }
    } catch (e) {
      errorMsg.value = '공고 정보를 불러오지 못했습니다.'
    }
  }
})

async function handleSubmit() {
  errorMsg.value = ''
  successMsg.value = ''

  if (!form.value.title || !form.value.company || !form.value.description) {
    errorMsg.value = '제목, 회사명, 공고 설명은 필수입니다.'
    return
  }

  loading.value = true

  const payload = {
    ...form.value,
    deadline: form.value.deadline ? new Date(form.value.deadline).toISOString() : null,
    job_category: form.value.job_category || null,
    region: form.value.region || null,
    experience: form.value.experience || null,
    education: form.value.education || null,
    external_url: form.value.external_url || null,
  }

  try {
    if (isEditMode.value) {
      await api.patch(`/jobs/${route.params.id}`, payload)
      successMsg.value = '채용공고가 수정되었습니다!'
    } else {
      await api.post('/jobs/', payload)
      successMsg.value = '채용공고가 등록되었습니다!'
    }
    setTimeout(() => router.push('/jobs'), 1200)
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

.form-header {
  margin-bottom: 36px;
}

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

.required {
  color: #e53935;
}

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