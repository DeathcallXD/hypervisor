from fastapi import APIRouter
from fastapi.responses import JSONResponse
from ..config import settings
from . import (
    organisation,
    user,
    cluster,
    deployment
)

router = APIRouter()

   
router.include_router(
    user.router,
    prefix=f"/user",
    tags=["User"],
)
router.include_router(
    organisation.router,
    prefix=f"/organisation",
    tags=["Organisation"],
)
router.include_router(
    cluster.router,
    prefix=f"/cluster",
    tags=["Cluster"],
)
router.include_router(
    deployment.router,
    prefix=f"/deployment",
    tags=["Deployment"],
)