from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Create async engine
engine = create_async_engine(SQLALCHEMY_DATABASE_URL,pool_size=5, max_overflow=10, echo=True)

# Create async sessionmaker
AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# Base class for models
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def create_all():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Error creating tables: {e}")