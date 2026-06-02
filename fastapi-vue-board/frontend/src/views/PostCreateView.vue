<template>
  <div class="create-container">
    <header class="create-header reveal">
      <p class="subtitle">NEW POST</p>
      <h1 class="title">게시글을<br>작성하세요!</h1>
    </header>
    <div class="form-card card reveal" style="--index: 1">
      <div class="input-group">
        <label>제목</label>
        <input type="text" v-model="post.title" placeholder="제목을 입력하세요" class="styled-input">
      </div>

      <div class="input-row">
        <div class="input-group">
          <label>직무 분야</label>
          <div class="select-wrapper">
            <select v-model="post.job_category" class="styled-select">
              <option value="">분야 선택</option>
              <option value="백엔드">백엔드</option>
              <option value="프론트엔드">프론트엔드</option>
              <option value="기획">기획</option>
              <option value="디자인">디자인</option>
              <option value="개발">개발</option>
              <option value="질문">질문</option>
              <option value="정보">정보</option>
            </select>
          </div>
        </div>

        <div class="input-group">
          <label>지역 (대분류)</label>
          <div class="select-wrapper">
            <select v-model="selectedCity" @change="handleCityChange" class="styled-select">
              <option value="">지역 선택</option>
              <option v-for="(districts, city) in locationOptions" :key="city" :value="city">
                {{ city }}
              </option>
            </select>
          </div>

        </div>

        <div class="input-group">
          <label>지역 (소분류)</label>
          <div class="select-wrapper">
            <input v-if="selectedCity === '원격'" v-model="selectedDistrict" type="text" placeholder="직접 입력해주세요"
              class="styled-input" />
            <select v-model="selectedDistrict" :disabled="!selectedCity" class="styled-select">
              <option value="">소분류 선택</option>
              <option v-for="district in locationOptions[selectedCity]" :key="district" :value="district">
                {{ district }}
              </option>
            </select>
          </div>

        </div>
      </div>

      <div class="input-group">
        <label>내용</label>
        <textarea v-model="post.content" rows="10" placeholder="내용을 상세히 입력해주세요" class="styled-textarea"></textarea>
      </div>

      <div class="actions">
        <button class="cancel-btn" @click="$router.back()">취소</button>
        <div class="actions-right">
          <button class="draft-btn" @click="saveDraft">임시저장</button>
          <button class="submit-btn" @click="submitPost" :disabled="isSubmitting">
            {{ isSubmitting ? '저장 중...' : '작성 완료' }}
          </button>
        </div>
      </div>

    </div>

    <!-- 비속어 안내 모달 -->
    <CensorshipModal :show="showCensorshipModal" :detail="censorshipDetail" @close="showCensorshipModal = false" />
    <div v-if="showDraftModal" class="draft-modal-overlay">
      <div class="draft-modal">
        <p class="draft-modal-text">✏️ 임시저장된 게시글이 있습니다.<br>이어서 작성하시겠어요?</p>
        <div class="draft-modal-actions">
          <button class="draft-no-btn" @click="discardDraft">아니오</button>
          <button class="draft-yes-btn" @click="loadDraft">예</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import CensorshipModal from '@/components/CensorshipModal.vue';

export default {
  components: {
    CensorshipModal
  },
  data() {
    return {
      post: {
        title: '',
        content: '',
        job_category: '',
        author_id: null
      },
      selectedCity: '',
      selectedDistrict: '',
      locationOptions: {
        '서울': ['강남구', '송파구', '서초구', '마포구', '영등포구'],
        '경기': ['판교', '수원시', '용인시', '고양시'],
        '원격': []
      },
      isSubmitting: false,
      showCensorshipModal: false,
      censorshipDetail: '',
      showDraftModal: false
    }
  },
  created() {
    const token = localStorage.getItem('access_token');
    if (!token) {
      alert("로그인이 필요한 서비스입니다.");
      this.$router.push('/login');
      return;
    }
    const draft = localStorage.getItem('post_draft');
    if (draft) {
      this.showDraftModal = true;
    }

    try {
      const parts = token.split('.');
      if (parts.length === 3) {
        const payload = JSON.parse(atob(parts[1]));
        if (payload && payload.sub) {
          this.post.author_id = payload.sub;
        }
      }
    } catch (e) {
      console.error("토큰 처리 중 오류:", e);
      alert("로그인 세션이 유효하지 않습니다.");
      this.$router.push('/login');
    }
  },
  mounted() {
    this.initReveal();
  },
  methods: {
    initReveal() {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) entry.target.classList.add("is-visible");
        });
      }, { threshold: 0.1 });
      document.querySelectorAll(".reveal").forEach(el => observer.observe(el));
    },
    handleCityChange() {
      this.selectedDistrict = '';
    },
    async submitPost() {
      if (!this.post.title || !this.post.content || !this.post.job_category) {
        alert("제목, 내용, 직무 분야를 모두 입력해주세요.");
        return;
      }

      const token = localStorage.getItem('access_token');
      if (!token) {
        alert("로그인 세션이 만료되었습니다. 다시 로그인해주세요.");
        this.$router.push('/login');
        return;
      }

      this.isSubmitting = true;
      const postData = {
        title: this.post.title,
        content: this.post.content,
        job_category: this.post.job_category,
        region: this.selectedDistrict
          ? `${this.selectedCity} ${this.selectedDistrict}`
          : this.selectedCity,
        author_id: this.post.author_id
      };

      try {
        await axios.post('http://localhost:8000/posts', postData, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        localStorage.removeItem('post_draft');
        alert("게시글이 성공적으로 등록되었습니다.");
        this.$router.push('/posts');
      } catch (error) {
        console.error("에러 발생:", error.response?.data);
        const detail = error.response?.data?.detail;

        // 비속어/검열 에러 체크 (백엔드 메시지에 따라 조정)
        if (error.response?.status === 400 && typeof detail === 'string' && detail.includes("부적절한")) {
          this.censorshipDetail = detail;
          this.showCensorshipModal = true;
        } else {
          alert("게시글 저장 실패: " + (typeof detail === 'object' ? JSON.stringify(detail) : detail));
        }
      } finally {
        this.isSubmitting = false;
      }
    },
    // 임시저장 불러오기
    loadDraft() {
      const draft = JSON.parse(localStorage.getItem('post_draft'));
      if (draft) {
        this.post.title = draft.title || '';
        this.post.content = draft.content || '';
        this.post.job_category = draft.job_category || '';
        this.selectedCity = draft.selectedCity || '';
        this.selectedDistrict = draft.selectedDistrict || '';
      }
      this.showDraftModal = false;
    },

    // 임시저장 무시하고 새 글
    discardDraft() {
      localStorage.removeItem('post_draft');
      this.showDraftModal = false;
    },

    // 임시저장 실행 (버튼에 연결)
    saveDraft() {
      const draft = {
        title: this.post.title,
        content: this.post.content,
        job_category: this.post.job_category,
        selectedCity: this.selectedCity,
        selectedDistrict: this.selectedDistrict
      };
      localStorage.setItem('post_draft', JSON.stringify(draft));
      alert('임시저장되었습니다.');
    },
  }
}
</script>

<style scoped>
/* 기존 디자인 시스템 테마 유지 */
.create-container {
  max-width: 850px;
  margin: 0 auto;
  padding: 60px 40px;
  font-family: 'Pretendard', sans-serif;
}

.create-header {
  margin-bottom: 40px;
}

.title {
  font-size: 32px;
  font-weight: 800;
  color: #1a1a1a;
  line-height: 1.3;
}

.subtitle {
  color: #a68b6a;
  font-weight: 700;
  margin-bottom: 10px;
}

.form-card {
  padding: 40px;
  background: white;
  border-radius: 30px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.03);
}

/* ───── 셀렉트 박스 공통 래퍼 ───── */
.select-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.select-wrapper::after {
  content: '▾';
  position: absolute;
  right: 16px;
  color: #a68b6a;
  font-size: 14px;
  pointer-events: none;
  transition: transform 0.2s;
}

.styled-select {
  width: 100%;
  appearance: none;
  -webkit-appearance: none;
  border: 1.5px solid transparent;
  background: #f8f6f3;
  padding: 14px 42px 14px 18px;
  border-radius: 14px;
  font-size: 14px;
  font-weight: 600;
  color: #3e2723;
  outline: none;
  cursor: pointer;
  transition: background 0.25s, border-color 0.25s, box-shadow 0.25s;
}

.styled-select:hover {
  background: #f0ebe4;
  border-color: #d7b89c;
}

.styled-select:focus {
  background: #fff;
  border-color: #a68b6a;
  box-shadow: 0 0 0 3px rgba(166, 139, 106, 0.15);
}

.styled-select:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  background: #f0ede9;
}

/* input-row를 3컬럼으로 변경하여 소분류 칸 확보 */
.input-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 25px;
}

label {
  font-size: 14px;
  font-weight: 700;
  color: #5d4037;
  padding-left: 5px;
}

.actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  /* 취소는 왼쪽, 나머지는 오른쪽 */
  margin-top: 28px;
  gap: 12px;
}

.actions-right {
  display: flex;
  gap: 12px;
}

.draft-btn {
  flex: none;
  padding: 16px;
  border-radius: 16px;
  font-weight: 700;
  font-size: 16px;
  cursor: pointer;
  transition: 0.3s;
  border: none;
  background: #f0ede9;
  color: #5d4037;
}

.draft-btn:hover {
  background: #d7ccc8;
}

.draft-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.draft-modal {
  background: white;
  border-radius: 24px;
  padding: 36px;
  width: 340px;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
}

.draft-modal-text {
  font-size: 16px;
  font-weight: 700;
  color: #333;
  line-height: 1.6;
  margin-bottom: 28px;
}

.draft-modal-actions {
  display: flex;
  gap: 40px;
}

.draft-no-btn {
  flex: 1;
  padding: 14px;
  border-radius: 14px;
  border: none;
  background: #f1f3f5;
  color: #666;
  font-weight: 700;
  font-size: 15px;
  cursor: pointer;
}

.draft-yes-btn {
  flex: 1;
  padding: 14px;
  border-radius: 14px;
  border: none;
  background: #5d4037;
  color: white;
  font-weight: 700;
  font-size: 15px;
  cursor: pointer;
}

.draft-yes-btn:hover {
  background: #3e2723;
}

.styled-input,
.styled-select,
.styled-textarea {
  border: none;
  background: #f8f6f3;
  padding: 16px 20px;
  border-radius: 14px;
  font-size: 15px;
  outline: none;
  transition: 0.3s;
}

.styled-input:focus,
.styled-textarea:focus {
  background: #f0ede9;
  box-shadow: inset 0 0 0 2px #d7ccc8;
}

.styled-textarea {
  min-height: 250px;
  resize: none;
  line-height: 1.6;
}

.button-group {
  display: flex;
  gap: 15px;
  margin-top: 20px;
}

.cancel-btn {
  flex: none;
  padding: 16px;
  border-radius: 16px;
  font-weight: 700;
  font-size: 16px;
  cursor: pointer;
  transition: 0.3s;
  border: none;
  background: #eee;
  color: #777;
}

.cancel-btn:hover {
  background: #e6dedd;
  transform: translateY(-3px);
}

.submit-btn {
  flex: none;
  padding: 16px;
  border-radius: 16px;
  font-weight: 700;
  font-size: 16px;
  cursor: pointer;
  transition: 0.3s;
  border: none;
  background: #5d4037;
  color: white;
}


.submit-btn:hover {
  background: #3e2723;
  transform: translateY(-3px);
}

/* 애니메이션 */
.reveal {
  opacity: 0;
  transform: translateY(2rem);
  filter: blur(8px);
  transition: all 0.8s ease-out;
}

.reveal.is-visible {
  opacity: 1;
  transform: translateY(0);
  filter: blur(0);
}
</style>