from fastapi import FastAPI, Depends

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from pathlib import Path

from src.database import get_db
from src.api.auth import auth_router
from src.api.leaderboards import lb_router

app = FastAPI()
frontend_directory = Path(__file__).parent.parent / "frontend"

app.include_router(auth_router)
app.include_router(lb_router)

app.mount("/static", StaticFiles(directory=frontend_directory), name="static")


@app.get("/")
async def root():
    return FileResponse(f"{frontend_directory}/index.html")


@app.get("/login")
async def login():
    return FileResponse(f"{frontend_directory}/login.html")


@app.get("/leaderboard/{slug}")
async def leaderboard_page(slug: str):
    return FileResponse(f"{frontend_directory}/leaderboard.html")


@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    res = await db.execute(text("SELECT 1"))

    return {"status": "healthy", "database": "connected", "result": res.scalar()}
