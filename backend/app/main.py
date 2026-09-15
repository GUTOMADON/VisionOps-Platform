"""FastAPI application entrypoint for the VisionOps Platform backend."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import detections, health, inference, stats
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Computer vision monitoring platform for construction site safety detection.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Ensure every error response is a consistent {"detail": ...} JSON body."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


app.include_router(health.router, prefix=settings.api_v1_prefix)
app.include_router(inference.router, prefix=settings.api_v1_prefix)
app.include_router(detections.router, prefix=settings.api_v1_prefix)
app.include_router(stats.router, prefix=settings.api_v1_prefix)


@app.get("/", tags=["health"])
def root() -> dict:
    return {"service": settings.app_name, "docs": "/docs"}
