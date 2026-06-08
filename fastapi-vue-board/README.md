# 📋 Career Board

FastAPI + Vue 3 기반의 취업 준비생을 위한 커뮤니티 플랫폼입니다.  
채용공고, 공모전 정보 제공부터 게시판·커뮤니티·실시간 채팅까지 통합 제공합니다.

---

## 🗂️ 목차

1. [기술 스택](#기술-스택)
2. [프로젝트 구조](#프로젝트-구조)
3. [실행 방법](#실행-방법)
4. [기능 목록](#기능-목록)
   - [인증 / 회원](#인증--회원)
   - [게시판 (Posts)](#게시판-posts)
   - [커뮤니티 (Community)](#커뮤니티-community)
   - [채용공고 (Jobs)](#채용공고-jobs)
   - [공모전 (Contests)](#공모전-contests)
   - [AI FAQ 챗봇](#ai-faq-챗봇)
   - [실시간 채팅](#실시간-채팅)
   - [알림 (Notifications)](#알림-notifications)
   - [관리자 (Admin)](#관리자-admin)
5. [API 엔드포인트](#api-엔드포인트)
6. [데이터 모델](#데이터-모델)
7. [주요 버그 수정 내역](#주요-버그-수정-내역)

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| **Backend** | FastAPI, SQLAlchemy (async), PostgreSQL, JWT (OAuth2), WebSocket |
| **Frontend** | Vue 3 (Composition + Options API), Vue Router, Pinia, Axios |
| **AI** | Groq / OpenAI / Gemini (FAQ 챗봇), Transformers (욕설/공격성 검열) |
| **이메일** | SMTP (이메일 인증, 비밀번호 재설정 메일) |
| **인프라** | Docker Compose (PostgreSQL) |

---

## 프로젝트 구조

```
fastapi-vue-board/
├── backend/
│   ├── main.py                      # FastAPI 앱 진입점 (DevCareer API)
│   └── app/
│       ├── database.py
│       ├── dependencies.py          # JWT 인증 의존성
│       ├── core/                    # config(Settings), security(JWT/해시)
│       ├── models/                  # SQLAlchemy ORM 모델
│       │   ├── user.py
│       │   ├── post.py
│       │   ├── comment.py
│       │   ├── community.py
│       │   ├── community_like.py
│       │   ├── interaction.py       # PostLike, Scrap 등
│       │   ├── email_verification.py
│       │   ├── report.py            # PostReport, CommunityReport
│       │   └── ...
│       ├── schemas/                 # Pydantic v2 스키마
│       ├── services/                # ai_service, email_service, external_opportunities
│       └── routers/                 # FastAPI 라우터
│           ├── auth.py
│           ├── post.py
│           ├── comment.py
│           ├── community.py
│           ├── chat.py
│           ├── report.py
│           ├── notification.py
│           └── ...
├── docs/                            # 이메일 인증 등 기능별 운영 가이드
├── frontend/
│   └── src/
│       ├── views/
│       │   ├── HomeView.vue
│       │   ├── PostView.vue
│       │   ├── PostDetailView.vue
│       │   ├── PostCreateView.vue
│       │   ├── CommunityView.vue
│       │   ├── CommunityCreateView.vue
│       │   ├── CommunityDetailView.vue
│       │   ├── JobListView.vue
│       │   ├── ContestListView.vue
│       │   ├── AiChatView.vue
│       │   ├── ChatView.vue
│       │   ├── ProfileView.vue
│       │   ├── AdminView.vue
│       │   └── ...
│       ├── stores/
│       │   └── auth.js              # Pinia 인증 스토어
│       └── router/
│           └── index.js
└── docker-compose.yml
```

---

## 실행 방법

### 1. 데이터베이스 실행

```bash
docker-compose up -d
```

### 2. 백엔드 실행

```bash
cd backend
pip install -r requirements.txt    # 또는 uv sync
uvicorn main:app --reload          # 또는 uv run fastapi dev main.py
```

> `.env`에 최소 `DATABASE_URL`, `SECRET_KEY`, `ADMIN_SECRET`가 필요합니다.
> 이메일 인증을 사용하려면 `SMTP_*` 값을 추가합니다([docs/email-verification.md](docs/email-verification.md)).

### 3. 프론트엔드 실행

```bash
cd frontend
npm install
npm run dev
```

> 기본 접속: `http://localhost:5173`  
> API 서버: `http://localhost:8000`  
> API 문서: `http://localhost:8000/docs`

---

## 기능 목록

### 인증 / 회원

| 기능 | 설명 |
|------|------|
| 회원가입 | 이메일·사용자명·비밀번호로 가입, 인증 메일 발송 |
| 이메일 인증 | 메일 링크로 `verify-email` 처리, 미인증 시 로그인 차단 |
| 로그인 | JWT Access Token 발급 (Bearer) |
| 비밀번호 재설정 | 이메일 재설정 링크 발송 후 변경 |
| 관리자 가입 | `/admin/register` — 별도 관리자 계정 생성 |
| 프로필 조회/수정 | 자기 정보 확인 및 수정 |
| 인증 가드 | `requiresAuth` / `guestOnly` / `requiresAdmin` 라우트 메타 |

- 토큰은 `localStorage`에 `access_token` 키로 저장
- Pinia `authStore`가 전역 로그인 상태·사용자 정보 관리

---

### 게시판 (Posts)

| 기능 | 설명 |
|------|------|
| 게시글 목록 | 최신순 정렬, 좋아요 수 표시 |
| 게시글 상세 | 본문, 댓글, 좋아요, 스크랩 |
| 게시글 작성 | 로그인 필요, AI 검열 필터 적용 |
| 게시글 수정 | 작성자 본인만 |
| 게시글 삭제 | 작성자 또는 관리자 |
| 댓글 작성 | 로그인 필요, AI 검열 필터 적용 |
| 댓글 수정 | 작성자 본인만 (인라인 편집) |
| 댓글 삭제 | 작성자 또는 관리자 |
| 좋아요 토글 | 로그인 필요, 중복 방지 |
| 스크랩 | 게시글 스크랩 토글 |
| 신고 | 게시글 신고 (`POST /reports/{post_id}`) |

**좋아요 수 집계**: 목록 쿼리에서 `PostLike` 테이블을 서브쿼리로 JOIN하여 실시간 집계

```python
# backend/app/routers/post.py
likes_subq = (
    select(PostLike.post_id, func.count(PostLike.user_id).label("like_count"))
    .group_by(PostLike.post_id)
    .subquery()
)
```

---

### 커뮤니티 (Community)

#### 카테고리 구조

| 키값 (DB) | 표시명 |
|-----------|--------|
| `job` | 직무별 게시판 💻 |
| `career` | 커리어 게시판 🚀 |
| `project` | 프로젝트 공유 게시판 🤝 |

#### 기능 목록

| 기능 | 설명 |
|------|------|
| 게시글 목록 | 전체 / 카테고리별 필터, 최신순·인기순 정렬, 키워드 검색 |
| 게시글 상세 | 본문, 댓글, 좋아요 |
| 게시글 작성 | 로그인 필요, 카테고리 선택, 익명 여부 설정 |
| 게시글 수정 | 작성자 본인만 (모달 팝업) |
| 게시글 삭제 | 작성자 또는 관리자 |
| 댓글 작성 | 로그인 필요, 익명 여부 설정 |
| 댓글 수정 | 작성자 본인만 (인라인 편집) |
| 댓글 삭제 | 작성자 또는 관리자 |
| 좋아요 토글 | 로그인 필요, 낙관적 업데이트 |
| 신고 | 커뮤니티 게시글 신고 (`POST /reports/community/{id}`) |
| 인기 주제 | 사이드바 — 좋아요+댓글 수 기반 상위 5개 표시 |

#### 익명 처리 설계 원칙

> **DB에는 항상 실제 user_id / owner_id를 저장하고, 화면 표시명(author_name)만 None으로 처리합니다.**

```python
# backend/app/routers/community.py
def _build_community_dict(community, username, like_count, comment_count):
    return {
        "owner_id": community.owner_id,          # 항상 실제 ID (수정/삭제 권한 판단용)
        "author_name": None if community.is_anonymous else username,  # 화면 표시만 익명
        ...
    }
```

```javascript
// frontend: 수정/삭제 버튼 표시 조건 (is_anonymous 여부와 무관)
v-if="post.owner_id === currentUserId"
v-if="comment.user_id === currentUserId"
```

---

### 채용공고 (Jobs)

| 기능 | 설명 |
|------|------|
| 목록 조회 | 전체 채용공고 목록 |
| 상세 조회 | 개별 채용공고 내용 |
| 등록 / 수정 / 삭제 | 관리자 전용 (`requiresAdmin`) |

---

### 공모전 (Contests)

| 기능 | 설명 |
|------|------|
| 목록 조회 | 전체 공모전 목록 |
| 상세 조회 | 개별 공모전 내용 |
| 등록 / 수정 / 삭제 | 관리자 전용 (`requiresAdmin`) |

---

### AI FAQ 챗봇

- 경로: `/faq`
- Groq / OpenAI / Gemini 중 설정된 provider로 취업·커리어 관련 질문 응답
- 로그인 불필요 (공개 접근)

---

### 실시간 채팅

- 경로: `/chat`
- 로그인 필요 (`requiresAuth`)
- WebSocket 기반 실시간 메시지 전송, 파일 첨부 지원

---

### 알림 (Notifications)

| 트리거 | 알림 내용 |
|--------|-----------|
| 커뮤니티 게시글 좋아요 | `"{표시명}님이 좋아요를 눌렀습니다."` |
| 커뮤니티 댓글 작성 | `"{표시명}님이 댓글을 작성하였습니다."` |

- 익명 행위자는 `"익명"`으로 표시
- `POST /community/{id}/like`, `POST /community/{id}/comments` 에서 자동 생성

---

### 관리자 (Admin)

- 경로: `/admin`
- `role == "admin"` 사용자만 접근 가능
- 기능: 사용자 관리, 신고 처리, 채용공고·공모전 CRUD

---

## API 엔드포인트

### 인증

```
POST   /auth/signup            회원가입
POST   /auth/resend-verification 이메일 인증 메일 재발송
GET    /auth/verify-email      이메일 인증
POST   /auth/login             로그인 (JWT 발급)
POST   /auth/signup/admin      관리자 가입
GET    /auth/me                내 정보 조회
```

### 게시판

```
GET    /posts/                 게시글 목록 (like_count 포함)
POST   /posts/                 게시글 작성 (인증 필요)
GET    /posts/{id}             게시글 상세
PATCH  /posts/{id}             게시글 수정 (작성자)
DELETE /posts/{id}             게시글 삭제 (작성자/관리자)

GET    /posts/{id}/comments    댓글 목록
POST   /posts/{id}/comments    댓글 작성 (인증 필요)
PATCH  /posts/{id}/comments/{cid}   댓글 수정 (작성자)
DELETE /posts/{id}/comments/{cid}   댓글 삭제 (작성자/관리자)

POST   /posts/{id}/like        좋아요 토글 (인증 필요)
POST   /posts/{id}/scrap       스크랩 토글 (인증 필요)
```

### 커뮤니티

```
GET    /community/             게시글 목록 (?category=job|career|project)
POST   /community/             게시글 작성 (인증 필요)
GET    /community/{id}         게시글 상세
PATCH  /community/{id}         게시글 수정 (작성자)
DELETE /community/{id}         게시글 삭제 (작성자/관리자)

GET    /community/{id}/comments       댓글 목록
POST   /community/{id}/comments       댓글 작성 (인증 필요)
PATCH  /community/{id}/comments/{cid} 댓글 수정 (작성자)
DELETE /community/{id}/comments/{cid} 댓글 삭제 (작성자/관리자)

POST   /community/{id}/like           좋아요 토글 (인증 필요)
GET    /community/{id}/like/status    좋아요 상태 조회
```

### 신고

```
POST   /reports/{post_id}              게시글 신고
POST   /reports/community/{id}         커뮤니티 게시글 신고
```

---

## 데이터 모델

### Community

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `id` | Integer PK | - |
| `title` | String | 제목 |
| `content` | Text | 본문 |
| `category` | String | `job` / `career` / `project` |
| `is_anonymous` | Boolean | 익명 여부 |
| `owner_id` | FK → users | **항상 실제 유저 ID 저장** |
| `created_at` | DateTime | 생성일시 |
| `updated_at` | DateTime | 수정일시 |

### CommunityComment

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `id` | Integer PK | - |
| `community_id` | FK → communities | 소속 게시글 |
| `user_id` | FK → users | **항상 실제 유저 ID 저장** |
| `content` | Text | 댓글 내용 |
| `is_anonymous` | Boolean | 익명 여부 |
| `parent_id` | FK → self | 대댓글용 (현재 미사용) |

### CommunityReport

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `id` | Integer PK | - |
| `community_id` | FK → communities CASCADE | 신고 대상 |
| `reporter_id` | FK → users | 신고자 |
| `reason` | Text | 신고 사유 |
| `is_resolved` | Boolean | 처리 여부 |
| `resolved_by` | FK → users | 처리 관리자 |

---

## 주요 버그 수정 내역

### 1. 댓글 등록 422 오류

- **원인**: `CommentCreate` 스키마에 `user_id: int` 필드가 있었으나 프론트엔드는 `content`만 전송
- **수정**: 스키마에서 `user_id` 제거, 라우터에서 `current_user.id` 직접 사용

```python
# before
class CommentCreate(CommentBase):
    user_id: int
    parent_id: Optional[int] = None

# after
class CommentCreate(CommentBase):
    parent_id: Optional[int] = None  # user_id는 JWT에서 자동 추출
```

### 2. 댓글 수정/삭제 버튼 미표시

- **원인**: 템플릿에 버튼 자체가 없었고, `comment.author_id` (존재하지 않는 필드) 참조
- **수정**: 버튼 추가 + `comment.user_id === currentUserId` 조건으로 변경

### 3. 게시글 목록 좋아요 수 항상 0

- **원인**: `GET /posts/` 쿼리에서 `PostLike` 집계 서브쿼리가 없었음
- **수정**: `PostLike` 테이블을 서브쿼리로 LEFT JOIN하여 `like_count` 집계

### 4. 익명 글/댓글 수정·삭제 불가

- **원인**: 익명 처리 시 DB의 `owner_id` / `user_id`를 `None`으로 저장 → 소유권 판단 불가
- **수정**: DB에는 항상 실제 ID 저장, `author_name`만 `None` 처리

### 5. 커뮤니티 글쓰기 → 게시판으로 이동되는 문제

- **원인**: `CommunityView.vue`의 버튼이 `/posts/create`로 하드코딩
- **수정**: `CommunityCreateView.vue` 별도 생성, `/community/create` 라우트 추가

### 6. 에러 메시지 `[object Object]` 출력

- **원인**: FastAPI 422 응답의 `detail`이 객체 배열인데 문자열로 직접 출력
- **수정**: `Array.isArray(detail)` 체크 후 `detail.map(e => e.msg).join(', ')` 처리

---

> 개발 기간: 2025 · 스택: FastAPI + Vue 3 + PostgreSQL
