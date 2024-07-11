from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from lib.generate_new_id import generate_new_id

from .constants import DeploymentStatus
from .models import Deployment

class DeploymentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_deployment(self, id: int, filters: dict) -> Deployment:
        query_filters = [getattr(Deployment, key) == value for key, value in filters.items()]
        if not id:
            get_deployment = await self.session.execute(select(Deployment).filter(*query_filters))
            deployment: Deployment = get_deployment.scalars().first()
        else:
            get_deployment = await self.session.execute(
                select(Deployment).filter(Deployment.id == id).filter(*query_filters)
            )
            deployment: Deployment = get_deployment.scalars().first()

        return deployment
    
    async def create_deployment(self, values: dict) -> Deployment:
        next_id = generate_new_id(Deployment)
        deployment = Deployment(**values, id=next_id)
        self.session.add(deployment)

        return deployment
    
    async def update_deployment(self, id: int, values: dict) -> Deployment:
        deployment = await self.get_deployment(id, {})
        for key, value in values.items():
            setattr(deployment, key, value)
        self.session.add(deployment)
        return deployment
    
    async def get_available_clusters(self, locked_cluster_ids: list) -> list:
        query = select(Deployment).filter(
            or_(
                Deployment.status == DeploymentStatus.QUEUED.value,
                Deployment.cluster_id.not_in(locked_cluster_ids)
            )
        )
        results = await self.session.execute(query)
        deployments = results.scalars().all()

        return [deployment.cluster_id for deployment in deployments]