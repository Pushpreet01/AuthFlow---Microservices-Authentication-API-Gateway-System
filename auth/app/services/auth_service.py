from psycopg.rows import dict_row
from fastapi import HTTPException

from db.auth import (
    CREATE_AUTH_RECORD,
    GET_AUTH_BY_USER_ID,
    UPDATE_PASSWORD_HASH,
    CREATE_REFRESH_TOKEN,
    GET_REFRESH_TOKEN,
    INVALIDATE_REFRESH_TOKEN,
    ROTATE_REFRESH_TOKEN,
)

from app.services.hash_service import HashService
from app.services.token_service import TokenService


class AuthService:
    def __init__(self, pool):
        self.pool = pool

    # REGISTER USER AUTH RECORD
    async def create_auth_record(self, user_id: int, password: str):
        hashed = HashService.hash_password(password)

        async with self.pool.connection() as conn:
            conn.row_factory = dict_row
            stmt = await conn.execute(CREATE_AUTH_RECORD, (user_id, hashed))
            row = await stmt.fetchone()
            return row

    # LOGIN FLOW
    async def login(self, user_id: int, password: str, user_agent: str):
        # 1. Get hashed password
        async with self.pool.connection() as conn:
            conn.row_factory = dict_row
            stmt = await conn.execute(GET_AUTH_BY_USER_ID, (user_id,))
            auth_row = await stmt.fetchone()

        if not auth_row:
            raise HTTPException(404, "User auth not found")

        # 2. Verify password
        if not HashService.verify_password(password, auth_row["password_hash"]):
            raise HTTPException(400, "Invalid credentials")

        # 3. Create tokens
        access_token = TokenService.create_access_token(user_id)
        refresh_token = TokenService.create_refresh_token()

        # 4. Store refresh token
        async with self.pool.connection() as conn:
            stmt = await conn.execute(
                CREATE_REFRESH_TOKEN,
                (user_id, refresh_token["hashed"], user_agent, refresh_token["expires_at"])
            )
            await stmt.fetchone()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token["raw"]
        }
    
    # UPDATE PASSWORD
    async def update_password(self, user_id: int, old_password: str, new_password: str):

        async with self.pool.connection() as conn:
            conn.row_factory = dict_row
            stmt = await conn.execute(GET_AUTH_BY_USER_ID, (user_id,))
            auth_row = await stmt.fetchone()

        if not auth_row:
            raise HTTPException(404, "User auth record not found")
        
        if not HashService.verify_password(old_password, auth_row["password_hash"]):
            raise HTTPException(400, "Old password is incorrect")
        
        if HashService.verify_password(new_password, auth_row["password_hash"]):
            raise HTTPException(400, "Password unchanged. Please choose a different password.")

        new_hashed = HashService.hash_password(new_password)

        async with self.pool.connection() as conn:
            conn.row_factory = dict_row
            stmt = await conn.execute(
                UPDATE_PASSWORD_HASH,
                (new_hashed, user_id)
            )
            row = await stmt.fetchone()

        return row

    # REFRESH TOKEN FLOW
    async def refresh(self, refresh_token: str, user_agent: str):
        hash_rf = HashService.hash_refresh_token(refresh_token)

        async with self.pool.connection() as conn:
            conn.row_factory = dict_row
            stmt = await conn.execute(GET_REFRESH_TOKEN, (hash_rf,))
            token_row = await stmt.fetchone()

        if not token_row or not token_row["is_valid"]:
            raise HTTPException(401, "Invalid refresh token")

        # Invalidate old token
        async with self.pool.connection() as conn:
            await conn.execute(ROTATE_REFRESH_TOKEN, (hash_rf,))

        user_id = token_row["user_id"]

        # Issue new tokens
        new_access = TokenService.create_access_token(user_id)
        new_refresh = TokenService.create_refresh_token()

        async with self.pool.connection() as conn:
            await conn.execute(
                CREATE_REFRESH_TOKEN,
                (user_id, new_refresh["hashed"], user_agent, new_refresh["expires_at"])
            )

        return {
            "access_token": new_access,
            "refresh_token": new_refresh["raw"]
        }

    # LOGOUT
    async def logout(self, refresh_token: str):
        hash_rf = HashService.hash_refresh_token(refresh_token)

        async with self.pool.connection() as conn:
            conn.row_factory = dict_row
            stmt = await conn.execute(INVALIDATE_REFRESH_TOKEN, (hash_rf,))
            #stmt = await conn.execute(GET_REFRESH_TOKEN, (hash_rf,))
            row = await stmt.fetchone()

            if row["is_valid"]:
                raise HTTPException(400, "Failed to invalidate refresh token, try again")

            return {"message": "Logged out"}
