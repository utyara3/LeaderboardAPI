from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select

from src.database import get_db, AsyncSession

from src.models.leaderboard import Leaderboard
from src.models.user import User

from src.schemas.leaderboard import LeaderboardResponse, LeaderboardCreate
from src.schemas.entry import EntrySubmit, EntryResponse
from src.schemas.query import LeaderboardTopQuery

from src.auth.dependencies import get_current_user

from src.services.leaderboard_service import (
    create_leaderboard,
    submit_entry,
    get_top_entries,
    get_player_entry,
    validate_values,
)

lb_router = APIRouter(prefix="/leaderboards", tags=["leaderboards"])


@lb_router.post("/", response_model=LeaderboardResponse)
async def create_leaderboard_route(
    lb_data: LeaderboardCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LeaderboardResponse:
    lb = await create_leaderboard(
        db=db,
        slug=lb_data.slug,
        name=lb_data.name,
        owner_id=current_user.id,
        fields_schema=lb_data.fields_schema,
        sort_field=lb_data.sort_field,
        sort_order=lb_data.sort_order,
    )

    return LeaderboardResponse.model_validate(lb)


@lb_router.get("/{slug}", response_model=LeaderboardResponse)
async def get_leaderboard_by_slug(
    slug: str, db: AsyncSession = Depends(get_db)
) -> LeaderboardResponse:
    res = await db.execute(select(Leaderboard).where(Leaderboard.slug == slug))
    lb = res.scalar_one_or_none()

    if lb is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Leaderboard {slug} not found",
        )

    return LeaderboardResponse.model_validate(lb)


@lb_router.post("/{slug}/submit", response_model=EntryResponse)
async def submit_record(
    slug: str,
    entry_data: EntrySubmit,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EntryResponse:
    res = await db.execute(select(Leaderboard).where(Leaderboard.slug == slug))
    lb = res.scalar_one_or_none()

    if lb is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Leaderboard {slug} not found.",
        )

    if lb.sort_field not in entry_data.values:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Required field '{lb.sort_field}' is missing",
        )

    validate_values(entry_data.values, lb.fields_schema)

    entry = await submit_entry(
        db=db,
        lb=lb,
        player_id=entry_data.player_id,
        values=entry_data.values,
    )

    return EntryResponse.model_validate(entry)


@lb_router.get("/{slug}/top", response_model=list[EntryResponse])
async def get_leaderboard_top(
    slug: str,
    query: LeaderboardTopQuery = Depends(),
    db: AsyncSession = Depends(get_db),
) -> list[EntryResponse]:
    offset = (query.page - 1) * query.limit
    entries = await get_top_entries(db=db, slug=slug, limit=query.limit, offset=offset)
    return [EntryResponse.model_validate(e) for e in entries]


@lb_router.get("/{slug}/player/{player_id}", response_model=EntryResponse)
async def get_player_by_id(
    slug: str, player_id: str, db: AsyncSession = Depends(get_db)
) -> EntryResponse:
    entry = await get_player_entry(db=db, slug=slug, player_id=player_id)

    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player {player_id} entry not found",
        )

    return EntryResponse.model_validate(entry)
