import os
import uvicorn
from fastapi import FastAPI
from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from alembic import command
from alembic.config import Config
from dotenv import load_dotenv

from app.routes.health_check import router as health_check_router
from app.routes.register import router as register_router
from app.routes.display import router as display_router
from app.routes.login import router as login_router
from app.routes.verify import router as verify_router

load_dotenv()  # Loading the environment variables from .env

# Database url whose configration is read from .env
DATABASE_URL = f"postgresql+asyncpg://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"

Base = (
    declarative_base()
)  # All the models (classes) that are going to be mapped to database tables have to inherit this.


class SignalAmplitude(Base):  # Table for stroring signal values.
    __tablename__ = "signal_amplitudes"

    id = Column(Integer, primary_key=True)
    amplitude = Column(Float)
    timestamp = Column(DateTime(timezone=True))


class User(Base):  # User model for SQLAlchemy (table)
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, unique=True, nullable=False)
    last_name = Column(String, unique=True, nullable=False)
    role = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)


# Setup SQLAlchemy Async Engine and Session. This session is then used below in get_db function and it can be used to interact with database (populate, etc.)
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db():  # Dependency to get the async database session
    async with SessionLocal() as db:
        yield db


async def init_db():
    """
    Inittalize database (create tables)
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    await engine.dispose()


app = FastAPI()
ALEMBIC_CONFIG = "alembic.ini"


@app.on_event("startup")
async def startup_event_on_database():
    """
    Initialize the database and run migrations on application startup.
    """

    await init_db()

    alembic_cfg = Config(ALEMBIC_CONFIG)
    command.upgrade(
        alembic_cfg, "head"
    )  # This will apply all migrations to the latest state upon running the app


@app.on_event("shutdown")
async def shutdown_event_on_database():
    """
    In order to clean up database connections when the app shuts down.
    """
    await close_db()


# All the routes at routes directory are registered here with their specified router.
app.include_router(health_check_router)
app.include_router(register_router)
app.include_router(display_router)
app.include_router(login_router)
app.include_router(verify_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
