import pytest
import asyncio
from sqlalchemy.sql import text
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from app.main import app, SignalAmplitude, get_db
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()  # To ensure loop session is created once for each test and is closed at the end.


# Override get_db dependnecy to use the test session.
def override_get_db(asyncsession: AsyncSession):
    app.dependency_overrides[get_db] = lambda: asyncsession


def test_health_check():
    """
    Testing the health_check endpoint.
    """
    response = client.get("/health_check")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_db_connectivity(async_session: AsyncSession):
    test_record = SignalAmplitude(
        amplitude=1.00, timestamp=datetime.now(timezone.utc)
    )
    async_session.add(test_record)  # Inserted a test record

    await async_session.commit()

    result = await async_session.execute(
        text("SELECT * FROM signal_amplitudes WHERE amplitude = :amplitude"),
        {"amplitude": 1.00},  # Quering the inserted data
    )

    record = result.fetchone()
    assert record is not None
    amplitude = record[1]
    assert amplitude == 1.00

    delete_query = text(
        "DELETE FROM signal_amplitudes WHERE amplitude = :amplitude"
    )  # The inserted data is removed afterwards (since this already the production database).
    await async_session.execute(delete_query, {"amplitude": 1.00})

    await async_session.commit()
