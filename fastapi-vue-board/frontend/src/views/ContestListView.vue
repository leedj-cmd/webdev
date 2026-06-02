<template>
  <div class="contest-container">
    <header class="contest-header reveal" style="--index: 0">
      <p class="subtitle">CONTEST & CHALLENGE</p>
      <h1 class="title">🏆 공모전</h1>
      <h3>IT 공모전과 해커톤에 도전하세요.</h3>
    </header>

    <div class="filter-wrapper card reveal" style="--index: 1">
      <div class="filter-top-row">
        <div class="search-box">
          <input type="text" v-model="searchQuery" placeholder="공모전 명, 주최 기관, 분야 검색" class="search-input">
        </div>

        <div class="sort-options">
          <span :class="{ active: currentSort === 'popular' }" @click="currentSort = 'popular'">인기순</span>
          <span class="divider">|</span>
          <span :class="{ active: currentSort === 'latest' }" @click="currentSort = 'latest'">최신순</span>
          <span class="divider">|</span>
          <span :class="{ active: currentSort === 'prize' }" @click="currentSort = 'prize'">상금순</span>
        </div>
      </div>

      <div class="category-row">
        <button v-for="category in categories" :key="category" @click="selectedCategory = category"
          :class="['tag-btn', { active: selectedCategory === category }]">
          {{ category }}
        </button>
      </div>
    </div>

    <div class="contest-grid">
      <div v-for="(contest, index) in sortedContests" :key="contest.id" class="contest-card card card-hidden"
        :class="{ 'no-link': !contest.externalUrl }" :style="{ '--index': index + 2 }" @click="openExternal(contest)">

        <div class="card-body">
          <div class="card-top-status">
            <button class="scrap-btn" @click.stop="toggleScrap(contest, 'contest')"
              :class="{ scrapped: isScrapped(contest, 'contest') }"
              :title="isScrapped(contest, 'contest') ? '스크랩 취소' : '스크랩'">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="bookmark-icon">
                <path d="M5 3h14a1 1 0 0 1 1 1v17l-8-4-8 4V4a1 1 0 0 1 1-1z" />
              </svg>
            </button>
            <span class="d-day-tag" :class="{ 'urgent': contest.dDay !== null && contest.dDay <= 7 }">
              {{ contest.dDay === null ? '상시/확인' : contest.dDay === 0 ? '오늘 마감' : `D-${contest.dDay}` }}
            </span>
            <span class="view-count">조회 {{ (contest.views || 0).toLocaleString() }}</span>
          </div>

          <div class="main-info-section">
            <div class="company-row">
              <p class="company-name-large">{{ contest.organizer }}</p>
              <div class="company-logo-small" :style="{ backgroundColor: contest.themeColor || '#ccc' }">
                <span class="logo-text-small">{{ contest.logoText || 'C' }}</span>
              </div>
            </div>

            <h3 class="contest-title">{{ contest.title }}</h3>

            <div class="skills-tags">
              <span v-for="tag in contest.tags" :key="tag" class="skill-badge">
                #{{ tag }}
              </span>
            </div>
          </div>

          <div class="card-footer">
            <div class="footer-item">
              <span class="label">총 시상금</span>
              <span class="value salary">{{ contest.prize }}</span>
            </div>
            <div class="footer-item">
              <span class="label">참가대상</span>
              <span class="value">{{ contest.target }}</span>
            </div>
            <div class="footer-item">
              <span class="label">혜택</span>
              <span class="value">{{ contest.benefit }}</span>
            </div>
          </div>
        </div>

        <div class="card-action">
          <button class="apply-btn" :disabled="!contest.externalUrl" @click.stop="openExternal(contest)">
            {{ contest.externalUrl ? '공모전 상세정보' : '외부 링크 준비중' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="status-box">공모전 정보를 불러오는 중입니다.</div>
    <div v-else-if="loadError" class="status-box error">{{ loadError }}</div>
    <div v-else-if="sortedContests.length === 0" class="status-box">조건에 맞는 공모전이 없습니다.</div>
  </div>
</template>

<script>
import api from '@/api/axios';

const THEME_COLORS = ['#FEE500', '#03C75A', '#0747AD', '#1e3a8a', '#5d4037', '#0050FF', '#2f855a'];

export default {
  data() {
    return {
      scrappedIds: [],
      currentUserId: null,
      searchQuery: '',
      selectedCategory: '전체',
      categories: ['전체', '기획', '아이디어', '디자인', '개발/SW', '논문/학술'],
      currentSort: 'popular',
      contests: [],
      isLoading: false,
      loadError: '',
      refreshTimer: null,
      refreshIntervalMs: 60000
    }
  },
  watch: {
    // 카테고리, 검색어, 정렬이 바뀌면 카드가 재렌더링되므로 initReveal 재실행
    sortedContests() {
      this.$nextTick(() => this.initReveal());
    }
  },
  computed: {
    filteredContests() {
      if (!this.contests || !Array.isArray(this.contests)) return [];
      let list = [...this.contests];

      // 카테고리 필터링
      if (this.selectedCategory !== '전체') {
        list = list.filter(item => item.category === this.selectedCategory);
      }

      // 검색어 필터링
      if (this.searchQuery) {
        const q = this.searchQuery.toLowerCase();
        list = list.filter(c =>
          (c.title && c.title.toLowerCase().includes(q)) ||
          (c.organizer && c.organizer.toLowerCase().includes(q)) ||
          (c.description && c.description.toLowerCase().includes(q)) ||
          (c.category && c.category.toLowerCase().includes(q)) ||
          (c.tags && c.tags.some(tag => tag.toLowerCase().includes(q)))
        );
      }
      return list;
    },
    sortedContests() {
      let list = [...this.filteredContests];

      if (this.currentSort === 'popular') {
        // 인기순 (조회수 기준)
        list.sort((a, b) => (b.views || 0) - (a.views || 0));
      } else if (this.currentSort === 'latest') {
        // 최신순 (날짜 기준)
        list.sort((a, b) => new Date(b.date || 0) - new Date(a.date || 0));
      } else if (this.currentSort === 'prize') {
        // 상금순 정렬 로직 수정
        list.sort((a, b) => {
          // '5,000만원' 같은 문자열에서 숫자만 추출하는 함수
          const getPrizeNumber = (prizeStr) => {
            if (!prizeStr) return 0;
            // 숫자가 아닌 모든 문자(쉼표, 만원 등)를 제거하고 숫자로 변환
            const num = parseInt(prizeStr.toString().replace(/[^0-9]/g, ''));
            return isNaN(num) ? 0 : num;
          };

          const prizeA = getPrizeNumber(a.prize);
          const prizeB = getPrizeNumber(b.prize);

          return prizeB - prizeA; // 상금이 큰 순서대로(내림차순)
        });
      }
      return list;
    }
  },
  mounted() {
    this.$nextTick(() => {
      setTimeout(async () => {
        await this.initializePage();
      }, 200);
    });
  },
  beforeUnmount() {
    this.stopAutoRefresh();
  },
  methods: {
    async initializePage() {
      try {
        await Promise.allSettled([
          this.fetchContests(),
          this.fetchCurrentUser(),
          this.fetchMyScraps()
        ]);
        this.initReveal();
        this.startAutoRefresh();
      } catch (error) {
        console.error("초기화 중 오류 발생:", error);
      }
    },
    startAutoRefresh() {
      this.stopAutoRefresh();
      this.refreshTimer = window.setInterval(() => {
        this.fetchContests({ silent: true });
        this.fetchMyScraps();
      }, this.refreshIntervalMs);
    },
    stopAutoRefresh() {
      if (this.refreshTimer) {
        window.clearInterval(this.refreshTimer);
        this.refreshTimer = null;
      }
    },
    initReveal() {
      const observerCallback = (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
          }
        });
      };
      const observer = new IntersectionObserver(observerCallback, { threshold: 0.1 });

      // .reveal(헤더, 검색창) + .card-hidden(카드) 둘 다 감지
      const targets = document.querySelectorAll(".reveal, .card-hidden");

      if (targets.length === 0) {
        setTimeout(() => this.initReveal(), 200);
        return;
      }
      targets.forEach((el) => observer.observe(el));
    },
    async fetchContests(options = {}) {
      const silent = Boolean(options.silent);
      if (!silent) {
        this.isLoading = true;
        this.loadError = '';
      }
      try {
        const { data } = await api.get('/contests/', { params: { limit: 100 } });
        this.contests = Array.isArray(data) ? data.map(this.mapContest) : [];
        this.$nextTick(() => this.initReveal());
      } catch (e) {
        console.error('공모전 로드 실패:', e);
        if (!silent) {
          this.loadError = '공모전 정보를 불러오지 못했습니다. 백엔드 서버 상태를 확인해 주세요.';
          this.contests = [];
        }
      } finally {
        if (!silent) this.isLoading = false;
      }
    },
    mapContest(contest) {
      const index = Math.max(0, Number(contest.id || 1) - 1);
      const description = contest.description || '';
      const tags = description
        .split(/[,#\n]/)
        .map((item) => item.trim())
        .filter(Boolean)
        .slice(0, 3);

      return {
        id: contest.id,
        organizer: contest.organizer || '주최 미정',
        title: contest.title || '제목 없음',
        dDay: this.getDday(contest.deadline),
        target: contest.target || '제한 없음',
        prize: contest.prize || '시상 내역 확인',
        benefit: contest.start_date ? `시작 ${this.formatDate(contest.start_date)}` : '상세 페이지 확인',
        views: contest.scrap_count || 0,
        date: contest.created_at,
        themeColor: THEME_COLORS[index % THEME_COLORS.length],
        logoText: (contest.organizer || 'C').trim().charAt(0).toUpperCase(),
        tags: tags.length ? tags : [contest.category || '공모전'],
        category: contest.category || '전체',
        externalUrl: this.normalizeUrl(contest.external_url),
        isExternal: Boolean(contest.is_external),
        source: contest.source || ''
      };
    },
    getDday(deadline) {
      if (!deadline) return null;
      const today = new Date();
      const end = new Date(deadline);
      today.setHours(0, 0, 0, 0);
      end.setHours(0, 0, 0, 0);
      return Math.max(0, Math.ceil((end - today) / (1000 * 60 * 60 * 24)));
    },
    formatDate(date) {
      if (!date) return '';
      return new Date(date).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' });
    },
    normalizeUrl(url) {
      if (!url || typeof url !== 'string') return '';
      const trimmed = url.trim();
      if (!trimmed) return '';
      return /^https?:\/\//i.test(trimmed) ? trimmed : `https://${trimmed}`;
    },
    openExternal(contest) {
      if (!contest.externalUrl) {
        alert('아직 연결된 외부 공모전 링크가 없습니다.');
        return;
      }
      window.open(contest.externalUrl, '_blank', 'noopener,noreferrer');
    },
    async fetchCurrentUser() {
      const token = localStorage.getItem('access_token');
      if (!token) return;
      try {
        const res = await api.get('/auth/me');
        this.currentUserId = res.data.id;
      } catch (e) { console.error("사용자 정보 로드 실패"); }
    },
    async fetchMyScraps() {
      const token = localStorage.getItem('access_token');
      if (!token) return;
      try {
        const res = await api.get('/scraps/');
        if (res.data && Array.isArray(res.data)) {
          this.scrappedIds = res.data.map(this.getScrapKeyFromResponse).filter(Boolean);
        }
      } catch (e) { this.scrappedIds = []; }
    },
    getScrapKeyFromResponse(scrap) {
      if (scrap.external_id) return `${scrap.scrap_type}:external:${scrap.external_id}`;
      if (scrap.job_id) return `job:${scrap.job_id}`;
      if (scrap.contest_id) return `contest:${scrap.contest_id}`;
      return '';
    },
    getScrapKey(item, type) {
      return item.isExternal ? `${type}:external:${item.id}` : `${type}:${item.id}`;
    },
    isScrapped(item, type) {
      return this.scrappedIds.includes(this.getScrapKey(item, type));
    },
    buildScrapPayload(item, type) {
      return {
        scrap_type: type,
        target_id: item.id,
        title: item.title,
        subtitle: [item.organizer, item.category, item.target].filter(Boolean).join(' · '),
        external_url: item.externalUrl,
        is_external: item.isExternal
      };
    },
    async toggleScrap(item, type) {
      const token = localStorage.getItem('access_token');
      if (!token) {
        alert('로그인 후 이용할 수 있습니다.');
        return;
      }

      const key = this.getScrapKey(item, type);
      const isScrapped = this.scrappedIds.includes(key);

      try {
        if (isScrapped) {
          this.scrappedIds = this.scrappedIds.filter(id => id !== key);
          const res = await api.get('/scraps/');

          if (res.data && Array.isArray(res.data)) {
            // 공모전이므로 contest_id로 비교
            const scrap = res.data.find(s => this.getScrapKeyFromResponse(s) === key);
            if (scrap) {
              await api.delete(`/scraps/${scrap.id}`);
            }
          }
        } else {
          this.scrappedIds = [...this.scrappedIds, key];
          await api.post('/scraps/', this.buildScrapPayload(item, type));
        }
        window.dispatchEvent(new CustomEvent('scraps-updated'));
      } catch (e) {
        console.error("스크랩 처리 중 에러:", e);
        await this.fetchMyScraps();
        alert(e.response?.data?.detail || '스크랩 처리 중 오류가 발생했습니다.');
      }
    }
  }
}
</script>

<style scoped>
.contest-container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 60px 40px;
  font-family: 'Pretendard', sans-serif;
}

.title {
  font-size: 34px;
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 5px;
}

.subtitle {
  color: #a68b6a;
  font-weight: 700;
  margin-bottom: 10px;
}

.filter-wrapper {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 25px;
  background: white;
  border-radius: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.filter-top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  gap: 20px;
}

.search-input {
  border: none;
  background: #f2f0ed;
  padding: 12px 20px;
  border-radius: 12px;
  width: 400px;
  outline: none;
}

.sort-options {
  white-space: nowrap;
  font-size: 14px;
  color: #bbb;
}

.sort-options span {
  cursor: pointer;
  margin: 0 10px;
}

.sort-options span.active {
  color: #5d4037;
  font-weight: 700;
}

.contest-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 25px;

}

.card {
  background: white;
  border-radius: 28px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.03);
  /* 부드러운 변화를 위해 반드시 필요 (0.3초 동안 부드럽게) */
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;

  /* 마우스 커서 모양 변경 */
  cursor: pointer;
}

.card.no-link {
  cursor: default;
}

.card:hover {
  /* 1.03배로 살짝 확대 (너무 크면 옆 카드와 겹치니 적당하게) */
  transform: translateY(-8px) scale(1.03);

  /* 그림자를 더 진하게 해서 붕 떠 있는 느낌 주기 */
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.12);

  /* 선택되었다는 느낌을 주기 위해 테두리 색상 강조 (선택 사항) */
  border-color: #5d4037;
}

.category-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-btn {
  padding: 8px 18px;
  border-radius: 25px;
  border: 1px solid #eee;
  background: white;
  color: #888;
  font-size: 13px;
  cursor: pointer;
}

.tag-btn.active {
  background: #5d4037;
  color: white;
  border-color: #5d4037;
}

.card-body {
  padding: 35px;
}

.card-top-status {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
  margin-bottom: 15px;
}

.d-day-tag {
  background: #f0e6db;
  color: #8d6e63;
  padding: 3px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 800;
}

.d-day-tag.urgent {
  background: #ffebee;
  color: #e53935;
}

.view-count {
  font-size: 12px;
  color: #ccc;
}

.company-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.company-name-large {
  font-size: 26px;
  font-weight: 800;
  color: #1a1a1a;
}

.company-logo-small {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-text-small {
  color: white;
  font-size: 16px;
  font-weight: 800;
}

.contest-title {
  font-size: 19px;
  font-weight: 700;
  color: #5d4037;
  margin-bottom: 12px;
}

.skill-badge {
  font-size: 12px;
  color: #a68b6a;
  background: #fdfaf7;
  padding: 2px 8px;
  border-radius: 4px;
  margin-right: 5px;
}

.card-footer {
  display: flex;
  gap: 30px;
  padding-top: 20px;
  border-top: 1px solid #f5f5f5;
  margin-top: 20px;
}

.footer-item {
  display: flex;
  flex-direction: column;
}

.label {
  font-size: 11px;
  color: #bbb;
}

.value {
  font-size: 14px;
  color: #555;
  font-weight: 600;
}

.salary {
  color: #5d4037;
}

.card-action {
  padding: 0 35px 35px 35px;
}

.apply-btn {
  width: 100%;
  background: #f8f6f3;
  border: none;
  padding: 15px;
  border-radius: 18px;
  color: #5d4037;
  font-weight: 700;
  cursor: pointer;
}

.apply-btn:hover {
  background: #5d4037;
  color: white;
}

.apply-btn:disabled {
  cursor: not-allowed;
  color: #aaa;
  background: #f3f3f3;
}

.apply-btn:disabled:hover {
  color: #aaa;
  background: #f3f3f3;
}

.status-box {
  margin-top: 24px;
  padding: 24px;
  border-radius: 12px;
  background: #f8f6f3;
  color: #5d4037;
  text-align: center;
  font-weight: 700;
}

.status-box.error {
  background: #ffebee;
  color: #c62828;
}

/* 배경과 테두리를 없앤 스크랩 버튼 */
.scrap-btn {
  background: none;
  border: none;
  outline: none;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s ease;
  margin-right: auto;
  /* 기존처럼 왼쪽 정렬 유지 */
}

/* 호버 시 살짝 커지는 효과 */
.scrap-btn:hover {
  transform: scale(1.1);
}

.scrap-btn:disabled,
.scrap-btn.disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

.scrap-btn:disabled:hover,
.scrap-btn.disabled:hover {
  transform: none;
}

/* 북마크 아이콘 기본 스타일 */
.bookmark-icon {
  width: 24px;
  height: 24px;
  fill: none;
  stroke: #ccc;
  stroke-width: 2;
  transition: all 0.3s ease;
}

/* 스크랩 활성화 상태 */
.scrapped .bookmark-icon {
  fill: #5d4037;
  stroke: #5d4037;
}

/* 호버 시 테두리 색상 변경 */
.scrap-btn:hover .bookmark-icon {
  stroke: #5d4037;
}

/* Reveal 애니메이션 */
.reveal {
  opacity: 0;
  transform: translateY(2rem);
  filter: blur(8px);
  transition: all 0.9s cubic-bezier(0.16, 1, 0.3, 1);
}

.reveal.is-visible {
  opacity: 1;
  transform: translateY(0);
  filter: blur(0);
}

/* 카드 전용 애니메이션 (기존 .reveal은 건드리지 않음) */
.card-hidden {
  opacity: 0;
  transform: translateY(2rem);
  filter: blur(8px);
  /* reveal 애니메이션 + hover 애니메이션 동시에 선언 */
  transition: opacity 0.9s cubic-bezier(0.16, 1, 0.3, 1),
    filter 0.9s cubic-bezier(0.16, 1, 0.3, 1),
    transform 0.9s cubic-bezier(0.16, 1, 0.3, 1),
    box-shadow 0.3s ease,
    border-color 0.3s ease;
}

.card-hidden.is-visible {
  opacity: 1;
  transform: translateY(0);
  filter: blur(0);
}

/* hover는 카드가 나타난 후에만 동작 */
.card-hidden.is-visible:hover {
  transform: translateY(-8px) scale(1.03);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.12);
  border-color: #5d4037;
}

@media (max-width: 900px) {
  .contest-grid {
    grid-template-columns: 1fr;
  }

  .filter-top-row {
    align-items: stretch;
    flex-direction: column;
  }

  .search-input {
    width: 100%;
  }
}
</style>
