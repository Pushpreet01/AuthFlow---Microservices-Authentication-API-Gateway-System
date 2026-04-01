from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from db.db_pool import get_db_pool
from app.services.user_service import UserService
from enum import Enum

class ReputationAction(str, Enum):
    inc = "inc"
    dec = "dec"

router = APIRouter()

# --Pydantic Request Models

class UserCreate(BaseModel):
    name: str
    email: str
    skill_level: str = "beginner"


class UserUpdate(BaseModel):
    name: str | None = None
    skill_level: str | None = None
    profile_photo: str | None = None
    video_verified: bool | None = None

# --Routes

@router.post("/create")
async def create_user(payload: UserCreate):
    pool = get_db_pool()
    service = UserService(pool)

    try:
        return await service.create_user(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/")
async def get_all_users():
    pool = get_db_pool()
    service = UserService(pool)

    users = await service.get_all_users()
    return users

@router.get("/{user_id}")
async def get_user(user_id: int):
    pool = get_db_pool()
    service = UserService(pool)

    user = await service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@router.get("/get-by-email/{email}")
async def get_user(email: str):
    pool = get_db_pool()
    service = UserService(pool)

    user = await service.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@router.patch("/{user_id}")
async def update_user(user_id: int, payload: UserUpdate):
    pool = get_db_pool()
    service = UserService(pool)

    updated = await service.update_user(user_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")

    return updated

@router.post("/{user_id}/reputation/{action}/{amount}")
async def increment_reputation(user_id: int, action: ReputationAction, amount: int):
    pool = get_db_pool()
    service = UserService(pool)

    if action == "inc":
        updated = await service.increment_reputation(amount, user_id)
    elif action == "dec":
        updated = await service.decrease_reputation(amount, user_id)
    else:
        raise HTTPException(status_code=400, detail="Invalid Reputation function. Use 'inc' or 'dec'.")
    
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")

    return updated

@router.delete("/{user_id}")
async def delete_user(user_id: int):
    pool = get_db_pool()
    service = UserService(pool)

    result = await service.delete_user(user_id)
    return result
