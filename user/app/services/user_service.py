from typing import Optional
from psycopg.rows import dict_row
from fastapi import HTTPException

# Import SQL queries
from db.users import (
    CREATE_USER,
    GET_USERS,
    GET_USER_BY_EMAIL,
    GET_USER_BY_ID,
    UPDATE_USER_PROFILE,
    INCREASE_REPUTATION,
    DECREASE_REPUTATION,
    DELETE_USER,
)

from app.models.users_models import UserRead, UserUpdate


class UserService:
    def __init__(self, pool):
        #pool passed from router
        self.pool = pool

    async def create_user(self, payload) -> UserRead:
        
        async with self.pool.connection() as conn:
            conn.row_factory = dict_row
            stmt = await conn.execute(
                CREATE_USER,
                (payload.name, payload.email, payload.skill_level),
            )
            row = await stmt.fetchone()

            if not row:
                raise HTTPException(status_code=500, detail="Failed to create user")

            return UserRead(**row)

    async def get_all_users(self) -> list[UserRead]:
        async with self.pool.connection() as conn:
            conn.row_factory = dict_row
            stmt = await conn.execute(GET_USERS)
            rows = await stmt.fetchall()
            return [UserRead(**row) for row in rows]

    async def get_user_by_email(self, email: str) -> Optional[UserRead]:
        async with self.pool.connection() as conn:
            conn.row_factory = dict_row
            stmt = await conn.execute(GET_USER_BY_EMAIL, (email,))
            row = await stmt.fetchone()
            if not row:
                return None
            return UserRead(**row)

    async def get_user_by_id(self, user_id: int) -> Optional[UserRead]:
        async with self.pool.connection() as conn:
            conn.row_factory = dict_row
            stmt = await conn.execute(GET_USER_BY_ID, (user_id,))
            row = await stmt.fetchone()

            if not row:
                return None

            return UserRead(**row)

    async def update_user(self, user_id: int, updates: UserUpdate) -> Optional[UserRead]:
        async with self.pool.connection() as conn:
            conn.row_factory = dict_row
            stmt = await conn.execute(
                UPDATE_USER_PROFILE,
                (
                    updates.name,
                    updates.skill_level,
                    updates.profile_photo,
                    updates.video_verified,
                    user_id,
                ),
            )
            row = await stmt.fetchone()

            if not row:
                return None

            return UserRead(**row)

    async def increment_reputation(self, amount: int, user_id: int) -> Optional[int]:
        async with self.pool.connection() as conn:
            conn.row_factory = dict_row
            stmt = await conn.execute(INCREASE_REPUTATION, (amount, user_id))
            row = await stmt.fetchone()
            if not row:
                return None
            return row

    async def decrease_reputation(self, amount: int, user_id: int) -> int:
        async with self.pool.connection() as conn:
            conn.row_factory = dict_row
            stmt = await conn.execute(DECREASE_REPUTATION, (amount, user_id))
            row = await stmt.fetchone()
            if not row:
                return None
            return row

    async def delete_user(self, user_id: int):
        async with self.pool.connection() as conn:
            await conn.execute(DELETE_USER, (user_id,))
            return {"status": "deleted"}
