from datetime import datetime
from uuid import uuid4
from app.database.supabase_client import supabase


# ------------------------------
# Helper: sanitize any DB record
# ------------------------------

def sanitize_record(record: dict) -> dict:
    """Convert all datetime fields to ISO strings."""
    sanitized = {}
    for key, val in record.items():
        if isinstance(val, datetime):
            sanitized[key] = val.isoformat()
        else:
            sanitized[key] = val
    return sanitized


async def upsert_webpage_record(user_id: str, url: str) -> dict:
    """
    Insert a webpage if it doesn't exist, or return existing one.
    Only JSON-safe dict is returned.
    'analyzed_at' is set only on insert, not updated here.
    """
    url_str = str(url)
    now_str = datetime.utcnow().isoformat()

    # Fetch existing record
    res = supabase.table("webpages").select("*").eq("user_id", user_id).eq("url", url_str).execute()
    if res.data and len(res.data) > 0:
        record = res.data[0]
        return sanitize_record(record)

    # Insert new record
    new_record = {
        "id": str(uuid4()),
        "user_id": user_id,
        "url": url_str,
        "created_at": now_str,
        "analyzed_at": now_str,  # initialize on insert
    }
    insert_res = supabase.table("webpages").insert(new_record).execute()
    record = insert_res.data[0]

    return sanitize_record(record)


async def update_run_status(run_id: str, status, error_message: str | None = None):
    """
    No DB action – state tracking handled in-memory.
    Just a stub for consistency.
    """
    # In-memory updates happen elsewhere (e.g., RunStateManager)
    return {"run_id": run_id, "status": status.value, "error": error_message}


async def update_webpage_status(webpage_id: str, status):
    """
    Optionally mark the webpage as recently analyzed.
    Updates analyzed_at timestamp safely as ISO string.
    """
    now_str = datetime.utcnow().isoformat()
    supabase.table("webpages").update({
        "analyzed_at": now_str
    }).eq("id", webpage_id).execute()


# ------------------------------
# Results
# ------------------------------
async def create_run_record(user_id: str, webpage_id: str) -> dict:
    """Create a JSON-safe in-memory run record."""
    run_id = str(uuid4())
    return {
        "id": run_id,
        "user_id": str(user_id),
        "webpage_id": str(webpage_id),
        "created_at": datetime.utcnow().isoformat(),
    }


# ------------------------------
# Save analysis result
# ------------------------------
async def save_run_result(run_id: str, organized_data: dict):
    """
    Store final analysis result in Supabase.
    All datetime values converted to ISO string.
    """
    now_str = datetime.utcnow().isoformat()
    record = {
        "id": run_id,
        "webpage_id": organized_data.get("webpage_id"),
        "content_score": 0.75,
        "seo_score": 0.82,
        "performance_score": 0.68,
        "accessibility_score": 0.9,
        "review_text": "Sample analysis report – replace with generated text later.",
        "raw_data": organized_data,
        "created_at": now_str,
    }

    supabase.table("analysis_results").insert(record).execute()
