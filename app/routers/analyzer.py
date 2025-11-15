# app/routers/analyzer.py
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import HttpUrl
from uuid import UUID
from app.schemas import WebpageCreate, RunStatus, InternalRunState
from app.auth import verify_token
from app.services.accessibility.analytics.browser_to_json_parser import browser_to_json_parser
from app.services import state_manager
from app.utils.db_helpers import (
    upsert_webpage_record,
    create_run_record,
    update_run_status,
    update_webpage_status,
    save_run_result,
)

router = APIRouter()


@router.post("/webpages/analyze", response_model=dict)
async def analyze_webpage(
    payload: WebpageCreate,
    background_tasks: BackgroundTasks,
    user_id=Depends(verify_token),
):
    try:
        # 1. Upsert webpage
        webpage = await upsert_webpage_record(user_id, payload.url)

        # 2. Create run record in DB (this returns run with id)
        run = await create_run_record(user_id, webpage["id"])

        # 2.5 create in-memory state
        await state_manager.create_run_state(run["id"], webpage["id"], user_id)

        # 3. Kick off background parsing
        background_tasks.add_task(analyze_webpage_background, run["id"], webpage["id"], str(payload.url))

        # 4. Return initial status immediately
        return {"webpage_id": webpage["id"], "run_id": run["id"], "status": "pending"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


from app.services.accessibility.collector import run_extractors
from app.services.accessibility.analytics.runner import run_analyzers
from app.services.report_generator import generate_report

async def analyze_webpage_background(run_id: str, webpage_id: str, url: HttpUrl):
    try:
        await update_run_status(run_id, RunStatus.running)
        await update_webpage_status(webpage_id, RunStatus.running)
        await state_manager.set_running(UUID(run_id))

        raw_data = await fetch_page(str(url))
        extracted_data = run_extractors(raw_data["elements"])

        # 🧠 new part: run analyzers + generate report
        analyzer_results = run_analyzers(extracted_data)
        report = generate_report(analyzer_results)

        # You can store the report under `organized_data` or a separate key
        organized_data = {
            "summary": raw_data["summary"],
            "elements": raw_data["elements"],
            "analysis_report": report,
        }

        await save_run_result(run_id, organized_data)
        await update_run_status(run_id, RunStatus.completed)
        await update_webpage_status(webpage_id, RunStatus.completed)
        await state_manager.set_completed(UUID(run_id))

    except Exception as e:
        await update_run_status(run_id, RunStatus.failed, str(e))
        await update_webpage_status(webpage_id, RunStatus.failed)
        await state_manager.set_failed(UUID(run_id), str(e))



# --- endpoints to query in-memory state ----

@router.get("/runs/{run_id}", response_model=InternalRunState)
async def get_run_state(run_id: UUID, user_id=Depends(verify_token)):
    state = await state_manager.get_run_state(run_id, user_id)
    if not state:
        raise HTTPException(status_code=404, detail="Run not found or not yours")
    return state


@router.get("/webpages/{webpage_id}/runs", response_model=list[InternalRunState])
async def list_runs_for_webpage(webpage_id: UUID, user_id=Depends(verify_token)):
    return await state_manager.list_runs_for_webpage(webpage_id, user_id)

