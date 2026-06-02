<template>
  <div class="create-container">
    <div class="create-card">
      <div class="create-header">
        <button class="back-btn" @click="$router.back()">← 돌아가기</button>
        <h1 class="create-title">✏️ 커뮤니티 글쓰기</h1>
      </div>

      <form @submit.prevent="submitPost" class="create-form">
        <!-- 카테고리 선택 -->
        <div class="form-group">
          <label class="form-label">카테고리 선택 <span class="required">*</span></label>
          <div class="category-select-grid">
            <button
              v-for="cat in categories"
              :key="cat.value"
              type="button"
              class="cat-btn"
              :class="{ active: form.category === cat.value }"
              @click="form.category = cat.value"
            >
              <span class="cat-btn-icon">{{ cat.icon }}</span>
              <span class="cat-btn-label">{{ cat.label }}</span>
            </button>
          </div>
        </div>

        <!-- 제목 -->
        <div class="form-group">
          <label class="form-label">제목 <span class="required">*</span></label>
          <input
            v-model="form.title"
            type="text"
            placeholder="제목을 입력해주세요."
            class="form-input"
            maxlength="100"
            required
          />
        </div>

        <!-- 내용 -->
        <div class="form-group">
          <label class="form-label">내용</label>
          <textarea
            v-model="form.content"
            placeholder="내용을 입력해주세요."
            class="form-textarea"
            rows="12"
          ></textarea>
        </div>

        <!-- 익명 여부 -->
        <div class="form-group anonymous-row">
          <label class="toggle-label">
            <input type="checkbox" v-model="form.is_anonymous" class="toggle-checkbox" />
            <span class="toggle-track">
              <span class="toggle-thumb"></span>
            </span>
            <span class="toggle-text">익명으로 작성</span>
          </label>
        </div>

        <!-- 에러 메시지 -->
        <p v-if="error" class="error-msg">{{ error }}</p>

        <!-- 버튼 -->
        <div class="form-actions">
          <button type="button" class="cancel-btn" @click="$router.back()">취소</button>
          <button type="submit" class="submit-btn" :disabled="submitting || !form.category || !form.title.trim()">
            {{ submitting ? '등록 중...' : '글 등록' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      form: {
        title: '',
        content: '',
        category: '',
        is_anonymous: false,
      },
      submitting: false,
      error: '',

      categories: [
        { value: 'job',     label: '직무 토크',    icon: '💻' },
        { value: 'career',  label: '커리어 토크',  icon: '🚀' },
        { value: 'project', label: '프로젝트 공유', icon: '🤝' },
      ],
    };
  },

  methods: {
    async submitPost() {
      if (!this.form.category) {
        this.error = '카테고리를 선택해주세요.';
        return;
      }
      if (!this.form.title.trim()) {
        this.error = '제목을 입력해주세요.';
        return;
      }

      this.submitting = true;
      this.error = '';

      const token = localStorage.getItem('access_token');
      if (!token) {
        this.$router.push('/login');
        return;
      }

      try {
        const res = await axios.post(
          'http://localhost:8000/community/',
          {
            title: this.form.title.trim(),
            content: this.form.content.trim() || null,
            category: this.form.category,
            is_anonymous: this.form.is_anonymous,
          },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        this.$router.push(`/community/${res.data.id}`);
      } catch (e) {
        this.error = e.response?.data?.detail || '글 등록에 실패했습니다.';
      } finally {
        this.submitting = false;
      }
    },
  },
};
</script>

<style scoped>
.create-container {
  max-width: 760px;
  margin: 0 auto;
  padding: 60px 20px 100px;
}

.create-card {
  background: white;
  border-radius: 28px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.04);
  padding: 48px;
}

.create-header {
  margin-bottom: 36px;
}
.back-btn {
  background: none;
  border: none;
  color: #a68b6a;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  margin-bottom: 16px;
  transition: color 0.2s;
}
.back-btn:hover { color: #5d4037; }
.create-title {
  font-size: 26px;
  font-weight: 800;
  color: #1a1a1a;
}

.create-form { display: flex; flex-direction: column; gap: 28px; }

.form-group { display: flex; flex-direction: column; gap: 10px; }
.form-label {
  font-size: 14px;
  font-weight: 700;
  color: #444;
}
.required { color: #e53935; }

/* 카테고리 선택 */
.category-select-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.cat-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 18px 12px;
  background: #fdfaf7;
  border: 2px solid #f0ede9;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}
.cat-btn:hover {
  border-color: #c8a882;
  transform: translateY(-2px);
}
.cat-btn.active {
  border-color: #5d4037;
  background: #f8f3ef;
}
.cat-btn-icon { font-size: 22px; }
.cat-btn-label {
  font-size: 13px;
  font-weight: 700;
  color: #444;
  text-align: center;
}

.form-input {
  width: 100%;
  box-sizing: border-box;
  padding: 14px 16px;
  border: 1.5px solid #e8e3de;
  border-radius: 12px;
  font-size: 15px;
  font-family: inherit;
  outline: none;
  transition: border-color 0.2s;
  background: #fdfcfb;
}
.form-input:focus { border-color: #5d4037; }

.form-textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 14px 16px;
  border: 1.5px solid #e8e3de;
  border-radius: 12px;
  font-size: 15px;
  font-family: inherit;
  outline: none;
  resize: vertical;
  line-height: 1.7;
  background: #fdfcfb;
  transition: border-color 0.2s;
}
.form-textarea:focus { border-color: #5d4037; }

/* 익명 토글 */
.anonymous-row { flex-direction: row; align-items: center; }
.toggle-label {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}
.toggle-checkbox { display: none; }
.toggle-track {
  width: 42px;
  height: 24px;
  background: #ddd;
  border-radius: 12px;
  position: relative;
  transition: background 0.2s;
}
.toggle-checkbox:checked + .toggle-track { background: #5d4037; }
.toggle-thumb {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 18px;
  height: 18px;
  background: white;
  border-radius: 50%;
  transition: left 0.2s;
  box-shadow: 0 1px 4px rgba(0,0,0,0.2);
}
.toggle-checkbox:checked + .toggle-track .toggle-thumb { left: 21px; }
.toggle-text {
  font-size: 14px;
  font-weight: 600;
  color: #666;
}

.error-msg {
  font-size: 14px;
  color: #e53935;
  background: #ffebee;
  padding: 10px 14px;
  border-radius: 8px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}
.cancel-btn {
  padding: 14px 28px;
  background: #f8f6f3;
  color: #888;
  border: 1px solid #e0d8d0;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}
.cancel-btn:hover { background: #eee; }
.submit-btn {
  padding: 14px 36px;
  background: #5d4037;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}
.submit-btn:hover:not(:disabled) { background: #3e2723; }
.submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
