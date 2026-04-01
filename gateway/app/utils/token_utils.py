from jose import jwt
from fastapi import HTTPException

from app.config import JWT_PUBLIC_KEY, JWT_ALGORITHM


class TokenUtils:

    @staticmethod
    def verify_access_token(token: str):
        try:
            data = jwt.decode(
                token,
                JWT_PUBLIC_KEY,
                algorithms=[JWT_ALGORITHM]
            )
            return data
        except Exception:
            raise HTTPException(401, "Invalid or expired access token")