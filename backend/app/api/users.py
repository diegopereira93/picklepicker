from fastapi import APIRouter, HTTPException, status, Request, Depends
from pydantic import BaseModel, field_validator
from typing import Optional
from app.db import get_connection
from app.middleware.auth import require_clerk_auth, ClerkAuthState

router = APIRouter(prefix="/users", tags=["users"])


class UserProfileRequest(BaseModel):
    user_id: str
    level: str
    style: Optional[str] = None
    budget_max: float

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        allowed = ["beginner", "intermediate", "advanced"]
        if v.lower() not in allowed:
            raise ValueError(f"level must be one of {allowed}")
        return v.lower()

    @field_validator("style")
    @classmethod
    def validate_style(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        allowed = ["control", "power", "balanced"]
        if v.lower() not in allowed:
            raise ValueError(f"style must be one of {allowed}")
        return v.lower()

    @field_validator("budget_max")
    @classmethod
    def validate_budget(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("budget_max must be greater than 0")
        return v


class UserProfileResponse(BaseModel):
    user_id: str
    level: str
    style: Optional[str]
    budget_max: float


@router.post("/profile", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
async def save_user_profile(
    request: UserProfileRequest,
    auth: ClerkAuthState = Depends(require_clerk_auth),
):
    user_id = auth.clerk_id
    async with get_connection() as conn:
        result = await conn.execute(
            """
            INSERT INTO user_profiles (user_id, level, style, budget_max, updated_at)
            VALUES (%(user_id)s, %(level)s, %(style)s, %(budget_max)s, NOW())
            ON CONFLICT (user_id) DO UPDATE SET
                level = EXCLUDED.level,
                style = EXCLUDED.style,
                budget_max = EXCLUDED.budget_max,
                updated_at = NOW()
            RETURNING user_id, level, style, budget_max
            """,
            {
                "user_id": user_id,
                "level": request.level,
                "style": request.style,
                "budget_max": request.budget_max,
            },
        )
        row = await result.fetchone()
        if not row:
            raise HTTPException(status_code=500, detail="Failed to save profile")

    return UserProfileResponse(
        user_id=row[0],
        level=row[1],
        style=row[2],
        budget_max=float(row[3]),
    )


@router.get("/profile/me", response_model=UserProfileResponse)
async def get_my_profile(auth: ClerkAuthState = Depends(require_clerk_auth)):
    user_id = auth.clerk_id

    async with get_connection() as conn:
        result = await conn.execute(
            """
            SELECT user_id, level, style, budget_max
            FROM user_profiles
            WHERE user_id = %(user_id)s
            """,
            {"user_id": user_id},
        )
        row = await result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Profile not found")

    return UserProfileResponse(
        user_id=row[0],
        level=row[1],
        style=row[2],
        budget_max=float(row[3]),
    )


@router.post("/migrate")
async def migrate_anonymous_profile(
    old_uuid: str,
    auth: ClerkAuthState = Depends(require_clerk_auth),
):
    async with get_connection() as conn:
        result = await conn.execute(
            """
            SELECT level, style, budget_max
            FROM user_profiles
            WHERE user_id = %(old_uuid)s
            """,
            {"old_uuid": old_uuid},
        )
        row = await result.fetchone()
        
        if row:
            await conn.execute(
                """
                INSERT INTO user_profiles (user_id, level, style, budget_max, updated_at)
                VALUES (%(new_user_id)s, %(level)s, %(style)s, %(budget_max)s, NOW())
                ON CONFLICT (user_id) DO UPDATE SET
                    level = EXCLUDED.level,
                    style = EXCLUDED.style,
                    budget_max = EXCLUDED.budget_max,
                    updated_at = NOW()
                """,
                {
                    "new_user_id": auth.clerk_id,
                    "level": row[0],
                    "style": row[1],
                    "budget_max": row[2],
                },
            )
            
            await conn.execute(
                "DELETE FROM user_profiles WHERE user_id = %(old_uuid)s",
                {"old_uuid": old_uuid},
            )
            await conn.commit()
    
    return {"status": "success"}
