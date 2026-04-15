from sqlalchemy import select, text

from fastapi import HTTPException, status

from collections.abc import Sequence

from src.database import AsyncSession
from src.models import User, Leaderboard, LeaderboardEntry

import uuid


async def create_leaderboard(
    db: AsyncSession,
    slug: str,
    name: str,
    owner_id: uuid.UUID,
    fields_schema: dict,
    sort_field: str,
    sort_order: str,
) -> Leaderboard:
    res = await db.execute(select(Leaderboard).where(Leaderboard.slug == slug))
    if res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Slug is already exists."
        )

    res = await db.execute(select(User).where(User.id == owner_id))
    if res.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is not exists."
        )

    leaderboard = Leaderboard(
        slug=slug,
        name=name,
        owner_id=owner_id,
        fields_schema=fields_schema,
        sort_field=sort_field,
        sort_order=sort_order,
    )

    db.add(leaderboard)
    await db.commit()
    await db.refresh(leaderboard)

    return leaderboard


async def submit_entry(
    db: AsyncSession,
    slug: str,
    player_id: str,
    values: dict,
    update_if_better: bool = True,
) -> LeaderboardEntry:
    res = await db.execute(select(Leaderboard).where(Leaderboard.slug == slug))
    lb = res.scalar_one_or_none()

    if lb is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Leaderboard {slug} not found.",
        )

    res = await db.execute(
        select(LeaderboardEntry)
        .where(LeaderboardEntry.leaderboard_id == lb.id)
        .where(LeaderboardEntry.player_id == player_id)
    )
    user_entry = res.scalar_one_or_none()

    if user_entry and update_if_better:
        current_score = user_entry.values.get(lb.sort_field)
        new_score = values.get(lb.sort_field)

        if current_score is None or new_score is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No value was found in the '{lb.sort_field}' "
                + f"field of the {'user record' if current_score is None else 'new record'}",
            )

        if lb.sort_order == "asc":
            if new_score >= current_score:
                return user_entry

        else:
            if new_score <= current_score:
                return user_entry

        user_entry.values = values

    else:
        user_entry = LeaderboardEntry(
            leaderboard_id=lb.id, player_id=player_id, values=values, rank=None
        )
        db.add(user_entry)

    await db.flush()

    direction = "ASC" if lb.sort_order == "asc" else "DESC"

    await db.execute(
        text(
            f"""
            WITH ranked AS (
                SELECT 
                    id,
                    RANK() OVER (
                        ORDER BY (values->:sort_field)::numeric {direction}
                    ) as new_rank
                FROM entries
                WHERE leaderboard_id = :lb_id
            )
            UPDATE entries
            SET rank = ranked.new_rank
            FROM ranked
            WHERE entries.id = ranked.id
            """
        ),
        {
            "sort_field": lb.sort_field,
            "lb_id": lb.id,
        },
    )

    await db.commit()
    await db.refresh(user_entry)

    return user_entry


async def get_top_entries(
    db: AsyncSession, slug: str, limit: int = 10
) -> Sequence[LeaderboardEntry]:
    res = await db.execute(select(Leaderboard).where(Leaderboard.slug == slug))
    lb = res.scalar_one_or_none()

    if lb is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Leaderboard {slug} not found",
        )

    res = await db.execute(
        select(LeaderboardEntry)
        .where(LeaderboardEntry.leaderboard_id == lb.id)
        .order_by(LeaderboardEntry.rank.asc())
        .limit(limit)
    )

    return res.scalars().all()


async def get_player_entry(
    db: AsyncSession, slug: str, player_id: str
) -> LeaderboardEntry | None:
    res = await db.execute(select(Leaderboard).where(Leaderboard.slug == slug))
    lb = res.scalar_one_or_none()

    if lb is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Leaderboard {slug} not found",
        )

    res = await db.execute(
        select(LeaderboardEntry)
        .where(LeaderboardEntry.leaderboard_id == lb.id)
        .where(LeaderboardEntry.player_id == player_id)
    )

    return res.scalar_one_or_none()
