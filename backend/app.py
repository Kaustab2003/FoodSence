"""
FoodSense AI+ Backend
FastAPI Application

Main server entry point.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn
import os
from datetime import datetime

# Import routes
from routes.analyze_food import router as analyze_router
from routes.barcode_lookup import router as barcode_router
from routes.vision_extract import router as vision_router
from routes.nutrition_extract import router as nutrition_router

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["200/hour"])

# Initialize FastAPI app
app = FastAPI(
    title="FoodSense AI+ API",
    description="AI-Native Food Understanding Co-Pilot",
    version="1.0.0"
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware (allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup event - Validate environment
@app.on_event("startup")
async def validate_environment():
    """Validate required environment variables on startup."""
    required_vars = ["GOOGLE_API_KEY", "AI_PROVIDER"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        raise RuntimeError(f"❌ Missing required environment variables: {', '.join(missing)}")
    
    print("✅ Environment validated successfully")
    print(f"✅ AI Provider: {os.getenv('AI_PROVIDER')}")
    print(f"✅ AI Model: {os.getenv('AI_MODEL', 'default')}")


# Register routes
app.include_router(analyze_router, prefix="/api", tags=["Analysis"])
app.include_router(barcode_router, prefix="/api", tags=["Barcode"])
app.include_router(vision_router, prefix="/api", tags=["Vision"])
app.include_router(nutrition_router, prefix="/api/nutrition", tags=["Nutrition"])


@app.get("/")
async def root():
    """Root endpoint - Basic health check."""
    return {
        "message": "FoodSense AI+ API is running",
        "status": "healthy",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint.
    Used by Railway, Docker, and monitoring tools.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "environment": {
            "ai_provider": os.getenv("AI_PROVIDER", "unknown"),
            "ai_model": os.getenv("AI_MODEL", "unknown"),
            "python_version": os.sys.version.split()[0]
        },
        "services": {
            "api": "running",
            "gemini_vision": "ready" if os.getenv("GOOGLE_API_KEY") else "not_configured",
            "nutrition_analyzer": "ready",
            "vision_extractor": "ready"
        }
    }


@app.get("/api/health")
async def api_health():
    """API health check - alias for /health."""
    return await health_check()


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload during development
    )
