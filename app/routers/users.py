from fastapi import APIRouter, Depends, HTTPException
from app.database.supabase_client import supabase
from app.database.auth import verify_token
from datetime import datetime
from app.schemas import UserResponse, UserUpdate, UserStats, UserQuota

try:
    from postgrest import APIError
except ImportError:
    from postgrest.exceptions import APIError

router = APIRouter(tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_user_profile(user_id: str = Depends(verify_token)):
    """Fetch the currently authenticated user's profile."""
    try:
        response = (
            supabase.table("profiles").select("*").eq("id", user_id).single().execute()
        )
    except APIError as e:
        raise HTTPException(status_code=500, detail=f"Supabase error: {str(e)}")

    if not response.data:
        raise HTTPException(status_code=404, detail="User not found")

    return response.data


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    update_data: UserUpdate, user_id: str = Depends(verify_token)
):
    """Update username/email for the authenticated user."""
    update_dict = {
        k: v for k, v in update_data.dict(exclude_unset=True).items() if v is not None
    }

    if not update_dict:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    try:
        response = (
            supabase.table("profiles")
            .update(update_dict, returning="representation")  # ✅ replaces .select("*")
            .eq("id", user_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")

        return response.data[0]

    except APIError as e:
        raise HTTPException(status_code=500, detail=f"Supabase error: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/stats", response_model=UserStats)
async def get_user_stats(user_id: str = Depends(verify_token)):
    """Fetch bookmark stats for the authenticated user."""
    try:
        response = (
            supabase.table("bookmarks")
            .select("created_at")
            .eq("user_id", user_id)
            .execute()
        )
    except APIError as e:
        raise HTTPException(status_code=500, detail=f"Supabase error: {str(e)}")

    bookmarks = response.data or []
    total = len(bookmarks)

    today = datetime.utcnow().date()
    daily_count = sum(
        1
        for b in bookmarks
        if b.get("created_at")
        and datetime.fromisoformat(b["created_at"].replace("Z", "+00:00")).date()
        == today
    )

    last_activity = max(
        (b.get("created_at") for b in bookmarks if b.get("created_at")), default=None
    )

    return {
        "total_bookmarks": total,
        "today_bookmarks": daily_count,
        "last_activity": last_activity,
    }


@router.get("/quota", response_model=UserQuota)
async def get_user_quota(user_id: str = Depends(verify_token)):
    """Return the user's daily bookmark quota."""
    daily_limit = 50  # adjust as needed
    today = datetime.utcnow().date()

    try:
        response = (
            supabase.table("bookmarks")
            .select("created_at")
            .eq("user_id", user_id)
            .execute()
        )
    except APIError as e:
        raise HTTPException(status_code=500, detail=f"Supabase error: {str(e)}")

    today_count = sum(
        1
        for b in response.data or []
        if b.get("created_at")
        and datetime.fromisoformat(b["created_at"].replace("Z", "+00:00")).date()
        == today
    )

    remaining = max(daily_limit - today_count, 0)

    return {
        "daily_limit": daily_limit,
        "used_today": today_count,
        "remaining": remaining,
    }
