from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from .config import settings

# Sync engine (for migrations and some operations)
engine = create_engine(
    settings.mysql_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG
)

# Async engine (for FastAPI endpoints)
async_engine = create_async_engine(
    settings.async_mysql_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG
)

# Session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Base class for models
Base = declarative_base()


# Dependency for sync sessions
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency for async sessions
async def get_async_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Initialize database tables
def init_db():
    # Import models to register them with Base
    from . import models  # noqa: F401
    Base.metadata.create_all(bind=engine)


async def init_async_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
