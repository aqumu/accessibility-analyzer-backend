from datetime import datetime
from uuid import uuid4
from app.database.supabase_client import supabase


# ------------------------------
# Webpage helpers
# ------------------------------
async def upsert_webpage_record(user_id: str, url: str) -> dict:
    """Insert webpage if not exists, or return existing one."""
    existing = supabase.table("webpages").select("*").eq("user_id", user_id).eq("url", url).execute()

    if existing.data:
        record = existing.data[0]
        supabase.table("webpages").update({"updated_at": datetime.utcnow()}).eq("id", record["id"]).execute()
        return record

    new_record = {
        "id": str(uuid4()),
        "user_id": user_id,
        "url": url,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    res = supabase.table("webpages").insert(new_record).execute()
    return res.data[0]


# ------------------------------
# Run helpers (in-memory state)
# ------------------------------
async def create_run_record(user_id: str, webpage_id: str) -> dict:
    """
    Create a new in-memory run record placeholder.
    In DB we don't create anything yet.
    """
    run_id = str(uuid4())
    return {
        "id": run_id,
        "user_id": user_id,
        "webpage_id": webpage_id,
        "created_at": datetime.utcnow(),
    }


async def update_run_status(run_id: str, status, error_message: str | None = None):
    """
    No DB action – state tracking handled in-memory.
    Just a stub for consistency.
    """
    # In-memory updates happen elsewhere (e.g., RunStateManager)
    return {"run_id": run_id, "status": status.value, "error": error_message}


async def update_webpage_status(webpage_id: str, status):
    """Optionally mark the webpage as recently analyzed."""
    # Only timestamp update, no need to store status permanently
    supabase.table("webpages").update({"analyzed_at": datetime.utcnow()}).eq("id", webpage_id).execute()


# ------------------------------
# Results
# ------------------------------
async def save_run_result(run_id: str, organized_data: dict):
    """
    Save extracted + analyzed data into analysis_results.
    We don’t store intermediate state — only final JSON.
    """
    record = {
        "id": run_id,
        "webpage_id": organized_data.get("webpage_id"),
        "content_score": 0.75,
        "seo_score": 0.82,
        "performance_score": 0.68,
        "accessibility_score": 0.9,
        "review_text": "Sample analysis report – replace with generated text later.",
        "raw_data": organized_data,
        "created_at": datetime.utcnow(),
    }

    supabase.table("analysis_results").insert(record).execute()
