import json
import requests
from sqlalchemy import select, and_, func
from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import any_, or_
from datetime import datetime, timedelta


from lib.logging_conf import set_logger
from lib.generate_new_id import generate_new_id
from lib.http_exception_detail import HttpExceptionDetail
from ..dependencies import get_async_session


from ..domains.user.schemas import (
    UserCreateRequest,
    UserCreateResponse,
    UserLoginRequest,
    UserLoginResponse,
)

from ..domains.user.services import (
    UserService,
)

from ..domains.user.repositories import UserRepository


router = APIRouter()
logger = set_logger(__name__)


@router.post(
    "/",
    response_model=UserCreateResponse
)
async def create_user(
    request_body: UserCreateRequest, 
    session: AsyncSession = Depends(get_async_session)
):
    return await UserService(session).create_user(request_body)


@router.get(
    "/{user_id}"
)
async def get_user( 
    user_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    return await UserRepository(session).get_user(user_id, {})


@router.post(
    "/login",
    response_model=UserLoginResponse
)
async def login(
    request_body: UserLoginRequest, 
    session: AsyncSession = Depends(get_async_session)
):
    return await UserService(session).login(request_body)