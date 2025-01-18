import uvicorn
from fastapi import FastAPI

# from alembic import command
# from alembic.config import Config

from app.models import Base
from app.dependencies import engine
from app.routes.health_check import router as health_check_router
from app.routes.register import router as register_router
from app.routes.display import router as display_router
from app.routes.login import router as login_router
from app.routes.verify import router as verify_router
from app.socket import router as websocket_router


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

    # alembic_cfg = Config(ALEMBIC_CONFIG)  # Uncomment these (two imports above as well) when a new change to datbase is added and run the app. Not needed for users on Docker.
    # command.upgrade(
    #    alembic_cfg, "head"
    # )  # This will apply all migrations to the latest state upon running the app.


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
app.include_router(websocket_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
