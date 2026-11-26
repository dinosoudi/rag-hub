import asyncio
import os
import subprocess
import sys

# Se fija antes de importar la app: el engine lee DATABASE_URL al arrancar.
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/raghub_test"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

import asyncpg
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.core.db import engine
from app.main import app


async def _ensure_database() -> None:
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        database="postgres",
    )
    try:
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = 'raghub_test'"
        )
        if not exists:
            await conn.execute("CREATE DATABASE raghub_test")
    finally:
        await conn.close()


@pytest.fixture(scope="session", autouse=True)
def _prepare_database():
    asyncio.run(_ensure_database())
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        check=True,
    )


@pytest.fixture(scope="session", autouse=True)
async def _dispose_engine(_prepare_database):
    yield
    await engine.dispose()


@pytest.fixture(autouse=True)
async def _clean_tables(_prepare_database):
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE collections CASCADE"))
    yield


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as http:
        yield http
