from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from core import session_int, current_user_dep
from crud import get_user_profile, get_user_games
from crud import get_game_by_id
from tables import Like, Comment
from schemas import SandboxResponse, UserSummary

router = APIRouter(prefix="/users", tags=["Users"])


# ── Helper: build game dict for user's games ──────────────────────

def build_game_dict(game, db: Session) -> dict:
    like_count    = db.query(Like).filter(Like.game_id == game.id, Like.is_like == True).count()
    dislike_count = db.query(Like).filter(Like.game_id == game.id, Like.is_like == False).count()

    return {
        "game_id":       game.id,
        "title":         game.title,
        "creator_id":    game.creator_id,
        "creator_name":  game.creator.username,
        "like_count":    like_count,
        "dislike_count": dislike_count,
        "play_count":    game.play_count,
        "runnable_url":  f"{game.sandbox.sandbox_url}?level_id={game.id}",
        "icon_url":      game.icon_url,
        "created_at":    game.created_at,
    }


@router.get("/{user_id}")
def get_profile(user_id: UUID, db: session_int):
    profile = get_user_profile(db=db, user_id=user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return profile


# ── GET: games created by user ────────────────────────────────────

@router.get("/{user_id}/games")
def get_games(user_id: UUID, db: session_int):
    games = get_user_games(db=db, user_id=user_id)
    return {
        "games": [build_game_dict(g, db) for g in games],
        "total": len(games),
    }