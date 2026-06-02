<template>
  <div class="post-detail-container">

    <header class="post-header reveal" style="--index: 0">
      <p class="subtitle" v-if="post.job_category">{{ post.job_category }} / {{ post.region }}</p>
      <p class="subtitle" v-else>COMMUNITY BOARD</p>
      <div class="title-row">
        <h1 class="title">{{ post.title }}</h1>
        <!-- ★ 메시지 보내기 버튼 추가 -->
        <button 
          v-if="currentUserId && post.author_id && post.author_id !== currentUserId" 
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
        <span>작성자: {{ post.author_name || post.author_id }}</span>
        <span class="divider">|</span>
        <span>작성일: {{ formatDate(post.created_at) }}</span>
        <span class="divider">|</span>
        <span>조회수: {{ post.view_count || 0 }}</span>
      </div>
    </header>

    <div class="content-card card reveal" style="--index: 1">
      <div class="post-content" style="white-space: pre-wrap;">
        {{ post.content }}
      </div>
    </div>

    <div class="interaction-section reveal" style="--index: 2">

      <div class="like-wrapper">
        <button class="like-btn" :class="{ 'liked': isLiked }" @click="toggleLike">
          <i class="fas fa-heart" v-if="isLiked"></i>
          <i class="far fa-heart" v-else></i>
          <span>좋아요 {{ likeCount }}</span>
        </button>
      </div>

      <hr class="section-divider" />

      <div class="comments-section">
        <h3 class="comments-title">댓글 <span>{{ comments.length }}</span></h3>

        <div class="comment-input-box">
          <textarea v-model="newComment" placeholder="댓글을 남겨보세요." rows="3"></textarea>
          <div class="comment-actions">
            <button class="submit-comment-btn" @click="submitComment" :disabled="!newComment.trim() || isSubmittingComment">
              {{ isSubmittingComment ? '등록 중...' : '등록' }}
            </button>
          </div>
        </div>

        <div class="comment-list">
          <div v-for="comment in comments" :key="comment.id" class="comment-item">
            <div class="comment-avatar">
              <div class="avatar-placeholder">{{ comment.author_name ? comment.author_name[0] : 'U' }}</div>
            </div>
            <div class="comment-content">
              <div class="comment-header">
                <span class="comment-author">{{ comment.author_name || 'User_' + comment.user_id }}</span>
                <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
                <!-- 본인 댓글일 때만 수정/삭제 버튼 표시 -->
                <div v-if="comment.user_id === currentUserId" class="comment-btn-group">
                  <button @click="startEditComment(comment)" class="comment-edit-btn">수정</button>
                  <button @click="deleteComment(comment.id)" class="comment-delete-btn">삭제</button>
                </div>
              </div>
              <!-- 수정 모드일 때 textarea, 아닐 때 텍스트 표시 -->
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

          <div v-if="comments.length === 0" class="no-comments">
            첫 번째 댓글을 남겨보세요!
          </div>
        </div>
      </div>
    </div>

    <div class="action-buttons reveal" style="--index: 3">
      <button class="back-btn" @click="goBack">목록으로</button>
      <!-- 삭제 버튼: 본인 또는 관리자에게만 표시 -->
      <button v-if="canDelete" class="delete-btn" @click="deletePost">
        🗑 게시글 삭제
      </button>
      <!-- 신고 버튼: 로그인한 유저에게만 표시 -->
      <button v-if="currentUserId" class="report-btn" @click="openReportModal">
        🚨 신고하기
      </button>
    </div>

    <!-- 신고 모달 -->
    <div v-if="reportModal" class="modal-overlay" @click.self="closeReportModal">
      <div class="modal-box">
        <h3>게시글 신고</h3>
        <p class="modal-desc">신고 사유를 입력해주세요. 허위 신고는 제재를 받을 수 있습니다.</p>
        <textarea
          v-model="reportReason"
          placeholder="신고 사유를 구체적으로 작성해주세요. (예: 욕설, 스팸, 불법 정보 등)"
          rows="4"
          class="report-textarea"
        ></textarea>
        <p v-if="reportError" class="report-error">{{ reportError }}</p>
        <p v-if="reportSuccess" class="report-success">✅ 신고가 접수되었습니다.</p>
        <div class="modal-btn-row">
          <button class="modal-cancel" @click="closeReportModal">취소</button>
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

    <!-- 비속어 안내 모달 -->
    <CensorshipModal 
      :show="showCensorshipModal" 
      :detail="censorshipDetail" 
      @close="showCensorshipModal = false" 
    />

  </div>
</template>

<script>
import api from '@/api/axios';
import CensorshipModal from '@/components/CensorshipModal.vue';

export default {
  components: {
    CensorshipModal
  },
  data() {
    return {
      post: {},
      comments: [],
      newComment: '',
      likeCount: 0,
      isLiked: false,
      currentUserId: null,
      isSubmittingComment: false,
      showCensorshipModal: false,
      censorshipDetail: '',
      currentUserRole: null,

      // 댓글 수정 관련
      editingCommentId: null,
      editingContent: '',

      // 신고 관련
      reportModal: false,
      reportReason: '',
      reportLoading: false,
      reportError: '',
      reportSuccess: false,
    };
  },
  computed: {
    canDelete() {
      return this.currentUserId && (
        this.currentUserId === this.post.author_id ||
        this.currentUserRole === 'admin'
      );
    }
  },
  mounted() {
    window.scrollTo({ top: 0, behavior: 'instant' })
  },
  async created() {
    await this.fetchPostDetail();
    await this.fetchCurrentUser();
    await this.fetchLikeStatus();
    await this.fetchComments();
  },
  methods: {
    async fetchPostDetail() {
      const postId = this.$route.params.id;
      try {
        const response = await api.get(`/posts/${postId}`);
        this.post = response.data;
      } catch (error) {
        console.error("게시글 로드 오류:", error);
      }
    },

    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
    },

    goBack() {
      this.$router.push('/posts');
    },

    async fetchComments() {
      try {
        const response = await api.get(`/comments/posts/${this.$route.params.id}`);
        this.comments = response.data;
      } catch (error) {
        console.error("댓글 불러오기 실패:", error);
      }
    },

    async toggleLike() {
      const token = localStorage.getItem('access_token');
      if (!token) {
        alert("로그인 후 이용할 수 있습니다.");
        return;
      }
      const postId = this.$route.params.id;

      const originalLiked = this.isLiked;
      const originalCount = this.likeCount;

      this.isLiked = !this.isLiked;
      this.likeCount += this.isLiked ? 1 : -1;

      try {
        if (this.isLiked) {
          await api.post(`/interactions/${postId}/likes`, {});
        } else {
          await api.delete(`/interactions/${postId}/likes/${this.currentUserId}`);
        }
        // 서버 실제 값으로 동기화
        await this.fetchLikeStatus();
      } catch (error) {
        console.error("좋아요 처리 실패:", error);
        this.isLiked = originalLiked;
        this.likeCount = originalCount;
      }
    },

    async fetchCurrentUser() {
      const token = localStorage.getItem('access_token');
      if (!token) return;
      try {
        const res = await api.get('/auth/me');
        this.currentUserId = res.data.id;
        this.currentUserRole = res.data.role;
      } catch (e) {
        console.error("유저 정보 로드 실패:", e);
      }
    },

    async fetchLikeStatus() {
      const postId = this.$route.params.id;
      try {
        const res = await api.get(`/interactions/${postId}/likes/status`);
        this.likeCount = res.data.count;
        this.isLiked = res.data.is_liked;
      } catch (e) {
        this.likeCount = 0;
        this.isLiked = false;
      }
    },

    async submitComment() {
      if (!this.newComment.trim()) return;

      const token = localStorage.getItem('access_token');
      if (!token) {
        alert("로그인 후 이용할 수 있습니다.");
        this.$router.push('/login');
        return;
      }

      this.isSubmittingComment = true;
      try {
        await api.post(`/comments/posts/${this.$route.params.id}`, {
          content: this.newComment
        });
        this.newComment = '';
        await this.fetchComments(); // 목록 새로고침
      } catch (error) {
        console.error("댓글 등록 실패:", error);
        const detail = error.response?.data?.detail;
        
        if (error.response?.status === 400 && typeof detail === 'string' && detail.includes("부적절한")) {
          this.censorshipDetail = detail;
          this.showCensorshipModal = true;
        } else {
          alert("댓글 등록에 실패했습니다.");
        }
      } finally {
        this.isSubmittingComment = false;
      }
    },

    async startChat() {
        const token = localStorage.getItem('access_token');
        if (!token) {
            alert("로그인 후 메시지를 보낼 수 있습니다.");
            this.$router.push('/login');
            return;
        }

        try {
            // 1. 이미 방이 있는지 확인하거나 새로 생성
            // 백엔드 /chat/rooms 에 POST 하여 1:1 방 생성 요청
            const res = await api.post('/chat/rooms', {
                name: `${this.post.author_name}님과의 대화`,
                type: 'direct',
                member_ids: [this.post.author_id]
            });
            
            // 2. 생성되거나 조회된 방 ID를 가지고 채팅 페이지로 이동
            this.$router.push({ path: '/chat', query: { room: res.data.id } });
        } catch (err) {
            console.error("채팅 시작 실패:", err);
            alert("상대방과 연결할 수 없습니다.");
        }
    },

    // ── 댓글 수정 시작
    startEditComment(comment) {
      this.editingCommentId = comment.id;
      this.editingContent = comment.content;
    },

    // ── 댓글 수정 취소
    cancelEdit() {
      this.editingCommentId = null;
      this.editingContent = '';
    },

    // ── 댓글 수정 저장
    async submitEditComment(commentId) {
      if (!this.editingContent.trim()) return;
      try {
        await api.patch(`/comments/${commentId}`, { content: this.editingContent });
        this.cancelEdit();
        await this.fetchComments();
      } catch (e) {
        alert(e.response?.data?.detail || '댓글 수정에 실패했습니다.');
      }
    },

    // ── 댓글 삭제
    async deleteComment(commentId) {
      if (!confirm('댓글을 삭제하시겠습니까?')) return;
      try {
        await api.delete(`/comments/${commentId}`);
        await this.fetchComments();
      } catch (e) {
        alert(e.response?.data?.detail || '댓글 삭제에 실패했습니다.');
      }
    },

    // ── 게시글 삭제
    async deletePost() {
      if (!confirm('게시글을 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.')) return;
      try {
        await api.delete(`/posts/${this.$route.params.id}`);
        this.$router.push('/posts');
      } catch (e) {
        alert(e.response?.data?.detail || '게시글 삭제에 실패했습니다.');
      }
    },

    // ── 신고 관련 메서드 ──
    openReportModal() {
      this.reportModal = true;
      this.reportReason = '';
      this.reportError = '';
      this.reportSuccess = false;
    },

    closeReportModal() {
      this.reportModal = false;
    },

    async submitReport() {
      if (!this.reportReason.trim()) return;
      this.reportLoading = true;
      this.reportError = '';
      try {
        await api.post(`/reports/posts/${this.$route.params.id}`, { reason: this.reportReason });
        this.reportSuccess = true;
        setTimeout(() => this.closeReportModal(), 1500);
      } catch (e) {
        const detail = e.response?.data?.detail;
        if (detail === '이미 신고한 게시글입니다.') {
          this.reportError = '이미 신고한 게시글입니다.';
        } else {
          this.reportError = detail || '신고 처리 중 오류가 발생했습니다.';
        }
      } finally {
        this.reportLoading = false;
      }
    },
  }
};
</script>

<style scoped>
.post-detail-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 60px 20px;
}

.post-header {
  text-align: left;
  margin-bottom: 40px;
  border-bottom: 2px solid #f0ede9;
  padding-bottom: 30px;
}

.title-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 20px;
}

.msg-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: #fdf5f0;
  border: 1.5px solid #ebdccf;
  border-radius: 12px;
  color: #835d43;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
  margin-top: 5px;
}

.msg-action-btn:hover {
  background: #835d43;
  color: white;
  border-color: #835d43;
  transform: translateY(-2px);
}

.subtitle {
  color: #a68b6a;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 2px;
  margin-bottom: 12px;
}

.title {
  font-size: 38px;
  font-weight: 800;
  color: #1a1a1a;
  line-height: 1.3;
  flex: 1;
}

.post-meta {
  display: flex;
  gap: 15px;
  font-size: 15px;
  color: #888;
  font-weight: 500;
}

.divider { color: #ddd; }

.content-card {
  background: white;
  padding: 50px 40px;
  border-radius: 24px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.03);
  min-height: 300px;
  margin-bottom: 40px;
}

.post-content {
  font-size: 17px;
  color: #333;
  line-height: 1.8;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 40px;
}

.back-btn {
  padding: 14px 40px;
  background: #f8f6f3;
  color: #5d4037;
  border: 1px solid #e0d8d0;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #5d4037;
  color: white;
}

/* 삭제 버튼 */
.delete-btn {
  padding: 14px 28px;
  background: #fff5f5;
  color: #c62828;
  border: 1px solid #ffcdd2;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.delete-btn:hover {
  background: #c62828;
  color: white;
  border-color: #c62828;
}

/* 신고 버튼 */
.report-btn {
  padding: 14px 28px;
  background: #fff5f5;
  color: #c62828;
  border: 1px solid #ffcdd2;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.report-btn:hover {
  background: #c62828;
  color: white;
  border-color: #c62828;
}

/* 신고 모달 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-box {
  background: white;
  border-radius: 24px;
  padding: 40px;
  width: 100%;
  max-width: 480px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
}

.modal-box h3 {
  font-size: 22px;
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 10px;
}

.modal-desc {
  font-size: 14px;
  color: #888;
  margin-bottom: 20px;
}

.report-textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 14px 16px;
  border: 1.5px solid #e0d8d0;
  border-radius: 12px;
  font-size: 15px;
  font-family: inherit;
  outline: none;
  resize: vertical;
  background: #fdfaf7;
  margin-bottom: 12px;
  transition: border-color 0.2s;
}

.report-textarea:focus {
  border-color: #c62828;
}

.report-error {
  font-size: 14px;
  color: #c62828;
  background: #ffebee;
  padding: 10px 14px;
  border-radius: 8px;
  margin-bottom: 12px;
}

.report-success {
  font-size: 14px;
  color: #2e7d32;
  background: #e8f5e9;
  padding: 10px 14px;
  border-radius: 8px;
  margin-bottom: 12px;
}

.modal-btn-row {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.modal-cancel {
  padding: 12px 24px;
  border: 1.5px solid #e0d8d0;
  border-radius: 12px;
  background: white;
  font-size: 14px;
  font-weight: 700;
  color: #888;
  cursor: pointer;
}

.modal-cancel:hover { background: #f8f6f3; }

.modal-submit {
  padding: 12px 24px;
  background: #c62828;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s;
}

.modal-submit:hover:not(:disabled) { background: #b71c1c; }

.modal-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 좋아요/댓글 스타일 */
.interaction-section { background: transparent; margin-bottom: 40px; }

.like-wrapper { display: flex; justify-content: center; margin-bottom: 30px; }

.like-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  background: white;
  border: 1px solid #e0d8d0;
  border-radius: 30px;
  font-size: 16px;
  font-weight: 600;
  color: #555;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}

.like-btn i { font-size: 18px; color: #ccc; }
.like-btn.liked i { color: #ff4757; }
.like-btn.liked { border-color: #ff4757; color: #ff4757; }
.like-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1); }

.section-divider { border: 0; height: 1px; background: #eaeaea; margin-bottom: 30px; }

.comments-title {
  font-size: 18px; font-weight: 700; color: #333;
  margin-bottom: 20px; display: flex; align-items: center; gap: 8px;
}
.comments-title span { color: #a68b6a; }

.comment-input-box {
  background: white; border: 1px solid #e0d8d0;
  border-radius: 16px; padding: 15px; margin-bottom: 30px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.02);
}
.comment-input-box textarea {
  width: 100%; border: none; resize: none; outline: none;
  font-size: 15px; color: #333; font-family: inherit;
}
.comment-actions { display: flex; justify-content: flex-end; margin-top: 10px; }

.submit-comment-btn {
  background: #5d4037; color: white; border: none;
  padding: 8px 20px; border-radius: 8px; font-weight: 600; cursor: pointer;
}
.submit-comment-btn:disabled { background: #ccc; cursor: not-allowed; }
.submit-comment-btn:hover:not(:disabled) { background: #4a332c; }

.comment-list { display: flex; flex-direction: column; gap: 20px; }

.comment-item {
  display: flex; gap: 15px; padding-bottom: 20px;
  border-bottom: 1px solid #f5f5f5;
}
.comment-avatar .avatar-placeholder {
  width: 40px; height: 40px; border-radius: 50%;
  background: #f0ede9; color: #a68b6a;
  display: flex; align-items: center; justify-content: center;
  font-weight: bold; font-size: 18px;
}
.comment-content { flex: 1; }
.comment-header {
  display: flex; align-items: center; gap: 10px; margin-bottom: 6px;
}
.comment-author { font-size: 15px; font-weight: 700; color: #333; }
.comment-date { font-size: 13px; color: #999; }
.comment-text { font-size: 15px; color: #555; line-height: 1.5; white-space: pre-wrap; }

/* 댓글 수정/삭제 버튼 */
.comment-btn-group {
  display: flex;
  gap: 6px;
  margin-left: auto;
}

.comment-edit-btn,
.comment-delete-btn {
  padding: 4px 10px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid;
  transition: all 0.2s;
}

.comment-edit-btn {
  background: #f8f6f3;
  color: #5d4037;
  border-color: #e0d8d0;
}
.comment-edit-btn:hover {
  background: #5d4037;
  color: white;
}

.comment-delete-btn {
  background: #fff5f5;
  color: #c62828;
  border-color: #ffcdd2;
}
.comment-delete-btn:hover {
  background: #c62828;
  color: white;
}

/* 댓글 수정 박스 */
.comment-edit-box {
  margin-top: 8px;
}
.comment-edit-box textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 10px 12px;
  border: 1.5px solid #e0d8d0;
  border-radius: 10px;
  font-size: 15px;
  font-family: inherit;
  outline: none;
  resize: vertical;
  background: #fdfaf7;
  transition: border-color 0.2s;
}
.comment-edit-box textarea:focus {
  border-color: #5d4037;
}
.comment-edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}
.comment-cancel-btn {
  padding: 6px 14px;
  font-size: 13px;
  font-weight: 600;
  border: 1px solid #e0d8d0;
  border-radius: 6px;
  background: white;
  color: #888;
  cursor: pointer;
}
.comment-cancel-btn:hover { background: #f8f6f3; }

.comment-save-btn {
  padding: 6px 14px;
  font-size: 13px;
  font-weight: 600;
  border: none;
  border-radius: 6px;
  background: #5d4037;
  color: white;
  cursor: pointer;
}
.comment-save-btn:hover { background: #4a332c; }

.no-comments {
  text-align: center; padding: 40px 0; color: #888;
  font-size: 15px; background: #fdfdfd;
  border-radius: 12px; border: 1px dashed #ddd;
}
</style>
