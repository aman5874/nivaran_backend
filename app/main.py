import logging
import time
import os
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config.settings import settings
from app.routers import generate_router, doctor_router
from app.utils.error_handlers import register_exception_handlers
from app.config.prompts import DEFAULT_SYSTEM_PROMPT
import datetime
now = datetime.datetime.now()
current_date = now.strftime("%d-%m-%Y")
current_time = now.strftime("%H:%M")
current_day = now.strftime("%A")

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)


# Create rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="Nivaran AI API",
    description=__doc__,
    version="0.1.0",
    docs_url="/docs" if os.environ.get("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.environ.get("ENVIRONMENT") != "production" else None
)

# Register exception handlers
register_exception_handlers(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add optimized request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    # Skip timing for non-API routes to reduce overhead
    if not request.url.path.startswith("/api/"):
        return await call_next(request)
        
    # Time the request processing
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Only add timing header for API routes
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Add health check endpoint
@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

# Include routers
app.include_router(generate_router)
app.include_router(doctor_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 