# Minigame App — FastAPI Backend

## Folder Structure
```
minigame-v2/
├── main.py                  # Entry point
├── requirements.txt
├── .env.example             # Copy to .env and fill in values
│
├── core/
│   ├── __init__.py
│   ├── config.py            # Reads .env variables
│   ├── database.py          # DB engine + session + Base
│   ├── security.py          # JWT + password hashing
│   └── deps.py              # get_current_user dependency
│
├── models/
│   ├── __init__.py
│   └── models.py            # All SQLAlchemy table models
│
├── schemas/
│   ├── __init__.py
│   ├── auth.py
│   ├── user.py
│   ├── game.py
│   └── social.py
│
└── routers/
    ├── __init__.py
    ├── auth.py              # /auth/*
    ├── users.py             # /users/*
    ├── games.py             # /games/* + /sandboxes
    └── social.py            # like, follow, comment
```

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Create .env file
```bash
cp .env.example .env
# Fill in your real Supabase credentials
```

### 3. Run server
```bash
uvicorn main:app --reload
```

### 4. Test endpoints
Visit: http://localhost:8000/docs

## All Endpoints

### Auth
- POST /auth/register
- POST /auth/login
- POST /auth/refresh
- GET  /auth/me

### Users
- GET  /users/{id}
- PUT  /users/{id}
- GET  /users/{id}/games
- GET  /users/{id}/followers
- GET  /users/{id}/following

### Games
- GET  /sandboxes
- GET  /games
- GET  /games/{id}
- POST /games
- PUT  /games/{id}
- DELETE /games/{id}
- POST /games/{id}/play

### Social
- POST   /games/{id}/like
- DELETE /games/{id}/like
- POST   /users/{id}/follow
- DELETE /users/{id}/follow
- GET    /games/{id}/comments
- POST   /games/{id}/comments
- DELETE /games/{id}/comments/{comment_id}
