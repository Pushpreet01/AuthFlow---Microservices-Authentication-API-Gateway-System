from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.token_utils import TokenUtils


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        # Public routes
        if request.url.path in ["/auth/login", "/auth/refresh", "/auth/register"]:
            return await call_next(request)

        # Extract access token from cookies
        access_token = request.cookies.get("access_token")

        if not access_token:
            raise HTTPException(401, "Access token missing")

        # Verify it
        request.state.user = TokenUtils.verify_access_token(access_token)

        return await call_next(request)