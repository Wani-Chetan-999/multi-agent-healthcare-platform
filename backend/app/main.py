import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Core configuration and database session layer
from app.core.config import settings
from app.models.base import Base
from app.database.session import async_engine
import app.models  # Ensures all models register onto Base.metadata

# Router Registries
from app.api.v1.auth import router as auth_router
from app.api.v1.chat import router as chat_router
from app.api.v1.medical import router as medical_router
from app.api.v1.orchestrator import router as orchestrator_router
from app.middleware.profiler import ClinicalLatencyProfilerMiddleware

from app.api.v1.orchestrator import router as orchestrator_router

# Setup technical logging framework
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# -------------------------------------------------------
# MODERN LIFESPAN MANAGER (Replaces @app.on_event)
# -------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown tasks.
    Replaces deprecated on_event decorators to prevent Starlette APIRouter TypeErrors.
    """
    # 🟢 STARTUP: Automatically construct user tables in PostgreSQL on boot
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Compliance Database schemas mapped successfully.")
    except Exception as e:
        logger.critical(f"Database table generation failed at startup: {str(e)}", exc_info=True)
        raise e

    yield  # ⏸️ Application executes incoming client loops here

    # 🔴 SHUTDOWN: Place any connection cleanup patterns here if needed
    logger.info("De-allocating operational clinical execution threads.")


# -------------------------------------------------------
# FASTAPI INSTANTIATION
# -------------------------------------------------------
app = FastAPI(
    title="Multi-Agent AI Healthcare Platform",
    version="1.0.0",
    description="Production-grade asynchronous AI core for automated clinical workflows.",
    lifespan=lifespan  # ✅ Correct modern deployment hooks
)
app.include_router(
    orchestrator_router,
    prefix="/api/v1/copilot",
    tags=["Clinical Copilot"]
)

# Apply CORS constraints for our frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------
# MIDDLEWARE ENGINE PIPELINE
# -------------------------------------------------------
@app.middleware("http")
async def audit_log_execution_duration(request: Request, call_next):
    """
    System middleware to calculate precision performance logs across agent executions.
    """
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"Route: {request.url.path} | Time Elapsed: {duration:.4f}s")
    return response

# Instantiate the custom latency profiler tracking framework
app.add_middleware(ClinicalLatencyProfilerMiddleware)

# -------------------------------------------------------
# GLOBAL EXCEPTION HANDLING LAYER
# -------------------------------------------------------
@app.exception_handler(Exception)
async def global_unhandled_exception_handler(request: Request, exc: Exception):
    """
    Catch-all crash safety net to prevent internal stack traces from leaking to public APIs.
    """
    logger.error(f"Critical unhandled system failure on route {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal unexpected server exception occurred. System triage is active."}
    )

# -------------------------------------------------------
# CORE APP ROUTING SCHEMES
# -------------------------------------------------------
@app.get("/health", status_code=status.HTTP_200_OK)
async def system_health_status_check():
    """
    Liveness and readiness checking endpoint for automated orchestrators or container deployments.
    """
    return {
        "status": "operational",
        "timestamp": time.time(),
        "platform": settings.PROJECT_NAME
    }

# Clean, structured router aggregation
app.include_router(orchestrator_router, prefix=f"{settings.API_V1_STR}/copilot", tags=["Unified Copilot Engine"])
app.include_router(orchestrator_router, prefix=f"{settings.API_V1_STR}/agentic", tags=["LangGraph Multi-Agent Engine"])
app.include_router(medical_router, prefix=f"{settings.API_V1_STR}/medical", tags=["Clinical Operations Engine"])
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(chat_router, prefix=f"{settings.API_V1_STR}/chat", tags=["AI Conversation Core"])


if __name__ == "__main__":
    import uvicorn
    # Using app.main:app ensures hot reloader works flawlessly on local file updates
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)