"""
tests for api/main.py — middleware, CORS, and exception handling.
"""

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from unittest.mock  import patch
from fastapi.testclient import TestClient


# request logging middleware.
def test_request_logging_middleware_logs_requests(caplog):
    import logging
    from serving.main import app

    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="text_to_sql"):
        client.get("/health")

    log_messages = " ".join(caplog.messages)
    assert "GET" in log_messages
    assert "/health" in log_messages


def test_request_logging_middleware_logs_status_code(caplog):
    import logging
    from serving.main import app

    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="text_to_sql"):
        client.get("/health")

    log_messages = " ".join(caplog.messages)
    assert "200" in log_messages


# global exception handler.
def test_global_exception_handler_returns_clean_json():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from serving.main import global_exception_handler

    # create a minimal app that always raises
    test_app = FastAPI()
    test_app.add_exception_handler(Exception, global_exception_handler)

    @test_app.get("/boom")
    def boom():
        raise RuntimeError("something went badly wrong")

    client   = TestClient(test_app, raise_server_exceptions=False)
    response = client.get("/boom")

    assert response.status_code == 500
    data = response.json()
    assert data["status"] == "error"
    assert "error" in data


def test_global_exception_handler_does_not_leak_traceback():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from serving.main import global_exception_handler

    test_app = FastAPI()
    test_app.add_exception_handler(Exception, global_exception_handler)

    @test_app.get("/boom")
    def boom():
        raise RuntimeError("internal secret error message")

    client   = TestClient(test_app, raise_server_exceptions=False)
    response = client.get("/boom")

    body = response.text
    # traceback details should not appear in the response body
    assert "Traceback" not in body
    assert "internal secret error message" not in body


# CORS.

def test_cors_allows_all_origins_in_development():
    with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
        # reimport to pick up the env var
        import importlib
        import serving.main as main_module
        importlib.reload(main_module)

        client   = TestClient(main_module.app)
        response = client.get("/health", headers={"Origin": "http://random-site.com"})

        assert response.headers.get("access-control-allow-origin") in ("*", "http://random-site.com")


def test_cors_restricts_origins_in_production():
    with patch.dict(os.environ, {
        "ENVIRONMENT":   "production",
        "FRONTEND_URL":  "https://myapp.com",
    }):
        import importlib
        import serving.main as main_module
        importlib.reload(main_module)

        client   = TestClient(main_module.app)
        response = client.options(
            "/health",
            headers={
                "Origin":                        "https://evil-site.com",
                "Access-Control-Request-Method": "GET",
            },
        )

        allow_origin = response.headers.get("access-control-allow-origin", "")
        assert "evil-site.com" not in allow_origin


# docs visibility.

def test_docs_available_in_development():
    with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
        import importlib
        import serving.main as main_module
        importlib.reload(main_module)

        client   = TestClient(main_module.app)
        response = client.get("/docs")
        assert response.status_code == 200


def test_docs_hidden_in_production():
    with patch.dict(os.environ, {"ENVIRONMENT": "production", "FRONTEND_URL": "https://myapp.com"}):
        import importlib
        import serving.main as main_module
        importlib.reload(main_module)

        client   = TestClient(main_module.app)
        response = client.get("/docs")
        assert response.status_code == 404