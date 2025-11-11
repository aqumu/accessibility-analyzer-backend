import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import bookmarks, users, analyzer
from app.utils.playwright_utils import startup_browser, shutdown_browser

app = FastAPI(title="Bookmark Tracker API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://accessibility-analyzer.ru",
        "https://api.accessibility-analyzer.ru"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(bookmarks.router, prefix="/api/bookmarks", tags=["bookmarks"])
app.include_router(analyzer.router, prefix="/api/analyzer", tags=["analyzer"])

@app.on_event("startup")
async def on_startup():
    await startup_browser()

@app.on_event("shutdown")
async def on_shutdown():
    await shutdown_browser()