# 취준생들을 위한 커뮤니티 웹 사이트

취업 준비생과 IT 개발자를 위한 커리어 커뮤니티 플랫폼입니다. 게시판, 채용 공고, 공모전, 커뮤니티, 실시간 채팅, 알림, AI FAQ를 한 곳에서 제공합니다.

## 프로젝트 개요

현재 핵심 애플리케이션은 `fastapi-vue-board` 폴더에 있습니다.

```text
webdev/
├── README.md
├── doc/                         # 프로젝트 분석/설계 문서
├── backend/                     # 초기/구버전 FastAPI 진입점
└── fastapi-vue-board/
    ├── docker-compose.yml       # PostgreSQL 로컬 실행
    ├── backend/                 # FastAPI API 서버
    └── frontend/                # Vue/Vite 프론트엔드
```

## Tech Stack

| Category | Stack | Description |
|---|---|---|
| Frontend | Vue 3, Vite | 사용자 인터페이스 및 SPA 개발 |
| Routing/State | Vue Router, Pinia | 화면 라우팅과 전역 상태 관리 |
| Backend | FastAPI | REST API, WebSocket, 비즈니스 로직 처리 |
| Database | PostgreSQL | 사용자, 게시글, 공고, 알림 등 데이터 저장 |
| ORM | SQLAlchemy Async | 비동기 데이터베이스 접근 |
| Authentication | JWT, OAuth2 Bearer | 토큰 기반 인증/인가 |
| Realtime | WebSocket | 채팅 및 알림 |
| AI | Groq/OpenAI/Gemini, Transformers | AI FAQ 답변 및 욕설/공격성 검열 |
| API Docs | Swagger/OpenAPI | FastAPI 자동 API 문서 |
| Container | Docker Compose | 로컬 PostgreSQL 실행 |
| Environment | Python 3.10+, Node 20.19+ 또는 22.12+ | 백엔드/프론트엔드 실행 환경 |

## 주요 기능

| 영역 | 기능 |
|---|---|
| 인증/회원 | 회원가입, 로그인, JWT 발급, 프로필 수정, 비밀번호 재설정, 관리자 승격 |
| 게시판 | 게시글 CRUD, 검색/필터, 조회수, 댓글/대댓글, 좋아요, 신고 |
| 채용 공고 | 관리자 등록 공고, 외부 공고 수집, 검색/필터, 스크랩 |
| 공모전 | 관리자 등록 공모전, 외부 공모전 수집, 검색/필터, 스크랩 |
| 커뮤니티 | 카테고리 게시판, 익명 글, 댓글/대댓글, 좋아요 |
| 채팅 | 1:1/그룹 채팅방, 메시지 조회/전송, 읽음 처리 |
| 알림 | 댓글, 좋아요, 채팅 이벤트 기반 DB 알림 및 WebSocket push |
| AI FAQ | 생성형 AI 답변, 금칙어와 ML 모델 기반 검열 |
| 관리자 | 회원 정지/해제, 신고 처리, 채용 공고/공모전 관리 |

## 빠른 실행

### 1. PostgreSQL 실행

```bash
cd fastapi-vue-board
docker compose up -d
```

### 2. 백엔드 환경 변수 설정

`fastapi-vue-board/backend/.env`에 최소한 다음 값을 설정합니다.

```env
DATABASE_URL=postgresql+asyncpg://postgres:1234@127.0.0.1:5432/project
SECRET_KEY=replace-with-secure-random-string
ADMIN_SECRET=replace-with-admin-secret
```

선택적으로 AI/외부 데이터 연동을 위해 다음 값을 추가할 수 있습니다.

```env
GROQ_API_KEY=
OPENAI_API_KEY=
GEMINI_API_KEY=
WORKNET_API_KEY=
KIPRIS_API_KEY=
```

### 3. 백엔드 실행

```bash
cd fastapi-vue-board/backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

API 문서:

- Swagger: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

### 4. 프론트엔드 실행

```bash
cd fastapi-vue-board/frontend
npm install
npm run dev
```

기본 개발 주소:

- Frontend: `http://localhost:5173`
- Backend: `http://127.0.0.1:8000`

## 주요 API 그룹

| Prefix | 설명 |
|---|---|
| `/auth` | 회원가입, 로그인, 프로필, 비밀번호 재설정 |
| `/posts` | 게시글 조회/작성/수정/삭제 |
| `/comments` | 게시글 댓글/대댓글 |
| `/interactions` | 좋아요, 북마크 |
| `/jobs` | 채용 공고 |
| `/contests` | 공모전 |
| `/scraps` | 채용/공모전 스크랩 |
| `/community` | 커뮤니티 게시판 |
| `/chat` | 채팅방, 메시지, 채팅 WebSocket |
| `/notifications` | 알림 조회/읽음 처리, 알림 WebSocket |
| `/reports` | 게시글 신고 |
| `/admin` | 회원/신고 관리자 기능 |
| `/faq` | FAQ, AI 답변, 검열 확인 |

상세 명세는 [API 명세](doc/04-API-명세.md)를 참고합니다.

## 문서

프로젝트 구조와 설계 분석은 `doc/` 폴더에 정리되어 있습니다.

| 문서 | 내용 |
|---|---|
| [문서 가이드](doc/00-문서-가이드.md) | 문서 사용 방법과 갱신 규칙 |
| [시스템 개요](doc/01-시스템-개요.md) | 전체 구조, 런타임 구성, 주요 도메인 |
| [기능 설계](doc/02-기능-설계.md) | 사용자/관리자/AI/실시간 기능 |
| [데이터베이스 설계](doc/03-데이터베이스-설계.md) | 주요 테이블과 관계 |
| [API 명세](doc/04-API-명세.md) | REST/WebSocket 엔드포인트 |
| [업무 플로우](doc/05-업무-플로우.md) | 회원, 게시글, 신고, 알림 등 흐름 |
| [프론트엔드 구조](doc/06-프론트엔드-구조.md) | Vue 라우팅, 상태, API 호출 구조 |
| [백엔드 구조](doc/07-백엔드-구조.md) | FastAPI 라우터, 서비스, 인증 구조 |
| [운영 배포](doc/08-운영-배포.md) | 로컬 실행, 환경 변수, 배포 점검 |
| [위험요소 및 개선 포인트](doc/09-위험요소-및-개선-포인트.md) | 보안/운영/구조 개선 과제 |

## UI/UX 디자인 변경

메인 페이지 UI/UX를 개선하면서 Supanova 디자인 스킬셋의 리디자인 기준을 반영했습니다. 기존 구조를 유지하되 첫 화면의 가독성, 탐색 흐름, 시각적 완성도를 높이는 방향으로 정리했습니다.

주요 변경 사항:

- 메인 페이지를 비대칭 에디토리얼 레이아웃 기반의 대시보드형 화면으로 재구성
- 히어로 영역에 검색, 추천 키워드, 주요 지표, 오늘의 핵심 탐색 정보를 한 번에 볼 수 있도록 개선
- 게시글, 채용 공고, 공모전 영역을 카드 중심 정보 패널로 정리하여 탐색 피로도 감소
- 상단 네비게이션을 플로팅 글래스 스타일로 변경하여 브랜드 인상과 사용성 강화
- Pretendard 기반 한글 타이포그래피, 부드러운 모션, 더블 베젤 카드 스타일 등 프리미엄 UI 요소 적용

## 운영 전 주의사항

현재 문서 분석 기준으로 운영 배포 전에 우선 검토해야 할 항목입니다.

- DB 마이그레이션 도구가 없고 앱 시작 시 `create_all()`을 사용합니다. Alembic 도입이 필요합니다.
- `/auth/find-password`가 개발용 `dev_token`을 반환하므로 운영 전 제거해야 합니다.
- 일부 상호작용 삭제 API가 path의 `user_id` 기준으로 동작해 소유권 검증 강화가 필요합니다.
- 프론트 일부 코드가 공통 Axios 인스턴스 대신 raw `axios` 또는 하드코딩 URL을 사용합니다.
- WebSocket URL 생성 방식이 채팅/알림에서 일관되지 않아 환경 변수 기반 정리가 필요합니다.
- 프로필 이미지 업로드에 파일 타입/크기 검증이 필요합니다.

자세한 내용은 [위험요소 및 개선 포인트](doc/09-위험요소-및-개선-포인트.md)를 참고합니다.
