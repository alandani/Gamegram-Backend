from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime


# ── Auth ──────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str


# ── User ──────────────────────────────────────────────────────────

class UserSummary(BaseModel):
    id: UUID
    username: str
    avatar_url: str | None

    model_config = {"from_attributes": True}

class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    avatar_url: str | None
    bio: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

class UserProfileResponse(BaseModel):
    id: UUID
    email: str
    username: str
    avatar_url: str | None
    bio: str | None
    created_at: datetime
    follower_count: int
    following_count: int
    game_count: int

class UpdateProfileRequest(BaseModel):
    username: str | None = None
    bio: str | None = None
    avatar_url: str | None = None


# ── Sandbox ───────────────────────────────────────────────────────

'''class SandboxResponse(BaseModel):
    id: UUID
    name: str
    sandbox_url: str
    icon_url: str | None

    model_config = {"from_attributes": True}'''

class SandboxResponse(BaseModel):
    id: UUID
    name: str
    sandbox_url: str
    runnable_url: str | None = None   # not in DB, constructed on the fly

    class Config:
        from_attributes = True


# ── Game ──────────────────────────────────────────────────────────

class CreateGameRequest(BaseModel):
    sandbox_id: UUID
    title: str
    description: str | None = None
    level_url: str
    icon_url: str | None = None

class UpdateGameRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    icon_url: str | None = None

class GameResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    level_url: str
    icon_url: str | None
    status: str
    play_count: int
    created_at: datetime
    creator: UserSummary
    sandbox: SandboxResponse
    like_count: int
    dislike_count: int
    comment_count: int

class GameFeedResponse(BaseModel):
    games: list[GameResponse]
    next_cursor: str | None


# ── Social ────────────────────────────────────────────────────────

class LikeRequest(BaseModel):
    is_like: bool

class LikeResponse(BaseModel):
    game_id: UUID
    is_like: bool
    like_count: int
    dislike_count: int

class FollowResponse(BaseModel):
    following_id: UUID
    follower_count: int

class CreateCommentRequest(BaseModel):
    content: str

class CommentResponse(BaseModel):
    id: UUID
    content: str
    created_at: datetime
    user: UserSummary

class CommentListResponse(BaseModel):
    comments: list[CommentResponse]
    total: int