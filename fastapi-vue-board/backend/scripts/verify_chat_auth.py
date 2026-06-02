from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHAT_ROUTER = ROOT / "app" / "routers" / "chat.py"


source = CHAT_ROUTER.read_text(encoding="utf-8")
model_source = (ROOT / "app" / "models" / "chat.py").read_text(encoding="utf-8")
schema_source = (ROOT / "app" / "schemas" / "chat.py").read_text(encoding="utf-8")

if "from app.dependencies import get_current_user" not in source:
    raise SystemExit("chat router must use the shared Authorization header auth dependency")

if "async def get_current_user(token: str" in source:
    raise SystemExit("chat router must not require a token query parameter for HTTP endpoints")

if '@router.post("/rooms/{room_id}/attachments"' not in source:
    raise SystemExit("chat router must expose an attachment upload endpoint")

if "UploadFile" not in source or "File(" not in source:
    raise SystemExit("chat attachment endpoint must accept multipart UploadFile input")

for required in [
    "def online_user_ids",
    "async def broadcast_presence",
    '"event": "presence"',
    "manager.add(room_id, user_id, websocket)",
    "manager.disconnect(room_id, user_id, websocket)",
]:
    if required not in source:
        raise SystemExit(f"chat router must support presence tracking: missing {required}")

if source.count("_send_chat_notifications(") < 3:
    raise SystemExit("chat router must notify recipients for both text and attachment messages")

for field in ["message_type", "file_url", "file_name", "file_size", "file_content_type"]:
    if field not in model_source:
        raise SystemExit(f"ChatMessage model must include {field}")
    if field not in schema_source:
        raise SystemExit(f"ChatMessageResponse schema must include {field}")

print("Chat auth dependency checks passed.")
