<template>
    <!-- 스킵 내비게이션 -->
    <a href="#contact-form" class="skip-link">본문 바로가기</a>

    <div class="contact-container">

        <!-- 헤더 -->
        <header class="contact-header reveal" style="--index: 0">
            <p class="subtitle" aria-label="섹션 분류: 문의하기">CONTACT</p>
            <h1 class="title">
                <span aria-hidden="true">💬</span> 문의하기
            </h1>
            <p class="header-desc"><b>궁금한 점이 있으시면 아래 양식을 통해 문의해 주세요. 빠른 시일 내에 답변 드리겠습니다.</b></p>
        </header>

        <!-- 채널 카드 -->
        <div class="channel-row reveal" style="--index: 1" aria-label="문의 채널 안내">
            <div class="channel-card">
                <div class="channel-icon" aria-hidden="true">📧</div>
                <h3>이메일 문의</h3>
                <p>support@mjc.com</p>
                <span>평일 09:00 ~ 18:00</span>
            </div>
            <div class="channel-card">
                <div class="channel-icon" aria-hidden="true">💬</div>
                <h3>채팅 문의</h3>
                <p>우측 하단 채팅 버튼</p>
                <span>평일 09:00 ~ 18:00</span>
            </div>
            <div class="channel-card">
                <div class="channel-icon" aria-hidden="true">📋</div>
                <h3>FAQ</h3>
                <p>자주 묻는 질문을 먼저 확인해 보세요</p>
                <router-link to="/frequently" class="faq-link">FAQ 바로가기 →</router-link>
            </div>
        </div>

        <!-- 문의 폼 -->
        <div class="form-wrap card reveal" style="--index: 2" id="contact-form">
            <h2 class="form-title">문의 양식</h2>

            <form @submit.prevent="submitForm" novalidate>
                <div class="form-row">
                    <div class="form-group">
                        <label for="contact-name">이름 <span class="required" aria-hidden="true">*</span></label>
                        <input id="contact-name" v-model="form.name" type="text" placeholder="이름을 입력해주세요" required
                            autocomplete="name" />
                    </div>
                    <div class="form-group">
                        <label for="contact-email">이메일 <span class="required" aria-hidden="true">*</span></label>
                        <input id="contact-email" v-model="form.email" type="email" placeholder="이메일을 입력해주세요" required
                            autocomplete="email" />
                    </div>
                </div>

                <div class="form-group">
                    <label for="contact-type">문의 유형 <span class="required" aria-hidden="true">*</span></label>
                    <select id="contact-type" v-model="form.type" required>
                        <option value="" disabled>문의 유형을 선택해주세요</option>
                        <option value="account">계정 관련</option>
                        <option value="job">채용 공고 관련</option>
                        <option value="community">커뮤니티 관련</option>
                        <option value="payment">결제 관련</option>
                        <option value="etc">기타</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="contact-subject">제목 <span class="required" aria-hidden="true">*</span></label>
                    <input id="contact-subject" v-model="form.subject" type="text" placeholder="문의 제목을 입력해주세요"
                        required />
                </div>

                <div class="form-group">
                    <label for="contact-content">문의 내용 <span class="required" aria-hidden="true">*</span></label>
                    <textarea id="contact-content" v-model="form.content" placeholder="문의하실 내용을 자세히 입력해주세요" rows="6"
                        required :maxlength="1000"></textarea>
                    <span class="char-count" aria-live="polite">{{ form.content.length }} / 1000</span>
                </div>

                <div class="form-group checkbox-group">
                    <label class="checkbox-label">
                        <input v-model="form.agree" type="checkbox" required />
                        <span>개인정보 수집 및 이용에 동의합니다. <a href="/privacy" target="_blank" rel="noopener">[내용 보기]</a></span>
                    </label>
                </div>

                <button type="submit" class="submit-btn" :disabled="isSubmitting">
                    <span v-if="!isSubmitting">문의 제출하기</span>
                    <span v-else>제출 중...</span>
                </button>

                <div v-if="submitSuccess" class="success-message" role="alert">
                    ✅ 문의가 성공적으로 접수되었습니다. 빠른 시일 내에 답변 드리겠습니다.
                </div>
            </form>
        </div>

    </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'

const form = reactive({
    name: '',
    email: '',
    type: '',
    subject: '',
    content: '',
    agree: false,
})

const isSubmitting = ref(false)
const submitSuccess = ref(false)

const submitForm = async () => {
    isSubmitting.value = true
    try {
        // TODO: API 연동
        // await axios.post('/api/contact', form)
        await new Promise((r) => setTimeout(r, 1000))
        submitSuccess.value = true
        Object.assign(form, { name: '', email: '', type: '', subject: '', content: '', agree: false })
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
.contact-container {
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

/* ── 채널 카드 행 ── */
.channel-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin: 36px 0 24px;
}

.channel-card {
    background: white;
    border-radius: 16px;
    padding: 24px 20px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
    border: 1px solid #f0e8e0;
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.channel-icon {
    font-size: 1.8rem;
    margin-bottom: 6px;
}

.channel-card h3 {
    font-size: 0.95rem;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0;
}

.channel-card p {
    font-size: 0.85rem;
    color: #555;
    margin: 0;
    line-height: 1.5;
}

.channel-card span {
    font-size: 0.78rem;
    color: #999;
}

.faq-link {
    font-size: 0.85rem;
    color: #5d4037;
    text-decoration: none;
    font-weight: 600;
    margin-top: 4px;
}

.faq-link:hover {
    text-decoration: underline;
}

/* ── 카드 공통 ── */
.card {
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

/* ── 폼 래퍼 ── */
.form-wrap {
    padding: 40px;
    border: 1px solid #f0e8e0;
}

.form-title {
    font-size: 20px;
    font-weight: 800;
    color: #1a1a1a;
    margin-bottom: 28px;
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
    position: relative;
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
.form-group select,
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
.form-group select:focus,
.form-group textarea:focus {
    border-color: #5d4037;
    box-shadow: 0 0 0 3px rgba(93, 64, 55, 0.2);
}

.form-group textarea {
    resize: vertical;
}

.char-count {
    font-size: 0.78rem;
    color: #999;
    text-align: right;
    margin-top: 4px;
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
    .channel-row {
        grid-template-columns: 1fr;
    }

    .form-row {
        grid-template-columns: 1fr;
    }

    .form-wrap {
        padding: 24px;
    }

    .title {
        font-size: 28px;
    }
}
</style>