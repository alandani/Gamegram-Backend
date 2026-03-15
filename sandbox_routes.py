from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from fastapi import Request
from typing import Annotated
from uuid import UUID
from fastapi.responses import JSONResponse

from schemas import SandboxResponse, GameResponse, UserSummary
from crud import get_all_sandboxes, get_sandbox_by_id, save_game_from_sandbox
from tables import Like, Comment
from core import session_int,supabase,current_user_dep

import httpx
from fastapi.responses import Response


router = APIRouter(prefix="/sandboxes", tags=["Sandboxes"])

SUPABASE_STORAGE_URL = "https://npmrrkwizgrjiodijvje.supabase.co/storage/v1/object/public/sandboxes/"

HEADERS_MAP = {
    ".data.br":         ("application/octet-stream", "br"),
    ".wasm.br":         ("application/wasm",         "br"),
    ".framework.js.br": ("application/javascript",   "br"),
    ".loader.js":       ("application/javascript",   None),
    ".html":            ("text/html",                None),
    ".css":             ("text/css",                 None),
    ".png":             ("image/png",                None),
    ".ico":             ("image/x-icon",             None),
}

@router.get("/{sandbox_id}/files/{file_path:path}")
async def serve_sandbox_file(sandbox_id: UUID, file_path: str, db: session_int):
    sandbox = get_sandbox_by_id(db=db, sandbox_id=sandbox_id)
    if not sandbox:
        raise HTTPException(status_code=404, detail="Sandbox not found")

    base_url = sandbox.sandbox_url.rsplit("/", 1)[0]

    # Fetch the requested file from Supabase
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{base_url}/{file_path}")

    if r.status_code != 200:
        raise HTTPException(status_code=404, detail="File not found")

    # Correct headers
    HEADERS_MAP = {
        ".data.br":         ("application/octet-stream", "br"),
        ".wasm.br":         ("application/wasm",         "br"),
        ".framework.js.br": ("application/javascript",   "br"),
        ".loader.js":       ("application/javascript",   None),
        ".html":            ("text/html",                None),
        ".css":             ("text/css",                 None),
        ".png":             ("image/png",                None),
        ".ico":             ("image/x-icon",             None),
    }

    content_type = "application/octet-stream"
    encoding = None
    for ext, (mime, enc) in HEADERS_MAP.items():
        if file_path.endswith(ext):
            content_type = mime
            encoding = enc
            break

    headers = {}
    if encoding:
        headers["Content-Encoding"] = encoding

    return Response(
        content=r.content,
        media_type=content_type,
        headers=headers
    )
# ── Helper ────────────────────────────────────────────────────────

def build_game_response(game, db: Session) -> GameResponse:
    like_count    = db.query(Like).filter(Like.game_id == game.id, Like.is_like == True).count()
    dislike_count = db.query(Like).filter(Like.game_id == game.id, Like.is_like == False).count()
    comment_count = db.query(Comment).filter(Comment.game_id == game.id).count()

    return GameResponse(
        id=game.id,
        title=game.title,
        description=game.description,
        level_url=game.level_url,
        icon_url=game.icon_url,
        status=game.status,
        play_count=game.play_count,
        created_at=game.created_at,
        creator=UserSummary.model_validate(game.creator),
        sandbox=SandboxResponse.model_validate(game.sandbox),
        like_count=like_count,
        dislike_count=dislike_count,
        comment_count=comment_count,
    )


# ── GET: all sandboxes feed ───────────────────────────────────────

@router.get("/", response_model=list[SandboxResponse])
def get_sandboxes_feed(db: session_int):
    sandboxes = get_all_sandboxes(db=db)
    return sandboxes

#---------------------
@router.get("/sandbox1", response_model=SandboxResponse)
def get_sandbox1(db: session_int,request: Request,sandbox_id= "b3fab486-79fc-46ac-9abc-12c142a82c28"):
    sandbox = get_sandbox_by_id(db=db, sandbox_id=sandbox_id)
    if not sandbox:
        raise HTTPException(status_code=404, detail="Sandbox not found")
    
    # Construct runnable URL pointing to your FastAPI proxy
    runnable_url = str(request.base_url) + f"sandboxes/{sandbox_id}/files/index.html?mode=edit&sandbox_id={sandbox_id}"
    
    return {
        "id": sandbox.id,
        "name": sandbox.name,
        "sandbox_url": sandbox.sandbox_url,
        "runnable_url": runnable_url        # constructed, not from DB
    }
#-----------------

# ── GET: specific sandbox by id ───────────────────────────────────


@router.get("/select/{sandbox_id}", response_model=SandboxResponse)
def get_sandbox(sandbox_id: UUID, db: session_int,current_user: current_user_dep,request: Request):
    sandbox = get_sandbox_by_id(db=db, sandbox_id=sandbox_id)
    if not sandbox:
        raise HTTPException(status_code=404, detail="Sandbox not found")
    
    # Construct runnable URL pointing to your FastAPI proxy
    runnable_url = str(request.base_url) + f"sandboxes/{sandbox_id}/files/index.html?mode=edit&sandbox_id={sandbox_id}&creator_id={current_user.id}"
    
    return {
        "id": sandbox.id,
        "name": sandbox.name,
        "sandbox_url": sandbox.sandbox_url,
        "runnable_url": runnable_url        # constructed, not from DB
    }


# ── POST: save .json + create game ───────────────────────────────

@router.post("/create", response_model=GameResponse, status_code=201)
def create_game_from_sandbox(
    db: session_int,
    sandbox_id: Annotated[str,Form()],
    current_user: Annotated[str,Form()],
    title: Annotated[str, Form()] = "Untitled",
    level_file: UploadFile = File(...)
):
    # Validate sandbox exists
    if not get_sandbox_by_id(db=db, sandbox_id=sandbox_id):
        raise HTTPException(status_code=404, detail="Sandbox not found")

    # Validate file type
    if not level_file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Only .json files allowed")

    try:
        game = save_game_from_sandbox(
            db=db,
            supabase=supabase,
            creator_id=current_user,
            sandbox_id=sandbox_id,
            json_bytes=level_file.file.read(),
            title=title,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save game: {str(e)}")

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "yay"})