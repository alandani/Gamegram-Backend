from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from datetime import datetime
from tables import Game,Sandbox
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from uuid import UUID
from tables import Game, Like, User, Follow


# ── CREATE ────────────────────────────────────────────────────────

def create_game(
    db: Session,
    creator_id: UUID,
    sandbox_id: UUID,
    level_url: str,
    title: str = "Untitled",
    description: str = None,
    icon_url: str = None,
) -> Game:
    game = Game(
        id=uuid4(),
        creator_id=creator_id,
        sandbox_id=sandbox_id,
        title=title,
        description=description,
        level_url=level_url,
        icon_url=icon_url,
    )
    db.add(game)
    db.flush()
    db.refresh(game)
    return game



def get_user_by_id(db: Session, user_id: UUID) -> User | None:
    return db.query(User).filter(User.id == user_id).first()
 
 
# ── READ: get user profile with counts ───────────────────────────
 
def get_user_profile(db: Session, user_id: UUID) -> dict | None:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
 
    follower_count  = db.query(Follow).filter(Follow.following_id == user_id).count()
    following_count = db.query(Follow).filter(Follow.follower_id == user_id).count()
    game_count      = db.query(Game).filter(Game.creator_id == user_id).count()
 
    return {
        "id":              user.id,
        "email":           user.email,
        "username":        user.username,
        "avatar_url":      user.avatar_url,
        "bio":             user.bio,
        "created_at":      user.created_at,
        "follower_count":  follower_count,
        "following_count": following_count,
        "game_count":      game_count,
    }
 
 
# ── READ: get games created by user ──────────────────────────────
 
def get_user_games(db: Session, user_id: UUID) -> list[Game]:
    return (
        db.query(Game)
        .filter(Game.creator_id == user_id, Game.status == "published")
        .order_by(Game.created_at.desc())
        .all()
    )

# ── READ: paginated feed (counter based) ─────────────────────────
# Uses joinedload to fetch creator + sandbox in ONE query
# Uses subquery to fetch like/dislike counts in ONE query
# Total: 1 query instead of 21+ queries for 10 games

def get_game_feed(db: Session, counter: int = 1) -> list:
    limit  = 10
    offset = (counter - 1) * limit

    # Subquery for like count per game
    like_subq = (
        db.query(Like.game_id, func.count(Like.id).label("like_count"))
        .filter(Like.is_like == True)
        .group_by(Like.game_id)
        .subquery()
    )

    # Subquery for dislike count per game
    dislike_subq = (
        db.query(Like.game_id, func.count(Like.id).label("dislike_count"))
        .filter(Like.is_like == False)
        .group_by(Like.game_id)
        .subquery()
    )

    # Main query — joins everything in one shot
    return (
        db.query(
            Game,
            func.coalesce(like_subq.c.like_count, 0).label("like_count"),
            func.coalesce(dislike_subq.c.dislike_count, 0).label("dislike_count"),
        )
        .options(
            joinedload(Game.creator),   # fetch creator in same query
            joinedload(Game.sandbox),   # fetch sandbox in same query
        )
        .outerjoin(like_subq, Game.id == like_subq.c.game_id)
        .outerjoin(dislike_subq, Game.id == dislike_subq.c.game_id)
        .filter(Game.status == "published")
        .order_by(Game.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    # returns list of (Game, like_count, dislike_count) tuples


# ── READ: single game by id ───────────────────────────────────────

def get_game_by_id(db: Session, game_id: UUID):
    like_subq = (
        db.query(Like.game_id, func.count(Like.id).label("like_count"))
        .filter(Like.is_like == True)
        .group_by(Like.game_id)
        .subquery()
    )

    dislike_subq = (
        db.query(Like.game_id, func.count(Like.id).label("dislike_count"))
        .filter(Like.is_like == False)
        .group_by(Like.game_id)
        .subquery()
    )

    return (
        db.query(
            Game,
            func.coalesce(like_subq.c.like_count, 0).label("like_count"),
            func.coalesce(dislike_subq.c.dislike_count, 0).label("dislike_count"),
        )
        .options(
            joinedload(Game.creator),
            joinedload(Game.sandbox),
        )
        .outerjoin(like_subq, Game.id == like_subq.c.game_id)
        .outerjoin(dislike_subq, Game.id == dislike_subq.c.game_id)
        .filter(Game.id == game_id)
        .first()
    )
    # returns (Game, like_count, dislike_count) tuple or None





# ── READ: feed ────────────────────────────────────────────────────

def get_feed(db: Session, cursor: str = None, limit: int = 10) -> list[Game]:
    query = db.query(Game).filter(Game.status == "published").order_by(Game.created_at.desc())

    if cursor:
        cursor_time = datetime.fromisoformat(cursor)
        query = query.filter(Game.created_at < cursor_time)

    return query.limit(limit).all()


# ── READ: games by user ───────────────────────────────────────────

def get_games_by_user(db: Session, user_id: UUID) -> list[Game]:
    return db.query(Game).filter(
        Game.creator_id == user_id,
        Game.status == "published"
    ).order_by(Game.created_at.desc()).all()



def get_all_sandboxes(db: Session) -> list[Sandbox]:
    return db.query(Sandbox).order_by(Sandbox.created_at.desc()).all()
 
 
# ── READ: get single sandbox by id ────────────────────────────────
 
def get_sandbox_by_id(db: Session, sandbox_id: UUID) -> Sandbox | None:
    return db.query(Sandbox).filter(Sandbox.id == sandbox_id).first()
 
 
# ── SAVE: upload .json to Supabase Storage + create game in db ────
# Called when user clicks "Create Game" in the app for a sandbox
 
def save_game_from_sandbox(
    db: Session,
    supabase,               # supabase client passed in from router
    creator_id: UUID,
    sandbox_id: UUID,
    json_bytes: bytes,      # raw .json file bytes from sandbox
    title: str = "Untitled",
) -> Game:
    # Upload .json to Supabase Storage
    gameid=uuid4()
    file_path = f"{gameid}.json"
 
    supabase.storage.from_("levels").upload(
        path=file_path,
        file=json_bytes,
        file_options={"content-type": "application/json"}
    )
 
    # Get public URL
    level_url = supabase.storage.from_("levels").get_public_url(file_path)
 
    # Save game to DB
    game = Game(
        id=gameid,
        creator_id=creator_id,
        sandbox_id=sandbox_id,
        title=title,
        level_url=level_url,
    )
    db.add(game)
    db.flush()
    db.refresh(game)
    return game


# ── UPDATE ────────────────────────────────────────────────────────

def update_game(
    db: Session,
    game: Game,
    title: str = None,
    description: str = None,
    icon_url: str = None,
) -> Game:
    if title is not None:
        game.title = title
    if description is not None:
        game.description = description
    if icon_url is not None:
        game.icon_url = icon_url
    db.flush()
    return game


# ── DELETE ────────────────────────────────────────────────────────

def delete_game(db: Session, game: Game) -> None:
    db.delete(game)
    db.flush()