import os
import requests
from functools import partial
from typing import Any, Coroutine
from datetime import datetime

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from starlette.exceptions import (
    HTTPException as StarletteHTTPException,  # pants: no-infer-dep
)

from session_middleware import SessionMiddleware
from src.config import settings
from src.handlers.error import ExceptionHandler
from src.internal import admin
from src.routers.api import router as router_api
from security_header_middleware import SecurityHeadersMiddleware


def get_application() -> FastAPI:
    """Configure, start and return the application."""

    application = FastAPI(
        docs_url="/backend/docs",
        openapi_url="/backend/documentation",
        redoc_url="/backend/openapi.json",
    )

    # including all the api routes
    application.include_router(
        router_api,
        prefix=f"/backend",
    )

    # handle startelette http exception
    @application.exception_handler(StarletteHTTPException)
    async def custom_exception_handler(request, exc):
        return await ExceptionHandler.handle_exception(request, exc)

    # handle pydantic exception
    @application.exception_handler(RequestValidationError)
    async def custom_exception_handler(request, exc):
        return await ExceptionHandler.handle_exception(request, exc)

    # handle any other exception
    @application.exception_handler(Exception)
    async def custom_exception_handler(request, exc):
        return await ExceptionHandler.handle_exception(request, exc)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    include_csp = False
    # if ENV.lower() == 'prod':
    #     include_csp = True
    application.add_middleware(SecurityHeadersMiddleware, csp=include_csp)

    session_middleware: partial[Coroutine[Any, Any, Any]] = partial(
        SessionMiddleware, some_attribute="my-app"
    )
    application.middleware("http")(session_middleware)

    return application


app = get_application()


@app.get("/docs", include_in_schema=False)
async def override_swagger():
    return get_swagger_ui_html(
        openapi_url="/backend/openapi.json",
        title="API docs",
        swagger_js_url="/static/swagger-ui-bundle.js",
    )

import uvicorn
if __name__ == "__main__":
    uvicorn.run("mewt_backend.main:app", port=1212, host="127.0.0.1")
