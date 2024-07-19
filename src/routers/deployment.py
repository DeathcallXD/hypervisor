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


from ..domains.deployment.schemas import (
    DeploymentCreateRequest,
)

from ..domains.deployment.services import (
    DeploymentService
)

from ..domains.deployment.repositories import (
    DeploymentRepository
)

router = APIRouter()
logger = set_logger(__name__)


@router.post("/")
async def create_deployment(
    request_body: DeploymentCreateRequest, 
    session: AsyncSession = Depends(get_async_session)
):
    return await DeploymentService(session).create_deployment(request_body)