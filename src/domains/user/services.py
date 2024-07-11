from sqlalchemy.ext.asyncio import AsyncSession

from lib.session_commit import SyncedCommit

from .utils import LoginUtils
from .repositories import UserRepository

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

        self.user_repo = UserRepository(session)
        self.synced_commit = SyncedCommit(session)

        self.login_utils = LoginUtils()
    

    async def create_user(self, name, username, password):
        user = await self.user_repo.create_user({
            "name": name, 
            "username": username, 
            "password": password
        })

        await self.synced_commit.commit()
        return user


    async def login(self, username, password):
        user = await self.user_repo.get_user(None, {"username": username})

        pass_in_db = user.password
        pass_in_request = password

        if self.login_utils.verify_pass(pass_in_db, pass_in_request):
            session_id, expires_at = self.login_utils.create_session(user.id)
            return {**user.__dict__, "session_id": session_id, "expires_at": expires_at}
        else:
            return None