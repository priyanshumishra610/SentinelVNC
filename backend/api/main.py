"""
FastAPI main application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
from backend.config import settings
from backend.models.database import engine, Base, get_mongo_db
from backend.api.routes import auth as auth_router
from backend.api.routes import alerts as alerts_router
from backend.api.routes import users as users_router
from backend.api.routes import detection as detection_router
from backend.api.routes import websocket as websocket_router

# Create database tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    Base.metadata.create_all(bind=engine)
    # Initialize MongoDB indexes
    mongo_db = get_mongo_db()
    mongo_db.events.create_index("timestamp")
    mongo_db.events.create_index("event_type")
    mongo_db.forensic.create_index("alert_id")
    mongo_db.forensic.create_index("timestamp")
    yield
    # Shutdown
    pass


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Government-grade cybersecurity AI system for VNC data exfiltration detection",
    lifespan=lifespan
)

# Security middleware
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.sentinelvnc.local"]
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:3000"] if settings.DEBUG else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Include routers
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users_router.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(alerts_router.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(detection_router.router, prefix="/api/v1/detection", tags=["Detection"])
app.include_router(websocket_router.router, prefix="/api/v1/ws", tags=["WebSocket"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

