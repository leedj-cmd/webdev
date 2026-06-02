<template>
  <div class="job-container">
    <header class="job-header reveal" style="--index: 0">
      <p class="subtitle">CAREER OPPORTUNITIES</p>
      <h1 class="title">💼 채용 공고</h1>
      <h3>IT 기업의 최신 기업 정보를 확인하세요.</h3>
    </header>

    <div class="filter-wrapper card reveal" style="--index: 1">
      <div class="filter-top-row">
        <div class="search-box">
          <i class="fas fa-search search-icon"></i>
          <input type="text" v-model="searchQuery" placeholder="공고 명, 회사명 검색" class="search-input">
        </div>

        <div class="sort-options">
          <span :class="{ active: currentSort === 'views' }" @click="currentSort = 'views'">인기순</span>
          <span class="divider">|</span>
          <span :class="{ active: currentSort === 'latest' }" @click="currentSort = 'latest'">최신순</span>
          <span class="divider">|</span>
          <span :class="{ active: currentSort === 'remaining' }" @click="currentSort = 'remaining'">마감순</span>
        </div>
      </div>

      <div class="category-row">
        <button v-for="category in categories" :key="category" @click="selectedCategory = category"
          :class="['tag-btn', { active: selectedCategory === category }]">
          {{ category }}
        </button>
      </div>
    </div>

    <div class="job-grid">
      <div v-for="(job, index) in sortedJobs" :key="job.id" class="job-card card card-hidden"
        :class="{ 'no-link': !job.externalUrl }" :style="{ '--index': index + 2 }" @click="openExternal(job)">
        <div class="card-body">
          <div class="card-top-status">
            <button class="scrap-btn" @click.stop="toggleScrap(job, 'job')"
              :class="{ scrapped: isScrapped(job, 'job') }" :title="isScrapped(job, 'job') ? '스크랩 취소' : '스크랩'">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="bookmark-icon">
                <path d="M5 3h14a1 1 0 0 1 1 1v17l-8-4-8 4V4a1 1 0 0 1 1-1z" />
              </svg>
            </button>
            <span class="d-day-tag" :class="{ 'urgent': job.dDay !== null && job.dDay <= 3 }">
              {{ job.dDay === null ? '상시/확인' : job.dDay === 0 ? '오늘 마감' : `D-${job.dDay}` }}
            </span>
            <span class="view-count">조회 {{ (job.views || 0).toLocaleString() }}</span>
          </div>

          <div class="main-info-section">
            <div class="company-row">
              <p class="company-name-large">{{ job.company }}</p>
              <div class="company-logo-small" :style="{ backgroundColor: job.themeColor || '#ccc' }">
                <span class="logo-text-small">{{ job.logoText || 'C' }}</span>
              </div>
            </div>

            <div class="title-with-logo">
              <h3 class="job-title">{{ job.title }}</h3>
            </div>

            <div class="skills-tags">
              <span v-for="skill in job.skills" :key="skill" class="skill-badge">
                #{{ skill }}
              </span>
            </div>
          </div>

          <div class="card-footer">
            <div class="footer-item">
              <span class="label">연봉</span>
              <span class="value salary">{{ job.salary }}</span>
            </div>
            <div class="footer-item">
              <span class="label">경력</span>
              <span class="value">{{ job.experience }}</span>
            </div>
            <div class="footer-item">
              <span class="label">지역</span>
              <span class="value">{{ job.location }}</span>
            </div>
          </div>
        </div>

        <div class="card-action">
          <button class="apply-btn" :disabled="!job.externalUrl" @click.stop="openExternal(job)">
            {{ job.externalUrl ? '공고 상세보기' : '외부 링크 준비중' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="status-box">채용 공고를 불러오는 중입니다.</div>
    <div v-else-if="loadError" class="status-box error">{{ loadError }}</div>
    <div v-else-if="sortedJobs.length === 0" class="status-box">조건에 맞는 채용 공고가 없습니다.</div>
  </div>
</template>

<script>
import api from '@/api/axios';

const THEME_COLORS = ['#0050FF', '#03C75A', '#FEE500', '#E1251B', '#0747AD', '#5d4037', '#2f855a'];

export default {
  data() {
    return {
      searchQuery: '',
      selectedCategory: '전체', // 필터링을 위해 반드시 필요
      categories: ['전체', '신입', '경력', '인턴', '정규직', '계약직', '프리랜서'],
      currentSort: 'views',
      scrappedIds: [],
      currentUserId: null,
      jobs: [],
      isLoading: false,
      loadError: '',
      refreshTimer: null,
      refreshIntervalMs: 60000
    }
  },
  computed: {
    filteredJobs() {
      // 1. 기본 데이터가 없으면 빈 배열 반환
      if (!this.jobs || !Array.isArray(this.jobs)) return [];

      // 2. 검색어와 선택된 카테고리를 가져옴 (trim으로 공백 제거)
      const query = this.searchQuery ? this.searchQuery.toLowerCase().trim() : '';
      const category = this.selectedCategory;

      // 3. 필터링 로직 하나로 통합
      return this.jobs.filter(job => {
        // 카테고리 조건: '전체'거나 데이터의 category와 일치해야 함
        const matchCategory = (category === '전체') || (job.category === category);

        // 검색어 조건: 제목, 회사명, 설명, 직무카테고리에 포함되어야 함
        const matchQuery = !query ||
          (job.title && job.title.toLowerCase().includes(query)) ||
          (job.company && job.company.toLowerCase().includes(query)) ||
          (job.description && job.description.toLowerCase().includes(query)) ||
          (job.job_category && job.job_category.toLowerCase().includes(query));

        // 두 조건을 모두 만족해야 화면에 표시됨
        return matchCategory && matchQuery;
      });
    },
    // sortedJobs는 수정된 filteredJobs를 기반으로 정렬만 수행
    sortedJobs() {
      const list = [...this.filteredJobs];
      if (this.currentSort === 'views') return list.sort((a, b) => (b.views || 0) - (a.views || 0));
      if (this.currentSort === 'latest') return list.sort((a, b) => new Date(b.date || 0) - new Date(a.date || 0));
      if (this.currentSort === 'remaining') return list.sort((a, b) => (a.dDay ?? 9999) - (b.dDay ?? 9999));
      return list;
    }
  },
  watch: {
    sortedJobs() {
      this.$nextTick(() => this.initReveal());
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
          this.fetchJobs(),
          this.fetchCurrentUser(),
          this.fetchMyScraps()
        ]);
        this.initReveal();
        this.startAutoRefresh();
      } catch (e) {
        console.error("Initialization error:", e);
      }
    },
    startAutoRefresh() {
      this.stopAutoRefresh();
      this.refreshTimer = window.setInterval(() => {
        this.fetchJobs({ silent: true });
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
      const targets = document.querySelectorAll(".reveal, .card-hidden"); // ← 수정

      if (targets.length === 0) {
        setTimeout(() => this.initReveal(), 200);
        return;
      }
      targets.forEach((el) => observer.observe(el));
    },
    async fetchJobs(options = {}) {
      const silent = Boolean(options.silent);
      if (!silent) {
        this.isLoading = true;
        this.loadError = '';
      }
      try {
        const { data } = await api.get('/jobs/', { params: { limit: 100 } });
        this.jobs = Array.isArray(data) ? data.map(this.mapJob) : [];
        this.$nextTick(() => this.initReveal());
      } catch (e) {
        console.error('채용 공고 로드 실패:', e);
        if (!silent) {
          this.loadError = '채용 공고를 불러오지 못했습니다. 백엔드 서버 상태를 확인해 주세요.';
          this.jobs = [];
        }
      } finally {
        if (!silent) this.isLoading = false;
      }
    },
    mapJob(job) {
      const index = Math.max(0, Number(job.id || 1) - 1);
      const description = job.description || '';
      const skills = description
        .split(/[,#\n]/)
        .map((item) => item.trim())
        .filter(Boolean)
        .slice(0, 3);

      return {
        id: job.id,
        company: job.company || '회사명 미정',
        title: job.title || '제목 없음',
        dDay: this.getDday(job.deadline),
        location: job.region || '지역 미정',
        experience: job.experience || '경력 무관',
        salary: job.education || '협의',
        views: job.scrap_count || 0,
        date: job.created_at,
        themeColor: THEME_COLORS[index % THEME_COLORS.length],
        logoText: (job.company || 'C').trim().charAt(0).toUpperCase(),
        skills: skills.length ? skills : [job.job_category || '채용'],
        category: this.getJobCategory(job.experience, job.job_category),
        externalUrl: this.normalizeUrl(job.external_url),
        isExternal: Boolean(job.is_external),
        source: job.source || ''
      };
    },
    getJobCategory(experience, jobCategory) {
      const text = `${experience || ''} ${jobCategory || ''}`;
      if (text.includes('인턴')) return '인턴';
      if (text.includes('계약')) return '계약직';
      if (text.includes('프리랜서')) return '프리랜서';
      if (text.includes('정규')) return '정규직';
      if (text.includes('신입')) return '신입';
      if (text.includes('경력')) return '경력';
      return jobCategory || '전체';
    },
    getDday(deadline) {
      if (!deadline) return null;
      const today = new Date();
      const end = new Date(deadline);
      today.setHours(0, 0, 0, 0);
      end.setHours(0, 0, 0, 0);
      return Math.max(0, Math.ceil((end - today) / (1000 * 60 * 60 * 24)));
    },
    normalizeUrl(url) {
      if (!url || typeof url !== 'string') return '';
      const trimmed = url.trim();
      if (!trimmed) return '';
      return /^https?:\/\//i.test(trimmed) ? trimmed : `https://${trimmed}`;
    },
    openExternal(job) {
      if (!job.externalUrl) {
        alert('아직 연결된 외부 공고 링크가 없습니다.');
        return;
      }
      window.open(job.externalUrl, '_blank', 'noopener,noreferrer');
    },
    async fetchCurrentUser() {
      const token = localStorage.getItem('access_token');
      if (!token) return;
      try {
        const res = await api.get('/auth/me');
        this.currentUserId = res.data.id;
      } catch (e) { console.error("User fetch failed", e); }
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
        subtitle: [item.company, item.location, item.experience].filter(Boolean).join(' · '),
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
          // 1. 스크랩 취소 로직
          const res = await api.get('/scraps/');

          if (res.data && Array.isArray(res.data)) {
            // 채용 공고(job)이므로 job_id로 비교해서 찾음
            const scrap = res.data.find(s => this.getScrapKeyFromResponse(s) === key);
            if (scrap) {
              await api.delete(`/scraps/${scrap.id}`);
            }
          }
        } else {
          this.scrappedIds = [...this.scrappedIds, key];
          // 2. 스크랩 추가 로직
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
.job-container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 60px 40px;
  font-family: 'Pretendard', sans-serif;
}

.filter-wrapper {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 25px;
  border-radius: 15px;
  background: white;
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
  transition: 0.3s;
}

.sort-options span.active {
  color: #5d4037;
  font-weight: 700;
}

.subtitle {
  color: #a68b6a;
  font-weight: 700;
  margin-bottom: 10px;
}

.job-grid {
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

.card-hidden {
  opacity: 0;
  transform: translateY(20px);
  filter: blur(8px);
  transition: opacity 0.8s ease-out,
    filter 0.8s ease-out,
    transform 0.8s ease-out,
    box-shadow 0.3s ease,
    border-color 0.3s ease;
}

.card-hidden.is-visible {
  opacity: 1;
  transform: translateY(0);
  filter: blur(0);
}

.card-hidden.is-visible:hover {
  transform: translateY(-8px) scale(1.03);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.12);
  border-color: #5d4037;
}


.card-body {
  padding: 40px 50px;
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

.job-title {
  font-size: 19px;
  font-weight: 700;
  color: #5d4037;
  margin-bottom: 12px;
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
  margin-top: 20px;
  border-top: 1px solid #f5f5f5;
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

.card-action {
  padding: 0 50px 40px;
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

/* 애니메이션 */
.reveal {
  opacity: 0;
  transform: translateY(2rem);
  transition: all 0.9s cubic-bezier(0.16, 1, 0.3, 1);
}

.reveal.is-visible {
  opacity: 1;
  transform: translateY(0);
}

@media (max-width: 900px) {
  .job-grid {
    grid-template-columns: 1fr;
  }

  .filter-top-row {
    align-items: stretch;
    flex-direction: column;
  }

  .search-input {
    width: 100%;
  }

  .card-body {
    padding: 30px;
  }

  .card-action {
    padding: 0 30px 30px;
  }
}
</style>
