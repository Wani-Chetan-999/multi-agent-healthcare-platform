import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("app.telemetry")
logging.basicConfig(level=logging.INFO)

class ClinicalLatencyProfilerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """
        Intersects the incoming request context, calculates execution latency, 
        and prints real-time telemetry markers to the logging console.
        """
        start_time = time.perf_counter()
        
        # Process the downstream pipeline operations
        response = await call_next(request)
        
        process_time = time.perf_counter() - start_time
        # Convert to milliseconds for clean readability
        latency_ms = process_time * 1000.0
        
        logger.info(
            f"📡 TELEMETRY PROFILE: Method={request.method} "
            f"Path={request.url.path} "
            f"Latency={latency_ms:.2f}ms "
            f"Status={response.status_code}"
        )
        
        # Inject performance telemetry headers into the outgoing response object
        response.headers["X-Process-Latency-MS"] = f"{latency_ms:.2f}"
        return response