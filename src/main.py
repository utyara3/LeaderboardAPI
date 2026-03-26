from fastapi import FastAPI, Depends

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db

app = FastAPI()


@app.get("/")
async def root(): ...


@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    res = await db.execute(text("SELECT 1"))

    return {"status": "healthy", "database": "connected", "result": res.scalar()}
