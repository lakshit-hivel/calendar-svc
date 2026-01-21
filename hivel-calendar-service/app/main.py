"""
Hivel Calendar Service - Main FastAPI Application
Google Calendar integration via Marketplace app.
"""

from fastapi import FastAPI
from app.api.routes import router

# Create FastAPI app
app = FastAPI(
    title="Hivel Calendar Service",
    description="Google Calendar integration via Marketplace",
    version="1.0.0"
)

# Include routes
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    print("🚀 Hivel Calendar Service starting...")
    print("📅 Google Calendar Marketplace integration ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    print("👋 Hivel Calendar Service shutting down...")


# For running with: python -m app.main
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
