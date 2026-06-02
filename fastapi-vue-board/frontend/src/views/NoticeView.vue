<template>
  <!-- 스킵 내비게이션 -->
  <a href="#main-content" class="skip-link">본문 바로가기</a>

  <div class="notice-container">
    <header class="notice-header reveal" style="--index: 0">
      <p class="subtitle" aria-label="섹션 분류: 공지사항">NOTICE</p>
      <h1 class="title">
        <span aria-hidden="true">📢</span> 공지사항
      </h1>
      <p class="header-desc"><b>DevCareer의 새로운 소식을 확인하세요</b></p>
    </header>

    <!-- 검색: label 명시 -->
    <div class="search-wrapper reveal" style="--index: 1">
      <label for="notice-search" class="sr-only">공지사항 검색</label>
      <input id="notice-search" v-model="searchQuery" class="search-input" type="search" placeholder="공지사항 검색"
        aria-controls="notice-list" autocomplete="off" />
    </div>

    <!-- 검색 결과 수 스크린리더 알림 -->
    <p class="sr-only" aria-live="polite" aria-atomic="true">
      {{ searchResultAnnouncement }}
    </p>

    <!-- 공지 목록 -->
    <ul id="notice-list" class="notice-list" role="list" aria-label="공지사항 목록">
      <li v-for="(n, i) in filteredNotices" :key="i" class="notice-item card reveal" :style="`--index: ${i + 2}`"
        :class="{ pinned: n.pinned }">
        <!-- div 클릭 → button으로 교체: 키보드/스크린리더 접근 가능 -->
        <button class="notice-item-btn" @click="openNotice(n)"
          :aria-label="`${n.pinned ? '필독 공지' : '공지'}: ${n.title}, ${n.date}`"
          :aria-pressed="selectedNotice?.title === n.title">
          <div class="notice-badge" :class="{ 'pinned-badge': n.pinned }" aria-hidden="true">
            {{ n.pinned ? '📌 필독' : '공지' }}
          </div>
          <div class="notice-content">
            <p class="notice-title">{{ n.title }}</p>
            <p class="notice-date">
              <time :datetime="toDatetime(n.date)">{{ n.date }}</time>
            </p>
          </div>
          <!-- 장식용 화살표 -->
          <span class="arrow-icon" aria-hidden="true">›</span>
        </button>
      </li>

      <!-- 검색 결과 없음 -->
      <li v-if="filteredNotices.length === 0" class="empty-state card reveal" style="--index: 2" role="status">
        검색 결과가 없습니다
      </li>
    </ul>

    <!-- 상세 모달 -->
    <Teleport to="body">
      <div v-if="selectedNotice" class="modal-overlay" @click.self="closeModal" @keydown.esc="closeModal" role="dialog"
        aria-modal="true" :aria-labelledby="'modal-title'" :aria-describedby="'modal-body'" ref="modalOverlayRef">
        <div class="modal-card" ref="modalCardRef">
          <div class="modal-header">
            <div class="notice-badge" :class="{ 'pinned-badge': selectedNotice.pinned }" aria-hidden="true">
              {{ selectedNotice.pinned ? '📌 필독' : '공지' }}
            </div>
            <button class="modal-close" @click="closeModal" aria-label="공지사항 모달 닫기" ref="modalCloseRef">
              <span aria-hidden="true">✕</span>
            </button>
          </div>

          <h2 class="modal-title" id="modal-title">
            {{ selectedNotice.title }}
          </h2>
          <p class="modal-date">
            <time :datetime="toDatetime(selectedNotice.date)">{{ selectedNotice.date }}</time>
          </p>
          <hr class="modal-divider" aria-hidden="true" />
          <div class="modal-body" id="modal-body" v-html="selectedNotice.body"></div>

          <div class="modal-footer">
            <p class="modal-preview-hint" aria-hidden="true">전체 내용은 상세 페이지에서 확인하세요</p>
            <button class="detail-btn" @click="goToDetail(selectedNotice)"
              aria-label="`${selectedNotice.title} 상세 페이지로 이동`">
              자세히 보기
              <span aria-hidden="true"> →</span>
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useNotices } from '@/composables/useNotices';

const searchQuery = ref('');
const selectedNotice = ref(null);
const { notices } = useNotices();
const router = useRouter();

// 모달 ref
const modalCardRef = ref(null);
const modalCloseRef = ref(null);
// 모달 열기 전 포커스된 요소 기억 (닫힐 때 복귀용)
let lastFocusedEl = null;

// 날짜 문자열 → datetime 속성용 변환 (예: "2026. 3. 2" → "2026-03-02")
const toDatetime = (dateStr) => {
  if (!dateStr) return '';
  return dateStr.replace(/\.\s*/g, '-').replace(/-$/, '').trim();
};

// 검색 결과 스크린리더 알림 텍스트
const searchResultAnnouncement = computed(() => {
  const q = searchQuery.value.trim();
  if (!q) return '';
  return `"${q}" 검색 결과: ${filteredNotices.value.length}건`;
});

const filteredNotices = computed(() => {
  const q = searchQuery.value.trim();
  const list = notices.value
    .slice()
    .sort((a, b) => {
      if (a.pinned && !b.pinned) return -1;
      if (!a.pinned && b.pinned) return 1;
      return new Date(b.date.replace(/\.\s*/g, '-')) - new Date(a.date.replace(/\.\s*/g, '-'));
    });
  if (!q) return list;
  return list.filter((n) => n.title.includes(q) || n.body.includes(q));
});

const openNotice = (notice) => {
  lastFocusedEl = document.activeElement;
  selectedNotice.value = notice;
  // 모달이 렌더된 후 닫기 버튼에 포커스
  nextTick(() => {
    modalCloseRef.value?.focus();
  });
};

const closeModal = () => {
  selectedNotice.value = null;
  // 모달 닫힌 후 원래 요소로 포커스 복귀
  nextTick(() => {
    lastFocusedEl?.focus();
  });
};

const goToDetail = (notice) => {
  const index = notices.value.findIndex((n) => n.title === notice.title);
  closeModal();
  router.push({ name: 'NoticeDetail', params: { id: index } });
};

// 모달 내 포커스 트랩
const handleFocusTrap = (e) => {
  if (!selectedNotice.value || !modalCardRef.value) return;
  const focusable = modalCardRef.value.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  if (e.key === 'Tab') {
    if (e.shiftKey) {
      if (document.activeElement === first) {
        e.preventDefault();
        last?.focus();
      }
    } else {
      if (document.activeElement === last) {
        e.preventDefault();
        first?.focus();
      }
    }
  }
};

onMounted(() => {
  document.addEventListener('keydown', handleFocusTrap);

  // prefers-reduced-motion 대응
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReduced) {
    document.querySelectorAll('.reveal').forEach((el) => el.classList.add('is-visible'));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => entries.forEach((e) => { if (e.isIntersecting) e.target.classList.add('is-visible'); }),
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

/* ── 스크린리더 전용 ── */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* ── 전체 컨테이너 ── */
.notice-container {
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
}

/* ── 검색 ── */
.search-wrapper {
  margin: 36px 0 24px;
}

.search-input {
  width: 100%;
  padding: 14px 20px;
  border: 1.5px solid #e8ddd5;
  border-radius: 14px;
  font-size: 14px;
  color: #333;
  background: white;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.2s;
}

.search-input:focus {
  border-color: #5d4037;
  /* 색상 외 수단으로도 포커스 표시 */
  box-shadow: 0 0 0 3px rgba(93, 64, 55, 0.2);
}

/* ── 목록 (ul/li 초기화) ── */
.notice-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  list-style: none;
  padding: 0;
  margin: 0;
}

/* ── li 내부 button 전체를 클릭 가능하게 ── */
.notice-item {
  padding: 0;
  overflow: hidden;
}

.notice-item.pinned {
  border-left: 3px solid #5d4037;
}

.notice-item-btn {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  width: 100%;
  background: none;
  border: none;
  cursor: pointer;
  text-align: left;
  transition: transform 0.15s, box-shadow 0.15s;
  border-radius: 16px;
  color: inherit;
  font-family: inherit;
}

.notice-item-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.08);
}

.notice-item-btn:focus-visible {
  outline: 2px solid #5d4037;
  outline-offset: 2px;
}

/* ── 뱃지 ── */
.notice-badge {
  flex-shrink: 0;
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

/* ── 공지 내용 ── */
.notice-content {
  flex: 1;
  min-width: 0;
}

.notice-title {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 4px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  white-space: normal;
}

.notice-date {
  font-size: 12px;
  color: #555;
  /* #000000 → 통일감 있게 조정, 충분한 대비 유지 */
}

.arrow-icon {
  flex-shrink: 0;
  font-size: 20px;
  color: #767676;
  /* #ccc → 대비비 3:1 이상 확보 (장식이지만 최소한의 대비) */
}

/* ── 빈 상태 ── */
.empty-state {
  text-align: center;
  padding: 60px 0;
  color: #767676;
  /* #bbb → 대비비 개선 */
  font-size: 14px;
}

/* ── 모달 오버레이 ── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  /* 0.35 → 0.5으로 배경 뚜렷하게 */
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 24px;
}

/* ── 모달 카드 ── */
.modal-card {
  background: white;
  border-radius: 20px;
  padding: 36px 40px;
  max-width: 620px;
  width: 100%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.15);
  animation: modalIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes modalIn {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.97);
  }

  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.modal-close {
  background: none;
  border: none;
  font-size: 18px;
  color: #555;
  /* #aaa → 대비비 개선 */
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  transition: color 0.2s, background 0.2s;
  line-height: 1;
}

.modal-close:hover {
  color: #1a1a1a;
  background: #f5f0ed;
}

.modal-close:focus-visible {
  outline: 2px solid #5d4037;
  outline-offset: 2px;
}

.modal-title {
  font-size: 20px;
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 8px;
  line-height: 1.4;
}

.modal-date {
  font-size: 13px;
  color: #555;
}

.modal-divider {
  border: none;
  border-top: 1px solid #f0e8e0;
  margin: 20px 0;
}

.modal-body {
  font-size: 14px;
  color: #000000;
  line-height: 1.9;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  white-space: normal;
}

.modal-body p {
  margin-bottom: 10px;
}


/* ── 공통 카드 ── */
.card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

/* ── 모달 하단 버튼 ── */
.modal-footer {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.modal-preview-hint {
  font-size: 12px;
  color: #999;
  margin: 0;
}


.detail-btn {
  padding: 10px 24px;
  background: #5d4037;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.detail-btn:hover {
  background: #3e2723;
}

.detail-btn:focus-visible {
  outline: 3px solid #3e2723;
  outline-offset: 3px;
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

  .modal-card {
    animation: none;
  }
}

/* ── 반응형 ── */
@media (max-width: 600px) {
  .modal-card {
    padding: 28px 24px;
  }

  .notice-title {
    font-size: 14px;
  }
}
</style>
