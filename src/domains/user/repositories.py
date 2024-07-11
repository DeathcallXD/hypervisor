
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from lib.generate_new_id import generate_new_id

from .models import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_users(self, filters: dict) -> list[User]:
        query_filters = [getattr(User, key) == value for key, value in filters.items()]
        get_user = await self.session.execute(select(User).filter(*query_filters))
        users: list[User] = get_user.scalars().all()
        
        return users


    async def get_user(self, id: int, filters: dict) -> User:
        query_filters = [getattr(User, key) == value for key, value in filters.items()]
        if not id:
            get_user = await self.session.execute(select(User).filter(*query_filters))
            user: User = get_user.scalars().first()
        else:
            get_user = await self.session.execute(
                select(User).filter(User.id == id).filter(*query_filters)
            )
            user: User = get_user.scalars().first()

        return user
    
    async def create_user(self, values: dict) -> User:
        next_id = generate_new_id(User)
        user = User(**values, id=next_id)
        self.session.add(user)

        return user
    
    async def update_user(self, id: int, values: dict) -> User:
        user = await self.get_user(id, {})
        for key, value in values.items():
            setattr(user, key, value)
        self.session.add(user)
        return user