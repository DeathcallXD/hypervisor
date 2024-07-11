
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from lib.generate_new_id import generate_new_id

from .models import Cluster

class ClusterRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_cluster(self, id: int, filters: dict) -> Cluster:
        query_filters = [getattr(Cluster, key) == value for key, value in filters.items()]
        if not id:
            get_cluster = await self.session.execute(select(Cluster).filter(*query_filters))
            cluster: Cluster = get_cluster.scalars().first()
        else:
            get_cluster = await self.session.execute(
                select(Cluster).filter(Cluster.id == id).filter(*query_filters)
            )
            cluster: Cluster = get_cluster.scalars().first()

        return cluster
    
    async def create_cluster(self, values: dict) -> Cluster:
        next_id = generate_new_id(Cluster)
        cluster = Cluster(**values, id=next_id)
        self.session.add(cluster)

        return cluster
    
    async def update_cluster(self, id: int, values: dict) -> Cluster:
        cluster = await self.get_cluster(id, {})
        for key, value in values.items():
            setattr(cluster, key, value)
        self.session.add(cluster)
        return cluster
    