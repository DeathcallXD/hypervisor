import json
from sqlalchemy.ext.asyncio import AsyncSession

from lib.http_exception_detail import HttpExceptionDetail
from lib.session_commit import SyncedCommit
from lib.logging_conf import set_logger

from utils.iac import PulumiUtils

from ..cluster.schemas import Resources
from .repositories import DeploymentRepository
from .constants import DeploymentStatus
from .utils.engine import DeploymentEngine

from ..cluster.repositories import ClusterRepository
from ..organisation.repositories import OrganisationRepository
from ..user.repositories import UserRepository

logger = set_logger(__name__)

class DeploymentService:
    def __init__(self, session: AsyncSession):
        self.session = session

        self.cluster_repo = ClusterRepository(session)
        self.org_repo = OrganisationRepository(session)
        self.user_repo = UserRepository(session)
        self.deployment_repo = DeploymentRepository(session)

        self.deployment_engine = DeploymentEngine()

        self.pulumi_utils = PulumiUtils()

        self.synced_commit = SyncedCommit(session)

    async def create_deployment(
        self, 
        name: str, 
        user_id: str, 
        cluster_id: str,
        priority: int,
        resources: Resources, 
        path_to_docker_image: str,
        description: str | None = None
    ):
        cluster = await self.cluster_repo.get_cluster(cluster_id, {})
        organisation_id = cluster.organisation_id

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

        deployment_status = DeploymentStatus.QUEUED.value
        deployment = await self.deployment_repo.create_deployment({
            "name": name,
            "description": description,
            "priority": priority,
            "cpu_allocated": resources.cpu_allocated,
            "memory_allocated": resources.memory_allocated,
            "path_to_docker_image": path_to_docker_image,
            "organisation_id": organisation.id,
            "cluster_id": cluster.id,
            "created_by": user.id,
            "status": deployment_status
        })

        self.deployment_engine._add_deployment_to_queue(
            cluster_id, 
            deployment.id, 
            priority, 
            resources.cpu_allocated,
            resources.memory_allocated, 
            deployment_status
        )

        await self.synced_commit.commit()
        return deployment
    
    async def _dequeue_deployment_manager_cluster(self, cluster_id: str):
        if not self.deployment_engine._is_cluster_locked(cluster_id):
            deployment_ids = self.deployment_engine._predict_deployments_to_deploy(cluster_id)

            for deployment_id in deployment_ids:
                try:
                    deployment = await self.deployment_repo.get_deployment(deployment_id, {})
                    if deployment.status != DeploymentStatus.QUEUED.value:
                        continue

                    resources = Resources(
                        cpu_allocated=deployment.cpu_allocated,
                        memory_allocated=deployment.memory_allocated
                    )
                    organisation_id = deployment.organisation_id

                    deployment_details = await self.pulumi_utils.create_deployment(
                        organisation_id=organisation_id, 
                        cluster_id=cluster_id, 
                        deployment_id=deployment_id,
                        resources=resources,
                        path_to_docker_image=deployment.path_to_docker_image
                    )
                    
                    await self.deployment_repo.update_deployment(deployment.id, {
                        "status": DeploymentStatus.DEPLOYED.value,
                        "notes": json.dumps(deployment_details.__dict__)
                    })

                    self.deployment_engine._remove_deployment_from_queue(cluster_id, deployment_id)
                except Exception as e:
                    logger.error(f"Error in _dequeue_deployment: {e}")
            
            await self.synced_commit.commit()

        else:
            logger.info(f"Cluster: {cluster_id} is locked, not processing deployment")


    async def _dequeue_deployment(self):
        locked_cluster_ids = self.deployment_engine._get_locked_clusters()

        queued_cluster_ids = await self.deployment_repo.get_available_clusters(locked_cluster_ids)
        for cluster_id in queued_cluster_ids:
            await self._dequeue_deployment_manager_cluster(cluster_id)