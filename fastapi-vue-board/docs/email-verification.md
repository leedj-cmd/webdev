# 이메일 인증 설정

회원가입 후 이메일 인증 링크를 열어야 로그인할 수 있습니다.

## 추천 무료 SMTP

2026-05-28 기준으로 Brevo 무료 플랜은 하루 300건 발송 제한이 있어 개발/소규모 운영의 인증 메일에 적합합니다. SMTP 방식으로 붙였기 때문에 Brevo 외에도 SMTP 정보를 제공하는 서비스라면 같은 환경변수로 교체할 수 있습니다.

## Brevo 설정 순서

1. Brevo 계정을 만들고 발신자 이메일을 인증합니다.
2. Brevo의 SMTP/Transactional Email 메뉴에서 SMTP 서버, 포트, 로그인, SMTP 키를 확인합니다.
3. `backend/.env`에 아래 값을 추가합니다.

```env
FRONTEND_URL=http://localhost:5173
EMAIL_FROM=인증한_발신자_이메일
EMAIL_FROM_NAME=TechBridge
SMTP_HOST=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_USERNAME=Brevo_SMTP_로그인_이메일
SMTP_PASSWORD=Brevo_SMTP_KEY
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

주의: `SMTP_PASSWORD`에는 Brevo API key나 Brevo 계정 비밀번호가 아니라 SMTP key를 넣어야 합니다. Brevo 공식 문서에서도 SMTP user는 SMTP login email address, SMTP password는 SMTP key를 사용하라고 안내합니다.

## 로컬 동작

`SMTP_HOST`가 비어 있으면 실제 메일을 보내지 않고 백엔드 콘솔에 인증 링크를 출력합니다. 로컬에서 메일 서비스 설정 전에도 회원가입 흐름을 확인할 수 있습니다.

## 사용자 흐름

1. 사용자가 `/register`에서 가입합니다.
2. 백엔드는 미인증 계정과 24시간짜리 인증 토큰을 생성합니다.
3. 인증 링크는 `/verify-email?token=...` 형식으로 발송됩니다.
4. 프론트의 인증 화면이 `/auth/verify-email`을 호출합니다.
5. 인증이 완료된 계정만 `/auth/login`에서 JWT를 받을 수 있습니다.

## 비밀번호 재설정 흐름

1. 사용자가 로그인 화면에서 비밀번호 재설정을 누르고 이메일을 입력합니다.
2. 백엔드는 15분짜리 재설정 토큰을 만들고 해시만 DB에 저장합니다.
3. 재설정 링크는 `/reset-password?token=...` 형식으로 발송됩니다.
4. 프론트의 재설정 화면이 새 비밀번호와 토큰을 `/auth/reset-password`로 보냅니다.
5. 사용된 토큰은 즉시 `used=true`로 바뀌어 재사용할 수 없습니다.
