<template>
  <div class="post-container">
    <header class="post-header reveal">
      <p class="subtitle">DEVELOPER LOUNGE</p>
      <h1 class="title">📝 게시글</h1>
      <h3>개발 지식과 경험을 공유하세요.</h3>
      <button class="write-btn" @click="goToWrite">글쓰기</button>
    </header>

    <div class="filter-wrapper reveal">
      <div class="search-row">
        <div class="search-box">
          <i class="fas fa-search search-icon"></i>
          <input type="text" v-model="searchQuery" placeholder="제목이나 작성자 검색" class="search-input">
        </div>
        <div class="sort-options">
          <span :class="{ active: currentSort === 'popular' }" @click="currentSort = 'popular'">인기순</span>
          <span class="divider">|</span>
          <span :class="{ active: currentSort === 'latest' }" @click="currentSort = 'latest'">최신순</span>
          <span class="divider">|</span>
          <span :class="{ active: currentSort === 'views' }" @click="currentSort = 'views'">조회순</span>
        </div>
      </div>

      <div class="category-row">
        <button v-for="category in categories" :key="category" @click="selectedCategory = category"
          :class="['tag-btn', { active: selectedCategory === category }]">
          {{ category }}
        </button>
      </div>
    </div>

    <div v-if="sortedPosts.length === 0" class="empty-state reveal">
      조건에 맞는 게시글이 없습니다.
    </div>

    <div class="post-list">
      <div v-for="(post, index) in sortedPosts" :key="post.id" class="post-item card card-hidden"
        :style="{ '--index': index + 2 }" @click="viewPost(post.id)">

        <div class="post-id-section">
          <span class="post-number">{{ post.id }}</span>
        </div>

        <div class="post-main-section">
          <h3 class="post-title">{{ post.title }}</h3>
          <p class="post-author">작성자: {{ post.author_name || post.author_id }}</p>
          <p class="post-like">❤️ {{ post.like_count || 0 }}</p>
          <p class="post-excerpt">{{ post.content }}</p>

        </div>

        <div class="post-meta-section">
          <div class="meta-item category-item">
            <span class="label">카테고리</span>
            <span class="value highlighted">{{ post.job_category || '미지정' }}</span>
          </div>
          <div class="meta-item">
            <span class="label">조회수</span>
            <span class="value">{{ post.view_count || 0 }}</span>
          </div>
          <div class="meta-item">
            <span class="label">작성일</span>
            <span class="value">{{ formatDate(post.created_at) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { useNotices } from '@/composables/useNotices'; // 경로는 실제 위치에 맞게 수정


export default {
  data() {

    return {
      searchQuery: '',
      selectedCategory: '전체',
      currentSort: 'popular',
      categories: ['전체', '백엔드', '프론트엔드', '기획', '디자인', '개발', '질문', '정보', '기타'],
      posts: []
    }
  },
  computed: {
    sortedPosts() {
      let list = Array.isArray(this.posts) ? [...this.posts] : [];

      // 공지글(9999)과 일반글 분리
      const pinned = list.filter(p => p.id === 9999);
      let normal = list.filter(p => p.id !== 9999);

      // 1. 검색어 필터링 (일반글에만 적용)
      if (this.searchQuery && this.searchQuery.trim() !== '') {
        const query = this.searchQuery.toLowerCase().trim();
        normal = normal.filter(p =>
          (p.title && p.title.toLowerCase().includes(query)) ||
          (p.content && p.content.toLowerCase().includes(query))
        );
      }

      // 2. 카테고리 필터링 (일반글에만 적용)
      if (this.selectedCategory && this.selectedCategory !== '전체') {
        normal = normal.filter(p => p.job_category === this.selectedCategory);
      }

      // 3. 정렬 (일반글에만 적용)
      if (this.currentSort === 'popular' || this.currentSort === 'views') {
        normal.sort((a, b) => (b.view_count || 0) - (a.view_count || 0));
      } else {
        normal.sort((a, b) => (b.id || 0) - (a.id || 0));
      }

      // 공지글 항상 맨 위 고정
      return [...pinned, ...normal];
    }

  },

  watch: {
    sortedPosts() {
      this.$nextTick(() => this.initReveal());
    }
  },

  async created() {
    const { notices } = useNotices();

    // id: 2 "게시판 안내 및 주의사항" 가져오기
    const noticePost = notices.value.find(n => n.id === 2);

    if (noticePost) {
      this.posts = [{
        id: 9999,
        title: '📌 ' + noticePost.title,
        author_id: 'admin',
        author_name: '관리자',
        job_category: '공지',
        content: noticePost.body.replace(/<[^>]*>/g, '').trim(), // HTML 태그 제거 후 텍스트만
        view_count: 0,
        like_count: 0,
        created_at: new Date(noticePost.date).toISOString()
      }];
    }
    await this.fetchPosts();
  },
  mounted() { this.initReveal(); },
  methods: {
    async fetchPosts() {
      try {
        const response = await axios.get('http://localhost:8000/posts/');
        if (response.data) {
          // API 데이터에는 like_count가 그대로 유지됨
          // 하드코딩 공지글은 따로 보존
          const fixedPosts = this.posts.filter(p => p.id === 9999);
          this.posts = [...fixedPosts, ...response.data];
        }
        this.$nextTick(() => this.initReveal());
      } catch (e) { console.error(e); }
    },
    initReveal() {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) entry.target.classList.add("is-visible");
        });
      }, { threshold: 0.1 });
      const targets = document.querySelectorAll(".reveal, .card-hidden"); // ← 추가

      if (targets.length === 0) {
        setTimeout(() => this.initReveal(), 200);
        return;
      }
      targets.forEach(el => observer.observe(el));
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`;
    },
    viewPost(id) {
      if (id === 9999) {
        this.$router.push('/notice/1'); // useNotices.js의 id: 1 "게시판 안내 및 주의사항"
        return;
      }
      this.$router.push(`/posts/${id}`);
    },
    goToWrite() {
      // 여기도 'access_token'으로 수정
      const token = localStorage.getItem('access_token');

      if (!token) {
        alert("로그인 후 이용할 수 있습니다.");
        this.$router.push('/login');
        return;
      }
      this.$router.push('/posts/create');
    }
  }
}
</script>

<style scoped>
/* 기본 컨테이너 설정 */
/* 1. 컨테이너 위치 조정: 헤더 시작 위치를 채용공고와 동일하게 맞춤 */
.post-container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 40px 40px 40px;
  /* 좌우 패딩 20px → 40px */
}

/* 2. 헤더 레이아웃: 위치 고정 및 글쓰기 버튼 우측 배치 */
.post-header {
  padding: 60px 20px 20px 0px;
  /* 왼쪽 패딩 35px → 0px */
  position: relative;
  text-align: left;
}


.post-header .subtitle {
  color: #a68b6a;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 2px;
  margin-bottom: 12px;
}

.post-header .title {
  font-size: 32px;
  font-weight: 800;
  color: #333;
  margin-bottom: 15px;
}

.post-header h3 b {
  font-size: 18px;
  color: #666;
  font-weight: 500;
}

/* 글쓰기 버튼: 템플릿 분류 없이 CSS로만 오른쪽 끝 고정 */
.write-btn {
  position: absolute;
  right: 0;
  bottom: 60px;
  /* 제목 라인에 맞춰 조절 */
  padding: 12px 28px;
  background-color: #5d4037;
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
}

.write-btn:hover {
  background: #3e2723;
  transform: translateY(-2px);
}

/* 필터 바 */
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


.search-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-box {
  display: flex;
  align-items: center;
  padding: 0;
  background: none;
  /* 기존 #f8f9fa 제거 */
}


.search-input {
  border: none;
  /* 기존 border: 1px solid #eee 제거 */
  background: #f2f0ed;
  /* 기존 #f8f6f3 → #f2f0ed */
  padding: 12px 20px;
  border-radius: 12px;
  width: 400px;
  outline: none;
}


.sort-options {
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

/* 리스트 및 카드 디자인 */
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
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.03);
}

.post-item:hover {
  transform: translateX(10px);
  background: #fdfaf7;
}

/* 섹션 구분 */
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
  font-size: 22px;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 6px;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.post-author {
  font-size: 13px;
  color: #a68b6a;
  font-weight: 600;
  margin-bottom: 4px;
}

.post-like {
  font-size: 13px;
  color: #e57373;
  font-weight: 600;
  margin-bottom: 4px;
}

.post-excerpt {
  font-size: 14px;
  color: #777;
  line-height: 1.4;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.post-meta-section {
  display: flex;
  gap: 40px;
  text-align: right;
  min-width: 180px;
  flex-shrink: 0;
}

.meta-item {
  display: flex;
  flex-direction: column;
}

.label {
  font-size: 15px;
  color: #550f0f;
  margin-bottom: 4px;
  text-transform: uppercase;
  text-align: center;
}

.value {
  font-size: 18px;
  color: #555;
  font-weight: 600;
  text-align: center;
}

/* 애니메이션을 위해 필수적인 CSS */
.reveal {
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.6s ease-out;
}

.reveal.is-visible {
  opacity: 1;
  transform: translateY(0);
}

/* 필터 영역 레이아웃 조정 */
.filter-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

/* 카테고리 태그 스타일 */
.category-tags {
  display: flex;
  gap: 10px;
  margin-top: 15px;
  /* 검색창 아래 간격 띄우기 */
  flex-wrap: wrap;
}

.category-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag-btn {
  padding: 8px 18px;
  border-radius: 25px;
  border: 1px solid #eee;
  background: white;
  color: #888;
  font-size: 13px;
  cursor: pointer;
  transition: 0.2s;
}

.tag-btn.active {
  background: #5d4037;
  color: white;
  border-color: #5d4037;
}

.tag-btn:hover {
  background: #e5e0d8;
}

/* 게시글 메타 영역 레이아웃 수정 */
.post-meta-section {
  display: flex;
  gap: 30px;
  min-width: 250px;
  justify-content: flex-end;
}

.category-item .value.highlighted {
  color: #5d4037;
  font-weight: 700;
}

/* 리스트 내 직무 분야 배지 */
.post-badge {
  display: inline-block;
  background: #f0ede9;
  color: #5d4037;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: bold;
  vertical-align: middle;
}

.empty-state {
  text-align: center;
  padding: 50px;
  color: #a68b6a;
}

.card-hidden {
  opacity: 0;
  transform: translateY(2rem);
  filter: blur(8px);
  transition: opacity 0.9s cubic-bezier(0.16, 1, 0.3, 1),
    filter 0.9s cubic-bezier(0.16, 1, 0.3, 1),
    transform 0.9s cubic-bezier(0.16, 1, 0.3, 1);
}

.card-hidden.is-visible {
  opacity: 1;
  transform: translateY(0);
  filter: blur(0);
}

.card-hidden.is-visible:hover {
  transform: translateX(10px);
  /* 기존 post-item hover 효과 유지 */
  background: #fdfaf7;
}

@media (max-width: 768px) {
  .post-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
    padding: 25px;
  }

  .post-meta-section {
    text-align: left;
    min-width: unset;
    gap: 20px;
    border-top: 1px solid #f5f5f5;
    padding-top: 15px;
    width: 100%;
  }

  .post-id-section {
    display: none;
  }

  /* 모바일에서는 ID 생략 가능 */
}
</style>