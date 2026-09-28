import asyncio
from pathlib import Path

import httpx2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_session
from app.main import app


TEST_DATABASE = Path(__file__).parent / "test_tasks.sqlite3"
test_engine = create_engine(
    f"sqlite:///{TEST_DATABASE}",
    connect_args={"check_same_thread": False},
)
TestingSession = sessionmaker(bind=test_engine, expire_on_commit=False)


async def override_get_session():
    with TestingSession() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


def setup_function() -> None:
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)


def teardown_module() -> None:
    test_engine.dispose()
    TEST_DATABASE.unlink(missing_ok=True)


async def exercise_task_crud() -> None:
    transport = httpx2.ASGITransport(app=app)
    async with httpx2.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        create_response = await client.post(
            "/tasks",
            json={"title": "Learn Python", "completed": False},
        )
        assert create_response.status_code == 201
        created = create_response.json()
        task_id = created["id"]

        assert (await client.get("/tasks")).json() == [created]
        assert (await client.get(f"/tasks/{task_id}")).json() == created
        assert (await client.delete(f"/tasks/{task_id}")).status_code == 204
        assert (await client.get(f"/tasks/{task_id}")).status_code == 404


def test_task_crud() -> None:
    # ASGITransport calls the app directly: no real network port is needed.
    asyncio.run(exercise_task_crud())
