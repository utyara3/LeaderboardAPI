from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select

from src.database import get_db
from src.models import Leaderboard, LeaderboardEntry
from src.schemas import UserCreate, UserLogin, UserResponse

lb_router = APIRouter(prefix="/leaderboards", tags=["leaderboards"])


@lb_router.post("/")
async def create_leaderboard(): ...


@lb_router.get("/{slug}")
async def get_leaderboard_by_slug(): ...


@lb_router.post("/{slug}/submit")
async def submit_record(): ...


@lb_router.get("/{slug}/top")
async def get_leaderboard_top(): ...


@lb_router.get("/{slug}/player/{player_id}")
async def get_player_by_id(): ...
