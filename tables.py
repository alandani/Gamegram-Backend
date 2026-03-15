import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Text, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, DeclarativeBase



class Base(DeclarativeBase):
    pass


# ── Tables ────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email         = Column(String(255), unique=True, nullable=False)
    username      = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    avatar_url    = Column(Text, nullable=True)
    bio           = Column(Text, nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)

    games     = relationship("Game", back_populates="creator", cascade="all, delete")
    likes     = relationship("Like", back_populates="user", cascade="all, delete")
    comments  = relationship("Comment", back_populates="user", cascade="all, delete")
    following = relationship("Follow", foreign_keys="Follow.follower_id", back_populates="follower", cascade="all, delete")
    followers = relationship("Follow", foreign_keys="Follow.following_id", back_populates="following_user", cascade="all, delete")


class Sandbox(Base):
    __tablename__ = "sandboxes"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name        = Column(String(100), nullable=False)
    sandbox_url = Column(Text, nullable=False)
    icon_url    = Column(Text, nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

    games = relationship("Game", back_populates="sandbox")


class Game(Base):
    __tablename__ = "games"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id  = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    sandbox_id  = Column(UUID(as_uuid=True), ForeignKey("sandboxes.id", ondelete="RESTRICT"), nullable=False)
    title       = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    level_url   = Column(Text, nullable=False)
    icon_url    = Column(Text, nullable=True)
    status      = Column(String(20), default="published")
    play_count  = Column(Integer, default=0)
    created_at  = Column(DateTime, default=datetime.utcnow)

    creator  = relationship("User", back_populates="games")
    sandbox  = relationship("Sandbox", back_populates="games")
    likes    = relationship("Like", back_populates="game", cascade="all, delete")
    comments = relationship("Comment", back_populates="game", cascade="all, delete")


class Like(Base):
    __tablename__ = "likes"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id    = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    game_id    = Column(UUID(as_uuid=True), ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    is_like    = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("user_id", "game_id", name="uq_user_game_like"),)

    user = relationship("User", back_populates="likes")
    game = relationship("Game", back_populates="likes")


class Follow(Base):
    __tablename__ = "follows"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    follower_id  = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    following_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at   = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("follower_id", "following_id", name="uq_follow"),)

    follower       = relationship("User", foreign_keys=[follower_id], back_populates="following")
    following_user = relationship("User", foreign_keys=[following_id], back_populates="followers")


class Comment(Base):
    __tablename__ = "comments"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id    = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    game_id    = Column(UUID(as_uuid=True), ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    content    = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="comments")
    game = relationship("Game", back_populates="comments")


# ── Create all tables ─────────────────────────────────────────────

#if __name__ == "__main__":
#    Base.metadata.create_all(engine)
#    print("All tables created successfully!")