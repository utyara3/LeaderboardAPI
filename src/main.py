from fastapi import FastAPI, Depends

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.api.auth import auth_router
from src.api.leaderboards import lb_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(lb_router)


@app.get("/")
async def root(): ...


@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    res = await db.execute(text("SELECT 1"))

    return {"status": "healthy", "database": "connected", "result": res.scalar()}
