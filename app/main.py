from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine
from app.api.items import router as items_router
from app.api.sources import router as sources_router
from app.schemas.health import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: verify DB connection
    try:
        async with engine.connect() as conn:
            await conn.execute(
                __import__("sqlalchemy").text("SELECT 1")
            )
        print("Database connection established")
    except Exception as e:
        print(f"Warning: Database not available at startup: {e}")
    yield
    # Shutdown: dispose engine
    await engine.dispose()


app = FastAPI(
    title="AI Pulse API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items_router)
app.include_router(sources_router)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    db_ok = False
    try:
        async with engine.connect() as conn:
            await conn.execute(
                __import__("sqlalchemy").text("SELECT 1")
            )
            db_ok = True
    except Exception:
        pass
    return {
        "status": "ok",
        "version": "0.1.0",
        "database": "connected" if db_ok else "disconnected",
    }
