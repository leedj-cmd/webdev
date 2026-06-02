<template>
  <!-- 스킵 내비게이션 -->
  <a href="#partnership-form" class="skip-link">본문 바로가기</a>

  <div class="partnership-container">

    <!-- 헤더 -->
    <header class="partnership-header reveal" style="--index: 0">
      <p class="subtitle" aria-label="섹션 분류: 제휴문의">PARTNERSHIP</p>
      <h1 class="title">
        <span aria-hidden="true">🤝</span> 제휴문의
      </h1>
      <p class="header-desc"><b>DevCareer와 함께 성장할 파트너를 환영합니다. 다양한 제휴 방식으로 협업할 수 있습니다.</b></p>
    </header>

    <!-- 제휴 유형 카드 -->
    <section class="type-section reveal" style="--index: 1" aria-labelledby="type-section-title">
      <h2 id="type-section-title" class="section-title">제휴 유형</h2>
      <div class="type-cards" role="list">
        <div class="type-card card" role="listitem">
          <div class="type-icon" aria-hidden="true">🏢</div>
          <h3>채용 파트너</h3>
          <p>IT 개발자 채용 공고를 게재하고 우수 인재를 발굴하세요. 다양한 노출 옵션과 지원자 관리 도구를 제공합니다.</p>
          <ul aria-label="채용 파트너 혜택">
            <li>채용 공고 무제한 등록</li>
            <li>지원자 관리 대시보드</li>
            <li>프리미엄 배너 노출</li>
          </ul>
        </div>

        <div class="type-card card featured" role="listitem">
          <div class="featured-badge" aria-label="인기 유형">인기</div>
          <div class="type-icon" aria-hidden="true">🎓</div>
          <h3>교육 파트너</h3>
          <p>개발자 교육 과정, 부트캠프, 온라인 강의를 홍보하고 수강생을 모집하세요.</p>
          <ul aria-label="교육 파트너 혜택">
            <li>강의/부트캠프 홍보 페이지</li>
            <li>커뮤니티 연계 프로모션</li>
            <li>수료생 취업 연계</li>
          </ul>
        </div>

        <div class="type-card card" role="listitem">
          <div class="type-icon" aria-hidden="true">📝</div>
          <h3>콘텐츠 파트너</h3>
          <p>기술 블로그, 미디어, 뉴스레터 등 개발자 관련 콘텐츠를 함께 제작하고 배포합니다.</p>
          <ul aria-label="콘텐츠 파트너 혜택">
            <li>공동 콘텐츠 기획</li>
            <li>뉴스레터 광고 삽입</li>
            <li>상호 링크 및 홍보</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- 제휴 신청 폼 -->
    <section class="form-section reveal" style="--index: 2" aria-labelledby="form-section-title" id="partnership-form">
      <div class="form-header">
        <h2 id="form-section-title" class="section-title">제휴 신청하기</h2>
        <p class="form-desc">아래 양식을 작성해 주시면 영업일 기준 2~3일 내 담당자가 연락드립니다.</p>
      </div>

      <form @submit.prevent="submitPartnership" class="partnership-form card" novalidate>

        <div class="form-row">
          <div class="form-group">
            <label for="ps-name">담당자명 <span class="required" aria-hidden="true">*</span></label>
            <input id="ps-name" v-model="form.name" type="text" placeholder="담당자 이름" required autocomplete="name" />
          </div>
          <div class="form-group">
            <label for="ps-position">직책</label>
            <input id="ps-position" v-model="form.position" type="text" placeholder="직책 또는 부서명"
              autocomplete="organization-title" />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="ps-company">회사명 <span class="required" aria-hidden="true">*</span></label>
            <input id="ps-company" v-model="form.company" type="text" placeholder="회사 또는 기관명" required
              autocomplete="organization" />
          </div>
          <div class="form-group">
            <label for="ps-website">웹사이트</label>
            <input id="ps-website" v-model="form.website" type="url" placeholder="https://example.com"
              autocomplete="url" />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="ps-email">연락처 이메일 <span class="required" aria-hidden="true">*</span></label>
            <input id="ps-email" v-model="form.email" type="email" placeholder="business@company.com" required
              autocomplete="email" />
          </div>
          <div class="form-group">
            <label for="ps-phone">연락처 전화번호</label>
            <input id="ps-phone" v-model="form.phone" type="tel" placeholder="02-0000-0000" autocomplete="tel" />
          </div>
        </div>

        <div class="form-group">
          <label>제휴 유형 <span class="required" aria-hidden="true">*</span></label>
          <div class="type-select-group" role="group" aria-label="제휴 유형 선택">
            <label v-for="t in partnerTypes" :key="t.value" class="type-radio"
              :class="{ active: form.type === t.value }">
              <input type="radio" v-model="form.type" :value="t.value" required />
              {{ t.label }}
            </label>
          </div>
        </div>

        <div class="form-group">
          <label for="ps-content">제안 내용 <span class="required" aria-hidden="true">*</span></label>
          <textarea id="ps-content" v-model="form.content" rows="6" placeholder="제휴 목적, 제안 내용, 기대 효과 등을 자유롭게 작성해 주세요."
            required></textarea>
        </div>

        <div class="form-group">
          <label for="ps-start">희망 시작 시기</label>
          <input id="ps-start" v-model="form.startDate" type="month" />
        </div>

        <div class="form-group checkbox-group">
          <label class="checkbox-label">
            <input v-model="form.agree" type="checkbox" required />
            <span>개인정보 수집 및 이용에 동의합니다. <a href="/privacy" target="_blank" rel="noopener">[내용 보기]</a></span>
          </label>
        </div>

        <button type="submit" class="submit-btn" :disabled="isSubmitting">
          <span v-if="!isSubmitting">제휴 신청 제출</span>
          <span v-else>제출 중...</span>
        </button>

        <div v-if="submitSuccess" class="success-message" role="alert">
          ✅ 제휴 신청이 접수되었습니다. 담당자가 영업일 기준 2~3일 내 연락드리겠습니다.
        </div>

      </form>
    </section>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'

const partnerTypes = [
  { value: 'recruit', label: '🏢 채용 파트너' },
  { value: 'edu', label: '🎓 교육 파트너' },
  { value: 'content', label: '📝 콘텐츠 파트너' },
  { value: 'etc', label: '💡 기타' },
]

const form = reactive({
  name: '',
  position: '',
  company: '',
  website: '',
  email: '',
  phone: '',
  type: '',
  content: '',
  startDate: '',
  agree: false,
})

const isSubmitting = ref(false)
const submitSuccess = ref(false)

const submitPartnership = async () => {
  isSubmitting.value = true
  try {
    // TODO: API 연동
    // await axios.post('/api/partnership', form)
    await new Promise((r) => setTimeout(r, 1000))
    submitSuccess.value = true
    Object.assign(form, {
      name: '', position: '', company: '', website: '',
      email: '', phone: '', type: '', content: '', startDate: '', agree: false,
    })
  } catch (e) {
    alert('제출 중 오류가 발생했습니다. 다시 시도해주세요.')
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  if (prefersReduced) {
    document.querySelectorAll('.reveal').forEach((el) => el.classList.add('is-visible'))
    return
  }
  const observer = new IntersectionObserver(
    (entries) => entries.forEach((e) => { if (e.isIntersecting) e.target.classList.add('is-visible') }),
    { threshold: 0.08 }
  )
  document.querySelectorAll('.reveal').forEach((el) => observer.observe(el))
})
</script>

<style scoped>
/* ── 스킵 내비게이션 ── */
.skip-link {
  position: absolute;
  top: -100%;
  left: 16px;
  background: #5d4037;
  color: white;
  padding: 10px 18px;
  border-radius: 0 0 8px 8px;
  font-size: 14px;
  font-weight: 600;
  z-index: 9999;
  text-decoration: none;
  transition: top 0.2s;
}

.skip-link:focus {
  top: 0;
}

/* ── 전체 컨테이너 ── */
.partnership-container {
  max-width: 780px;
  margin: 0 auto;
  padding: 60px 24px 100px;
  font-family: 'Pretendard', 'Noto Sans KR', sans-serif;
  color: #2c2c2c;
}

/* ── 헤더 ── */
.subtitle {
  color: #7a5c3a;
  font-weight: 700;
  font-size: 13px;
  letter-spacing: 0.1em;
  margin-bottom: 10px;
}

.title {
  font-size: 36px;
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 10px;
}

.header-desc {
  font-size: 16px;
  color: #2c2c2c;
  font-weight: 400;
  line-height: 1.6;
}

/* ── 섹션 타이틀 ── */
.section-title {
  font-size: 20px;
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 20px;
}

/* ── 카드 공통 ── */
.card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

/* ── 제휴 유형 섹션 ── */
.type-section {
  margin: 36px 0 32px;
}

.type-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.type-card {
  padding: 28px 22px;
  border: 1px solid #f0e8e0;
  position: relative;
}

.type-card.featured {
  border-color: #5d4037;
  box-shadow: 0 4px 24px rgba(93, 64, 55, 0.12);
}

.featured-badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: #5d4037;
  color: white;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 4px 14px;
  border-radius: 20px;
  white-space: nowrap;
}

.type-icon {
  font-size: 2rem;
  margin-bottom: 12px;
}

.type-card h3 {
  font-size: 1rem;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 10px;
}

.type-card p {
  font-size: 0.85rem;
  color: #555;
  line-height: 1.6;
  margin-bottom: 14px;
}

.type-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.type-card ul li {
  font-size: 0.83rem;
  color: #2d3748;
}

.type-card ul li::before {
  content: '✓ ';
  color: #5d4037;
  font-weight: 700;
}

/* ── 폼 섹션 ── */
.form-section {
  margin-top: 8px;
}

.form-header {
  margin-bottom: 24px;
}

.form-desc {
  font-size: 0.9rem;
  color: #718096;
  margin-top: 4px;
}

.partnership-form {
  padding: 40px;
  border: 1px solid #f0e8e0;
}

/* ── 폼 레이아웃 ── */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
}

.form-group label {
  font-size: 0.88rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 8px;
}

.required {
  color: #e53e3e;
}

/* ── 입력 공통 ── */
.form-group input,
.form-group textarea {
  border: 1.5px solid #e8ddd5;
  border-radius: 14px;
  padding: 12px 16px;
  font-size: 0.92rem;
  color: #2c2c2c;
  background: white;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  font-family: inherit;
}

.form-group input:focus,
.form-group textarea:focus {
  border-color: #5d4037;
  box-shadow: 0 0 0 3px rgba(93, 64, 55, 0.2);
}

.form-group textarea {
  resize: vertical;
}

/* ── 제휴 유형 라디오 ── */
.type-select-group {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.type-radio {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1.5px solid #e8ddd5;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.88rem;
  color: #555;
  background: white;
  transition: all 0.2s;
  user-select: none;
}

.type-radio input {
  display: none;
}

.type-radio.active {
  border-color: #5d4037;
  background: #5d4037;
  color: white;
  font-weight: 600;
}

/* ── 체크박스 ── */
.checkbox-group {
  margin-bottom: 24px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.88rem;
  color: #555;
  cursor: pointer;
}

.checkbox-label input {
  width: 16px;
  height: 16px;
  accent-color: #5d4037;
  flex-shrink: 0;
}

.checkbox-label a {
  color: #5d4037;
  text-decoration: none;
}

.checkbox-label a:hover {
  text-decoration: underline;
}

/* ── 제출 버튼 ── */
.submit-btn {
  width: 100%;
  padding: 14px;
  background-color: #5d4037;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
  font-family: inherit;
}

.submit-btn:hover:not(:disabled) {
  background-color: #3e2723;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.submit-btn:focus-visible {
  outline: 3px solid #3e2723;
  outline-offset: 3px;
}

/* ── 성공 메시지 ── */
.success-message {
  margin-top: 20px;
  padding: 14px;
  background: #f0fff4;
  border: 1px solid #9ae6b4;
  border-radius: 10px;
  color: #276749;
  font-size: 0.9rem;
  text-align: center;
}

/* ── reveal 애니메이션 ── */
.reveal {
  opacity: 0;
  transform: translateY(1.5rem);
  transition: all 0.7s cubic-bezier(0.16, 1, 0.3, 1);
  transition-delay: calc(var(--index, 0) * 0.07s);
}

.reveal.is-visible {
  opacity: 1;
  transform: translateY(0);
}

@media (prefers-reduced-motion: reduce) {
  .reveal {
    opacity: 1;
    transform: none;
    transition: none;
  }
}

/* ── 반응형 ── */
@media (max-width: 600px) {
  .type-cards {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .partnership-form {
    padding: 24px;
  }

  .title {
    font-size: 28px;
  }
}
</style>