from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
from dotenv import load_dotenv
from supabase import create_client
import os

load_dotenv(override=True)

# ── Database Connection ───────────────────────────────────────────

engine = create_engine(os.getenv("DATABASE_URL"), echo=False, pool_pre_ping=True)
sessionfac=sessionmaker(bind=engine,autoflush=False)

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

def init_session():
    session=sessionfac()
    try:
        yield session
    finally:
        session.close()

session_int=Annotated[Session,Depends(init_session)]


bearer = HTTPBearer()
 
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    token = credentials.credentials
 
    # Verify token with Supabase
    try:
        response = supabase.auth.get_user(token)
        user     = response.user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
 
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
 
    return user
 
current_user_dep = Annotated[object, Depends(get_current_user)]