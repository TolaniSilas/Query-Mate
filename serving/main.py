"""
main.py - FASTAPI application for QueryMate serving.
"""

import time
import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from serving.routes import query
from serving.schemas.models import HealthResponse
from querymate.core.logger import get_logger


logger = get_logger(__name__)
VERSION = "1.0.0"


app = FastAPI(
    title = "QueryMate Serving",
    description = "natural language interface for relational databases.",
    version = VERSION,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """log all incoming requests with method, path, status code, and duration."""

    start_time = time.perf_counter()
    response = await call_next(request)
    end_time = time.perf_counter()

    duration = (end_time - start_time) * 1000

    logger.info("serving | %s %s --> %d | %.1fms", request.method, request.url.path, response.status_code, duration)

    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("serving | unhandled exception | %s %s | %s", request.method, request.url.path, traceback.format_exc())

    return JSONResponse(
        status_code = 500,
        content = {
            "status": "error",
            "error": "An unexpected error occurred. Please try again or contact support.",
        }
    )


app.include_router(query.router, prefix="/serving", tags=["query"])


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health_check():
    return HealthResponse(status="ok", version=VERSION)








# run with: uvicorn serving.main:app --reload --port 8000