from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from jose import JWTError

from app.database import get_db, AsyncSessionLocal
from app.models.notification import Notification
from app.models.user import User
from app.dependencies import get_current_user
from app.core.security import decode_token

router = APIRouter(prefix="/notifications", tags=["Notifications"])


# ── WebSocket 연결 관리 (user_id 기준)
class NotificationManager:
    def __init__(self):
        # { user_id: [WebSocket, ...] }
        self.active: dict[int, list[WebSocket]] = {}

    def add(self, user_id: int, ws: WebSocket):
        self.active.setdefault(user_id, []).append(ws)

    def disconnect(self, user_id: int, ws: WebSocket):
        if user_id in self.active:
            try:
                self.active[user_id].remove(ws)
            except ValueError:
                pass

    async def send_to_user(self, user_id: int, data: dict):
        for ws in list(self.active.get(user_id, [])):
            try:
                await ws.send_json(data)
            except Exception:
                pass


notification_manager = NotificationManager()


async def create_notification(
    db: AsyncSession,
    recipient_id: int,
    actor_name: Optional[str],
    notification_type: str,
    message: str,
    related_type: Optional[str] = None,
    related_id: Optional[int] = None,
):
    """알림 DB 저장 + WebSocket 실시간 전송 헬퍼"""
    notif = Notification(
        recipient_id=recipient_id,
        actor_name=actor_name,
        notification_type=notification_type,
        message=message,
        related_type=related_type,
        related_id=related_id,
    )
    db.add(notif)
    await db.commit()
    await db.refresh(notif)

    await notification_manager.send_to_user(
        recipient_id,
        {
            "id": notif.id,
            "actor_name": notif.actor_name,
            "type": notification_type,
            "message": message,
            "related_type": related_type,
            "related_id": related_id,
            "is_read": False,
            "created_at": notif.created_at.isoformat() if notif.created_at else None,
        },
    )
    return notif


# ── 1. 내 알림 목록 조회
@router.get("/")
async def get_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification)
        .where(Notification.recipient_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
    )
    notifications = result.scalars().all()
    return [
        {
            "id": n.id,
            "actor_name": n.actor_name,
            "type": n.notification_type,
            "message": n.message,
            "related_type": n.related_type,
            "related_id": n.related_id,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        }
        for n in notifications
    ]


# ── 2. 전체 읽음 처리 (단일보다 먼저 라우팅되어야 하므로 위에 배치)
@router.patch("/read-all")
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification).where(
            Notification.recipient_id == current_user.id,
            Notification.is_read == False,
        )
    )
    notifs = result.scalars().all()
    for n in notifs:
        n.is_read = True
    await db.commit()
    return {"message": f"{len(notifs)}개의 알림을 읽음 처리했습니다."}


# ── 3. 단일 알림 읽음 처리
@router.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.recipient_id == current_user.id,
        )
    )
    notif = result.scalar_one_or_none()
    if not notif:
        raise HTTPException(status_code=404, detail="알림을 찾을 수 없습니다.")
    notif.is_read = True
    await db.commit()
    return {"message": "읽음 처리되었습니다."}


# ── 4. WebSocket: 실시간 알림 수신
@router.websocket("/ws")
async def notification_ws(websocket: WebSocket, token: str):
    await websocket.accept()

    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            await websocket.close(code=1008)
            return
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        await websocket.close(code=1008)
        return

    notification_manager.add(user_id, websocket)
    try:
        while True:
            # 연결 유지용 (클라이언트가 ping 전송 가능)
            await websocket.receive_text()
    except WebSocketDisconnect:
        notification_manager.disconnect(user_id, websocket)