from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine
from app.api.categories import router as categories_router
from app.api.images import router as images_router
from app.api.items import router as items_router
from app.api.sources import router as sources_router
from app.schemas.health import HealthResponse
from app.llm.client import LLMClients
from app.scheduler.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: init LLM clients
    if settings.DEEPSEEK_API_KEY:
        app.state.llm = LLMClients.from_settings(settings)
        print("LLM clients initialized (DeepSeek)")
    else:
        print("Warning: DEEPSEEK_API_KEY not set — LLM pipeline disabled")
    # Start scheduler
    app.state.scheduler = start_scheduler()
    # Verify DB connection
    try:
        async with engine.connect() as conn:
            await conn.execute(
                __import__("sqlalchemy").text("SELECT 1")
            )
        print("Database connection established")
    except Exception as e:
        print(f"Warning: Database not available at startup: {e}")
    yield
    # Shutdown: scheduler, LLM clients, DB engine
    stop_scheduler(getattr(app.state, "scheduler", None))
    if hasattr(app.state, "llm"):
        await app.state.llm.close()
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
app.include_router(images_router)
app.include_router(categories_router)


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
