from pydantic import BaseModel, ConfigDict, Field

from datetime import datetime

from typing import Literal

import uuid


class LeaderboardCreate(BaseModel):
    slug: str = Field(..., min_length=3, max_length=100, pattern=r"^[a-z0-9-]+$")
    name: str = Field(..., min_length=1, max_length=200)
    fields_schema: dict[str, dict]
    sort_field: str = Field(..., min_length=1)
    sort_order: Literal["asc", "desc"]


class LeaderboardResponse(BaseModel):
    id: uuid.UUID
    slug: str
    name: str
    owner_id: uuid.UUID
    fields_schema: dict
    sort_field: str
    sort_order: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
