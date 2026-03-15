from fastapi import APIRouter, HTTPException,Request
from sqlalchemy.orm import Session
from uuid import UUID

from core import session_int
from crud import get_game_feed, get_game_by_id

router = APIRouter(prefix="/games", tags=["Games"])

# ── Helper ────────────────────────────────────────────────────────
# crud now returns (Game, like_count, dislike_count) tuples

def build_game_dict(row,baseurl) -> dict:
    game, like_count, dislike_count = row
    BASE_URL='https://gamegram-backend-2fqi.onrender.com/'
    # Construct proxy URL instead of raw Supabase URL
    runnable_url = str(BASE_URL)+f"sandboxes/{game.sandbox.id}/files/index.html?mode=noedit&level_id={game.id}"
    
    return {
        "game_id":       game.id,
        "title":         game.title,
        "creator_id":    game.creator_id,
        "creator_name":  game.creator.username,
        "like_count":    like_count,
        "dislike_count": dislike_count,
        "play_count":    game.play_count,
        "runnable_url":  runnable_url,   # ← proxy URL with level_id
        "icon_url":      game.icon_url,
        "created_at":    game.created_at,
    }

# ── GET: paginated feed ───────────────────────────────────────────

@router.get("/")
def feed(request: Request,counter: int = 1, db: session_int = None):
    if counter < 1:
        raise HTTPException(status_code=400, detail="Counter must be 1 or greater")

    rows = get_game_feed(db=db, counter=counter)

    return {
        "counter": counter,
        "total":   len(rows),
        "games":   [build_game_dict(row,request.base_url) for row in rows],
    }


# ── GET: single game ──────────────────────────────────────────────

@router.get("/{game_id}")
def get_game(request: Request,game_id: UUID, db: session_int = None):
    row = get_game_by_id(db=db, game_id=game_id)
    if not row:
        raise HTTPException(status_code=404, detail="Game not found")
    return build_game_dict(row,request.base_url)
