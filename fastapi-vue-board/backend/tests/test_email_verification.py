import importlib
import smtplib
import unittest
from unittest.mock import AsyncMock, patch
from types import SimpleNamespace

from fastapi import HTTPException

from app.core import security


class EmailVerificationTokenTests(unittest.TestCase):
    def test_verification_tokens_are_random_and_hashable(self):
        self.assertTrue(
            hasattr(security, "generate_verification_token"),
            "security.generate_verification_token is required",
        )
        self.assertTrue(
            hasattr(security, "hash_verification_token"),
            "security.hash_verification_token is required",
        )

        first_token = security.generate_verification_token()
        second_token = security.generate_verification_token()
        first_hash = security.hash_verification_token(first_token)

        self.assertIsInstance(first_token, str)
        self.assertGreaterEqual(len(first_token), 32)
        self.assertNotEqual(first_token, second_token)
        self.assertNotEqual(first_token, first_hash)
        self.assertEqual(first_hash, security.hash_verification_token(first_token))
        self.assertEqual(len(first_hash), 64)


class EmailVerificationLoginPolicyTests(unittest.TestCase):
    def test_unverified_users_are_blocked_from_login(self):
        auth = importlib.import_module("app.routers.auth")
        guard = getattr(auth, "ensure_email_verified_for_login", None)
        self.assertIsNotNone(guard, "auth.ensure_email_verified_for_login is required")

        with self.assertRaises(HTTPException) as raised:
            guard(SimpleNamespace(email_verified=False))

        self.assertEqual(raised.exception.status_code, 403)
        self.assertIn("이메일 인증", raised.exception.detail)

    def test_verified_users_can_continue_to_login(self):
        auth = importlib.import_module("app.routers.auth")
        guard = getattr(auth, "ensure_email_verified_for_login", None)
        self.assertIsNotNone(guard, "auth.ensure_email_verified_for_login is required")

        self.assertIsNone(guard(SimpleNamespace(email_verified=True)))


class EmailVerificationDeliveryTests(unittest.IsolatedAsyncioTestCase):
    async def test_smtp_authentication_errors_return_service_unavailable(self):
        auth = importlib.import_module("app.routers.auth")
        user = SimpleNamespace(email="user@example.com", username="사용자")
        auth_error = smtplib.SMTPAuthenticationError(535, b"Authentication failed")

        with patch.object(auth, "send_verification_email", AsyncMock(side_effect=auth_error)):
            with self.assertRaises(HTTPException) as raised:
                await auth.deliver_verification_email(user, "token")

        self.assertEqual(raised.exception.status_code, 503)
        self.assertIn("SMTP 설정", raised.exception.detail)

    async def test_password_reset_email_delivery_reuses_smtp_error_handling(self):
        auth = importlib.import_module("app.routers.auth")
        user = SimpleNamespace(email="user@example.com", username="사용자")
        auth_error = smtplib.SMTPAuthenticationError(535, b"Authentication failed")

        self.assertTrue(
            hasattr(auth, "deliver_password_reset_email"),
            "auth.deliver_password_reset_email is required",
        )

        with patch.object(auth, "send_password_reset_email", AsyncMock(side_effect=auth_error)):
            with self.assertRaises(HTTPException) as raised:
                await auth.deliver_password_reset_email(user, "token")

        self.assertEqual(raised.exception.status_code, 503)
        self.assertIn("SMTP 설정", raised.exception.detail)


class PasswordResetResponseTests(unittest.TestCase):
    def test_password_reset_request_response_does_not_expose_token(self):
        auth = importlib.import_module("app.routers.auth")

        self.assertTrue(
            hasattr(auth, "password_reset_request_response"),
            "auth.password_reset_request_response is required",
        )

        response = auth.password_reset_request_response()

        self.assertEqual(response["message"], "비밀번호 찾기 안내를 발송했습니다")
        self.assertNotIn("token", response)

    def test_current_password_reset_rejects_wrong_current_password(self):
        auth = importlib.import_module("app.routers.auth")

        self.assertTrue(
            hasattr(auth, "ensure_current_password_for_reset"),
            "auth.ensure_current_password_for_reset is required",
        )

        user = SimpleNamespace(password=security.hash_password("correct-password"))
        with self.assertRaises(HTTPException) as raised:
            auth.ensure_current_password_for_reset(user, "wrong-password")

        self.assertEqual(raised.exception.status_code, 401)
        self.assertIn("이메일 또는 현재 비밀번호", raised.exception.detail)

    def test_current_password_reset_accepts_correct_current_password(self):
        auth = importlib.import_module("app.routers.auth")

        self.assertTrue(
            hasattr(auth, "ensure_current_password_for_reset"),
            "auth.ensure_current_password_for_reset is required",
        )

        user = SimpleNamespace(password=security.hash_password("correct-password"))

        self.assertIsNone(auth.ensure_current_password_for_reset(user, "correct-password"))


if __name__ == "__main__":
    unittest.main()
