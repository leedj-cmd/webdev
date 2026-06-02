<template>
    <!-- 스킵 내비게이션 -->
    <a href="#main-content" class="skip-link">본문 바로가기</a>

    <div class="detail-container">

        <div v-if="notice">
            <!-- 뒤로가기 -->
            <button class="back-btn" @click="router.back()" aria-label="이전 페이지로 돌아가기">
                <span aria-hidden="true">←</span>
                뒤로 가기
            </button>

            <!-- main 랜드마크: 스킵 링크 타겟 -->
            <main id="main-content">
                <article class="detail-card card reveal" style="--index: 0" aria-labelledby="detail-title">
                    <!-- 상단 배지 + 날짜 -->
                    <div class="detail-meta">
                        <span class="notice-badge" :class="{ 'pinned-badge': notice.pinned }"
                            :aria-label="notice.pinned ? '필독 공지' : '일반 공지'">
                            <!-- 이모지는 장식 처리 -->
                            <span aria-hidden="true">{{ notice.pinned ? '📌 필독' : '공지' }}</span>
                        </span>
                        <time class="detail-date" :datetime="toDatetime(notice.date)">
                            {{ notice.date }}
                        </time>
                    </div>

                    <!-- 제목: article의 aria-labelledby 타겟 -->
                    <h1 class="detail-title" id="detail-title">
                        {{ notice.title }}
                    </h1>

                    <hr class="divider" aria-hidden="true" />

                    <!-- 본문: v-html 사용 시 실제 운영에서는 DOMPurify 등으로 sanitize 권장 -->
                    <div class="detail-body" v-html="notice.body"></div>
                </article>

                <!-- 이전 / 다음 네비게이션: nav 시맨틱 태그 -->
                <nav class="nav-wrapper reveal" style="--index: 1" aria-label="공지사항 이전글 다음글 이동">
                    <button class="nav-btn" :disabled="!prevNotice" :aria-disabled="!prevNotice" :aria-label="prevNotice
                        ? `이전 공지사항: ${prevNotice.title}`
                        : '이전 공지사항 없음'" @click="!prevNotice ? null : navigate(currentId - 1)">
                        <span class="nav-label" aria-hidden="true">이전 공지</span>
                        <span class="nav-title">
                            {{ prevNotice ? prevNotice.title : '이전 공지가 없습니다.' }}
                        </span>
                    </button>

                    <div class="nav-divider" aria-hidden="true"></div>

                    <button class="nav-btn" :disabled="!nextNotice" :aria-disabled="!nextNotice" :aria-label="nextNotice
                        ? `다음 공지사항: ${nextNotice.title}`
                        : '다음 공지사항 없음'" @click="!nextNotice ? null : navigate(currentId + 1)">
                        <span class="nav-label" aria-hidden="true">다음 공지</span>
                        <span class="nav-title">
                            {{ nextNotice ? nextNotice.title : '다음 공지가 없습니다.' }}
                        </span>
                    </button>
                </nav>
            </main>
        </div>

        <!-- 존재하지 않는 공지: role="status"로 스크린리더 알림 -->
        <div v-else class="not-found card reveal" style="--index: 0" role="status" aria-live="polite">
            <p>존재하지 않는 공지사항입니다.</p>
            <button class="back-btn" @click="router.push('/notice')" aria-label="공지사항 목록 페이지로 이동">
                목록으로 돌아가기
            </button>
        </div>

    </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useNotices } from '@/composables/useNotices';

const route = useRoute();
const router = useRouter();
const { notices } = useNotices();

const currentId = computed(() => parseInt(route.params.id));
const notice = computed(() => notices.value[currentId.value] ?? null);
const prevNotice = computed(() => notices.value[currentId.value - 1] ?? null);
const nextNotice = computed(() => notices.value[currentId.value + 1] ?? null);

// 날짜 문자열 → datetime 속성용 변환 + zero-padding
// 예: "2026. 3. 2" → "2026-03-02"
const toDatetime = (dateStr) => {
    if (!dateStr) return '';
    const parts = dateStr.replace(/\s/g, '').split('.').filter(Boolean);
    if (parts.length < 3) return dateStr;
    const [y, m, d] = parts;
    return `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
};

const navigate = (id) => {
    router.push({ name: 'NoticeDetail', params: { id } });
};

onMounted(() => {
    // 페이지 이동 시 스크롤 최상단으로
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // prefers-reduced-motion 대응
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) {
        document.querySelectorAll('.reveal').forEach((el) => el.classList.add('is-visible'));
        return;
    }

    const observer = new IntersectionObserver(
        (entries) => entries.forEach((e) => {
            if (e.isIntersecting) e.target.classList.add('is-visible');
        }),
        { threshold: 0.08 }
    );
    document.querySelectorAll('.reveal').forEach((el) => observer.observe(el));
});
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
.detail-container {
    max-width: 780px;
    margin: 0 auto;
    padding: 48px 24px 100px;
    font-family: 'Pretendard', 'Noto Sans KR', sans-serif;
    color: #2c2c2c;
}

/* ── 뒤로가기 ── */
.back-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: none;
    border: none;
    color: #7a5c3a;
    /* #a68b6a → 대비비 개선 */
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    margin-bottom: 28px;
    padding: 6px 2px;
    border-radius: 4px;
    transition: color 0.2s;
}

.back-btn:hover {
    color: #5d4037;
}

.back-btn:focus-visible {
    outline: 2px solid #5d4037;
    outline-offset: 3px;
}

/* ── 본문 카드 ── */
.detail-card {
    padding: 48px 52px;
    margin-bottom: 20px;
}

.detail-meta {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 18px;
}

.notice-badge {
    padding: 4px 10px;
    background: #f5ede6;
    color: #5d4037;
    font-size: 11px;
    font-weight: 700;
    border-radius: 6px;
}

.pinned-badge {
    background: #3e2723;
    color: #fff;
}

.detail-date {
    font-size: 13px;
    color: #000000;
    /* #000000 → 본문과 구분되는 중간 톤으로 */
}

.detail-title {
    font-size: 26px;
    font-weight: 800;
    color: #1a1a1a;
    line-height: 1.4;
    margin-bottom: 0;
}

.divider {
    border: none;
    border-top: 1px solid #f0e8e0;
    margin: 28px 0;
}

.detail-body {
    font-size: 15px;
    color: #000000;
    /* #000000 → 순수 검정보다 가독성 높은 값 */
    line-height: 2;
}

.detail-body p {
    margin-bottom: 14px;
}

.detail-body strong {
    color: #3e2723;
}

/* ── 이전 / 다음 네비게이션 ── */
.nav-wrapper {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: stretch;
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
    overflow: hidden;
}

.nav-btn {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 20px 24px;
    background: none;
    border: none;
    cursor: pointer;
    text-align: left;
    transition: background 0.15s;
    border-radius: 0;
}

.nav-btn:last-child {
    text-align: right;
    align-items: flex-end;
}

.nav-btn:not(:disabled):hover {
    background: #faf5f0;
}

.nav-btn:disabled,
.nav-btn[aria-disabled='true'] {
    cursor: default;
    opacity: 0.4;
}

/* 비활성 버튼은 포커스 제외 */
.nav-btn:disabled {
    pointer-events: none;
}

.nav-btn:focus-visible {
    outline: 2px solid #5d4037;
    outline-offset: -2px;
    /* 카드 내부이므로 inset */
}

.nav-label {
    font-size: 11px;
    font-weight: 700;
    color: #7a5c3a;
    /* #a68b6a → 대비비 개선 */
    letter-spacing: 0.06em;
}

.nav-title {
    font-size: 14px;
    font-weight: 600;
    color: #1a1a1a;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 260px;
}

.nav-divider {
    width: 1px;
    background: #f0e8e0;
    margin: 12px 0;
}

/* ── 없는 공지 ── */
.not-found {
    text-align: center;
    padding: 80px 24px;
    color: #767676;
    /* #aaa → 대비비 개선 */
    font-size: 15px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
}

/* ── 공통 카드 ── */
.card {
    background: white;
    border-radius: 20px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

/* ── 애니메이션 ── */
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

/* ── 애니메이션 비선호 사용자 대응 ── */
@media (prefers-reduced-motion: reduce) {
    .reveal {
        opacity: 1;
        transform: none;
        transition: none;
    }
}

/* ── 반응형 ── */
@media (max-width: 600px) {
    .detail-card {
        padding: 32px 24px;
    }

    .detail-title {
        font-size: 20px;
    }

    .nav-title {
        max-width: 120px;
    }
}
</style>
