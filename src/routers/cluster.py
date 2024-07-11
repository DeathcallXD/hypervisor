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


from ..domains.cluster.schemas import (
    ClusterCreateRequest,
)

from ..domains.cluster.services import (
    ClusterService
)

from ..domains.cluster.repositories import (
    ClusterRepository
)


router = APIRouter()
logger = set_logger(__name__)


@router.post("/")
async def create_cluster(
    request_body: ClusterCreateRequest, 
    session: AsyncSession = Depends(get_async_session)
):
    name = request_body.name
    organisation_id = request_body.organisation_id
    user_id = request_body.user_id
    resources = request_body.resources
    description = request_body.description
    return await ClusterService(session).create_cluster(name, organisation_id, user_id, resources, description)

@router.get(
    "/{organisation_id}"
)
async def get_cluster_in_organisation( 
    organisation_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    return await ClusterRepository(session).get_cluster(None, {"organisation_id": organisation_id})

@router.get(
    "/{user_id}"
)
async def get_cluster_created_by_user( 
    user_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    return await ClusterRepository(session).get_cluster(None, {"user_id": user_id})