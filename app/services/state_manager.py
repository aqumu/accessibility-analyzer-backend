# app/services/state_manager.py
from typing import Dict, Optional, List
import asyncio
from datetime import datetime
from uuid import UUID
from app.schemas import InternalRunState, RunStatus

_state: Dict[str, InternalRunState] = {}
_lock = asyncio.Lock()


async def create_run_state(run_id: UUID, webpage_id: UUID, user_id: UUID) -> InternalRunState:
    async with _lock:
        state = InternalRunState(
            run_id=run_id,
            webpage_id=webpage_id,
            user_id=user_id,
            status=RunStatus.pending,
            started_at=None,
            finished_at=None,
            error_message=None,
        )
        _state[str(run_id)] = state
        return state


async def set_running(run_id: UUID) -> Optional[InternalRunState]:
    async with _lock:
        key = str(run_id)
        state = _state.get(key)
        if state:
            state.status = RunStatus.running
            state.started_at = datetime.utcnow()
            state.error_message = None
        return state


async def set_completed(run_id: UUID) -> Optional[InternalRunState]:
    async with _lock:
        key = str(run_id)
        state = _state.get(key)
        if state:
            state.status = RunStatus.completed
            state.finished_at = datetime.utcnow()
        return state


async def set_failed(run_id: UUID, error: Optional[str] = None) -> Optional[InternalRunState]:
    async with _lock:
        key = str(run_id)
        state = _state.get(key)
        if state:
            state.status = RunStatus.failed
            state.finished_at = datetime.utcnow()
            state.error_message = error
        return state


async def get_run_state(run_id: UUID, user_id: UUID) -> Optional[InternalRunState]:
    async with _lock:
        state = _state.get(str(run_id))
        if state and state.user_id == user_id:
            return state
        return None


async def list_runs_for_webpage(webpage_id: UUID, user_id: UUID) -> List[InternalRunState]:
    async with _lock:
        return [s for s in _state.values() if s.webpage_id == webpage_id and s.user_id == user_id]


async def list_runs_for_user(user_id: UUID) -> List[InternalRunState]:
    async with _lock:
        return [s for s in _state.values() if s.user_id == user_id]


async def cleanup_finished_older_than(hours: int = 24) -> None:
    """Optional cleanup helper."""
    import datetime as dt
    cutoff = datetime.utcnow() - dt.timedelta(hours=hours)
    async with _lock:
        for key, state in list(_state.items()):
            if state.finished_at and state.finished_at < cutoff:
                del _state[key]
