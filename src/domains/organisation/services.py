from sqlalchemy.ext.asyncio import AsyncSession

from lib.session_commit import SyncedCommit

from .repositories import OrganisationRepository
from .utils import OrganisationUtils

from ..user.repositories import UserRepository

class OrganisationService:
    def __init__(self, session: AsyncSession):
        self.session = session

        self.org_repo = OrganisationRepository(session)
        self.use_repo = UserRepository(session)
        self.org_utils = OrganisationUtils()

        self.synced_commit = SyncedCommit(session)

    async def create_organisation(self, user_id: str, values: dict):
        values["invite_code"] = self.org_utils.generate_invite_code()
        organisation = await self.org_repo.create_organisation(values)

        user = await self.use_repo.get_user(user_id, {})
        await self.use_repo.update_user(user.id, {"organisation_id": organisation.id})

        await self.synced_commit.commit()

        return organisation
    
    async def join_organisation(self, user_id: str, ivt_code: str):
        org = await self.org_repo.get_organisation(None, {"invite_code": ivt_code})

        user = await self.use_repo.get_user(user_id, {})
        user = await self.use_repo.update_user(user.id, {"organisation_id": org.id})

        await self.synced_commit.commit()

        return user