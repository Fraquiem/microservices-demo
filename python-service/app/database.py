from collections.abc import AsyncGenerator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


DATABASE_PATH = Path(__file__).resolve().parent.parent / "tasks.sqlite3"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# SQLite normally restricts a connection to one thread. FastAPI may execute
# sync endpoint functions in different worker threads, so this local demo opts out.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class that gives SQLAlchemy models their database mapping."""


async def get_session() -> AsyncGenerator[Session, None]:
    """Provide one database session per request, then always close it."""

    with SessionLocal() as session:
        yield session
