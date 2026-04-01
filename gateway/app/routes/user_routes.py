from fastapi import APIRouter, Request, HTTPException
from enum import Enum
from app.config import USER_SERVICE_URL
from app.proxy import forward_request

router = APIRouter(prefix="/users")

class ReputationAction(str, Enum):
    inc = "inc"
    dec = "dec"


@router.get("/me")
async def get_me(request: Request):
    user_id = request.state.user["sub"]

    backend_response = await forward_request(
        USER_SERVICE_URL,
        f"/{user_id}",
        "GET",
        request=request
    )

    if backend_response.status_code != 200:
        raise HTTPException(backend_response.status_code, backend_response.json().get("detail", "Error fetching user data"))

    return backend_response.json()

@router.get("/get-by-email/{email}")
async def get_user_by_email(request: Request, email: str):
    backend_response = await forward_request(
        USER_SERVICE_URL,
        f"/get-by-email/{email}",
        "GET",
        request=request
    )

    if backend_response.status_code != 200:
        raise HTTPException(
            status_code=backend_response.status_code,
            detail=backend_response.json().get("detail", "User not found")
        )

    return backend_response.json()

@router.patch("/modify")
async def update_user(request: Request):
    user_id = request.state.user["sub"]

    body = await request.json()
    backend_response = await forward_request(
        USER_SERVICE_URL,
        f"/{user_id}",
        "PATCH",
        request=request,
        data=body
    )

    if backend_response.status_code != 200:
        raise HTTPException(
            status_code=backend_response.status_code,
            detail=backend_response.json().get("detail", "User not found")
        )

    return backend_response.json()

@router.post("/reputation/{action}/{amount}")
async def change_reputation(request: Request, action: str, amount: int):
    user_id = request.state.user["sub"]

    backend_response = await forward_request(
        USER_SERVICE_URL,
        f"/{user_id}/reputation/{action}/{amount}",
        "POST",
        request=request
    )

    if backend_response.status_code != 200:
        raise HTTPException(
            status_code=backend_response.status_code,
            detail=backend_response.json().get("detail", "User not found or invalid action")
        )

    return backend_response.json()

@router.delete("/delete")
async def delete_user(request: Request):
    user_id = request.state.user["sub"]

    backend_response = await forward_request(
        USER_SERVICE_URL,
        f"/{user_id}",
        "DELETE",
        request=request
    )

    if backend_response.status_code not in (200, 204):
        raise HTTPException(
            status_code=backend_response.status_code,
            detail=backend_response.json().get("detail", "Failed to delete user")
        )

    return backend_response.json()