from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    """JSON accepted by POST /tasks."""

    title: str = Field(min_length=1)
    completed: bool = False


class TaskRead(BaseModel):
    """Public JSON returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    completed: bool
