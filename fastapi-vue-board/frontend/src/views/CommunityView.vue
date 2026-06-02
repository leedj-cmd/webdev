<template>
  <div class="community-page-wrapper">
    <header class="community-header reveal">
      <div class="header-left">
        <p class="subtitle">COMMUNITY</p>
        <h1 class="title">💬 커뮤니티</h1>
        <h3>개발자들과 소통하고 지식을 나누세요</h3>
      </div>
      <button class="write-btn" @click="goToCreate">
        <i class="fas fa-pen"></i> 글쓰기
      </button>
    </header>

    <main class="page-main">
      <!-- 검색 / 정렬 / 글쓰기 -->
      <div class="filter-wrapper reveal">
        <div class="search-box">
          <i class="fas fa-search search-icon"></i>
          <input v-model="searchQuery" type="text" placeholder="키워드 검색" class="search-input" />
        </div>
        <div class="filter-right">
          <div class="sort-options">
            <span :class="{ active: currentSort === 'latest' }" @click="currentSort = 'latest'">최신순</span>
            <span class="divider">|</span>
            <span :class="{ active: currentSort === 'popular' }" @click="currentSort = 'popular'">인기순</span>
          </div>
        </div>
      </div>

      <div class="content-layout">
        <!-- 좌측 메인 -->
        <div class="main-column">

          <!-- 카테고리 카드 -->
          <section class="reveal">
            <h2 class="section-title">📋 커뮤니티 카테고리</h2>
            <div class="category-grid">
              <div
                v-for="cat in categoryCards"
                :key="cat.id"
                class="category-card"
                :class="{ active: selectedCategory === cat.id }"
                @click="selectedCategory = selectedCategory === cat.id ? null : cat.id"
              >
                <div class="icon-box" :style="{ backgroundColor: cat.color + '18' }">
                  <span class="cat-icon-text">{{ cat.icon }}</span>
                </div>
                <div class="cat-info">
                  <h3 class="cat-name">{{ cat.name }}</h3>
                  <span class="cat-count">{{ getCategoryCount(cat.id) }}개</span>
                </div>
              </div>
            </div>
          </section>

          <!-- 게시글 목록 -->
          <section class="reveal" style="margin-top: 40px;">
            <h2 class="section-title">📝 커뮤니티 글</h2>

            <div v-if="loading" class="loading-state">불러오는 중...</div>

            <div v-else-if="sortedPosts.length === 0" class="empty-state">
              작성된 게시글이 없습니다. 첫 번째 글을 작성해보세요!
            </div>

            <div v-else class="post-list">
              <div
                v-for="(post, index) in sortedPosts"
                :key="post.id"
                class="post-item"
                @click="goToDetail(post.id)"
              >
                <div class="post-id-section">
                  <span class="post-number">{{ index + 1 }}</span>
                </div>

                <div class="post-main-section">
                  <h3 class="post-title">{{ post.title }}</h3>
                  <p class="post-author">{{ post.is_anonymous ? '익명' : (post.author_name || `User_${post.owner_id}`) }}</p>
                  <p class="post-excerpt">{{ post.content }}</p>
                </div>

                <div class="post-meta-section">
                  <div class="meta-item">
                    <span class="label">카테고리</span>
                    <span class="value highlighted">{{ categoryLabel(post.category) }}</span>
                  </div>
                  <div class="meta-item">
                    <span class="label">좋아요</span>
                    <span class="value">❤️ {{ post.like_count }}</span>
                  </div>
                  <div class="meta-item">
                    <span class="label">댓글</span>
                    <span class="value">💬 {{ post.comment_count }}</span>
                  </div>
                  <div class="meta-item">
                    <span class="label">작성일</span>
                    <span class="value">{{ formatDate(post.created_at) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>

        <!-- 우측 사이드바 -->
        <aside class="side-column">
          <div class="side-card reveal">
            <h3 class="side-title">⚡ 실시간 인기 토픽</h3>
            <ul class="topic-list">
              <li
                v-for="(post, idx) in popularPosts.slice(0, 5)"
                :key="post.id"
                class="topic-item"
                @click="goToDetail(post.id)"
              >
                <span class="topic-rank">{{ idx + 1 }}</span>
                <span class="topic-text">{{ post.title }}</span>
              </li>
              <li v-if="popularPosts.length === 0" class="topic-item">
                <span class="topic-text" style="color: #bbb;">게시글이 없습니다</span>
              </li>
            </ul>
          </div>

          <div class="side-card reveal">
            <h3 class="side-title">📢 공지사항</h3>
            <ul class="notice-list">
              <li v-for="notice in notices.slice(0, 5)" :key="notice.id" class="notice-item">
                <span class="notice-text">{{ notice.title }}</span>
                <span class="notice-date">{{ notice.date }}</span>
              </li>
            </ul>
          </div>
        </aside>
      </div>
    </main>
  </div>
</template>

<script>
import axios from 'axios';
import { useNotices } from '@/composables/useNotices';

export default {
  setup() {
    const { notices } = useNotices();
    return { notices };
  },
  data() {
    return {
      posts: [],
      loading: true,
      searchQuery: '',
      currentSort: 'latest',
      selectedCategory: 'all',

      categoryCards: [
        { id: 'all',     name: '전체보기',          icon: '🌐', color: '#64748b' },
        { id: 'job',     name: '직무 토크',    icon: '💻', color: '#3b82f6' },
        { id: 'career',  name: '커리어 토크',  icon: '🚀', color: '#10b981' },
        { id: 'project', name: '프로젝트 공유', icon: '🤝', color: '#f59e0b' },
      ],

      catColors: {
        job:     '#3b82f6',
        career:  '#10b981',
        project: '#f59e0b',
      },
    };
  },

  computed: {
    filteredPosts() {
      let list = [...this.posts];
      if (this.selectedCategory !== 'all') {
        list = list.filter(p => p.category === this.selectedCategory);
      }
      if (this.searchQuery.trim()) {
        const q = this.searchQuery.toLowerCase();
        list = list.filter(p =>
          p.title.toLowerCase().includes(q) ||
          (p.content && p.content.toLowerCase().includes(q))
        );
      }
      return list;
    },

    sortedPosts() {
      return [...this.filteredPosts].sort((a, b) => {
        if (this.currentSort === 'popular') return (b.like_count || 0) - (a.like_count || 0);
        return new Date(b.created_at) - new Date(a.created_at);
      });
    },

    popularPosts() {
      return [...this.posts].sort((a, b) => (b.like_count || 0) - (a.like_count || 0));
    },
  },

  async created() {
    await this.fetchPosts();
  },

  methods: {
    async fetchPosts() {
      this.loading = true;
      try {
        const res = await axios.get('http://localhost:8000/community/');
        this.posts = res.data;
      } catch (e) {
        console.error('커뮤니티 목록 로드 실패:', e);
      } finally {
        this.loading = false;
      }
    },

    getCategoryCount(catId) {
      if (catId === 'all') return this.posts.length;
      return this.posts.filter(p => p.category === catId).length;
    },

    categoryLabel(cat) {
      const map = { job: '직무 토크', career: '커리어 토크', project: '프로젝트 공유' };
      return map[cat] || cat;
    },

    getCatColor(cat) {
      return this.catColors[cat] || '#888';
    },

    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      const now = new Date();
      const diff = Math.floor((now - date) / 1000);
      if (diff < 60) return '방금 전';
      if (diff < 3600) return `${Math.floor(diff / 60)}분 전`;
      if (diff < 86400) return `${Math.floor(diff / 3600)}시간 전`;
      return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`;
    },

    goToCreate() {
      const token = localStorage.getItem('access_token');
      if (!token) {
        alert('로그인 후 이용할 수 있습니다.');
        this.$router.push('/login');
        return;
      }
      this.$router.push('/community/create');
    },

    goToDetail(id) {
      this.$router.push(`/community/${id}`);
    },
  },
};
</script>

<style scoped>
.community-page-wrapper {
  font-family: 'Pretendard', sans-serif;
  letter-spacing: -0.03em;
}

.community-header {
  max-width: 1440px;
  margin: 0 auto;
  padding: 60px 40px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
}

.community-header .subtitle {
  color: #a68b6a;
  font-weight: 700;
  margin-bottom: 10px;
}
.community-header .title {
  font-size: 34px;
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 8px;
}

.page-main {
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 40px 100px;
}

/* 검색/필터 바 */
.filter-wrapper {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: 20px 32px;
  background: white;
  border-radius: 20px;
  border: 1px solid #f0ede9;
  box-shadow: 0 4px 16px rgba(0,0,0,0.03);
  margin-bottom: 32px;
}
.search-box {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #bbb;
}
.search-icon { font-size: 15px; }
.search-input {
  border: none;
  outline: none;
  background: transparent;
  font-size: 15px;
  width: 300px;
  color: #333;
}
.filter-right {
  display: flex;
  align-items: center;
  gap: 24px;
}
.sort-options {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #bbb;
  font-weight: 600;
  cursor: pointer;
}
.sort-options span { transition: color 0.2s; }
.sort-options span.active { color: #5d4037; }
.sort-options .divider { color: #ddd; cursor: default; }
.write-btn {
  position: absolute;
  right: 40px;
  bottom: 60px;
  display: flex;
  align-items: center;
  gap: 8px;
  background: #5d4037;
  color: white;
  border: none;
  padding: 11px 22px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}
.write-btn:hover { background: #3e2723; transform: translateY(-1px); }

.more-btn {
  background: none;
  border: 1.5px solid #d6c4b0;
  color: #a68b6a;
  font-size: 13px;
  font-weight: 700;
  padding: 6px 16px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.more-btn:hover {
  background: #5d4037;
  border-color: #5d4037;
  color: white;
}

/* 2단 레이아웃 */
.content-layout {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 30px;
  align-items: start;
}

.section-title {
  font-size: 20px;
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header .section-title {
  margin-bottom: 0;
  /* section-header가 margin을 대신 관리 */
}

/* 카테고리 카드 */
.category-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}
.category-card {
  background: white;
  border: 2px solid transparent;
  border-radius: 20px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.04);
  padding: 22px;
  cursor: pointer;
  transition: all 0.25s ease;
}
.category-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(0,0,0,0.07);
}
.category-card.active { border-color: #5d4037; }
.icon-box {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 14px;
}
.cat-icon-text { font-size: 20px; }
.cat-name {
  font-size: 15px;
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 6px;
}
.cat-count {
  font-size: 13px;
  font-weight: 700;
  color: #a68b6a;
  background: #fdfaf7;
  padding: 3px 10px;
  border-radius: 6px;
  display: inline-block;
}

/* 게시글 목록 */
.post-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.post-item {
  display: flex;
  align-items: center;
  padding: 25px 40px;
  background: white;
  border-radius: 24px;
  cursor: pointer;
  transition: 0.3s;
  box-shadow: 0 10px 40px rgba(0,0,0,0.03);
}
.post-item:hover {
  transform: translateX(10px);
  background: #fdfaf7;
}
.post-id-section {
  width: 60px;
  flex-shrink: 0;
}
.post-number {
  font-size: 20px;
  font-weight: 800;
  color: #422e26;
}
.post-main-section {
  flex: 1;
  padding: 0 20px;
  overflow: hidden;
}
.post-title {
  font-size: 20px;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 6px;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}
.post-author {
  font-size: 14px;
  color: #a68b6a;
  font-weight: 600;
  margin-bottom: 4px;
}
.post-excerpt {
  font-size: 15px;
  color: #777;
  line-height: 1.4;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}
.post-meta-section {
  display: flex;
  gap: 28px;
  text-align: right;
  flex-shrink: 0;
}
.meta-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.meta-item .label {
  font-size: 12px;
  color: #bbb;
  font-weight: 600;
  text-transform: uppercase;
}
.meta-item .value {
  font-size: 14px;
  color: #555;
  font-weight: 600;
}
.meta-item .value.highlighted {
  color: #5d4037;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 60px 0;
  color: #aaa;
  font-size: 15px;
  background: white;
  border-radius: 18px;
  border: 1px dashed #ddd;
}

/* 사이드바 */
.side-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
  position: sticky;
  top: 100px;
}
.side-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.03);
  border: 1px solid #f5f0eb;
}
.side-title {
  font-size: 15px;
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 16px;
}
.topic-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.topic-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  cursor: pointer;
}
.topic-rank {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  background: #f8f6f3;
  color: #a68b6a;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 800;
}
.topic-text {
  font-size: 13px;
  color: #444;
  font-weight: 600;
  line-height: 1.4;
  transition: color 0.2s;
}
.topic-item:hover .topic-text { color: #5d4037; }
.notice-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.notice-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f5f5f5;
}
.notice-item:last-child { border-bottom: none; padding-bottom: 0; }
.notice-text { font-size: 13px; color: #444; font-weight: 600; }
.notice-date { font-size: 11px; color: #bbb; font-weight: 700; flex-shrink: 0; }

/* 애니메이션 */
.reveal { animation: fadeUp 0.6s ease-out forwards; }
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}

@media (max-width: 1100px) {
  .content-layout { grid-template-columns: 1fr; }
  .side-column { position: static; }
  .category-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>