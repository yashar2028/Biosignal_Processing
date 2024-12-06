import os
from fastapi import FastAPI
from sqlalchemy import Column, Integer, Float, DateTime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from alembic import command
from alembic.config import Config
from dotenv import load_dotenv


load_dotenv()  # Loading the environment variables from .env

# Database url whose configration is read from .env
DATABASE_URL = f"postgresql+asyncpg://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"

Base = (
    declarative_base()
)  # All the models (classes) that are going to be mapped to database tables have to inherit this.


class SignalAmplitude(Base):
    __tablename__ = "signal_amplitudes"

    id = Column(Integer, primary_key=True)
    amplitude = Column(Float)
    timestamp = Column(DateTime(timezone=True))


# Setup SQLAlchemy Async Engine and Session. This session is then used below in get_db function and it can be used to interact with database (populate, etc.)
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db():  # Dependency to get the async database session
    async with SessionLocal() as db:
        yield db


app = FastAPI()

ALEMBIC_CONFIG = "alembic.ini"


@app.on_event("startup")
async def startup_event():
    """Run migrations on application startup."""
    alembic_cfg = Config(ALEMBIC_CONFIG)
    command.upgrade(
        alembic_cfg, "head"
    )  # This will apply all migrations to the latest state upon running the app
