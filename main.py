"""
Main FastAPI Application for Digital Library Assistant.
Third-Year Computer Engineering AI Course CI3 Project.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import os

from app.database import init_db
from app.seed_data import seed_database_if_empty
from app.routes.chat import router as chat_router
from app.routes.books import router as books_router
from app.routes.info import router as info_router
from app.routes.admin import router as admin_router, auth_router
from app.routes.diagnostics import router as diag_router

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="Digital Library Assistant API",
    description="Intelligent Conversational Library Assistant for College of Engineering",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event: ensure database schema and seed data are loaded
@app.on_event("startup")
def on_startup():
    print("[STARTUP] Initializing database schema...")
    init_db()
    print("[STARTUP] Checking and seeding database records...")
    seed_database_if_empty()
    print("[STARTUP] Digital Library Assistant ready!")

# Include API Routers
app.include_router(chat_router)
app.include_router(books_router)
app.include_router(info_router)
app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(diag_router)

# Mount static assets
if not STATIC_DIR.exists():
    STATIC_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/health")
def health_check():
    return {"status": "ok", "app": "Digital Library Assistant", "version": "1.0.0"}

@app.get("/")
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "Digital Library Assistant API is running. Static frontend not yet compiled."}
