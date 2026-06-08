# API 명세

## 공통 규칙

- 로컬 기본 API 주소: `http://127.0.0.1:8000`
- 프론트 기본 개발 주소: `http://localhost:5173`
- 인증 방식: `Authorization: Bearer <access_token>`
- API 문서 자동 생성: FastAPI 기본 Swagger `/docs`, OpenAPI `/openapi.json`
- 대부분의 요청/응답은 JSON입니다. 프로필 이미지는 multipart form-data입니다.

## 상태 확인

| Method | Path | 인증 | 설명 |
|---|---|---|---|
| GET | `/` | 불필요 | 서버 상태 확인, `{"status": "ok"}` 반환 |

## Auth

| Method | Path | 인증 | 설명 |
|---|---|---|---|
| POST | `/auth/signup` | 불필요 | 일반 회원가입, 인증 메일 발송 |
| POST | `/auth/resend-verification` | 불필요 | 인증 메일 재발송 |
| GET | `/auth/verify-email?token=` | 불필요 | 이메일 인증 링크 처리 |
| POST | `/auth/login` | 불필요 | 로그인, access/refresh token 발급 (이메일 인증 필요) |
| POST | `/auth/logout` | 불필요 | 서버 상태 변경 없는 로그아웃 메시지 반환 |
| POST | `/auth/refresh` | 불필요 | refresh token으로 토큰 재발급 |
| POST | `/auth/find-id` | 불필요 | 닉네임으로 마스킹 이메일 조회 |
| POST | `/auth/find-password` | 불필요 | 비밀번호 재설정 링크 메일 발송 |
| PATCH | `/auth/reset-password` | 불필요 | 재설정 토큰으로 비밀번호 변경 |
| PATCH | `/auth/reset-password/current` | 필요 | 현재 비밀번호 확인 후 변경 |
| GET | `/auth/me` | 필요 | 내 정보 조회 |
| PATCH | `/auth/profile` | 필요 | 닉네임, 소개 수정 |
| POST | `/auth/profile/image` | 필요 | 프로필 이미지 업로드 |
| PATCH | `/auth/change-password` | 필요 | 로그인 상태 비밀번호 변경 |
| DELETE | `/auth/me` | 필요 | 회원 탈퇴 |
| POST | `/auth/signup/admin?admin_secret=` | 불필요 | 관리자 회원가입 |
| PATCH | `/auth/promote/admin?email=&admin_secret=` | 불필요 | 관리자 승격 |
| GET | `/auth/profile/{user_id}` | 불필요 | 사용자 프로필 조회 |
| GET | `/auth/activity` | 필요 | 내 게시글/댓글 활동 조회 |
| GET | `/auth/likes` | 필요 | 추천한 게시글 조회 |

## Posts

| Method | Path | 인증 | 설명 |
|---|---|---|---|
| GET | `/posts/` | 불필요 | 게시글 목록, `skip`, `limit`, `search`, `job_category`, `region` |
| GET | `/posts/popular` | 불필요 | 조회수 기준 인기 게시글 |
| GET | `/posts/like_count` | 불필요 | 좋아요 수 기준 게시글 목록 |
| GET | `/posts/{post_id}` | 불필요 | 게시글 상세, 조회수 증가 |
| POST | `/posts/` | 필요 | 게시글 작성, 정지 회원 제한, AI 검열 |
| PATCH | `/posts/{post_id}` | 필요 | 작성자 본인 수정 |
| DELETE | `/posts/{post_id}` | 필요 | 작성자 또는 관리자 삭제 |

## Comments

| Method | Path | 인증 | 설명 |
|---|---|---|---|
| POST | `/comments/posts/{post_id}` | 필요 | 댓글/대댓글 작성, AI 검열, 알림 생성 |
| GET | `/comments/posts/{post_id}` | 불필요 | 게시글 댓글 목록 |
| PATCH | `/comments/{comment_id}` | 필요 | 작성자 본인 댓글 수정 |
| DELETE | `/comments/{comment_id}` | 필요 | 작성자 또는 관리자 댓글 삭제 |

## Interactions

| Method | Path | 인증 | 설명 |
|---|---|---|---|
| GET | `/interactions/{post_id}/likes/status` | 선택 | 좋아요 수와 현재 유저 좋아요 여부 |
| POST | `/interactions/{post_id}/likes` | 필요 | 좋아요 추가, 작성자에게 알림 |
| DELETE | `/interactions/{post_id}/likes/{user_id}` | 불명확 | 좋아요 취소 |
| POST | `/interactions/{post_id}/bookmarks` | 필요 | 북마크 추가 |
| DELETE | `/interactions/{post_id}/bookmarks/{user_id}` | 불명확 | 북마크 취소 |

주의: 삭제 API는 현재 토큰 사용자와 path의 `user_id` 일치 여부를 검증하지 않습니다.

## Jobs

| Method | Path | 인증 | 설명 |
|---|---|---|---|
| GET | `/jobs/` | 불필요 | 채용 공고 목록, 외부 공고 포함 가능 |
| GET | `/jobs/{job_id}` | 불필요 | 내부 DB 채용 공고 상세 |
| POST | `/jobs/` | 관리자 | 채용 공고 등록 |
| PATCH | `/jobs/{job_id}` | 관리자 | 채용 공고 수정 |
| DELETE | `/jobs/{job_id}` | 관리자 | 채용 공고 비활성화 |
| POST | `/jobs/{job_id}/scrap` | 필요 | 내부 공고 스크랩 |
| DELETE | `/jobs/{job_id}/scrap` | 필요 | 내부 공고 스크랩 취소 |

목록 query:

- `skip`, `limit`
- `include_external`
- `external_limit`
- `search`
- `job_category`
- `region`
- `experience`

## Contests

| Method | Path | 인증 | 설명 |
|---|---|---|---|
| GET | `/contests/` | 불필요 | 공모전 목록, 외부 공모전 포함 가능 |
| GET | `/contests/{contest_id}` | 불필요 | 내부 DB 공모전 상세 |
| POST | `/contests/` | 관리자 | 공모전 등록 |
| PATCH | `/contests/{contest_id}` | 관리자 | 공모전 수정 |
| DELETE | `/contests/{contest_id}` | 관리자 | 공모전 비활성화 |
| POST | `/contests/{contest_id}/scrap` | 필요 | 내부 공모전 스크랩 |
| DELETE | `/contests/{contest_id}/scrap` | 필요 | 내부 공모전 스크랩 취소 |

목록 query:

- `skip`, `limit`
- `include_external`
- `external_limit`
- `search`
- `category`
- `target`

## Scraps

| Method | Path | 인증 | 설명 |
|---|---|---|---|
| POST | `/scraps/` | 필요 | 채용/공모전 스크랩 추가, 외부 데이터 지원 |
| GET | `/scraps/` | 필요 | 내 스크랩 목록 |
| DELETE | `/scraps/{scrap_id}` | 필요 | 내 스크랩 삭제 |
| GET | `/scraps/check?scrap_type=&target_id=` | 필요 | 내부 데이터 스크랩 여부 확인 |

## Community

| Method | Path | 인증 | 설명 |
|---|---|---|---|
| GET | `/community/` | 불필요 | 커뮤니티 목록, `category`, 검색/정렬 필터 |
| GET | `/community/{community_id}` | 불필요 | 커뮤니티 글 상세 |
| POST | `/community/` | 필요 | 커뮤니티 글 작성, 카테고리/익명 선택 |
| PATCH | `/community/{community_id}` | 필요 | 작성자 본인 글 수정 |
| DELETE | `/community/{community_id}` | 필요 | 작성자 또는 관리자 글 삭제 |
| POST | `/community/{community_id}/like` | 필요 | 커뮤니티 글 좋아요 토글, 알림 생성 |
| GET | `/community/{community_id}/like/status` | 필요 | 좋아요 수와 현재 유저 좋아요 여부 |
| GET | `/community/{community_id}/comments` | 불필요 | 댓글 목록 |
| POST | `/community/{community_id}/comments` | 필요 | 댓글/대댓글 작성, 알림 생성 |
| PATCH | `/community/{community_id}/comments/{comment_id}` | 필요 | 작성자 본인 댓글 수정 |
| DELETE | `/community/{community_id}/comments/{comment_id}` | 필요 | 작성자 또는 관리자 댓글 삭제 |

익명 글/댓글도 DB에는 실제 `owner_id`/`user_id`를 저장하고, 응답의 `author_name`만 `null`로 내려 수정·삭제 권한 판단이 가능합니다.

## Chat

| Method | Path | 인증 | 설명 |
|---|---|---|---|
| POST | `/chat/rooms` | 필요 | 채팅방 생성 또는 기존 1:1 방 조회 |
| GET | `/chat/rooms` | 필요 | 내 채팅방 목록 |
| GET | `/chat/rooms/{room_id}` | 필요 | 채팅방 상세 |
| DELETE | `/chat/rooms/{room_id}` | 필요 | 채팅방 나가기 |
| GET | `/chat/rooms/{room_id}/members` | 필요 | 참여자 목록 |
| GET | `/chat/rooms/{room_id}/messages` | 필요 | 메시지 목록 |
| PATCH | `/chat/rooms/{room_id}/read` | 필요 | 메시지 읽음 처리 |
| POST | `/chat/rooms/{room_id}/attachments` | 필요 | 파일 첨부 메시지 전송 (multipart) |
| WS | `/chat/ws/{room_id}?token=` | 필요 | 실시간 메시지 |

## Notifications

| Method | Path | 인증 | 설명 |
|---|---|---|---|
| GET | `/notifications/` | 필요 | 내 알림 최근 50개 |
| PATCH | `/notifications/read-all` | 필요 | 전체 읽음 |
| PATCH | `/notifications/{notification_id}/read` | 필요 | 단일 읽음 |
| WS | `/notifications/ws?token=` | 필요 | 실시간 알림 수신 |

## Reports

| Method | Path | 인증 | 설명 |
|---|---|---|---|
| POST | `/reports/posts/{post_id}` | 필요 | 게시글 신고, 중복 신고 방지 |
| POST | `/reports/community/{community_id}` | 필요 | 커뮤니티 글 신고, 중복 신고 방지 |

## Admin

| Method | Path | 인증 | 설명 |
|---|---|---|---|
| GET | `/admin/users` | 관리자 | 회원 목록 |
| PATCH | `/admin/users/{user_id}/suspend` | 관리자 | 회원 정지 |
| PATCH | `/admin/users/{user_id}/unsuspend` | 관리자 | 회원 정지 해제 |
| GET | `/admin/reports` | 관리자 | 신고 목록, `is_resolved` 필터 |
| PATCH | `/admin/reports/{report_id}/resolve` | 관리자 | 신고 처리 |
| DELETE | `/admin/reports/{report_id}/resolve-and-delete` | 관리자 | 게시글 삭제 후 신고 처리 |

## FAQ / AI

| Method | Path | 인증 | 설명 |
|---|---|---|---|
| POST | `/faq/` | 관리자 | FAQ 등록 |
| GET | `/faq/` | 불필요 | FAQ 목록 |
| POST | `/faq/ask` | 불필요 | 생성형 AI 답변 |
| POST | `/faq/check-censorship` | 필요 | 욕설/공격성 검열 |

