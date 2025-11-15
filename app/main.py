from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import bookmarks, users, analyzer

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