<template>
  <div class="detail-container">

    <!-- 게시글 헤더 -->
    <header class="post-header reveal">
      <span class="category-badge">{{ categoryLabel(post.category) }}</span>
      <div class="title-row">
        <h1 class="post-title">{{ post.title }}</h1>
        <button
          v-if="currentUserId && !post.is_anonymous && post.owner_id && post.owner_id !== currentUserId"
          class="msg-action-btn"
          @click="startChat"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
          메시지 보내기
        </button>
      </div>
      <div class="post-meta">
        <span>작성자: {{ post.is_anonymous ? '익명' : (post.author_name || `User_${post.owner_id}`) }}</span>
        <span class="divider">|</span>
        <span>작성일: {{ formatDate(post.created_at) }}</span>
      </div>
    </header>

    <!-- 본문 -->
    <div class="content-card reveal">
      <div class="post-content" style="white-space: pre-wrap;">{{ post.content }}</div>
    </div>

    <!-- 좋아요 / 댓글 / 신고 -->
    <div class="interaction-section reveal">

      <!-- 좋아요 -->
      <div class="like-wrapper">
        <button class="like-btn" :class="{ liked: isLiked }" @click="toggleLike">
          <i class="fas fa-heart" v-if="isLiked"></i>
          <i class="far fa-heart" v-else></i>
          <span>좋아요 {{ likeCount }}</span>
        </button>
      </div>

      <hr class="section-divider" />

      <!-- 댓글 -->
      <div class="comments-section">
        <h3 class="comments-title">댓글 <span>{{ comments.length }}</span></h3>

        <div class="comment-input-box">
          <textarea v-model="newComment" placeholder="댓글을 남겨보세요." rows="3"></textarea>
          <div class="comment-input-footer">
            <label class="anon-label">
              <input type="checkbox" v-model="newCommentAnon" />
              <span>익명</span>
            </label>
            <button class="submit-comment-btn" @click="submitComment" :disabled="!newComment.trim()">등록</button>
          </div>
        </div>

        <div class="comment-list">
          <div v-for="comment in comments" :key="comment.id" class="comment-item">
            <div class="comment-avatar">
              <div class="avatar-placeholder">
                {{ comment.is_anonymous ? '?' : (comment.author_name ? comment.author_name.charAt(0) : 'U') }}
              </div>
            </div>
            <div class="comment-content">
              <div class="comment-header">
                <span class="comment-author">
                  {{ comment.is_anonymous ? '익명' : (comment.author_name || `User_${comment.user_id}`) }}
                </span>
                <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
                <!-- 본인 댓글 수정/삭제 (익명 댓글도 본인이면 표시) -->
                <div v-if="comment.user_id === currentUserId" class="comment-btn-group">
                  <button @click="startEditComment(comment)" class="comment-edit-btn">수정</button>
                  <button @click="deleteComment(comment.id)" class="comment-delete-btn">삭제</button>
                </div>
              </div>

              <!-- 수정 모드 -->
              <div v-if="editingCommentId === comment.id" class="comment-edit-box">
                <textarea v-model="editingContent" rows="3"></textarea>
                <div class="comment-edit-actions">
                  <button @click="cancelEdit" class="comment-cancel-btn">취소</button>
                  <button @click="submitEditComment(comment.id)" class="comment-save-btn">저장</button>
                </div>
              </div>
              <p v-else class="comment-text">{{ comment.content }}</p>
            </div>
          </div>

          <div v-if="comments.length === 0" class="no-comments">첫 번째 댓글을 남겨보세요!</div>
        </div>
      </div>
    </div>

    <!-- 하단 버튼 -->
    <div class="action-buttons reveal">
      <button class="back-btn" @click="$router.push('/community')">목록으로</button>
      <button v-if="canEdit" class="edit-btn" @click="openEditModal">✏️ 수정</button>
      <button v-if="canDelete" class="delete-btn" @click="deletePost">🗑 삭제</button>
      <button v-if="currentUserId" class="report-btn" @click="reportModal = true">🚨 신고</button>
    </div>

    <!-- 게시글 수정 모달 -->
    <div v-if="editModal" class="modal-overlay" @click.self="editModal = false">
      <div class="modal-box">
        <h3>게시글 수정</h3>
        <div class="form-group">
          <label class="modal-label">제목</label>
          <input v-model="editForm.title" class="modal-input" />
        </div>
        <div class="form-group" style="margin-top:14px;">
          <label class="modal-label">내용</label>
          <textarea v-model="editForm.content" rows="8" class="modal-textarea"></textarea>
        </div>
        <div class="form-group" style="margin-top:14px;">
          <label class="modal-label">카테고리</label>
          <select v-model="editForm.category" class="modal-select">
            <option value="job">직무 토크</option>
            <option value="career">커리어 토크</option>
            <option value="project">프로젝트 공유</option>
          </select>
        </div>
        <p v-if="editError" class="modal-error">{{ editError }}</p>
        <div class="modal-btn-row">
          <button class="modal-cancel" @click="editModal = false">취소</button>
          <button class="modal-submit" @click="submitEdit" :disabled="editSubmitting">
            {{ editSubmitting ? '저장 중...' : '저장' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 신고 모달 -->
    <div v-if="reportModal" class="modal-overlay" @click.self="reportModal = false">
      <div class="modal-box">
        <h3>게시글 신고</h3>
        <p class="modal-desc">신고 사유를 입력해주세요. 허위 신고는 제재를 받을 수 있습니다.</p>
        <textarea
          v-model="reportReason"
          placeholder="신고 사유를 구체적으로 작성해주세요."
          rows="4"
          class="modal-textarea"
        ></textarea>
        <p v-if="reportError" class="modal-error">{{ reportError }}</p>
        <p v-if="reportSuccess" class="modal-success">✅ 신고가 접수되었습니다.</p>
        <div class="modal-btn-row">
          <button class="modal-cancel" @click="reportModal = false">취소</button>
          <button
            class="modal-submit"
            @click="submitReport"
            :disabled="!reportReason.trim() || reportLoading || reportSuccess"
          >
            {{ reportLoading ? '처리 중...' : '신고 접수' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import axios from 'axios';
import api from '@/api/axios';

export default {
  data() {
    return {
      post: {},
      comments: [],
      newComment: '',
      newCommentAnon: false,
      likeCount: 0,
      isLiked: false,
      currentUserId: null,
      currentUserRole: null,

      // 댓글 수정
      editingCommentId: null,
      editingContent: '',

      // 게시글 수정 모달
      editModal: false,
      editForm: { title: '', content: '', category: '' },
      editError: '',
      editSubmitting: false,

      // 신고 모달
      reportModal: false,
      reportReason: '',
      reportError: '',
      reportSuccess: false,
      reportLoading: false,
    };
  },

  computed: {
    canEdit() {
      return this.currentUserId && this.currentUserId === this.post.owner_id;
    },
    canDelete() {
      return this.currentUserId && (
        this.currentUserId === this.post.owner_id ||
        this.currentUserRole === 'admin'
      );
    },
  },

  mounted() {
    window.scrollTo({ top: 0, behavior: 'instant' })
  },
  async created() {
    await Promise.all([
      this.fetchPost(),
      this.fetchCurrentUser(),
    ]);
    await Promise.all([
      this.fetchLikeStatus(),
      this.fetchComments(),
    ]);
  },

  methods: {
    async fetchPost() {
      const id = this.$route.params.id;
      try {
        const res = await axios.get(`http://localhost:8000/community/${id}`);
        this.post = res.data;
      } catch (e) {
        console.error('게시글 로드 실패:', e);
      }
    },

    async fetchCurrentUser() {
      const token = localStorage.getItem('access_token');
      if (!token) return;
      try {
        const res = await axios.get('http://localhost:8000/auth/me', {
          headers: { Authorization: `Bearer ${token}` },
        });
        this.currentUserId = res.data.id;
        this.currentUserRole = res.data.role;
      } catch (e) {
        console.error('유저 정보 로드 실패:', e);
      }
    },

    async fetchLikeStatus() {
      const id = this.$route.params.id;
      const token = localStorage.getItem('access_token');
      try {
        const res = await axios.get(
          `http://localhost:8000/community/${id}/like/status`,
          token ? { headers: { Authorization: `Bearer ${token}` } } : {}
        );
        this.likeCount = res.data.count;
        this.isLiked = res.data.is_liked;
      } catch (e) {
        this.likeCount = 0;
        this.isLiked = false;
      }
    },

    async fetchComments() {
      const id = this.$route.params.id;
      try {
        const res = await axios.get(`http://localhost:8000/community/${id}/comments`);
        this.comments = res.data;
      } catch (e) {
        console.error('댓글 로드 실패:', e);
      }
    },

    async toggleLike() {
      const token = localStorage.getItem('access_token');
      if (!token) { alert('로그인 후 이용할 수 있습니다.'); return; }
      const prevLiked = this.isLiked;
      const prevCount = this.likeCount;
      this.isLiked = !this.isLiked;
      this.likeCount += this.isLiked ? 1 : -1;
      try {
        await axios.post(
          `http://localhost:8000/community/${this.$route.params.id}/like`,
          {},
          { headers: { Authorization: `Bearer ${token}` } }
        );
        await this.fetchLikeStatus();
      } catch (e) {
        this.isLiked = prevLiked;
        this.likeCount = prevCount;
        console.error('좋아요 실패:', e);
      }
    },

    async submitComment() {
      if (!this.newComment.trim()) return;
      const token = localStorage.getItem('access_token');
      if (!token) { alert('로그인 후 댓글을 작성할 수 있습니다.'); return; }
      const content = this.newComment;
      this.newComment = '';
      try {
        await axios.post(
          `http://localhost:8000/community/${this.$route.params.id}/comments`,
          { content, is_anonymous: this.newCommentAnon },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        await this.fetchComments();
      } catch (e) {
        this.newComment = content;
        const detail = e.response?.data?.detail;
        alert(Array.isArray(detail) ? detail.map(d => d.msg).join(', ') : (detail || '댓글 작성 실패'));
      }
    },

    async startChat() {
      const token = localStorage.getItem('access_token');
      if (!token) {
        alert('로그인 후 메시지를 보낼 수 있습니다.');
        this.$router.push('/login');
        return;
      }
      if (this.post.is_anonymous || !this.post.owner_id || this.post.owner_id === this.currentUserId) return;

      try {
        const res = await api.post('/chat/rooms', {
          name: `${this.post.author_name || `User_${this.post.owner_id}`}님과의 대화`,
          type: 'direct',
          member_ids: [this.post.owner_id],
        });
        this.$router.push({ path: '/chat', query: { room: res.data.id } });
      } catch (e) {
        console.error('채팅 시작 실패:', e);
        alert(e.response?.data?.detail || '상대방과 연결할 수 없습니다.');
      }
    },

    startEditComment(comment) {
      this.editingCommentId = comment.id;
      this.editingContent = comment.content;
    },
    cancelEdit() { this.editingCommentId = null; this.editingContent = ''; },

    async submitEditComment(commentId) {
      if (!this.editingContent.trim()) return;
      const token = localStorage.getItem('access_token');
      try {
        await axios.patch(
          `http://localhost:8000/community/${this.$route.params.id}/comments/${commentId}`,
          { content: this.editingContent },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        this.cancelEdit();
        await this.fetchComments();
      } catch (e) {
        alert(e.response?.data?.detail || '댓글 수정 실패');
      }
    },

    async deleteComment(commentId) {
      if (!confirm('댓글을 삭제하시겠습니까?')) return;
      const token = localStorage.getItem('access_token');
      try {
        await axios.delete(
          `http://localhost:8000/community/${this.$route.params.id}/comments/${commentId}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        await this.fetchComments();
      } catch (e) {
        alert(e.response?.data?.detail || '댓글 삭제 실패');
      }
    },

    // 게시글 수정
    openEditModal() {
      this.editForm = {
        title: this.post.title,
        content: this.post.content || '',
        category: this.post.category,
      };
      this.editError = '';
      this.editModal = true;
    },

    async submitEdit() {
      if (!this.editForm.title.trim()) { this.editError = '제목을 입력해주세요.'; return; }
      this.editSubmitting = true;
      this.editError = '';
      const token = localStorage.getItem('access_token');
      try {
        const res = await axios.patch(
          `http://localhost:8000/community/${this.$route.params.id}`,
          {
            title: this.editForm.title.trim(),
            content: this.editForm.content.trim() || null,
            category: this.editForm.category,
          },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        this.post = res.data;
        this.editModal = false;
      } catch (e) {
        this.editError = e.response?.data?.detail || '수정에 실패했습니다.';
      } finally {
        this.editSubmitting = false;
      }
    },

    // 게시글 삭제
    async deletePost() {
      if (!confirm('게시글을 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.')) return;
      const token = localStorage.getItem('access_token');
      try {
        await axios.delete(`http://localhost:8000/community/${this.$route.params.id}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        this.$router.push('/community');
      } catch (e) {
        alert(e.response?.data?.detail || '삭제에 실패했습니다.');
      }
    },

    // 신고
    async submitReport() {
      if (!this.reportReason.trim()) return;
      this.reportLoading = true;
      this.reportError = '';
      const token = localStorage.getItem('access_token');
      try {
        await axios.post(
          `http://localhost:8000/reports/community/${this.$route.params.id}`,
          { reason: this.reportReason },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        this.reportSuccess = true;
        setTimeout(() => { this.reportModal = false; this.reportSuccess = false; }, 1500);
      } catch (e) {
        this.reportError = e.response?.data?.detail || '신고 처리 중 오류가 발생했습니다.';
      } finally {
        this.reportLoading = false;
      }
    },

    // 유틸
    categoryLabel(cat) {
      const map = { job: '직무 토크', career: '커리어 토크', project: '프로젝트 공유' };
      return map[cat] || cat;
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const d = new Date(dateString);
      return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
    },
  },
};
</script>

<style scoped>
.detail-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 60px 20px 100px;
}

/* 헤더 */
.post-header {
  margin-bottom: 32px;
  border-bottom: 2px solid #f0ede9;
  padding-bottom: 28px;
}
.title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 16px;
}
.category-badge {
  display: inline-block;
  background: #f8f3ef;
  color: #5d4037;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 20px;
  margin-bottom: 14px;
  letter-spacing: 0.05em;
}
.post-title {
  font-size: 32px;
  font-weight: 800;
  color: #1a1a1a;
  line-height: 1.3;
  margin-bottom: 0;
  flex: 1;
}
.msg-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  padding: 10px 18px;
  border: 1.5px solid #ebdccf;
  border-radius: 12px;
  background: #fdf5f0;
  color: #835d43;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}
.msg-action-btn:hover {
  background: #835d43;
  color: white;
  border-color: #835d43;
  transform: translateY(-2px);
}
.post-meta {
  display: flex;
  gap: 12px;
  font-size: 14px;
  color: #999;
}
.divider { color: #ddd; }

/* 본문 */
.content-card {
  background: white;
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.04);
  padding: 44px 40px;
  min-height: 260px;
  margin-bottom: 36px;
}
.post-content { font-size: 16px; color: #333; line-height: 1.85; }

/* 좋아요/댓글 */
.interaction-section { margin-bottom: 40px; }
.like-wrapper { display: flex; justify-content: center; margin-bottom: 28px; }
.like-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 26px;
  background: white;
  border: 1px solid #e0d8d0;
  border-radius: 30px;
  font-size: 15px;
  font-weight: 600;
  color: #555;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 10px rgba(0,0,0,0.04);
}
.like-btn i { color: #ccc; font-size: 17px; }
.like-btn.liked i { color: #ff4757; }
.like-btn.liked { border-color: #ff4757; color: #ff4757; }
.like-btn:hover { transform: translateY(-2px); }

.section-divider { border: 0; height: 1px; background: #eee; margin-bottom: 28px; }

.comments-title {
  font-size: 17px;
  font-weight: 700;
  color: #333;
  margin-bottom: 18px;
}
.comments-title span { color: #a68b6a; margin-left: 6px; }

.comment-input-box {
  background: white;
  border: 1px solid #e0d8d0;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 28px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}
.comment-input-box textarea {
  width: 100%;
  border: none;
  resize: none;
  outline: none;
  font-size: 15px;
  color: #333;
  font-family: inherit;
  box-sizing: border-box;
}
.comment-input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}
.anon-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #888;
  cursor: pointer;
}

.submit-comment-btn {
  background: #5d4037;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  font-family: inherit;
}
.submit-comment-btn:disabled { background: #ccc; cursor: not-allowed; }
.submit-comment-btn:hover:not(:disabled) { background: #4a332c; }

.comment-list { display: flex; flex-direction: column; gap: 18px; }
.comment-item {
  display: flex;
  gap: 14px;
  padding-bottom: 18px;
  border-bottom: 1px solid #f5f5f5;
}
.avatar-placeholder {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #f0ede9;
  color: #a68b6a;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 16px;
  flex-shrink: 0;
}
.comment-content { flex: 1; }
.comment-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.comment-author { font-size: 14px; font-weight: 700; color: #333; }
.comment-date { font-size: 12px; color: #aaa; }
.comment-text { font-size: 14px; color: #555; line-height: 1.6; white-space: pre-wrap; }

.comment-btn-group { display: flex; gap: 6px; margin-left: auto; }
.comment-edit-btn, .comment-delete-btn {
  padding: 3px 10px;
  font-size: 12px;
  font-weight: 600;
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid;
  font-family: inherit;
  transition: all 0.2s;
}
.comment-edit-btn { background: #f8f6f3; color: #5d4037; border-color: #e0d8d0; }
.comment-edit-btn:hover { background: #5d4037; color: white; }
.comment-delete-btn { background: #fff5f5; color: #c62828; border-color: #ffcdd2; }
.comment-delete-btn:hover { background: #c62828; color: white; }

.comment-edit-box { margin-top: 8px; }
.comment-edit-box textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 10px 12px;
  border: 1.5px solid #e0d8d0;
  border-radius: 10px;
  font-size: 14px;
  font-family: inherit;
  outline: none;
  resize: vertical;
}
.comment-edit-box textarea:focus { border-color: #5d4037; }
.comment-edit-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 6px; }
.comment-cancel-btn {
  padding: 5px 14px;
  border: 1px solid #e0d8d0;
  border-radius: 6px;
  background: white;
  color: #888;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
}
.comment-save-btn {
  padding: 5px 14px;
  border: none;
  border-radius: 6px;
  background: #5d4037;
  color: white;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
}

.no-comments {
  text-align: center;
  padding: 40px;
  color: #bbb;
  font-size: 14px;
  background: #fdfdfd;
  border-radius: 12px;
  border: 1px dashed #ddd;
}

/* 하단 버튼 */
.action-buttons {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 40px;
}
.back-btn {
  padding: 13px 36px;
  background: #f8f6f3;
  color: #5d4037;
  border: 1px solid #e0d8d0;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}
.back-btn:hover { background: #5d4037; color: white; }
.edit-btn {
  padding: 13px 24px;
  background: #f8f6f3;
  color: #5d4037;
  border: 1px solid #e0d8d0;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}
.edit-btn:hover { background: #5d4037; color: white; }
.delete-btn, .report-btn {
  padding: 13px 24px;
  background: #fff5f5;
  color: #c62828;
  border: 1px solid #ffcdd2;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}
.delete-btn:hover, .report-btn:hover { background: #c62828; color: white; border-color: #c62828; }

/* 모달 공통 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}
.modal-box {
  background: white;
  border-radius: 24px;
  padding: 38px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
}
.modal-box h3 {
  font-size: 20px;
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 18px;
}
.modal-desc { font-size: 13px; color: #888; margin-bottom: 14px; }
.modal-label { font-size: 13px; font-weight: 700; color: #555; display: block; margin-bottom: 6px; }
.modal-input {
  width: 100%;
  box-sizing: border-box;
  padding: 12px 14px;
  border: 1.5px solid #e0d8d0;
  border-radius: 10px;
  font-size: 15px;
  font-family: inherit;
  outline: none;
}
.modal-input:focus { border-color: #5d4037; }
.modal-textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 12px 14px;
  border: 1.5px solid #e0d8d0;
  border-radius: 10px;
  font-size: 14px;
  font-family: inherit;
  outline: none;
  resize: vertical;
  background: #fdfaf7;
}
.modal-textarea:focus { border-color: #5d4037; }
.modal-select {
  width: 100%;
  box-sizing: border-box;
  padding: 12px 14px;
  border: 1.5px solid #e0d8d0;
  border-radius: 10px;
  font-size: 14px;
  font-family: inherit;
  outline: none;
  background: white;
  cursor: pointer;
}
.modal-error {
  font-size: 13px;
  color: #c62828;
  background: #ffebee;
  padding: 10px 14px;
  border-radius: 8px;
  margin-top: 12px;
}
.modal-success {
  font-size: 13px;
  color: #2e7d32;
  background: #e8f5e9;
  padding: 10px 14px;
  border-radius: 8px;
  margin-top: 12px;
}
.modal-btn-row {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}
.modal-cancel {
  padding: 11px 22px;
  border: 1.5px solid #e0d8d0;
  border-radius: 10px;
  background: white;
  font-size: 14px;
  font-weight: 700;
  color: #888;
  cursor: pointer;
  font-family: inherit;
}
.modal-cancel:hover { background: #f8f6f3; }
.modal-submit {
  padding: 11px 22px;
  background: #5d4037;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s;
  font-family: inherit;
}
.modal-submit:hover:not(:disabled) { background: #3e2723; }
.modal-submit:disabled { opacity: 0.5; cursor: not-allowed; }

@media (max-width: 768px) {
  .title-row {
    flex-direction: column;
  }

  .msg-action-btn {
    width: 100%;
    justify-content: center;
  }
}

.reveal { animation: fadeUp 0.6s ease-out forwards; }
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>
