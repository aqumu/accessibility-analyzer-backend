# app/routes/bookmarks.py
from fastapi import APIRouter, HTTPException, Depends
from app.database.supabase_client import supabase
from app.database.auth import verify_token
from supabase import SupabaseException

router = APIRouter(tags=["bookmarks"])


@router.get("/")
async def get_bookmarks(user_id: str = Depends(verify_token)):
    """Fetch all bookmarks for the authenticated user."""
    try:
        response = (
            supabase.table("bookmarks").select("*").eq("user_id", user_id).execute()
        )
        return response.data or []
    except SupabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def add_bookmark(bookmark: dict, user_id: str = Depends(verify_token)):
    """Insert new bookmark for the authenticated user."""
    bookmark_with_user = {**bookmark, "user_id": user_id}
    try:
        response = supabase.table("bookmarks").insert(bookmark_with_user).execute()
        return response.data
    except SupabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{bookmark_id}")
async def delete_bookmark(bookmark_id: str, user_id: str = Depends(verify_token)):
    """Delete a bookmark by ID for the authenticated user."""
    try:
        response = (
            supabase.table("bookmarks")
            .delete()
            .eq("id", bookmark_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Bookmark not found")

        return {"message": "Bookmark deleted successfully"}
    except SupabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
