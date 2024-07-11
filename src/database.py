from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from .config import settings

DATABASE_URL = settings.DATABASE_URL


# setup sync session class
SYNC_DATABASE_URL = DATABASE_URL[0:10] + "+psycopg2" + DATABASE_URL[10:]
#TODO : need to make sure this is created once per startup
sync_engine = create_engine(SYNC_DATABASE_URL,poolclass=NullPool,pool_pre_ping=True,pool_recycle=300)
sync_session = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# setup async session class
ASYNC_DATABASE_URL = DATABASE_URL[0:10] + "+asyncpg" + DATABASE_URL[10:]
#TODO : need to make sure this is created once per startup
async_engine = create_async_engine(ASYNC_DATABASE_URL,poolclass=NullPool,pool_pre_ping=True,pool_recycle=300)
async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)