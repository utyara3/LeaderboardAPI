from sqlalchemy import select, text

from fastapi import HTTPException, status

from collections.abc import Sequence

from src.database import AsyncSession
from src.models import User, Leaderboard, LeaderboardEntry

import uuid


def validate_values(values: dict, fields_schema: dict):
    for field_name, field_type in fields_schema.items():
        if field_name in values:
            expected_type = field_type.get("type")
            actual_value = values[field_name]

            if expected_type == "integer":
                if not isinstance(actual_value, (int)) or isinstance(
                    actual_value, bool
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Field '{field_name}' must be integer",
                    )

            if expected_type == "number":
                if not isinstance(actual_value, (int, float)) or isinstance(
                    actual_value, bool
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Field '{field_name}' must be number",
                    )

            if expected_type == "string":
                if not isinstance(actual_value, str):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Field '{field_name}' must be string",
                    )

            else:
                ...  # ???


async def create_leaderboard(
    db: AsyncSession,
    slug: str,
    name: str,
    owner_id: uuid.UUID,
    fields_schema: dict,
    sort_field: str,
    sort_order: str,
) -> Leaderboard:
    if sort_field not in fields_schema:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sort field '{sort_field}' must be in fields_schema",
        )
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
    db: AsyncSession, lb: Leaderboard, player_id: str, values: dict
) -> LeaderboardEntry:
    res = await db.execute(
        select(LeaderboardEntry)
        .where(LeaderboardEntry.leaderboard_id == lb.id)
        .where(LeaderboardEntry.player_id == player_id)
    )
    user_entry = res.scalar_one_or_none()

    if user_entry:
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
                        ORDER BY (values->:sort_field)::numeric {direction},
                        created_at ASC 
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
    db: AsyncSession, slug: str, limit: int, offset: int
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
        .offset(offset)
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
