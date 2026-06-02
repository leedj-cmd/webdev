<template>
  <main class="home-page">
    <section v-if="hasSearchQuery" class="search-results-section page-shell">
      <div class="search-results-head">
        <div>
          <span class="eyebrow">Search Results</span>
          <h2>
            "{{ searchTerm }}" 검색 결과
            <span>{{ totalSearchResults }}건</span>
          </h2>
        </div>
        <RouterLink to="/" class="panel-link">검색 초기화</RouterLink>
      </div>

      <div v-if="searchLoading" class="empty-state search-state">검색 결과를 불러오는 중입니다.</div>
      <div v-else-if="searchError" class="empty-state search-state">{{ searchError }}</div>
      <div v-else-if="!totalSearchResults" class="empty-state search-state">조건에 맞는 결과가 없습니다.</div>

      <div v-else class="search-result-grid">
        <article v-for="group in searchResultGroups" :key="group.key" class="double-shell search-result-panel">
          <div class="double-core search-result-core">
            <div class="search-result-header">
              <span>{{ group.label }}</span>
              <strong>{{ group.items.length }}건</strong>
            </div>

            <div v-if="group.items.length" class="card-list">
              <button
                v-for="item in group.items.slice(0, 5)"
                :key="`${group.key}-${item.id || item.external_url || item.resultTitle}`"
                type="button"
                class="item-card search-result-card"
                @click="openSearchResult(group.key, item)"
              >
                <span class="cat-chip">{{ item.resultBadge }}</span>
                <strong>{{ item.resultTitle }}</strong>
                <small>{{ item.resultSubtitle }}</small>
                <p v-if="item.resultDescription">{{ item.resultDescription }}</p>
              </button>
              
              <RouterLink 
                v-if="group.items.length > 5" 
                :to="{ path: group.link, query: { search: searchTerm } }" 
                class="more-results-link"
              >
                {{ group.label }} 검색 결과 더보기
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </RouterLink>
            </div>

            <div v-else class="empty-state">해당 영역의 결과가 없습니다.</div>
          </div>
        </article>
      </div>
    </section>

    <section class="hero-section">
      <svg class="hero-signal-map" viewBox="0 0 1440 620" preserveAspectRatio="none" aria-hidden="true">
        <path class="signal-line signal-line-secondary" d="M40 355 C260 210 420 240 590 330 S960 500 1395 240" />
        <path class="signal-line signal-line-primary" d="M115 450 C340 320 520 390 705 300 S1010 155 1325 305" />
        <path class="signal-line signal-line-dotted" d="M205 200 C410 120 615 170 780 245 S1045 395 1235 145" />
      </svg>
      <div class="hero-grid page-shell">
        <div class="hero-copy reveal" style="--index: 0">
          <span class="eyebrow">Developer Career Radar</span>
          <p class="hero-subtitle">
            채용, 공모전, 커뮤니티 글이 따로 흩어지지 않도록 지금 중요한 정보만 압축해 보여줍니다.
            급하게 찾는 순간에도 바로 행동으로 이어질 수 있게 구성했습니다.
          </p>

          <article class="hero-signal-card double-shell">
            <div class="double-core hero-signal-core">
              <div class="signal-copy">
                <span class="signal-kicker">TechBridge Signal</span>
                <strong>TechBridge는 흩어진 커리어 정보를 하나의 흐름으로 연결합니다.</strong>
                <p>필요한 순간에 채용, 공모전, 커뮤니티 인사이트가 같은 방향을 가리키도록 첫 화면부터 정리해 둡니다.</p>
              </div>
              <div class="signal-orbit" aria-hidden="true">
                <span class="orbit-ring"></span>
                <span class="orbit-track">
                  <span class="orbit-node orbit-node-jobs">
                    <span class="orbit-label">Jobs</span>
                  </span>
                  <span class="orbit-node orbit-node-contests">
                    <span class="orbit-label">Awards</span>
                  </span>
                  <span class="orbit-node orbit-node-posts">
                    <span class="orbit-label">Posts</span>
                  </span>
                </span>
                <span class="orbit-core">TB</span>
              </div>
            </div>
          </article>

          <div class="hero-actions">
            <RouterLink to="/jobs" class="primary-cta">
              인기 채용 보기
              <span class="btn-icon">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                  <path d="M5 12h14" />
                  <path d="m13 5 7 7-7 7" />
                </svg>
              </span>
            </RouterLink>
            <RouterLink to="/posts" class="secondary-cta">오늘 게시글 둘러보기</RouterLink>
          </div>
        </div>

        <div class="hero-stack">
          <article class="terminal-card reveal" style="--index: 1">
            <div class="terminal-bar">
              <div class="terminal-controls" aria-hidden="true">
                <span class="terminal-dot red"></span>
                <span class="terminal-dot yellow"></span>
                <span class="terminal-dot green"></span>
              </div>
              <span class="terminal-title">techbridge.scan</span>
            </div>
            <div class="terminal-code" aria-label="오늘의 집중 영역">
              <p><span class="code-muted">$</span> <span class="code-green">techbridge</span> <span class="code-blue">scan</span> <span class="code-orange">--today</span></p>
              <p class="code-spacer"></p>
              <p><span class="code-blue">jobs</span> <span class="code-muted">......</span> <span class="code-string">백엔드 · 프론트엔드 · 신입 공고</span></p>
              <p><span class="code-blue">contests</span> <span class="code-muted">..</span> <span class="code-string">AI · 데이터 · 마감 임박</span></p>
              <p><span class="code-blue">community</span> <span class="code-muted">.</span> <span class="code-string">면접 후기 · 프로젝트 회고</span></p>
              <p class="code-spacer"></p>
              <p><span class="code-green">status</span> <span class="code-muted">....</span> <span class="code-white">next step is ready</span></p>
            </div>
          </article>
        </div>
      </div>
    </section>

    <section class="dashboard-section page-shell">
      <div class="section-head reveal" style="--index: 0">
        <div>
          <span class="eyebrow">Curated Feed</span>
          <h2>
            놓치면 안 되는
            <span class="section-title-accent">커리어 신호</span>
          </h2>
        </div>
        <div class="section-brief">
          <div class="section-summary">
            <div v-for="summary in feedSummaries" :key="summary.label" class="summary-item">
              <span class="summary-dot" :style="{ background: summary.color }"></span>
              <span class="summary-label">{{ summary.label }}</span>
              <strong>{{ summary.value }}</strong>
              <small>{{ summary.caption }}</small>
            </div>
          </div>
        </div>
      </div>

      <div class="dashboard-grid">
        <div class="dashboard-column dashboard-column-main">
          <!-- 최근 게시글 -->
          <article class="double-shell panel panel-posts reveal" style="--index: 1">
          <div class="double-core panel-core">
            <div class="panel-header">
              <div>
                <span class="panel-kicker">Posts</span>
                <h3>최근 게시글</h3>
              </div>
              <RouterLink to="/posts" class="panel-link">더보기</RouterLink>
            </div>
            <div class="card-list">
              <article
                v-for="post in recentPosts" :key="post.id"
                class="item-card clickable"
                @click="goToPost(post.id)"
              >
                <div class="item-top">
                  <div class="author-row">
                    <div class="avatar-sm" :style="{ background: post.avatarColor }">{{ post.author[0] }}</div>
                    <span class="author-name">{{ post.author }}</span>
                    <span v-if="post.category" class="cat-chip">{{ post.category }}</span>
                  </div>
                  <time class="item-time">{{ post.time }}</time>
                </div>
                <h4 class="item-title">{{ post.title }}</h4>
                <div class="item-footer">
                  <span class="stat-item">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
                    {{ post.likes }}
                  </span>
                  <span class="stat-item">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                    {{ post.comments }}
                  </span>
                </div>
              </article>
              <div v-if="!recentPosts.length" class="empty-state">게시글을 불러오는 중입니다.</div>
            </div>
          </div>
          </article>

          <!-- 커뮤니티 -->
          <article class="double-shell panel panel-community reveal" style="--index: 4">
            <div class="double-core panel-core">
              <div class="panel-header">
                <div>
                  <span class="panel-kicker">Community</span>
                  <h3>커뮤니티 글</h3>
                </div>
                <RouterLink to="/community" class="panel-link">더보기</RouterLink>
              </div>
              <div class="community-grid">
                <article
                  v-for="post in communityPosts" :key="post.id"
                  class="item-card community-item clickable"
                  @click="goToCommunity(post.id)"
                >
                  <div class="item-top">
                    <span class="cat-chip">{{ post.categoryLabel }}</span>
                    <time class="item-time">{{ post.time }}</time>
                  </div>
                  <h4 class="item-title">{{ post.title }}</h4>
                  <p v-if="post.content" class="item-preview">{{ post.content }}</p>
                  <div class="item-footer">
                    <div class="author-row-sm">
                      <div class="avatar-sm" :style="{ background: post.avatarColor }">{{ post.author[0] }}</div>
                      <span class="author-name">{{ post.author }}</span>
                    </div>
                    <div class="stat-row">
                      <span class="stat-item">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
                        {{ post.like_count || 0 }}
                      </span>
                      <span class="stat-item">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                        {{ post.comment_count || 0 }}
                      </span>
                    </div>
                  </div>
                </article>
                <div v-if="!communityPosts.length" class="empty-state community-empty">커뮤니티 글을 불러오는 중입니다.</div>
              </div>
            </div>
          </article>
        </div>

        <div class="dashboard-column dashboard-column-side">
          <!-- 채용 공고 -->
          <article class="double-shell panel panel-jobs reveal" style="--index: 2">
          <div class="double-core panel-core">
            <div class="panel-header">
              <div>
                <span class="panel-kicker">Jobs</span>
                <h3>추천 채용</h3>
              </div>
              <RouterLink to="/jobs" class="panel-link">더보기</RouterLink>
            </div>
            <div class="card-list">
              <article
                v-for="job in jobPostings" :key="job.id"
                class="item-card job-item clickable"
                @click="goToJob(job)"
              >
                <div class="item-top">
                  <div class="company-badge">{{ (job.company || '?')[0] }}</div>
                  <div class="company-info">
                    <strong class="company-name">{{ job.company }}</strong>
                    <span class="job-title-text">{{ job.title }}</span>
                  </div>
                </div>
                <div class="job-meta-row">
                  <span v-if="job.location" class="meta-tag">📍 {{ job.location }}</span>
                  <span v-if="job.experience" class="meta-tag">{{ job.experience }}</span>
                </div>
                <div v-if="job.tags.length" class="chip-row">
                  <span v-for="tag in job.tags" :key="tag" class="chip chip-dark">{{ tag }}</span>
                </div>
              </article>
              <div v-if="!jobPostings.length" class="empty-state">채용공고를 불러오는 중입니다.</div>
            </div>
          </div>
          </article>

        <!-- 공모전 -->
        <article class="double-shell panel panel-contests reveal" style="--index: 3">
          <div class="double-core panel-core">
            <div class="panel-header">
              <div>
                <span class="panel-kicker">Contests</span>
                <h3>이번 주 공모전</h3>
              </div>
              <RouterLink to="/contests" class="panel-link">더보기</RouterLink>
            </div>
            <div class="card-list">
              <article
                v-for="contest in contests" :key="contest.id"
                class="item-card contest-item clickable"
                @click="goToContest(contest)"
              >
                <div class="item-top">
                  <div class="company-badge contest-badge">{{ (contest.company || '?')[0] }}</div>
                  <div class="company-info">
                    <strong class="company-name">{{ contest.company }}</strong>
                    <span class="job-title-text">{{ contest.title }}</span>
                  </div>
                  <span class="dday-badge" :class="{ urgent: contest.dday !== '마감' && contest.dday <= 3 }">
                    D-{{ contest.dday }}
                  </span>
                </div>
                <div class="job-meta-row">
                  <span class="prize-tag">🏆 {{ contest.prize }}</span>
                </div>
                <div v-if="contest.tags.length" class="chip-row">
                  <span v-for="tag in contest.tags" :key="tag" class="chip">{{ tag }}</span>
                </div>
              </article>
              <div v-if="!contests.length" class="empty-state">공모전을 불러오는 중입니다.</div>
            </div>
          </div>
        </article>

        </div>

        <aside class="double-shell panel panel-brief reveal" style="--index: 5">
          <div class="double-core panel-core brief-core">
            <div class="panel-header">
              <div>
                <span class="panel-kicker">Quick Brief</span>
                <h3>오늘의 탐색 루틴</h3>
              </div>
            </div>

            <div class="brief-list">
              <p class="routine-note">
                탐색 루틴을 따라가면 오늘 확인할 공고, 읽을 글, 저장할 정보를 순서대로 파악할 수 있습니다.
              </p>
              <div v-for="brief in quickBriefs" :key="brief.title" class="brief-item">
                <span>{{ brief.step }}</span>
                <strong>{{ brief.title }}</strong>
                <p>{{ brief.description }}</p>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </section>
  </main>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, computed, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import api from '@/api/axios'

const route = useRoute()
const router = useRouter()

const recentPosts = ref([])
const jobPostings = ref([])
const contests = ref([])
const communityPosts = ref([])
const searchResults = ref({
  posts: [],
  jobs: [],
  contests: [],
  communities: [],
})
const searchLoading = ref(false)
const searchError = ref('')

const feedSummaries = computed(() => [
  { label: '읽을 글', value: recentPosts.value.length || '0', caption: '실무 팁', color: '#8b6a50' },
  { label: '지원 공고', value: jobPostings.value.length || '0', caption: '채용 후보', color: '#2f6f73' },
  { label: '마감 공모전', value: contests.value.length || '0', caption: '이번 주', color: '#8f5f9a' },
])

const searchTerm = computed(() => {
  const raw = route.query.search
  return Array.isArray(raw) ? raw[0] || '' : raw || ''
})

const hasSearchQuery = computed(() => searchTerm.value.trim().length > 0)

const searchResultGroups = computed(() => [
  { key: 'posts', label: '게시글', items: searchResults.value.posts, link: '/posts' },
  { key: 'jobs', label: '채용 공고', items: searchResults.value.jobs, link: '/jobs' },
  { key: 'contests', label: '공모전', items: searchResults.value.contests, link: '/contests' },
  { key: 'communities', label: '커뮤니티', items: searchResults.value.communities, link: '/community' },
])

const totalSearchResults = computed(() =>
  searchResultGroups.value.reduce((total, group) => total + group.items.length, 0),
)

const quickBriefs = [
  {
    step: '01',
    title: '마감 임박 공고부터 확인',
    description: '이번 주 안에 지원 가능한 공고와 공모전을 먼저 보여줘서 우선순위를 빠르게 잡을 수 있습니다.',
  },
  {
    step: '02',
    title: '실무형 게시글로 감 잡기',
    description: '지원 전에 필요한 인증, CRUD, 데이터베이스 설계 글을 함께 둘러보며 기술 감각을 정리합니다.',
  },
  {
    step: '03',
    title: '관심 항목 정리',
    description: '지원할 공고와 다시 읽을 글을 구분해 다음 행동을 빠르게 결정합니다.',
  },
]

const logHomeDataError = (label, reason) => {
  console.error(`홈 ${label} 데이터 로딩 실패:`, reason)
}

const resetSearchResults = () => {
  searchResults.value = {
    posts: [],
    jobs: [],
    contests: [],
    communities: [],
  }
  searchError.value = ''
  searchLoading.value = false
}

const safeData = (result) => (
  result.status === 'fulfilled' && Array.isArray(result.value.data)
    ? result.value.data
    : []
)

const normalizeSearchValue = (value) => String(value ?? '').toLowerCase()

const matchesSearch = (values, query) => {
  const lowered = normalizeSearchValue(query)
  return values.some(value => normalizeSearchValue(value).includes(lowered))
}

const createPreview = (value, maxLength = 72) => {
  const text = String(value || '').replace(/\s+/g, ' ').trim()
  return text.length > maxLength ? `${text.slice(0, maxLength)}...` : text
}

const fetchHomeSearchResults = async (rawQuery) => {
  const query = rawQuery.trim()
  if (!query) {
    resetSearchResults()
    return
  }

  searchLoading.value = true
  searchError.value = ''

  const [postResult, jobResult, contestResult, communityResult] = await Promise.allSettled([
    api.get('/posts/', { params: { limit: 6, search: query } }),
    api.get('/jobs/', { params: { limit: 6, search: query } }),
    api.get('/contests/', { params: { limit: 6, search: query } }),
    api.get('/community/'),
  ])

  const categoryLabel = { job: '직무별', career: '커리어', project: '프로젝트 공유' }

  searchResults.value = {
    posts: safeData(postResult).map(post => ({
      ...post,
      resultTitle: post.title || '제목 없음',
      resultSubtitle: post.author_name ? `작성자 ${post.author_name}` : '게시글',
      resultDescription: createPreview(post.content),
      resultBadge: post.job_category || '게시글',
    })),
    jobs: safeData(jobResult).map(job => ({
      ...job,
      resultTitle: job.title || '채용 공고',
      resultSubtitle: job.company || '회사명 미정',
      resultDescription: [job.region, job.experience].filter(Boolean).join(' · '),
      resultBadge: job.job_category || '채용',
    })),
    contests: safeData(contestResult).map(contest => ({
      ...contest,
      resultTitle: contest.title || '공모전',
      resultSubtitle: contest.organizer || '주최 미정',
      resultDescription: [contest.category, contest.target, contest.prize].filter(Boolean).join(' · '),
      resultBadge: contest.category || '공모전',
    })),
    communities: safeData(communityResult)
      .filter(item => matchesSearch(
        [item.title, item.content, item.author_name, categoryLabel[item.category], item.category],
        query,
      ))
      .slice(0, 6)
      .map(item => ({
        ...item,
        resultTitle: item.title || '커뮤니티 글',
        resultSubtitle: item.author_name || '익명',
        resultDescription: createPreview(item.content),
        resultBadge: categoryLabel[item.category] || item.category || '커뮤니티',
      })),
  }

  if ([postResult, jobResult, contestResult, communityResult].every(result => result.status === 'rejected')) {
    searchError.value = '검색 결과를 불러오지 못했습니다. 잠시 후 다시 시도해주세요.'
  }

  searchLoading.value = false
}

const fetchHomeData = async () => {
  const [postResult, jobResult, contestResult, communityResult] = await Promise.allSettled([
    api.get('/posts/', { params: { limit: 3 } }),
    api.get('/jobs/', { params: { limit: 3, include_external: false } }),
    api.get('/contests/', { params: { limit: 3, include_external: false } }),
    api.get('/community/', { params: { limit: 4 } }),
  ])

  if (postResult.status === 'fulfilled') {
    recentPosts.value = postResult.value.data.slice(0, 3).map(post => ({
      ...post,
      author: post.author_name || '익명',
      avatarColor: `hsl(${(post.id * 137) % 360}, 60%, 88%)`,
      category: post.job_category || '자유',
      time: timeAgo(post.created_at),
      likes: post.like_count || 0,
      comments: 0,
      tags: [post.job_category].filter(Boolean),
    }))
  } else {
    logHomeDataError('게시글', postResult.reason)
  }

  if (jobResult.status === 'fulfilled') {
    jobPostings.value = jobResult.value.data.slice(0, 3).map(job => ({
      ...job,
      logo: null,
      isNew: job.created_at
        ? Date.now() - new Date(job.created_at).getTime() < 1000 * 60 * 60 * 24 * 7
        : false,
      location: job.region || '지역 미정',
      tags: [job.job_category, job.experience].filter(Boolean),
      dday: calculateDDay(job.deadline),
    }))
  } else {
    logHomeDataError('채용공고', jobResult.reason)
  }

  if (contestResult.status === 'fulfilled') {
    contests.value = contestResult.value.data.slice(0, 3).map(c => ({
      ...c,
      logo: null,
      company: c.organizer || '주최 미정',
      isNew: c.created_at
        ? Date.now() - new Date(c.created_at).getTime() < 1000 * 60 * 60 * 24 * 7
        : false,
      tags: [c.category, c.target].filter(Boolean),
      prize: c.prize || '상금 미정',
      dday: calculateDDay(c.deadline),
    }))
  } else {
    logHomeDataError('공모전', contestResult.reason)
  }

  if (communityResult.status === 'fulfilled') {
    const categoryLabel = { job: '직무별', career: '커리어', project: '프로젝트 공유' }
    communityPosts.value = communityResult.value.data.slice(0, 4).map(c => ({
      ...c,
      author: c.author_name || '익명',
      avatarColor: `hsl(${(c.id * 97) % 360}, 60%, 88%)`,
      time: timeAgo(c.created_at),
      categoryLabel: categoryLabel[c.category] || c.category,
    }))
  } else {
    logHomeDataError('커뮤니티', communityResult.reason)
  }
}

const goToPost = (id) => router.push(`/posts/${id}`)
const goToCommunity = (id) => router.push(`/community/${id}`)
const goToJob = (job) => {
  if (job.external_url) window.open(job.external_url, '_blank', 'noopener')
  else router.push(`/jobs/${job.id}`)
}
const goToContest = (contest) => {
  if (contest.external_url) window.open(contest.external_url, '_blank', 'noopener')
  else router.push(`/contests/${contest.id}`)
}

const openSearchResult = (type, item) => {
  if (type === 'posts') {
    goToPost(item.id)
    return
  }
  if (type === 'jobs') {
    goToJob(item)
    return
  }
  if (type === 'contests') {
    goToContest(item)
    return
  }
  if (type === 'communities') {
    goToCommunity(item.id)
  }
}

const handleImgError = (event) => {
  event.target.style.display = 'none'
  event.target.parentElement.classList.add('logo-fallback')
}

function timeAgo(isoStr) {
  if (!isoStr) return ''
  const diff = Date.now() - new Date(isoStr).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1) return '방금 전'
  if (m < 60) return `${m}분 전`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}시간 전`
  return `${Math.floor(h / 24)}일 전`
}

function calculateDDay(deadlineStr) {
  if (!deadlineStr) return '?'
  const diff = new Date(deadlineStr).getTime() - Date.now()
  const days = Math.ceil(diff / (1000 * 60 * 60 * 24))
  return days >= 0 ? days : '마감'
}

let observer

const initRevealObserver = () => {
  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible')
          observer.unobserve(entry.target)
        }
      })
    },
    { threshold: 0.18 },
  )

  document.querySelectorAll('.reveal').forEach((element) => {
    observer.observe(element)
  })
}

onMounted(() => {
  initRevealObserver()
  fetchHomeData()
})

watch(
  searchTerm,
  (query) => {
    fetchHomeSearchResults(query)
  },
  { immediate: true },
)

onBeforeUnmount(() => {
  observer?.disconnect()
})
</script>

<style scoped>
.home-page {
  position: relative;
  padding-bottom: 6rem;
}

.page-shell {
  width: min(1200px, calc(100% - 32px));
  margin: 0 auto;
}

.hero-section {
  position: relative;
  overflow: hidden;
  padding: 8rem 0 2.5rem;
}

.hero-signal-map {
  position: absolute;
  inset: 4.8rem 0 0;
  width: 100%;
  height: min(38rem, 72vh);
  pointer-events: none;
  z-index: 0;
  opacity: 0.62;
}

.signal-line {
  fill: none;
  stroke-linecap: round;
  stroke-width: 1.2;
}

.signal-line-primary {
  stroke: rgba(47, 111, 115, 0.34);
}

.signal-line-secondary {
  stroke: rgba(126, 90, 65, 0.2);
}

.signal-line-dotted {
  stroke: rgba(47, 111, 115, 0.24);
  stroke-dasharray: 1 18;
  stroke-width: 3;
}

.hero-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(0, 1.28fr) minmax(280px, 0.72fr);
  gap: clamp(1rem, 3vw, 2rem);
  align-items: center;
}

.hero-copy {
  display: grid;
  gap: 1.25rem;
  padding: 1rem 0;
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 0.9rem;
  border-radius: 999px;
  background: rgba(196, 142, 102, 0.12);
  border: 1px solid rgba(196, 142, 102, 0.18);
  color: var(--color-accent);
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.section-head h2,
.panel-header h3,
.feed-card h4 {
  text-wrap: balance;
  word-break: keep-all;
}

.hero-subtitle {
  max-width: 58rem;
  color: var(--color-muted);
  font-size: 1.04rem;
  line-height: 1.8;
  word-break: keep-all;
}

.double-shell {
  padding: 1px;
  border-radius: 2rem;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.78), rgba(255, 255, 255, 0.32)),
    rgba(17, 24, 39, 0.05);
  box-shadow:
    0 30px 80px -42px rgba(43, 31, 18, 0.26),
    inset 0 1px 0 rgba(255, 255, 255, 0.68);
}

.double-core {
  border-radius: calc(2rem - 1px);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(253, 249, 243, 0.86));
  box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.55);
}

.primary-cta,
.secondary-cta,
.panel-link,
.feed-card,
.nav-link,
.btn-ghost,
.btn-primary,
.icon-btn,
.user-menu {
  transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

.primary-cta,
.secondary-cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  min-height: 3.5rem;
  padding: 0.95rem 1.15rem 0.95rem 1.5rem;
  border: 0;
  border-radius: 999px;
  cursor: pointer;
  font-size: 0.98rem;
  font-weight: 600;
  text-decoration: none;
  white-space: nowrap;
}

.primary-cta {
  color: #fffaf5;
  background: linear-gradient(135deg, #2f2722, #7e5a41);
  box-shadow: 0 18px 40px -26px rgba(126, 90, 65, 0.85);
}

.secondary-cta {
  color: var(--color-ink);
  background: rgba(255, 255, 255, 0.64);
  border: 1px solid rgba(77, 61, 46, 0.12);
}

.primary-cta:hover,
.secondary-cta:hover,
.panel-link:hover,
.feed-card:hover {
  transform: translateY(-2px) scale(1.01);
}

.primary-cta:active,
.secondary-cta:active {
  transform: scale(0.98);
}

.btn-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.95rem;
  height: 1.95rem;
  border-radius: 999px;
  background: rgba(255, 250, 245, 0.16);
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  flex-wrap: wrap;
}

.hero-actions {
  margin-top: 0.1rem;
}

.hero-signal-card {
  overflow: hidden;
}

.hero-signal-core {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 12rem;
  align-items: center;
  gap: 1.5rem;
  min-height: 12rem;
  padding: 1.35rem;
}

.signal-copy {
  display: grid;
  gap: 0.65rem;
}

.signal-kicker {
  color: var(--color-accent);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.signal-copy strong {
  max-width: 35rem;
  color: var(--color-ink);
  font-family: var(--font-display);
  font-size: clamp(1.45rem, 3vw, 2.35rem);
  font-weight: 800;
  line-height: 1.28;
  word-break: keep-all;
}

.signal-copy p {
  max-width: 36rem;
  margin: 0;
  color: var(--color-muted);
  line-height: 1.72;
  word-break: keep-all;
}

.signal-orbit {
  position: relative;
  min-height: 10rem;
  border-radius: 999px;
}

.orbit-ring {
  position: absolute;
  inset: 1.05rem;
  border: 1px dashed rgba(126, 90, 65, 0.26);
  border-radius: 999px;
}

.orbit-track {
  position: absolute;
  inset: 0;
  border-radius: 999px;
  animation: orbit-clockwise 18s linear infinite;
  transform-origin: center;
}

.orbit-core,
.orbit-node {
  position: absolute;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  box-shadow: 0 18px 38px -28px rgba(47, 39, 34, 0.62);
}

.orbit-core {
  inset: 50% auto auto 50%;
  width: 4.4rem;
  height: 4.4rem;
  transform: translate(-50%, -50%);
  background: linear-gradient(135deg, #312821, #835d43);
  color: #fff8f2;
  font-weight: 800;
  letter-spacing: 0.02em;
}

.orbit-node {
  top: 50%;
  left: 50%;
  min-width: 4.6rem;
  min-height: 2.35rem;
  padding: 0 0.85rem;
  background: rgba(255, 255, 255, 0.8);
  color: #5d4a38;
  font-size: 0.78rem;
  font-weight: 800;
}

.orbit-label {
  display: inline-flex;
  animation: orbit-label-counter 18s linear infinite;
}

.orbit-node-jobs {
  transform: translate(-50%, -50%) rotate(-90deg) translateX(3.7rem) rotate(90deg);
}

.orbit-node-contests {
  transform: translate(-50%, -50%) rotate(30deg) translateX(3.7rem) rotate(-30deg);
}

.orbit-node-posts {
  transform: translate(-50%, -50%) rotate(150deg) translateX(3.7rem) rotate(-150deg);
}

@keyframes orbit-clockwise {
  to {
    transform: rotate(360deg);
  }
}

@keyframes orbit-label-counter {
  to {
    transform: rotate(-360deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .orbit-track,
  .orbit-label {
    animation: none;
  }
}

.hero-stack {
  display: grid;
  gap: 1rem;
}

.search-results-section {
  padding: 1.5rem 0 2rem;
}

.search-results-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.search-results-head h2 {
  margin: 0.75rem 0 0;
  color: var(--color-ink);
  font-family: var(--font-display);
  font-size: clamp(1.5rem, 3vw, 2.25rem);
  line-height: 1.25;
  word-break: keep-all;
}

.search-results-head h2 span {
  color: var(--color-accent);
  font-size: 0.78em;
}

.search-result-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
}

.search-result-core {
  min-height: 100%;
  padding: 1rem;
}

.search-result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.search-result-header span {
  color: var(--color-muted);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.search-result-header strong {
  color: var(--color-ink);
  font-size: 0.9rem;
}

.search-result-card {
  width: 100%;
  border: 1px solid rgba(90, 72, 55, 0.08);
  color: inherit;
  cursor: pointer;
  text-align: left;
}

.search-result-card strong,
.search-result-card small,
.search-result-card p {
  display: block;
}

.search-result-card strong {
  margin-top: 0.55rem;
  color: var(--color-ink);
  font-size: 0.95rem;
  line-height: 1.45;
  word-break: keep-all;
}

.search-result-card small {
  margin-top: 0.25rem;
  color: var(--color-muted);
  font-size: 0.78rem;
  font-weight: 700;
}

.search-result-card p {
  margin: 0.55rem 0 0;
  color: var(--color-muted);
  font-size: 0.82rem;
  line-height: 1.55;
}

.search-state {
  margin-top: 1rem;
}

.panel-core {
  padding: 1.35rem;
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.panel-kicker {
  display: block;
  margin-bottom: 0.45rem;
  color: var(--color-muted);
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.section-head h2 {
  font-family: var(--font-display);
  letter-spacing: -0.04em;
}

.mini-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.42rem 0.78rem;
  border-radius: 999px;
  background: rgba(196, 142, 102, 0.14);
  color: var(--color-accent);
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.06em;
}

.terminal-card {
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 1.65rem;
  background: #1f1e1c;
  box-shadow: 0 30px 80px -38px rgba(31, 30, 28, 0.5);
}

.terminal-bar {
  display: flex;
  align-items: center;
  gap: 1rem;
  min-height: 3.15rem;
  padding: 0 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.09);
  background: #181716;
}

.terminal-controls {
  display: flex;
  align-items: center;
  gap: 0.55rem;
}

.terminal-dot {
  width: 0.78rem;
  height: 0.78rem;
  border-radius: 999px;
}

.terminal-dot.red {
  background: #f05252;
}

.terminal-dot.yellow {
  background: #f7a928;
}

.terminal-dot.green {
  background: #65a832;
}

.terminal-title {
  color: rgba(248, 242, 232, 0.9);
  font-family: Georgia, serif;
  font-size: 1.05rem;
  font-weight: 700;
}

.terminal-code {
  overflow-x: auto;
  padding: 1.5rem 1.45rem 1.65rem;
  color: #d9d3ca;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: clamp(0.88rem, 1.5vw, 1.05rem);
  line-height: 1.85;
  white-space: nowrap;
}

.terminal-code p {
  margin: 0;
}

.terminal-code .code-spacer {
  height: 0.8rem;
}

.code-indent {
  padding-left: 1.4rem;
}

.code-indent-2 {
  padding-left: 2.8rem;
}

.code-indent-3 {
  padding-left: 4.2rem;
}

.code-blue {
  color: #2d7edb;
}

.code-green {
  color: #55a630;
}

.code-orange {
  color: #e89522;
}

.code-string {
  color: #d7d1c7;
}

.code-muted {
  color: #f0ece5;
}

.code-white {
  color: #fffaf2;
}

.brief-list {
  display: grid;
  gap: 0.95rem;
  margin-top: 1.15rem;
}

.routine-note {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0;
  padding: 1rem;
  border-radius: 1.2rem;
  background: rgba(49, 40, 33, 0.06);
  color: var(--color-muted);
  font-size: 0.92rem;
  line-height: 1.7;
  text-align: center;
  word-break: keep-all;
}

.brief-item,
.routine-note {
  min-height: 100%;
}

/* ── 공통 카드 리스트 */
.card-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 1.1rem;
}

.item-card {
  padding: 0.95rem 1rem;
  border-radius: 1.1rem;
  border: 1px solid rgba(90, 72, 55, 0.08);
  background: rgba(255, 255, 255, 0.7);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.item-card:hover {
  border-color: rgba(126, 90, 65, 0.2);
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 8px 28px -12px rgba(94, 76, 60, 0.22);
  transform: translateY(-1px);
}

.item-top {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.55rem;
}

.item-title {
  font-size: 0.97rem;
  font-weight: 700;
  color: var(--color-ink);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: keep-all;
}

.item-preview {
  margin-top: 0.4rem;
  font-size: 0.85rem;
  color: var(--color-muted);
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-time {
  margin-left: auto;
  font-size: 0.78rem;
  color: #aaa;
  white-space: nowrap;
}

.item-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 0.65rem;
  gap: 0.5rem;
}

.author-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  min-width: 0;
}

.author-row-sm {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.stat-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.28rem;
  font-size: 0.82rem;
  color: var(--color-muted);
}

.avatar-sm {
  width: 1.65rem;
  height: 1.65rem;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.72rem;
  font-weight: 700;
  color: #5d4a38;
  flex-shrink: 0;
}

.author-name {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--color-ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 7rem;
}

.cat-chip {
  display: inline-flex;
  align-items: center;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  background: rgba(196, 142, 102, 0.12);
  color: var(--color-accent);
  font-size: 0.72rem;
  font-weight: 700;
  white-space: nowrap;
}

/* ── 채용 / 공모전 카드 */
.company-badge {
  width: 2.4rem;
  height: 2.4rem;
  border-radius: 0.7rem;
  background: linear-gradient(135deg, rgba(196, 142, 102, 0.18), rgba(255, 255, 255, 0.9));
  border: 1px solid rgba(196, 142, 102, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 800;
  color: var(--color-accent);
  flex-shrink: 0;
}

.contest-badge {
  background: linear-gradient(135deg, rgba(100, 80, 180, 0.1), rgba(255, 255, 255, 0.9));
  border-color: rgba(100, 80, 180, 0.18);
  color: #6450b4;
}

.company-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.18rem;
}

.company-name {
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--color-ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.job-title-text {
  font-size: 0.82rem;
  color: var(--color-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.job-meta-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-top: 0.55rem;
}

.meta-tag, .prize-tag {
  font-size: 0.78rem;
  color: var(--color-muted);
}

.dday-badge {
  margin-left: auto;
  padding: 0.22rem 0.6rem;
  border-radius: 999px;
  background: rgba(49, 40, 33, 0.07);
  color: var(--color-ink);
  font-size: 0.75rem;
  font-weight: 700;
}

.dday-badge.urgent {
  background: rgba(200, 60, 40, 0.1);
  color: #c03828;
}

.new-badge {
  padding: 0.2rem 0.5rem;
  border-radius: 999px;
  background: rgba(46, 125, 50, 0.1);
  color: #2e7d32;
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.04em;
}

.hot-badge {
  padding: 0.2rem 0.5rem;
  border-radius: 999px;
  background: rgba(200, 60, 40, 0.1);
  color: #c03828;
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.04em;
}

.chip-row {
  display: flex;
  gap: 0.45rem;
  flex-wrap: wrap;
  margin-top: 0.55rem;
}

.empty-state {
  padding: 1.4rem;
  text-align: center;
  font-size: 0.88rem;
  color: #b8b1a6;
  border: 1px dashed rgba(90, 72, 55, 0.12);
  border-radius: 1rem;
}

.feed-card h4,
.brief-item strong {
  display: block;
  color: var(--color-ink);
  font-size: 1rem;
  line-height: 1.45;
  word-break: keep-all;
}

.feed-card p,
.section-head p,
.brief-item p,
.detail-row,
.feed-footer,
.brand-row p {
  color: var(--color-muted);
  line-height: 1.7;
  word-break: keep-all;
}

.dashboard-section {
  padding-top: 7rem;
}

.section-head {
  display: grid;
  grid-template-columns: minmax(0, 0.82fr) minmax(0, 1.18fr);
  gap: clamp(1.5rem, 4vw, 3rem);
  align-items: start;
  margin-bottom: 2.4rem;
  padding-bottom: 1.6rem;
  border-bottom: 1px solid rgba(90, 72, 55, 0.08);
}

.section-head h2 {
  margin-top: 1.1rem;
  font-size: clamp(2rem, 4vw, 3.3rem);
  color: var(--color-ink);
  line-height: 1.08;
}

.section-title-accent {
  display: block;
  color: var(--color-accent);
}

.section-head p {
  max-width: 36rem;
  font-size: 0.98rem;
}

.section-brief {
  display: grid;
  gap: 1.25rem;
  padding-top: 0;
}

.section-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  align-items: start;
  gap: 0.75rem;
}

.summary-item {
  display: grid;
  grid-template-columns: auto 1fr;
  column-gap: 0.5rem;
  row-gap: 0.2rem;
  align-items: center;
  padding: 0.9rem 0;
  border-top: 1px solid rgba(90, 72, 55, 0.1);
}

.summary-dot {
  width: 0.58rem;
  height: 0.58rem;
  border-radius: 999px;
}

.summary-label {
  color: var(--color-muted);
  font-size: 0.78rem;
  font-weight: 700;
}

.summary-item strong {
  grid-column: 1 / -1;
  color: var(--color-ink);
  font-family: var(--font-display);
  font-size: 2rem;
  line-height: 1;
  letter-spacing: -0.04em;
}

.summary-item small {
  grid-column: 1 / -1;
  color: var(--color-muted);
  font-size: 0.8rem;
  font-weight: 600;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 0.8fr);
  gap: 1rem;
  align-items: stretch;
}

.dashboard-column {
  display: grid;
  gap: 1rem;
  align-content: start;
}

.dashboard-column-side {
  grid-template-rows: auto minmax(0, 1fr);
}

.panel-contests {
  height: 100%;
}

.panel-contests .panel-core {
  height: 100%;
}

.panel-core {
  padding: 1.4rem;
}

.panel-header h3 {
  color: var(--color-ink);
  font-family: var(--font-display);
  font-size: 1.55rem;
  line-height: 1.06;
  letter-spacing: -0.04em;
}

.panel-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2.75rem;
  padding: 0 1rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(88, 70, 53, 0.1);
  color: var(--color-ink);
  font-size: 0.9rem;
  font-weight: 600;
  text-decoration: none;
  white-space: nowrap;
}

.chip {
  display: inline-flex;
  align-items: center;
  padding: 0.3rem 0.65rem;
  border-radius: 999px;
  background: rgba(196, 142, 102, 0.12);
  color: var(--color-accent);
  font-size: 0.75rem;
  font-weight: 600;
}

.chip-dark {
  background: rgba(49, 40, 33, 0.08);
  color: var(--color-ink);
}

.clickable {
  cursor: pointer;
}

.panel-community {
  grid-column: auto;
}

.panel-brief {
  grid-column: 1 / -1;
}

.community-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
  margin-top: 1.1rem;
}

.community-empty {
  grid-column: auto;
}

@media (max-width: 768px) {
  .panel-community {
    grid-column: span 1;
  }
  .community-grid {
    grid-template-columns: 1fr;
  }
  .community-empty {
    grid-column: span 1;
  }
}

.brief-core {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, 0.42fr);
  gap: 0.75rem;
  align-items: stretch;
}

.brief-core .panel-header {
  grid-column: 1 / -1;
}

.brief-list {
  grid-column: 1 / -1;
  grid-template-columns: minmax(220px, 0.9fr) repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
  margin-top: 0;
}

.brief-item {
  padding: 1rem;
  border-radius: 1.35rem;
  background: rgba(255, 255, 255, 0.68);
  border: 1px solid rgba(90, 72, 55, 0.08);
}

.brief-item span {
  color: var(--color-accent);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.brief-item strong {
  margin-top: 0.45rem;
}

.brief-item p {
  margin-top: 0.45rem;
  font-size: 0.92rem;
}

.reveal {
  opacity: 0;
  transform: translateY(2rem);
  filter: blur(8px);
}

.reveal.is-visible {
  animation: fadeInUp 0.9s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  animation-delay: calc(var(--index, 0) * 80ms);
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(2rem);
    filter: blur(8px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
    filter: blur(0);
  }
}

@media (max-width: 1024px) {
  .hero-grid,
  .dashboard-grid,
  .section-head {
    grid-template-columns: 1fr;
  }

  .search-result-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .section-head {
    gap: 1.1rem;
  }

  .dashboard-column {
    display: contents;
  }

  .panel-posts {
    order: 1;
  }

  .panel-jobs {
    order: 2;
  }

  .panel-contests {
    order: 3;
  }

  .panel-community {
    order: 4;
  }

  .panel-brief {
    order: 5;
  }

  .brief-core {
    grid-template-columns: 1fr;
  }

  .brief-core .panel-header {
    grid-column: auto;
  }

  .brief-list {
    grid-template-columns: 1fr;
  }

  .panel-posts {
    grid-row: auto;
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding-top: 7rem;
  }

  .hero-signal-map {
    top: 5.6rem;
    height: 30rem;
    opacity: 0.36;
  }

  .dashboard-section {
    padding-top: 5rem;
  }

  .section-head {
    margin-bottom: 1.5rem;
  }

  .section-summary {
    grid-template-columns: 1fr;
  }

  .page-shell {
    width: min(100% - 24px, 1200px);
  }

  .hero-copy {
    padding-top: 0.5rem;
  }

  .search-results-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .search-result-grid {
    grid-template-columns: 1fr;
  }

  .hero-signal-core {
    grid-template-columns: 1fr;
  }

  .signal-orbit {
    min-height: 8.5rem;
  }

  .primary-cta,
  .secondary-cta {
    width: 100%;
  }

  .panel-header,
  .feed-meta {
    flex-direction: column;
    align-items: flex-start;
  }
}
.more-results-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 14px;
  margin-top: 8px;
  background: #f8f6f3;
  border-radius: 12px;
  color: #5d4037;
  font-size: 14px;
  font-weight: 700;
  text-decoration: none;
  transition: all 0.2s ease;
}

.more-results-link:hover {
  background: #5d4037;
  color: white;
}

.more-results-link svg {
  transition: transform 0.2s ease;
}

.more-results-link:hover svg {
  transform: translateX(4px);
}
</style>
