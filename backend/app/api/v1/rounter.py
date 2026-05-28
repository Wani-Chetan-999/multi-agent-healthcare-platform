from fastapi import APIRouter
from app.api.v1 import auth
from app.api.v1 import orchestrator  # Our new unified copilot router module

api_router = APIRouter()

# 1. Keep your secure authorization entry endpoints intact
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# 2. Wire up the new multi-turn conversational core mapping
api_router.include_router(orchestrator.router, prefix="/copilot", tags=["Unified Copilot Engine"])

# ❌ REMOVE OR COMMENT OUT THESE CORES TO PREVENT COLLISION DISPATCHES:
# api_router.include_router(chat.router, prefix="/chat", tags=["Legacy Chat"])
# api_router.include_router(medical.router, prefix="/medical", tags=["Legacy Tools"])