from fastapi import APIRouter, HTTPException
from uuid import UUID
from tables import Game
from core import session_int


router = APIRouter(prefix="/bootstrap", tags=["Bootstrap"])


@router.get("/{game_id}")
def get_level(game_id: UUID, db: session_int = None):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        return None
    
    level_url=game.level_url
    if not level_url:
        raise HTTPException(status_code=404, detail="Game not found")
    return {"level_url": level_url}
 