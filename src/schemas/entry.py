from pydantic import BaseModel, Field, ConfigDict

from datetime import datetime

from typing import Any

import uuid


class EntrySubmit(BaseModel):
    player_id: str = Field(..., min_length=1, max_length=100)
    values: dict
    update_if_better: bool = True


class EntryResponse(BaseModel):
    id: uuid.UUID
    leaderboard_id: uuid.UUID
    player_id: str
    values: dict[str, Any]
    rank: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
