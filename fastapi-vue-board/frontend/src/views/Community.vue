<template>
  <div class="page-wrapper">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-inner">
        <div class="header-title">
          <span class="header-icon">👥</span>
          <div>
            <h1>커뮤니티</h1>
            <p>개발자들과 소통하고 지식을 나누세요</p>
          </div>
        </div>
        <button class="btn-primary" @click="goToWrite">✏️ 글쓰기</button>
      </div>
      <!-- Search -->
      <div class="header-search">
        <span class="search-icon">🔍</span>
        <input v-model="searchQuery" type="text" placeholder="커뮤니티 검색..." class="search-input" />
      </div>
    </div>

    <div class="content-layout">
      <!-- Main Content -->
      <div class="main-section">

        <!-- Category Cards -->
        <div class="section-title">

        </div>
        <div class="category-grid">
          <div
            v-for="cat in categoryCards"
            :key="cat.id"
            class="category-card"
            :style="{ borderTop: `3px solid ${cat.color}` }"
            @click="selectedBoard = cat.id"
          >
            <div class="cat-icon">{{ cat.icon }}</div>
            <div class="cat-info">
              <h4>{{ cat.name }}</h4>
              <p>{{ cat.desc }}</p>
              <span class="cat-count">{{ cat.count }}개 게시글</span>
            </div>
          </div>
        </div>

        <!-- Recent Posts -->
        <div class="section-title" style="margin-top: 32px;">
          <span>📝</span> 최근 게시글
          <div class="board-tabs">
            <button
              v-for="tab in boardTabs"
              :key="tab.value"
              class="board-tab"
              :class="{ active: selectedBoard === tab.value }"
              @click="selectedBoard = tab.value"
            >{{ tab.label }}</button>
          </div>
        </div>

        <div class="post-list">
          <div
            v-for="post in filteredPosts"
            :key="post.id"
            class="post-item"
            @click="goToPost(post.id)"
          >
            <div class="post-content">
              <div class="post-top">
                <span class="post-category" :style="{ color: getCatColor(post.category) }">{{ post.category }}</span>
                <span v-if="post.isHot" class="badge-hot">🔥 인기</span>
              </div>
              <h3 class="post-title">{{ post.title }}</h3>
              <p class="post-preview">{{ post.preview }}</p>
              <div class="post-meta">
                <div class="author-info">
                  <img :src="post.avatar" class="avatar" />
                  <span class="author">{{ post.author }}</span>
                  <span class="date">{{ post.date }}</span>
                </div>
                <div class="post-stats">
                  <span>👁 {{ post.views }}</span>
                  <span>💬 {{ post.comments }}</span>
                  <span>❤️ {{ post.likes }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Load More -->
        <button class="btn-load-more">더보기 ↓</button>
      </div>

      <!-- Right Sidebar -->
      <div class="sidebar">
        <!-- Hot Topics -->
        <div class="sidebar-card">
          <h3 class="sidebar-title">🔥 실시간 인기 토픽</h3>
          <ul class="hot-list">
            <li v-for="(topic, i) in hotTopics" :key="i" class="hot-item">
              <span class="hot-rank" :class="{ top: i < 3 }">{{ i + 1 }}</span>
              <span class="hot-text">{{ topic }}</span>
            </li>
          </ul>
        </div>

        <!-- Active Users -->
        <div class="sidebar-card">
          <h3 class="sidebar-title">✨ 이번 주 활발한 멤버</h3>
          <ul class="user-list">
            <li v-for="user in activeUsers" :key="user.id" class="user-item">
              <img :src="user.avatar" class="user-avatar" />
              <div class="user-info">
                <span class="user-name">{{ user.name }}</span>
                <span class="user-posts">게시글 {{ user.posts }}개</span>
              </div>
              <span class="user-badge">{{ user.badge }}</span>
            </li>
          </ul>
        </div>

        <!-- Notice -->
        <div class="sidebar-card notice-card">
          <h3 class="sidebar-title">📢 공지사항</h3>
          <ul class="notice-list">
            <li v-for="notice in notices" :key="notice.id" class="notice-item">
              <span class="notice-text">{{ notice.text }}</span>
              <span class="notice-date">{{ notice.date }}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const searchQuery = ref('')
const selectedBoard = ref('all')

const boardTabs = [
  { label: '전체', value: 'all' },
  { label: '취업 정보', value: '취업 정보' },
  { label: '스터디', value: '스터디' },
  { label: '업계 정보', value: '업계 정보' },
]

const categoryCards = [
  { id: '취업 정보', name: '인기 게시판', desc: '가장 인기 있는 게시글 모음', icon: '📈', count: '1,234', color: '#3366ff' },
  { id: '기술', name: '직무별 게시판', desc: '개발, 디자인, AI 직무 관련 토론', icon: '💻', count: '567', color: '#00b96b' },
  { id: '스터디', name: '업계 게시판', desc: '취업, 커리어, 업계 동향 정보', icon: '💬', count: '432', color: '#ff8c00' },
  { id: '모집', name: '스터디/프로젝트', desc: '함께 공부하고 프로젝트 팀원 모집', icon: '🤝', count: '891', color: '#9c27b0' },
]

const catColors = {
  '취업 정보': '#3366ff', '기술': '#00b96b', '스터디': '#ff8c00', '모집': '#9c27b0', '업계 정보': '#f44336'
}
const getCatColor = (cat) => catColors[cat] || '#888'

const posts = ref([
  {
    id: 1, title: 'JWT 인증 vs Session 인증, 무엇이 더 나을까?',
    preview: '최근 프로젝트에서 JWT를 사용해보았는데 Session 방식과 비교했을 때...',
    category: '기술', author: '개발자김', date: '3시간 전',
    views: 1234, comments: 28, likes: 47, isHot: true,
    avatar: 'https://via.placeholder.com/28x28/3366ff/ffffff?text=김'
  },
  {
    id: 2, title: 'WebSocket 채팅방 구현 시 레이스 컨디션 방지법',
    preview: 'WebSocket으로 실시간 채팅을 구현하다가 동시 접속 시 문제가 발생했습니다.',
    category: '기술', author: '백엔드이', date: '5시간 전',
    views: 876, comments: 15, likes: 32, isHot: false,
    avatar: 'https://via.placeholder.com/28x28/00b96b/ffffff?text=이'
  },
  {
    id: 3, title: 'DB 인덱스 설계 베스트 프랙티스',
    preview: '대용량 데이터를 다루면서 인덱스 설계의 중요성을 느꼈습니다.',
    category: '기술', author: 'DBA박', date: '어제',
    views: 2341, comments: 41, likes: 89, isHot: true,
    avatar: 'https://via.placeholder.com/28x28/ff8c00/ffffff?text=박'
  },
  {
    id: 4, title: 'React Query vs SWR 실전 비교',
    preview: 'React Query와 SWR을 실제 프로젝트에서 모두 사용해본 경험 공유.',
    category: '기술', author: '프론트최', date: '2일 전',
    views: 1567, comments: 33, likes: 61, isHot: false,
    avatar: 'https://via.placeholder.com/28x28/9c27b0/ffffff?text=최'
  },
  {
    id: 5, title: 'Vue3 + FastAPI 스터디원 모집합니다',
    preview: 'Vue3와 FastAPI를 함께 공부할 스터디원을 모집합니다. 주 1회 진행...',
    category: '스터디', author: '스터디장', date: '3일 전',
    views: 445, comments: 12, likes: 18, isHot: false,
    avatar: 'https://via.placeholder.com/28x28/f44336/ffffff?text=스'
  },
])

const hotTopics = [
  'JWT 인증 vs Session 인증, 무엇이 더 나을까?',
  'WebSocket 채팅방 구현 시 레이스 컨디션 방지법',
  'DB 인덱스 설계 베스트 프랙티스',
  'React Query vs SWR 실전 비교',
]

const activeUsers = [
  { id: 1, name: '개발자_김', posts: 47, badge: '🏆', avatar: 'https://via.placeholder.com/32x32/3366ff/ffffff?text=김' },
  { id: 2, name: '백엔드_이', posts: 38, badge: '🥈', avatar: 'https://via.placeholder.com/32x32/00b96b/ffffff?text=이' },
  { id: 3, name: 'DBA_박', posts: 29, badge: '🥉', avatar: 'https://via.placeholder.com/32x32/ff8c00/ffffff?text=박' },
]

const notices = [
  { id: 1, text: '커뮤니티 이용규칙 업데이트 안내', date: '04.10' },
  { id: 2, text: '5월 해커톤 참여자 모집 공고', date: '04.08' },
  { id: 3, text: '스터디 매칭 서비스 오픈 예정', date: '04.05' },
]

const filteredPosts = computed(() => {
  let result = posts.value
  if (selectedBoard.value !== 'all') {
    result = result.filter(p => p.category === selectedBoard.value)
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(p => p.title.toLowerCase().includes(q) || p.preview.toLowerCase().includes(q))
  }
  return result
})

const goToPost = (id) => router.push(`/posts/${id}`)
const goToWrite = () => router.push('/posts/write')
</script>

<style scoped>
.page-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px 60px;
  font-family: 'Pretendard', 'Apple SD Gothic Neo', sans-serif;
}

.page-header {
  background: linear-gradient(135deg, #f5f0ff 0%, #ede7ff 100%);
  border-radius: 16px;
  padding: 32px;
  margin: 24px 0 24px;
}
.header-inner { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.header-title { display: flex; align-items: center; gap: 16px; }
.header-icon { font-size: 36px; }
.header-title h1 { font-size: 24px; font-weight: 700; color: #1a1a2e; margin: 0 0 4px; }
.header-title p { font-size: 14px; color: #888; margin: 0; }
.btn-primary {
  background: #7c4dff; color: white;
  border: none; padding: 10px 20px; border-radius: 8px;
  font-size: 14px; font-weight: 600; cursor: pointer; transition: background 0.2s;
}
.btn-primary:hover { background: #6a3de8; }

.header-search {
  display: flex; align-items: center;
  background: white; border: 1.5px solid #e8e0ff;
  border-radius: 10px; padding: 10px 16px; gap: 10px;
}
.search-icon { color: #aaa; }
.search-input { flex: 1; border: none; outline: none; font-size: 14px; background: transparent; }

.content-layout { display: grid; grid-template-columns: 1fr 300px; gap: 24px; }
@media (max-width: 900px) { .content-layout { grid-template-columns: 1fr; } }

/* Section Title */
.section-title {
  display: flex; align-items: center; gap: 8px;
  font-size: 16px; font-weight: 700; color: #1a1a2e;
  margin-bottom: 16px;
}
.board-tabs { display: flex; gap: 6px; margin-left: auto; }
.board-tab {
  padding: 5px 12px; border-radius: 8px;
  border: 1px solid #e8e0ff; background: white;
  color: #888; font-size: 12px; cursor: pointer; transition: all 0.2s;
}
.board-tab:hover { border-color: #7c4dff; color: #7c4dff; }
.board-tab.active { background: #7c4dff; color: white; border-color: #7c4dff; }

/* Category Grid */
.category-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
@media (max-width: 768px) { .category-grid { grid-template-columns: repeat(2, 1fr); } }

.category-card {
  background: white; border: 1.5px solid #f0ebff;
  border-radius: 14px; padding: 16px; cursor: pointer;
  transition: all 0.2s; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.category-card:hover { box-shadow: 0 8px 24px rgba(124,77,255,0.12); transform: translateY(-2px); }
.cat-icon { font-size: 24px; margin-bottom: 8px; }
.cat-info h4 { font-size: 13px; font-weight: 700; color: #1a1a2e; margin: 0 0 4px; }
.cat-info p { font-size: 11px; color: #aaa; margin: 0 0 6px; line-height: 1.4; }
.cat-count { font-size: 11px; color: #7c4dff; font-weight: 600; }

/* Post List */
.post-list { display: flex; flex-direction: column; }
.post-item {
  padding: 18px 0; border-bottom: 1px solid #f5f0ff;
  cursor: pointer; transition: background 0.15s; border-radius: 8px;
}
.post-item:hover { background: #faf8ff; padding-left: 8px; }
.post-content { padding: 0 8px; }
.post-top { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.post-category { font-size: 12px; font-weight: 600; }
.badge-hot { font-size: 11px; color: #ff4757; font-weight: 600; }
.post-title { font-size: 15px; font-weight: 600; color: #1a1a2e; margin: 0 0 6px; }
.post-item:hover .post-title { color: #7c4dff; }
.post-preview {
  font-size: 13px; color: #888; margin: 0 0 12px; line-height: 1.5;
  display: -webkit-box; -webkit-line-clamp: 2; line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.post-meta { display: flex; align-items: center; justify-content: space-between; }
.author-info { display: flex; align-items: center; gap: 8px; }
.avatar { width: 24px; height: 24px; border-radius: 50%; object-fit: cover; }
.author { font-size: 13px; font-weight: 600; color: #555; }
.date { font-size: 12px; color: #aaa; }
.post-stats { display: flex; gap: 12px; }
.post-stats span { font-size: 12px; color: #aaa; }

.btn-load-more {
  width: 100%; margin-top: 20px; padding: 12px;
  background: white; border: 1.5px solid #e8e0ff;
  border-radius: 10px; color: #7c4dff; font-size: 14px;
  font-weight: 600; cursor: pointer; transition: all 0.2s;
}
.btn-load-more:hover { background: #f5f0ff; }

/* Sidebar */
.sidebar { display: flex; flex-direction: column; gap: 16px; }
.sidebar-card {
  background: white; border: 1.5px solid #f0ebff;
  border-radius: 16px; padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.sidebar-title { font-size: 15px; font-weight: 700; color: #1a1a2e; margin: 0 0 14px; }

.hot-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 10px; }
.hot-item { display: flex; align-items: flex-start; gap: 8px; cursor: pointer; }
.hot-rank {
  width: 20px; height: 20px; border-radius: 50%;
  background: #f0f0f0; color: #888; font-size: 11px; font-weight: 700;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 1px;
}
.hot-rank.top { background: #7c4dff; color: white; }
.hot-text { font-size: 13px; color: #333; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

.user-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 12px; }
.user-item { display: flex; align-items: center; gap: 10px; }
.user-avatar { width: 32px; height: 32px; border-radius: 50%; object-fit: cover; }
.user-info { flex: 1; display: flex; flex-direction: column; }
.user-name { font-size: 13px; font-weight: 600; color: #333; }
.user-posts { font-size: 12px; color: #aaa; }
.user-badge { font-size: 18px; }

.notice-card { background: #faf8ff; }
.notice-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 10px; }
.notice-item { display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; }
.notice-text { font-size: 13px; color: #444; line-height: 1.4; cursor: pointer; }
.notice-text:hover { color: #7c4dff; }
.notice-date { font-size: 11px; color: #aaa; white-space: nowrap; }
</style>
