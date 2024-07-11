import json
from sqlalchemy.ext.asyncio import AsyncSession

from lib.http_exception_detail import HttpExceptionDetail
from lib.session_commit import SyncedCommit
from lib.logging_conf import set_logger

from utils.iac import PulumiUtils

from .schemas import Resources
from .repositories import ClusterRepository

from ..deployment.repositories import DeploymentRepository
from ..organisation.repositories import OrganisationRepository
from ..user.repositories import UserRepository

from ..deployment.utils.engine import DeploymentEngine

logger = set_logger(__name__)

class ClusterService:
    def __init__(self, session: AsyncSession):
        self.session = session

        "Repositories"
        self.cluster_repo = ClusterRepository(session)
        self.org_repo = OrganisationRepository(session)
        self.user_repo = UserRepository(session)
        self.deployment_repo = DeploymentRepository(session)

        "Deployment Engine"
        self.deployment_engine = DeploymentEngine()
        
        "IaC Utils"
        self.pulumi_utils = PulumiUtils()

        self.synced_commit = SyncedCommit(session)

    async def create_cluster(
        self, 
        name: str, 
        organisation_id: str, 
        user_id: str, 
        resources: Resources, 
        description: str | None = None
    ):

        organisation = await self.org_repo.get_organisation(organisation_id, {})
        user = await self.user_repo.get_user(user_id, {})

        if not organisation or not user:
            logger.error(f"Organisation or user not found")
            raise HttpExceptionDetail(
                status_code=404,
                message="Organisation or user not found",
                error_code="E0001"
            )
        
        if user.organisation_id != organisation_id:
            logger.error(f"User is not part of the organisation")
            raise HttpExceptionDetail(
                status_code=403,
                message="User is not part of the organisation",
                error_code="E0002"
            )

        cluster = await self.cluster_repo.create_cluster({
            "name": name,
            "description": description,
            "cpu_allocated": resources.cpu_allocated,
            "memory_allocated": resources.memory_allocated,
            "organisation_id": organisation.id,
            "created_by": user.id
        })

        """
            Creating a stack only when an organisation demands their first stack,
            to save unnecessary infra cost
        """
        if not self.pulumi_utils.is_stack_exists(organisation_id):
            await self.pulumi_utils.create_stack(organisation_id)

        cluster_details = await self.pulumi_utils.create_cluster(organisation_id, cluster.id, resources)

        self.deployment_engine._add_free_resource_to_map(
            cluster.id, resources.cpu_allocated, resources.memory_allocated
        )

        await self.cluster_repo.update_cluster(cluster.id, {
            "notes": json.dumps(cluster_details.__dict__)
        })

        await self.synced_commit.commit()
        return cluster