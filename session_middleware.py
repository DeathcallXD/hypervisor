from lib.http_exception_detail import HttpExceptionDetail
from typing import Any, Callable
from fastapi import Response, Request
import json
from lib.redis import RedisManager
from lib.logging_conf import set_logger
from lib.http_exception_detail import HttpExceptionDetail
from src.config import settings
from src.domains.user.utils import LoginUtils

from datetime import datetime

REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT
REDIS_PASSWORD = settings.REDIS_PASSWORD


logger = set_logger(__name__)


async def SessionMiddleware(request: Request, call_next: Callable, some_attribute: Any) -> Response: 
    # get request params required for authentication and authorization
    request_host = request.headers["HOST"]
    request_path = request.url.path
    request_method = request.method
    session_id = request.headers.get("session-id")
    user_id = request.headers.get("user-id")
    origin = request.headers.get("Origin")
    ip = request.headers.get('x-forwarded-for')
    if ip:
        ip = ip.split(":")[0]
    else:
        ip = request.client.host

    logger.debug(f"{request_host = }, {request_method = }, {request_path = }, {session_id = }, {user_id = }, {origin = }")
    logger.debug(f"............................ request ip: {ip} for user_id: {user_id} and session_id: {session_id} ............................")

    # # bypass on localhost  CAN BE UNCOMMENTED IF REQRUIED TO BE TESTED LOCALLY
    if ("localhost" in request_host or "127.0.0.1" in request_host ):
        logger.debug("session bypassed when running locally")
        return await call_next(request)
    
    if (
        ("/user/login" == request_path) or
        ("/user" == request_path and request_method == "POST")
    ):
        logger.info("API for document uploading is bypassed, as it is not required")
        return await call_next(request)
    
    if not LoginUtils().verify_session(user_id, session_id):
        logger.debug("session is valid")
        raise HttpExceptionDetail(
            status_code=401, 
            message="Invalid session", 
            error_code="S401"
        )

    return await call_next(request)