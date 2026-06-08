# DevCareer API (Backend)

취업/커리어 커뮤니티 플랫폼의 FastAPI 백엔드입니다. 게시판, 채용 공고, 공모전, 커뮤니티, 채팅, 알림, AI FAQ, 이메일 인증을 제공합니다.

## 기술 스택

- FastAPI, SQLAlchemy Async, asyncpg, PostgreSQL
- Pydantic / pydantic-settings
- JWT (python-jose), bcrypt
- WebSocket (채팅, 알림)
- AI: Groq / OpenAI / Gemini, Transformers 검열 모델
- 이메일: SMTP (`smtplib`)

## 디렉터리 구조

```text
backend/
├── main.py               # 앱 진입점, 라우터 등록, lifespan(init_db + AI 모델 로드)
├── pyproject.toml        # uv 의존성
├── requirements.txt
├── create_tables.py      # 개발용 테이블 재생성 (drop all 포함, 운영 금지)
├── seed_opportunities.py # 샘플 채용/공모전 시드
└── app/
    ├── core/             # config.py(Settings), security.py(JWT/해시)
    ├── database.py       # async engine/session, init_db()
    ├── dependencies.py   # 인증 의존성(get_current_user 등)
    ├── models/           # SQLAlchemy 모델
    ├── schemas/          # Pydantic 스키마
    ├── routers/          # 도메인별 API 라우터
    └── services/         # ai_service, email_service, external_opportunities
```

## 실행

### 1. PostgreSQL

```bash
cd ..            # fastapi-vue-board
docker compose up -d
```

### 2. 환경 변수 (`backend/.env`)

```env
DATABASE_URL=postgresql+asyncpg://postgres:1234@127.0.0.1:5432/project
SECRET_KEY=replace-with-secure-random-string
ADMIN_SECRET=replace-with-admin-secret
```

선택: AI(`GROQ_API_KEY`/`OPENAI_API_KEY`/`GEMINI_API_KEY`), 외부 데이터(`WORKNET_API_KEY`, `KIPRIS_API_KEY`),
이메일(`SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_FROM`, `FRONTEND_URL`).
이메일 SMTP 상세는 [../docs/email-verification.md](../docs/email-verification.md) 참고.

### 3. 서버 실행

```bash
uv run fastapi dev main.py
# 또는
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

- Swagger: `http://127.0.0.1:8000/docs`
- Health: `GET /` → `{"status": "ok"}`

## 라우터

`auth`, `post`, `comment`, `interaction`, `job`, `contest`, `scrap`, `admin`, `chat`,
`notification`, `report`, `community`, `faq` 가 `main.py`에 등록됩니다.
전체 엔드포인트는 [../../docs/04-API-명세.md](../../docs/04-API-명세.md)에 정리되어 있습니다.

## 참고

- `init_db()`는 시작 시 `create_all()` 후 `scraps`/`chat_messages`/`users` 누락 컬럼을 `ALTER TABLE`로 보정합니다(임시 마이그레이션 대체).
- 백엔드 구조 상세: [../../docs/07-백엔드-구조.md](../../docs/07-백엔드-구조.md)
