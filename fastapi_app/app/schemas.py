from pydantic import BaseModel, Field
from typing import Generic, Optional, TypeVar
from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel

class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"

# --- Request Schemas ---
class BoardCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.todo
    due_date: Optional[date] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[date] = None

# --- Response Schemas ---
ItemType = TypeVar("ItemType")


class PaginatedResponse(BaseModel, Generic[ItemType]):
    items: list[ItemType]
    total: int
    page: int
    page_size: int

class BoardResponse(BaseModel):
    id: int
    title: str
    owner_id: int
    created_at: datetime

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    board_id: int
    due_date: Optional[date]
    created_at: datetime