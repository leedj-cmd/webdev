from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


# ─────────────────────────────────────────
# 커뮤니티 게시글
# ─────────────────────────────────────────

class CommunityCreate(BaseModel):
    title: str
    content: Optional[str] = None
    category: str           # "job" | "career" | "project"
    is_anonymous: bool = False


class CommunityUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None


class CommunityRead(BaseModel):
    id: int
    title: str
    content: Optional[str] = None
    category: str
    is_anonymous: bool
    owner_id: Optional[int] = None
    author_name: Optional[str] = None   # 익명이면 None → 프론트에서 '익명' 표시
    created_at: datetime
    updated_at: Optional[datetime] = None
    like_count: int = 0
    comment_count: int = 0

    class Config:
        from_attributes = True


# ─────────────────────────────────────────
# 댓글 + 대댓글
# ─────────────────────────────────────────

class CommunityCommentCreate(BaseModel):
    content: str
    is_anonymous: bool = False
    parent_id: Optional[int] = None


class CommunityCommentUpdate(BaseModel):
    content: str


class CommunityCommentRead(BaseModel):
    id: int
    community_id: int
    user_id: Optional[int] = None
    author_name: Optional[str] = None
    content: str
    is_anonymous: bool
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    like_count: int = 0
    replies: List["CommunityCommentRead"] = []

    class Config:
        from_attributes = True


CommunityCommentRead.model_rebuild()


# ─────────────────────────────────────────
# 커뮤니티 신고
# ─────────────────────────────────────────

class CommunityReportCreate(BaseModel):
    reason: str


class CommunityReportResponse(BaseModel):
    id: int
    community_id: int
    reporter_id: int
    reason: str
    is_resolved: bool
    created_at: datetime

    model_config = {"from_attributes": True}
