import os
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv


load_dotenv()  # Loading the environment variables from .env

# Database url whose configration is read from .env
DATABASE_URL = f"postgresql+asyncpg://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"

# Setup SQLAlchemy Async Engine and Session. This session is then used below in get_db function and it can be used to interact with database (populate, etc.)
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db():  # Dependency to get the async database session
    async with SessionLocal() as db:
        yield db


app = FastAPI()
