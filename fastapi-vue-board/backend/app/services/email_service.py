import asyncio
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from urllib.parse import urlencode

from app.core.config import settings


def build_verification_link(token: str) -> str:
    query = urlencode({"token": token})
    return f"{settings.FRONTEND_URL.rstrip('/')}/verify-email?{query}"


def build_password_reset_link(token: str) -> str:
    query = urlencode({"token": token})
    return f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?{query}"


def build_verification_email(username: str, verification_link: str) -> tuple[str, str]:
    text = (
        f"{username}님, TechBridge 회원가입을 완료하려면 아래 링크를 열어주세요.\n\n"
        f"{verification_link}\n\n"
        "이 링크는 24시간 동안 사용할 수 있습니다."
    )
    html = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #2a1e15;">
      <h2>TechBridge 이메일 인증</h2>
      <p>{username}님, 회원가입을 완료하려면 아래 버튼을 눌러 이메일을 인증해주세요.</p>
      <p>
        <a href="{verification_link}"
           style="display:inline-block;padding:12px 18px;background:#6b4c38;color:#fff;text-decoration:none;border-radius:8px;">
          이메일 인증하기
        </a>
      </p>
      <p>버튼이 열리지 않으면 아래 주소를 브라우저에 붙여넣어 주세요.</p>
      <p><a href="{verification_link}">{verification_link}</a></p>
      <p style="color:#7a5c42;font-size:13px;">이 링크는 24시간 동안 사용할 수 있습니다.</p>
    </div>
    """
    return text, html


def build_password_reset_email(username: str, reset_link: str) -> tuple[str, str]:
    text = (
        f"{username}님, TechBridge 비밀번호를 재설정하려면 아래 링크를 열어주세요.\n\n"
        f"{reset_link}\n\n"
        "이 링크는 15분 동안 사용할 수 있습니다. 요청하지 않았다면 이 메일을 무시해주세요."
    )
    html = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #2a1e15;">
      <h2>TechBridge 비밀번호 재설정</h2>
      <p>{username}님, 아래 버튼을 눌러 새 비밀번호를 설정해주세요.</p>
      <p>
        <a href="{reset_link}"
           style="display:inline-block;padding:12px 18px;background:#6b4c38;color:#fff;text-decoration:none;border-radius:8px;">
          비밀번호 재설정하기
        </a>
      </p>
      <p>버튼이 열리지 않으면 아래 주소를 브라우저에 붙여넣어 주세요.</p>
      <p><a href="{reset_link}">{reset_link}</a></p>
      <p style="color:#7a5c42;font-size:13px;">이 링크는 15분 동안 사용할 수 있습니다.</p>
    </div>
    """
    return text, html


def _send_email_sync(to_email: str, subject: str, text: str, html: str) -> bool:
    if not settings.SMTP_HOST:
        print(f"[email disabled] {subject} -> {to_email}\n{text}")
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = formataddr((settings.EMAIL_FROM_NAME, settings.EMAIL_FROM))
    message["To"] = to_email
    message.set_content(text)
    message.add_alternative(html, subtype="html")

    if settings.SMTP_USE_SSL:
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
            if settings.SMTP_USERNAME:
                smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            smtp.send_message(message)
    else:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
            if settings.SMTP_USE_TLS:
                smtp.starttls()
            if settings.SMTP_USERNAME:
                smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            smtp.send_message(message)

    return True


async def send_verification_email(to_email: str, username: str, token: str) -> bool:
    verification_link = build_verification_link(token)
    text, html = build_verification_email(username, verification_link)
    return await asyncio.to_thread(
        _send_email_sync,
        to_email,
        "TechBridge 이메일 인증을 완료해주세요",
        text,
        html,
    )


async def send_password_reset_email(to_email: str, username: str, token: str) -> bool:
    reset_link = build_password_reset_link(token)
    text, html = build_password_reset_email(username, reset_link)
    return await asyncio.to_thread(
        _send_email_sync,
        to_email,
        "TechBridge 비밀번호 재설정 안내",
        text,
        html,
    )
