from fastapi import APIRouter, Request, Response, HTTPException
from app.config import AUTH_SERVICE_URL
from app.proxy import forward_request

router = APIRouter(prefix="/auth")


@router.post("/register")
async def register(request: Request):
    body = await request.json()

    backend_response = await forward_request(
        AUTH_SERVICE_URL,
        "/register",        # Auth-service orchestrates user creation + auth creation
        "POST",
        request=request,
        data=body
    )

    # Return whatever auth-service returns
    return backend_response.json()

@router.post("/login")
async def login(request: Request, response: Response):
    body = await request.json()
    
    backend_response = await forward_request(
        AUTH_SERVICE_URL,
        "/login",
        "POST",
        request=request,
        data=body
    )

    if backend_response.status_code != 200:
        raise HTTPException(400, "Invalid credentials")

    tokens = backend_response.json()

    # Set cookies the gateway takes responsibility
    response.set_cookie(
        "access_token",
        tokens["access_token"],
        httponly=True,
        #secure=True,
        samesite="strict",
        max_age=900 #15 mins
    )

    response.set_cookie(
        "refresh_token",
        tokens["refresh_token"],
        httponly=True,
        #secure=True,
        samesite="strict",
        max_age=60 * 60 * 24 * 30 # 30 days
    )

    return {"message": "Login successful"}


@router.post("/refresh")
async def refresh(request: Request, response: Response):

    refresh_token = request.cookies.get("refresh_token")

    backend_response = await forward_request(
        AUTH_SERVICE_URL,
        "/refresh",
        "POST",
        request=request,
        data={"refresh_token": refresh_token},
    )

    if backend_response.status_code != 200:
        raise HTTPException(400, "Invalid refresh token")

    tokens = backend_response.json()

    response.set_cookie("access_token", tokens["access_token"], httponly=True) #secure=True)
    response.set_cookie("refresh_token", tokens["refresh_token"], httponly=True) #secure=True)

    return {"message": "Tokens refreshed successfully"}


@router.post("/logout")
async def logout(request: Request, response: Response):

    refresh_token = request.cookies.get("refresh_token")

    backend_response = await forward_request(
        AUTH_SERVICE_URL,
        "/logout",
        "POST",
        request=request,
        data={"refresh_token": refresh_token},
    )

    if backend_response.status_code != 200:
        raise HTTPException(backend_response.status_code, "Failed to logout")

    log = backend_response.json()

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return log

@router.post("/change-password")
async def change_password(request: Request):
    body = await request.json()

    backend_response = await forward_request(
        AUTH_SERVICE_URL,
        "/change-password",
        "POST",
        request=request,
        data=body,
    )

    if backend_response.status_code != 200:
        raise HTTPException(backend_response.status_code, backend_response.json().get("detail", "Failed to change password"))

    log = backend_response.json()

    return log
