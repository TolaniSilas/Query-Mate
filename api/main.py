"""
fastapi application entry point.
registers all routers, middleware, and global exception handling.

run with:
    uvicorn api.main:app --reload --port 8000
"""

import os
import time
import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.routes import connection, query, schema
from api.schemas.models import HealthResponse
from querymate.core.logger import get_logger


logger = get_logger(__name__)

VERSION     = "1.0.0"
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development").lower()


app = FastAPI(
    title       = "QueryMate API",
    description = "natural language interface for relational databases.",
    version     = VERSION,
    # hide docs in production
    docs_url    = "/docs" if ENVIRONMENT == "development" else None,
    redoc_url   = "/redoc" if ENVIRONMENT == "development" else None,
)


# cors for locked frontend domain in production.
allowed_origins = (
    ["*"] if ENVIRONMENT == "development"
    else [os.environ.get("FRONTEND_URL", "")]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = allowed_origins,
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)


# request logging middleware, this logs method, path, status, and response time.
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = (time.perf_counter() - start) * 1000

    logger.info(
        "api | %s %s --> %d | %.1fms",
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )
    return response


# global exception handler for preventing internal details leaking in 500 responses.
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "api | unhandled exception | %s %s | %s",
        request.method,
        request.url.path,
        traceback.format_exc(),
    )
    return JSONResponse(
        status_code = 500,
        content     = {
            "status": "error",
            "error":  "An unexpected error occurred. Please try again or contact support.",
        },
    )


# routers.
app.include_router(connection.router, prefix="/api", tags=["connection"])
app.include_router(query.router, prefix="/api", tags=["query"])
app.include_router(schema.router, prefix="/api", tags=["schema"])


# health check.
@app.get("/health", response_model=HealthResponse, tags=["health"])
def health_check():
    return HealthResponse(status="ok", version=VERSION)