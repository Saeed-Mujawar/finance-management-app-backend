from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Create async engine
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, 
    echo=True,
    pool_size=1,                # Minimum number of connections in the pool
    max_overflow=0,             # Maximum number of connections above `pool_size`
    pool_pre_ping=True,         # Enable pre-ping to check the connection's validity before using
    pool_recycle=1800           # Recycle connections every 30 minutes (or as needed)
)
# Create async sessionmaker
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # Ensure objects remain usable after commit
    class_=AsyncSession
)
# Base class for models
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def create_all():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Error creating tables: {e}")