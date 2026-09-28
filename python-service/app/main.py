from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base, engine, get_session
from app.models import Task
from app.schemas import TaskCreate, TaskRead


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # For a tiny classroom demo, creating missing tables at startup is clearer
    # than adding Alembic. Rails uses the explicit migration in db/migrate.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Task API - FastAPI",
    description="Small API for comparison with Rails API mode.",
    lifespan=lifespan,
)

DatabaseSession = Annotated[Session, Depends(get_session)]


def find_task(task_id: int, session: Session) -> Task:
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get("/tasks", response_model=list[TaskRead])
async def list_tasks(session: DatabaseSession) -> list[Task]:
    return list(session.scalars(select(Task).order_by(Task.id)))


@app.get("/tasks/{task_id}", response_model=TaskRead)
async def get_task(task_id: int, session: DatabaseSession) -> Task:
    return find_task(task_id, session)


@app.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreate, session: DatabaseSession) -> Task:
    task = Task(**payload.model_dump())
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_task(task_id: int, session: DatabaseSession) -> Response:
    task = find_task(task_id, session)
    session.delete(task)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
