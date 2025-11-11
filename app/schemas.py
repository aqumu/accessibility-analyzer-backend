from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum
from uuid import UUID



# ----------------------------
# Base user models
# ----------------------------


class UserBase(BaseModel):
    """Shared user properties."""

    public_name: Optional[str] = None


class UserCreate(UserBase):
    """Used for creating a user profile (optional if using Supabase Auth)."""

    pass


class UserUpdate(BaseModel):
    """Used for profile editing via /users/me PUT."""

    public_name: Optional[str] = Field(None, max_length=50)


class UserResponse(BaseModel):
    id: str
    public_name: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ----------------------------
# Stats and quota
# ----------------------------


class UserStats(BaseModel):
    """Bookmark statistics returned by /users/stats."""

    total_bookmarks: int
    today_bookmarks: int
    last_activity: Optional[datetime]


class UserQuota(BaseModel):
    """Daily quota info."""

    daily_limit: int
    used_today: int
    remaining: int


# -------------------------------------
# ENUMS
# -------------------------------------
class WebpageStatus(str, Enum):
    pending = "pending"
    analyzing = "analyzing"
    completed = "completed"
    failed = "failed"


class RunStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


# -------------------------------------
# EXISTING ELEMENT MODELS (YOURS)
# -------------------------------------
class ElementAttributes(BaseModel):
    alt: Optional[str] = None
    title: Optional[str] = None
    tabindex: Optional[str] = None


class ElementVisibility(BaseModel):
    display: Optional[str] = None
    visibility: Optional[str] = None


class ElementColors(BaseModel):
    text: Optional[str] = None
    background: Optional[str] = None


class ElementData(BaseModel):
    tag: str
    id: Optional[str] = None
    class_: Optional[str] = None
    role: Optional[str] = None
    aria: Dict[str, Optional[str]] = {}
    attributes: ElementAttributes
    visibility: ElementVisibility
    colors: ElementColors
    text: Optional[str] = None

    class Config:
        fields = {"class_": "class"}


class PageSummary(BaseModel):
    total_elements: int
    interactive_elements: int


class PageData(BaseModel):
    url: HttpUrl
    summary: PageSummary
    elements: List[ElementData]


# -------------------------------------
# NEW: DATABASE + API MODELS
# -------------------------------------
class WebpageBase(BaseModel):
    url: HttpUrl


class WebpageCreate(WebpageBase):
    pass


class WebpageInDB(WebpageBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    last_run_id: Optional[UUID] = None
    status: WebpageStatus

    class Config:
        orm_mode = True


class RunBase(BaseModel):
    webpage_id: UUID
    status: RunStatus = RunStatus.pending
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error_message: Optional[str] = None


class RunInDB(RunBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


# -------------------------------------
# RESULTS / RESPONSES
# -------------------------------------
class RunResult(BaseModel):
    summary: Optional[PageSummary]
    elements: Optional[List[ElementData]]


class RunDetail(RunInDB):
    result: Optional[RunResult]


class WebpageDetail(WebpageInDB):
    last_run: Optional[RunDetail]


# -------------------------------------
# LIST RESPONSES
# -------------------------------------
class WebpageListItem(BaseModel):
    id: UUID
    url: HttpUrl
    status: WebpageStatus
    last_run_status: Optional[RunStatus]
    last_run_finished_at: Optional[datetime]
    summary: Optional[PageSummary]


class WebpageListResponse(BaseModel):
    items: List[WebpageListItem]


class RunListItem(BaseModel):
    id: UUID
    webpage_id: UUID
    status: RunStatus
    started_at: Optional[datetime]
    finished_at: Optional[datetime]


class RunListResponse(BaseModel):
    items: List[RunListItem]


class InternalRunState(BaseModel):
    run_id: UUID
    webpage_id: UUID
    user_id: UUID
    status: RunStatus
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error_message: Optional[str] = None

