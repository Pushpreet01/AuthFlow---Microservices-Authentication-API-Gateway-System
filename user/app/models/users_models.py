from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# 1. Base model shared across others
class UserBase(BaseModel):
    name: str = Field(..., max_length=100)
    email: EmailStr
    skill_level: str = Field(default="beginner")
    video_verified: bool = False
    profile_photo: Optional[str] = None
    reputation_score: int = 0


# 2. Model for user creation (signup)
class UserCreate(BaseModel):
    password: str = Field(..., min_length=6)

# 3. Model returned to client (never exposes password_hash)
class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # ORM / DB row support

# Alias for compatibility
UserOut = UserRead


# 4. Internal model for DB insert (password_hash included)
class UserDB(UserBase):
    id: int
    password_hash: str
    created_at: datetime

    class Config:
        from_attributes = True


# 5. Partial update model (PATCH / PUT)
class UserUpdate(BaseModel):
    name: Optional[str] = None
    skill_level: Optional[str] = None
    profile_photo: Optional[str] = None
    video_verified: Optional[bool] = None

    class Config:
        extra = "forbid"
