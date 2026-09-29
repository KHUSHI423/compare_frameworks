from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from ..database import get_db
from ..models import Board, Task, User, TaskStatus as TaskStatusEnum
from ..auth import get_current_user
from ..schemas import TaskCreate, TaskUpdate, TaskResponse, PaginatedResponse

router = APIRouter(prefix="/boards/{board_id}/tasks", tags=["Tasks"])

@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    board_id: int,
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify board ownership
    result = await db.execute(select(Board).where(Board.id == board_id, Board.owner_id == current_user.id))
    board = result.scalar_one_or_none()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found or not owned")
        
    task = Task(**task_data.model_dump(), board_id=board_id)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

@router.get("", response_model=PaginatedResponse[TaskResponse])
async def list_tasks(
    board_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status_filter: Optional[TaskStatusEnum] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check ownership first
    board_result = await db.execute(select(Board).where(Board.id == board_id, Board.owner_id == current_user.id))
    if not board_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Board not found or not owned")
    
    # Build query with optional filter
    stmt = select(Task).where(Task.board_id == board_id)
    count_stmt = select(func.count(Task.id)).where(Task.board_id == board_id)
    
    if status_filter:
        stmt = stmt.where(Task.status == status_filter)
        count_stmt = count_stmt.where(Task.status == status_filter)
        
    total = (await db.execute(count_stmt)).scalar()
    offset = (page - 1) * page_size
    tasks = (await db.execute(stmt.offset(offset).limit(page_size))).scalars().all()
    
    return PaginatedResponse(items=tasks, total=total, page=page, page_size=page_size)

@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    board_id: int,
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify board ownership
    board_result = await db.execute(select(Board).where(Board.id == board_id, Board.owner_id == current_user.id))
    if not board_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Board not found or not owned")
        
    task_result = await db.execute(select(Task).where(Task.id == task_id, Task.board_id == board_id))
    task = task_result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
        
    await db.commit()
    await db.refresh(task)
    return task

@router.delete("/{task_id}", status_code=204)
async def delete_task(
    board_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    board_result = await db.execute(select(Board).where(Board.id == board_id, Board.owner_id == current_user.id))
    if not board_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Board not found or not owned")
        
    task_result = await db.execute(select(Task).where(Task.id == task_id, Task.board_id == board_id))
    task = task_result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    await db.delete(task)
    await db.commit()