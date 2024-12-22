# This is the database configuration that all the test cases in test.py working with database session are going to use.

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.main import DATABASE_URL, Base

engine = create_async_engine(DATABASE_URL, echo=True)
TestSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(
    scope="module", autouse=True
)  # Autouse ensures the database is set up before any test runs.
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.create_all
        )  # Creating the tables in the database before action.
    yield

    pass  # We don't drop the tables here to preserve them for real data in production.


@pytest.fixture
async def async_session():  # Yielding the async session to be used in tests.
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
