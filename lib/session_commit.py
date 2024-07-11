from sqlalchemy.ext.asyncio import AsyncSession

class SyncedCommit:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def commit(self):
        await self.session.commit()