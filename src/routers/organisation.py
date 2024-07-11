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

from ..domains.organisation.schemas import (
    OrganisationCreateRequest,
    OrganisationCreateResponse,
    UserOrganisationJoinRequest
)

from ..domains.organisation.services import (
    OrganisationService
)

from ..domains.organisation.repositories import (
    OrganisationRepository
)

from ..domains.user.repositories import (
    UserRepository
)


router = APIRouter()
logger = set_logger(__name__)


@router.post(
    "/",
    response_model=OrganisationCreateResponse
)
async def create_organisation(
    request_body: OrganisationCreateRequest, 
    session: AsyncSession = Depends(get_async_session)
):
    name = request_body.name
    description = request_body.description
    logo_url = request_body.logo_url
    user_id = request_body.user_id
    return await OrganisationService(session).create_organisation(user_id, {"name": name, "description": description, "logo_url": logo_url})

@router.get(
    "/{organisation_id}",
)
async def get_organisation( 
    organisation_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    return await OrganisationRepository(session).get_organisation(organisation_id, {})

@router.get(
    "/users/{organisation_id}"
)
async def get_users_in_organisation( 
    organisation_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    return await UserRepository(session).get_users({"organisation_id": organisation_id})

@router.patch(
    "/join",
)
async def join_organisation( 
    request_body: UserOrganisationJoinRequest,
    session: AsyncSession = Depends(get_async_session)
):
    ivt_code = request_body.invite_code
    user_id = request_body.user_id
    return await OrganisationService(session).join_organisation(user_id, ivt_code)