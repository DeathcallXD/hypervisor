
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from lib.generate_new_id import generate_new_id

from .models import Organisation

class OrganisationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_organisation(self, id: int, filters: dict) -> Organisation:
        query_filters = [getattr(Organisation, key) == value for key, value in filters.items()]
        if not id:
            get_organisation = await self.session.execute(select(Organisation).filter(*query_filters))
            organisation: Organisation = get_organisation.scalars().first()
        else:
            get_organisation = await self.session.execute(
                select(Organisation).filter(Organisation.id == id).filter(*query_filters)
            )
            organisation: Organisation = get_organisation.scalars().first()

        return organisation
    
    async def create_organisation(self, values: dict) -> Organisation:
        next_id = generate_new_id(Organisation)
        organisation = Organisation(**values, id=next_id)
        self.session.add(organisation)

        return organisation
    
    async def update_organisation(self, id: int, values: dict) -> Organisation:
        organisation = await self.get_organisation(id, {})
        for key, value in values.items():
            setattr(organisation, key, value)
        self.session.add(organisation)
        return organisation