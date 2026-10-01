from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .database import Base, SessionLocal, engine
from .seed import seed_products
from .routers import store, ai
ROOT=Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(bind=engine)
    db=SessionLocal()
    try: seed_products(db)
    finally: db.close()
    yield
app=FastAPI(title="Samay Sutra API",version="2.0.0",lifespan=lifespan)
allowed_origins = [origin.strip() for origin in __import__("os").getenv("FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")]
# Vite can choose a nearby local port if 5173 is busy. Allow any localhost
# development port, while keeping explicitly configured production origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(store.router); app.include_router(ai.router)
app.mount("/static",StaticFiles(directory=ROOT / "static"),name="static")
@app.get("/", include_in_schema=False)
def api_root():
    """Keep the API root explicit: the React UI is intentionally not served here."""
    return {
        "service": "Samay Sutra FastAPI backend",
        "message": "Backend is running. Start the React frontend with `cd frontend; npm run dev` and open http://localhost:5173.",
        "docs": "/docs",
    }
@app.get("/health")
def health(): return {"status":"ok"}
