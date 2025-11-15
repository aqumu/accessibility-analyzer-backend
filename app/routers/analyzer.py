from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from uuid import UUID
from fastapi.encoders import jsonable_encoder
from app.schemas import WebpageCreate, RunStatus, InternalRunState
from app.database.auth import verify_token
from app.services import state_manager
from app.database.db_helpers import (
    upsert_webpage_record,
    create_run_record,
    update_run_status,
    update_webpage_status,
)
from app.services.analytics.browser_to_json_parser.browser_to_json_parser import parse_url
from app.services.analytics.json_parser.models import DocumentFactory
# from app.services.analytics.rules_analyzer.analyzer import
from app.services.report_generator import generate_report
import pprint
from pydantic import BaseModel, HttpUrl


router = APIRouter()

# ============================================================
#                PUBLIC ENDPOINT: START ANALYSIS
# ============================================================

@router.post("/webpages/analyze", response_model=dict)
async def analyze_webpage(
    payload: WebpageCreate,
    background_tasks: BackgroundTasks,
    user_id=Depends(verify_token),
):
    try:
        # 1. Upsert webpage (JSON-safe)
        webpage = await upsert_webpage_record(user_id, payload.url)

        # 2. Create in-memory run record
        run = await create_run_record(user_id, webpage["id"])

        # 3. Initialize in-memory state
        await state_manager.create_run_state(run["id"], webpage["id"], user_id)

        # 4. Start background analysis task
        background_tasks.add_task(
            analyze_webpage_background,
            run_id=run["id"],
            webpage_id=webpage["id"],
            url=str(payload.url),
        )

        # 5. Return JSON-safe response
        return jsonable_encoder({
            "webpage_id": webpage["id"],
            "run_id": run["id"],
            "status": "pending",
        })

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================
#          BACKGROUND EXECUTION: NEW PARSER PIPELINE
# ============================================================

async def analyze_webpage_background(
    run_id: str,
    webpage_id: str,
    url: HttpUrl,
):
    try:
        # Mark running
        await update_run_status(run_id, RunStatus.running)
        await update_webpage_status(webpage_id, RunStatus.running)
        await state_manager.set_running(UUID(run_id))

        # 1. Parse webpage into raw structured DOM JSON (in-memory only)
        raw_json = await parse_url(str(url))

        if raw_json is None:
            raise RuntimeError("Parser returned None (URL unreachable or invalid).")

        # 2. Convert to DocumentModel
        document = DocumentFactory.load_from_json(raw_json)

        # 3. Run analyzers
        # analyzer_results = run_model_analyzers(document)

        # 4. Generate report for frontend
        # report = generate_report(analyzer_results)

        # 5. Store ONLY the report in DB
        # save_payload = {
        #     "analysis_report": report,
        # }

        # await save_run_result(run_id, save_payload)

        # Mark completed
        await update_run_status(run_id, RunStatus.completed)
        await update_webpage_status(webpage_id, RunStatus.completed)
        await state_manager.set_completed(UUID(run_id))

    except Exception as e:
        await update_run_status(run_id, RunStatus.failed, str(e))
        await update_webpage_status(webpage_id, RunStatus.failed)
        await state_manager.set_failed(UUID(run_id), str(e))



# ============================================================
#                    IN-MEMORY RUN STATE
# ============================================================

@router.get("/runs/{run_id}", response_model=InternalRunState)
async def get_run_state(run_id: UUID, user_id=Depends(verify_token)):
    state = await state_manager.get_run_state(run_id, user_id)
    if not state:
        raise HTTPException(status_code=404, detail="Run not found or not yours")
    return state


@router.get("/webpages/{webpage_id}/runs", response_model=list[InternalRunState])
async def list_runs_for_webpage(webpage_id: UUID, user_id=Depends(verify_token)):
    return await state_manager.list_runs_for_webpage(webpage_id, user_id)
