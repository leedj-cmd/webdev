<template>
    <div class="faq-container">

        <header class="faq-header reveal" style="--index: 0">
            <p class="subtitle">HELP CENTER</p>
            <h1 class="title">💬 자주 묻는 질문</h1>
            <h3>궁금한 점을 빠르게 찾아보세요.</h3>
        </header>

        <div class="faq-list reveal" style="--index: 1">
            <div v-for="(faq, index) in faqs" :key="faq.id" class="faq-item card" :data-faq-id="faq.id"
                :style="{ '--index': index + 2 }" :class="{
                    open: openId === faq.id,
                    'card-hidden': !visibleIds.has(faq.id),
                    'is-visible': visibleIds.has(faq.id)
                }" @click="toggle(faq.id)">

                <div class="faq-question">
                    <span class="faq-q-mark">Q</span>
                    <p class="faq-q-text">{{ faq.question }}</p>
                    <svg class="faq-chevron" width="18" height="18" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" stroke-width="2">
                        <path d="m6 9 6 6 6-6" />
                    </svg>
                </div>

                <Transition name="faq-expand">
                    <div v-if="openId === faq.id" class="faq-answer">
                        <span class="faq-a-mark">A</span>
                        <p class="faq-a-text">{{ faq.answer }}</p>
                    </div>
                </Transition>
            </div>
        </div>

    </div>
</template>

<script>
export default {
    data() {
        return {
            faqs: [
                { id: 1, question: 'DevCareer는 어떤 서비스인가요?', answer: 'DevCareer는 IT 개발자를 위한 통합 커리어 플랫폼입니다.\n채용 공고, 공모전 정보, 커뮤니티, AI 기반 질문 답변까지 개발자의 취업과 성장을 한 곳에서 지원합니다.' },
                { id: 2, question: '회원가입은 어떻게 하나요?', answer: '우측 상단의 [회원가입] 버튼을 클릭하면 이메일 또는 소셜 계정(GitHub, Google)으로 간편하게 가입하실 수 있습니다.\n가입 후 프로필을 작성하면 맞춤 채용 공고 추천을 받을 수 있어요.' },
                { id: 3, question: '채용 공고는 어떻게 등록하나요?', answer: '기업 회원으로 가입하신 후 [채용 공고 등록] 메뉴를 이용해 주세요.\n공고 검토 후 24시간 이내에 게시되며, 등록 문의는 고객지원 > 문의하기를 통해 접수해 주시면 됩니다.' },
                { id: 4, question: '공모전 정보는 어떻게 업데이트되나요?', answer: '공모전 정보는 주요 대회 공식 사이트와 연계하여 자동으로 수집·업데이트됩니다.\n새로운 공모전이 등록되면 관심 분야로 설정해 두신 경우 알림을 받으실 수 있습니다.' },
                { id: 5, question: '커뮤니티에서 어떤 활동을 할 수 있나요?', answer: '커뮤니티에서는 개발 관련 질문과 답변, 취업 후기, 프로젝트 팀원 모집, 스터디 모집 등 다양한 활동이 가능합니다.\n활발한 활동을 통해 포인트를 쌓으면 프로필에 배지가 부여됩니다.' },
                { id: 6, question: '비밀번호를 잊어버렸어요. 어떻게 재설정하나요?', answer: '로그인 페이지의 [비밀번호 찾기]를 클릭하시면 가입 시 등록한 이메일로 재설정 링크가 발송됩니다.\n메일이 오지 않을 경우 스팸 함을 확인하시거나 고객지원으로 문의해 주세요.' },
                { id: 7, question: '작성한 게시글이나 댓글을 수정·삭제할 수 있나요?', answer: '내가 작성한 게시글과 댓글은 언제든지 수정하거나 삭제할 수 있습니다.\n마이페이지 > 내 게시글에서 한눈에 관리하실 수 있으며, 신고 누적 게시글은 관리자 검토 후 제한될 수 있습니다.' },
                { id: 8, question: 'AI 질문 답변 기능은 어떻게 사용하나요?', answer: '우측 하단의 채팅 버튼을 클릭하면 AI 어시스턴트가 활성화됩니다.\n코딩 질문, 이력서 조언, 면접 준비 등 개발 커리어와 관련된 다양한 질문을 자유롭게 해보세요.' },
            ],
            openId: null,
            visibleIds: new Set(),
        }
    },

    mounted() {
        this.$nextTick(() => this.initReveal())
    },

    methods: {
        toggle(id) {
            this.openId = this.openId === id ? null : id
        },

        initReveal() {
            if (this._observer) return

            this._observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('is-visible')

                        const id = entry.target.dataset.faqId
                        if (id) {
                            const next = new Set(this.visibleIds)
                            next.add(Number(id))
                            this.visibleIds = next
                        }

                        this._observer.unobserve(entry.target)
                    }
                })
            }, { threshold: 0.1 })

            const targets = document.querySelectorAll('.reveal, .faq-item[data-faq-id]')
            if (targets.length === 0) {
                setTimeout(() => {
                    this._observer = null
                    this.initReveal()
                }, 200)
                return
            }
            targets.forEach(el => this._observer.observe(el))
        },
    }
}
</script>

<style scoped>
.faq-container {
    max-width: 860px;
    margin: 0 auto;
    padding: 0 40px 60px 40px;
}

/* ── 헤더 ── */
.faq-header {
    padding: 60px 0 20px;
    position: relative;
    text-align: left;
}

.faq-header .subtitle {
    color: #a68b6a;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 2px;
    margin-bottom: 12px;
}

.faq-header .title {
    font-size: 32px;
    font-weight: 800;
    color: #333;
    margin-bottom: 10px;
}

/* ── 목록 래퍼 ── */
.faq-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
    max-width: 100%;
}

/* ── FAQ 아이템 ── */
.faq-item {
    background: white;
    border-radius: 20px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.03);
    cursor: pointer;
    overflow: hidden;
    transition: box-shadow 0.3s ease, border-color 0.3s ease;
    border: 1.5px solid transparent;
}

.faq-item:hover {
    box-shadow: 0 12px 36px rgba(93, 64, 55, 0.1);
    border-color: rgba(93, 64, 55, 0.15);
}

.faq-item.open {
    border-color: rgba(93, 64, 55, 0.25);
    box-shadow: 0 14px 40px rgba(93, 64, 55, 0.12);
}

/* ── 질문 행 ── */
.faq-question {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 22px 28px;
}

.faq-q-mark {
    flex-shrink: 0;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: linear-gradient(135deg, #5d4037, #a68b6a);
    color: white;
    font-size: 14px;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
}

.faq-q-text {
    flex: 1;
    font-size: 16px;
    font-weight: 700;
    color: #1a1a1a;
    line-height: 1.45;
    word-break: keep-all;
}

.faq-chevron {
    flex-shrink: 0;
    color: #a68b6a;
    transition: transform 0.3s ease;
}

.faq-item.open .faq-chevron {
    transform: rotate(180deg);
}

/* ── 답변 ── */
.faq-answer {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    padding: 24px 28px;
    background-color: #fdfbf9;
    border-top: 1px solid #f0ede9;
}

.faq-a-mark {
    flex-shrink: 0;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #e8e1da;
    color: #5d4037;
    font-size: 14px;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 15px;
}

.faq-a-text {
    flex: 1;
    font-size: 15px;
    color: #4a3f35;
    line-height: 1.7;
    word-break: keep-all;
    white-space: pre-wrap;
}

/* ── 펼치기 트랜지션 ── */
.faq-expand-enter-active {
    transition: opacity 0.25s ease, transform 0.25s ease;
}

.faq-expand-leave-active {
    transition: opacity 0.15s ease, transform 0.15s ease;
}

.faq-expand-enter-from {
    opacity: 0;
    transform: translateY(-8px);
}

.faq-expand-leave-to {
    opacity: 0;
    transform: translateY(-8px);
}

/* ── 카드 등장 애니메이션 ── */
.reveal {
    opacity: 0;
    transform: translateY(20px);
    transition: all 0.8s ease-out;
}

.reveal.is-visible {
    opacity: 1;
    transform: translateY(0);
}

.card-hidden {
    opacity: 0;
    transform: translateY(20px);
    filter: blur(8px);
    transition: opacity 0.8s ease-out,
        filter 0.8s ease-out,
        transform 0.8s ease-out,
        box-shadow 0.3s ease,
        border-color 0.3s ease;
    transition-delay: calc(var(--index) * 0.07s);
}

.card-hidden.is-visible {
    opacity: 1;
    transform: translateY(0);
    filter: blur(0);
}

/* ── 반응형 ── */
@media (max-width: 768px) {
    .faq-container {
        padding: 0 20px 40px 20px;
    }

    .faq-question {
        padding: 18px 20px;
        gap: 12px;
    }

    .faq-answer {
        padding: 0 20px 18px 20px;
        padding-top: 14px;
        gap: 12px;
    }

    .faq-q-text {
        font-size: 15px;
    }
}
</style>