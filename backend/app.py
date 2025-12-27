"""
FoodSense AI+ Backend
FastAPI Application

Main server entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import routes
from routes.analyze_food import router as analyze_router
from routes.barcode_lookup import router as barcode_router

# Initialize FastAPI app
app = FastAPI(
    title="FoodSense AI+ API",
    description="AI-Native Food Understanding Co-Pilot",
    version="1.0.0"
)

# CORS middleware (allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(analyze_router, prefix="/api", tags=["Analysis"])
app.include_router(barcode_router, prefix="/api", tags=["Barcode"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "FoodSense AI+ API is running",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "services": {
            "api": "running",
            "intent_engine": "ready",
            "reasoning_engine": "ready",
            "explanation_generator": "ready"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload during development
    )
