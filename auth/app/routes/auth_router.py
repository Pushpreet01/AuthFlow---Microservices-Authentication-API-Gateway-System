from fastapi import APIRouter, Depends, HTTPException, Header, Response, Request
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv
import os

from db.db_pool import get_db_pool
from app.services.auth_service import AuthService

load_dotenv()
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")

router = APIRouter()


# Pydantic Schemas

class RegisterAuth(BaseModel):
    name: str 
    email: str 
    skill_level: str = "beginner"
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class ChangePasswordRequest(BaseModel):
    user_id: int
    old_password: str
    new_password: str


class RefreshRequest(BaseModel):
    refresh_token: str


# ROUTES

@router.post("/register")
async def register(payload: RegisterAuth, request: Request):

    # 1. Create user in user-service
    async with httpx.AsyncClient() as client:
        user_res = await client.post(
            f"{USER_SERVICE_URL}/create",
            json={
                "name": payload.name,
                "email": payload.email,
                "skill_level": payload.skill_level,
            }
        )

    if user_res.status_code != 200:
        raise HTTPException(400, "User service failed to create user")

    user_data = user_res.json()
    user_id = user_data["id"]

    # 2. Create auth record
    pool = get_db_pool()
    service = AuthService(pool)

    try:
        auth_row = await service.create_auth_record(user_id, payload.password)
    except Exception as e:
        # 3. Rollback user service
        async with httpx.AsyncClient() as client:
            await client.delete(f"{USER_SERVICE_URL}/{user_id}")   # You must add this route in user service
        
        raise HTTPException(500, "Failed to create auth record, user rolled back")

    return {
        "message": "Signup complete",
        "user_id": user_id,
        "auth_id": auth_row["id"],
    }


@router.post("/login")
async def login(payload: LoginRequest, user_agent: str = Header(default="unknown")):

    async with httpx.AsyncClient() as client:
        user_res = await client.get(
            f"{USER_SERVICE_URL}/get-by-email/{payload.email}")

    if user_res.status_code != 200:
        raise HTTPException(status_code=user_res.status_code, detail=user_res.json().get("detail", "User not found"))

    user_data = user_res.json()
    user_id = user_data["id"]

    pool = get_db_pool()
    service = AuthService(pool)

    tokens = await service.login(user_id, payload.password, user_agent)

    return tokens


@router.post("/refresh")
async def refresh_tokens(payload: RefreshRequest, user_agent: str = Header(default="unknown")):
    pool = get_db_pool()
    service = AuthService(pool)

    tokens = await service.refresh(payload.refresh_token, user_agent)

    return tokens


@router.post("/logout")
async def logout(payload: RefreshRequest, Response: Response):
    pool = get_db_pool()
    service = AuthService(pool)

    log = await service.logout(payload.refresh_token)

    return log



@router.post("/change-password")
async def change_password(payload: ChangePasswordRequest):
    pool = get_db_pool()
    service = AuthService(pool)

    row = await service.update_password(
        payload.user_id,
        payload.old_password,
        payload.new_password
    )

    if not row:
        raise HTTPException(500, "Password update failed")

    return {"message": "Password updated successfully"}
