from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload
from typing import List
from jose import JWTError
from pathlib import Path
from uuid import uuid4
import asyncio

from app.database import get_db, AsyncSessionLocal
from app.models.user import User
from app.models.chat import ChatRoom, ChatMember, ChatMessage
from app.schemas.chat import (
    ChatRoomCreate, ChatRoomResponse,
    ChatMemberResponse, ChatMessageResponse
)
from app.core.security import decode_token
from app.dependencies import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
ALLOWED_FILE_EXTENSIONS = {".pdf", ".txt", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".zip"}
MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024
CHAT_UPLOAD_DIR = Path("uploads/chat")


# ── WebSocket 연결 관리
class ConnectionManager:
    def __init__(self):
        self.active: dict[int, dict[int, list[WebSocket]]] = {}

    def add(self, room_id: int, user_id: int, ws: WebSocket):
        room_connections = self.active.setdefault(room_id, {})
        room_connections.setdefault(user_id, []).append(ws)

    def disconnect(self, room_id: int, user_id: int, ws: WebSocket):
        room_connections = self.active.get(room_id)
        if not room_connections:
            return
        user_connections = room_connections.get(user_id)
        if not user_connections:
            return
        try:
            user_connections.remove(ws)
        except ValueError:
            pass
        if not user_connections:
            room_connections.pop(user_id, None)
        if not room_connections:
            self.active.pop(room_id, None)

    def online_user_ids(self, room_id: int) -> list[int]:
        return sorted(self.active.get(room_id, {}).keys())

    async def broadcast(self, room_id: int, message: dict):
        for user_connections in list(self.active.get(room_id, {}).values()):
            for ws in list(user_connections):
                try:
                    await ws.send_json(message)
                except:
                    pass

    async def broadcast_presence(self, room_id: int):
        await self.broadcast(room_id, {
            "event": "presence",
            "online_user_ids": self.online_user_ids(room_id),
        })


manager = ConnectionManager()


# ── 1. 채팅방 생성 또는 조회
@router.post("/rooms", response_model=ChatRoomResponse, status_code=201)
async def create_room(
    data: ChatRoomCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 1:1 채팅인 경우 기존 방이 있는지 먼저 확인
    if data.type == "direct" and len(data.member_ids) == 1:
        other_id = data.member_ids[0]
        # 내가 나 자신에게 보내는 것은 방지 (필요 시 허용 가능)
        if other_id == current_user.id:
            raise HTTPException(status_code=400, detail="자기 자신과는 대화할 수 없습니다")
            
        stmt = (
            select(ChatRoom)
            .join(ChatMember)
            .where(ChatRoom.type == "direct")
            .where(ChatMember.user_id.in_([current_user.id, other_id]))
            .group_by(ChatRoom.id)
            .having(func.count(ChatMember.id) == 2)
        )
        existing = await db.execute(stmt)
        room = existing.scalar_one_or_none()
        if room:
            # 기존 방이 있으면 정보 보강해서 반환
            return await _get_room_with_details(room.id, current_user.id, db)

    # 방 새로 생성
    room = ChatRoom(name=data.name, type=data.type, created_by=current_user.id)
    db.add(room)
    await db.flush()

    # 나 추가
    db.add(ChatMember(room_id=room.id, user_id=current_user.id))
    # 상대방들 추가
    for uid in data.member_ids:
        if uid == current_user.id: continue
        user_check = await db.execute(select(User).where(User.id == uid))
        if not user_check.scalar_one_or_none():
            raise HTTPException(status_code=404, detail=f"유저 {uid}를 찾을 수 없습니다")
        db.add(ChatMember(room_id=room.id, user_id=uid))

    await db.commit()
    return await _get_room_with_details(room.id, current_user.id, db)


# ── 2. 내 채팅방 목록 (상세 정보 포함)
@router.get("/rooms", response_model=List[ChatRoomResponse])
async def get_rooms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 내가 속한 모든 방 ID 조회
    stmt = select(ChatRoom.id).join(ChatMember).where(ChatMember.user_id == current_user.id)
    result = await db.execute(stmt)
    room_ids = result.scalars().all()
    
    rooms_data = []
    for rid in room_ids:
        rd = await _get_room_with_details(rid, current_user.id, db)
        rooms_data.append(rd)
        
    # 최근 메시지 시간 순 정렬
    rooms_data.sort(key=lambda x: x.last_message_time or x.created_at, reverse=True)
    return rooms_data


# ── 3. 채팅방 상세 조회
@router.get("/rooms/{room_id}", response_model=ChatRoomResponse)
async def get_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _check_member(room_id, current_user.id, db)
    return await _get_room_with_details(room_id, current_user.id, db)


# ── 상세 정보 조회 헬퍼
async def _get_room_with_details(room_id: int, user_id: int, db: AsyncSession):
    stmt = (
        select(ChatRoom)
        .options(selectinload(ChatRoom.members).selectinload(ChatMember.user))
        .where(ChatRoom.id == room_id)
    )
    res = await db.execute(stmt)
    room = res.scalar_one()
    
    # 마지막 메시지 조회
    msg_stmt = (
        select(ChatMessage)
        .where(ChatMessage.room_id == room_id)
        .order_by(desc(ChatMessage.created_at))
        .limit(1)
    )
    msg_res = await db.execute(msg_stmt)
    last_msg = msg_res.scalar_one_or_none()
    
    # 안 읽은 메시지 수
    unread_stmt = (
        select(func.count(ChatMessage.id))
        .where(and_(
            ChatMessage.room_id == room_id,
            ChatMessage.sender_id != user_id,
            ChatMessage.is_read == False
        ))
    )
    unread_res = await db.execute(unread_stmt)
    unread_count = unread_res.scalar()
    
    # 응답 객체 구성
    room_resp = ChatRoomResponse.from_orm(room)
    if last_msg:
        room_resp.last_message = last_msg.content
        room_resp.last_message_time = last_msg.created_at
    room_resp.unread_count = unread_count
    
    return room_resp


# ── 4. 채팅방 나가기
@router.delete("/rooms/{room_id}")
async def leave_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await _get_member(room_id, current_user.id, db)
    await db.delete(member)
    await db.commit()
    return {"message": "채팅방에서 나갔습니다"}


# ── 5. 참여자 목록
@router.get("/rooms/{room_id}/members", response_model=List[ChatMemberResponse])
async def get_members(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _check_member(room_id, current_user.id, db)
    result = await db.execute(
        select(ChatMember).where(ChatMember.room_id == room_id)
    )
    return result.scalars().all()


# ── 6. 메시지 조회
@router.get("/rooms/{room_id}/messages", response_model=List[ChatMessageResponse])
async def get_messages(
    room_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _check_member(room_id, current_user.id, db)
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.room_id == room_id)
        .order_by(ChatMessage.created_at.asc())
        .offset(skip).limit(limit)
    )
    return result.scalars().all()


# ── 7. 읽음 처리
@router.patch("/rooms/{room_id}/read")
async def mark_as_read(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _check_member(room_id, current_user.id, db)
    result = await db.execute(
        select(ChatMessage).where(
            and_(
                ChatMessage.room_id == room_id,
                ChatMessage.sender_id != current_user.id,
                ChatMessage.is_read == False,
            )
        )
    )
    messages = result.scalars().all()
    for msg in messages:
        msg.is_read = True
    await db.commit()
    return {"message": f"{len(messages)}개의 메시지를 읽음 처리했습니다"}


# ── 8. 첨부파일 업로드 메시지 전송
@router.post("/rooms/{room_id}/attachments", response_model=ChatMessageResponse, status_code=201)
async def upload_attachment(
    room_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _check_member(room_id, current_user.id, db)

    original_name = Path(file.filename or "attachment").name
    extension = Path(original_name).suffix.lower()
    allowed_extensions = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_FILE_EXTENSIONS
    if extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식입니다")

    payload = await file.read()
    file_size = len(payload)
    if file_size > MAX_ATTACHMENT_BYTES:
        raise HTTPException(status_code=400, detail="첨부파일은 10MB 이하만 업로드할 수 있습니다")

    message_type = "image" if extension in ALLOWED_IMAGE_EXTENSIONS else "file"
    room_dir = CHAT_UPLOAD_DIR / str(room_id)
    room_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid4().hex}{extension}"
    stored_path = room_dir / stored_name
    await asyncio.to_thread(stored_path.write_bytes, payload)

    file_url = f"/uploads/chat/{room_id}/{stored_name}"
    message = ChatMessage(
        room_id=room_id,
        sender_id=current_user.id,
        content=original_name,
        message_type=message_type,
        file_url=file_url,
        file_name=original_name,
        file_size=file_size,
        file_content_type=file.content_type,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)

    members_result = await db.execute(select(ChatMember).where(ChatMember.room_id == room_id))
    room_members = members_result.scalars().all()
    await _send_chat_notifications(
        room_id=room_id,
        sender_id=current_user.id,
        sender_username=current_user.username,
        members=room_members,
    )

    response = ChatMessageResponse.model_validate(message)
    await manager.broadcast(room_id, response.model_dump(mode="json"))
    return response


# ── 9. WebSocket 실시간 메시지 전송
@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    room_id: int,
    websocket: WebSocket,
    token: str,
):
    await websocket.accept()

    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        await websocket.close(code=1008)
        return

    async with AsyncSessionLocal() as db:
        member_check = await db.execute(
            select(ChatMember).where(
                and_(ChatMember.room_id == room_id, ChatMember.user_id == user_id)
            )
        )
        if not member_check.scalar_one_or_none():
            await websocket.close(code=1008)
            return

        # 발신자 username 조회 (알림 메시지용)
        sender_result = await db.execute(select(User).where(User.id == user_id))
        sender = sender_result.scalar_one_or_none()
        sender_username = sender.username if sender else str(user_id)

    manager.add(room_id, user_id, websocket)
    await manager.broadcast_presence(room_id)
    try:
        while True:
            text = await websocket.receive_text()

            async with AsyncSessionLocal() as db:
                msg = ChatMessage(room_id=room_id, sender_id=user_id, content=text)
                db.add(msg)
                await db.commit()
                await db.refresh(msg)

                # 같은 방 멤버들에게 알림 전송 (발신자 제외)
                members_result = await db.execute(
                    select(ChatMember).where(ChatMember.room_id == room_id)
                )
                room_members = members_result.scalars().all()

            # 알림은 DB 세션 종료 후 별도 처리
            await _send_chat_notifications(
                room_id=room_id,
                sender_id=user_id,
                sender_username=sender_username,
                members=room_members,
            )

            response = ChatMessageResponse.model_validate(msg)
            await manager.broadcast(room_id, response.model_dump(mode="json"))
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(room_id, user_id, websocket)
        await manager.broadcast_presence(room_id)


async def _send_chat_notifications(
    room_id: int,
    sender_id: int,
    sender_username: str,
    members: list,
):
    """채팅 메시지 수신 알림 - 발신자 제외 모든 멤버에게 전송"""
    # notification_manager를 지연 import하여 순환 참조 방지
    from app.routers.notification import notification_manager, create_notification

    for member in members:
        if member.user_id == sender_id:
            continue
        async with AsyncSessionLocal() as db:
            await create_notification(
                db=db,
                recipient_id=member.user_id,
                actor_name=sender_username,
                notification_type="chat",
                message=f"{sender_username}님에게 연락이 왔습니다.",
                related_type="chat_room",
                related_id=room_id,
            )


# ── 내부 헬퍼
async def _get_member(room_id: int, user_id: int, db: AsyncSession) -> ChatMember:
    result = await db.execute(
        select(ChatMember).where(
            and_(ChatMember.room_id == room_id, ChatMember.user_id == user_id)
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=403, detail="해당 채팅방의 멤버가 아닙니다")
    return member


async def _check_member(room_id: int, user_id: int, db: AsyncSession):
    await _get_member(room_id, user_id, db)
