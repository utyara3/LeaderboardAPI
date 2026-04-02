from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator

from datetime import datetime

import uuid


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    password: str = Field(..., min_length=8, max_length=72)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        return v.lower()


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    username: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
