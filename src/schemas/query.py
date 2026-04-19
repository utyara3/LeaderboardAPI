from pydantic import BaseModel, Field


class PaginationQuery(BaseModel):
    limit: int = Field(default=10, ge=1, le=100)
    page: int = Field(default=1, ge=1)


class LeaderboardTopQuery(PaginationQuery): ...
