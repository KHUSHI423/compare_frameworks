from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from ..database import get_db
from ..models import Board, User
from ..auth import get_current_user
from ..schemas import BoardCreate, BoardResponse, PaginatedResponse
import csv
import io
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models import Board, Task, Attachment, User
from ..auth import get_current_user
from ..config import settings

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ... [Previous Board Routes] ...

@router.post("/{board_id}/attachment")
async def upload_attachment(
    board_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify ownership
    result = await db.execute(select(Board).where(Board.id == board_id, Board.owner_id == current_user.id))
    board = result.scalar_one_or_none()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found or not owned")

    # Save file safely
    safe_filename = f"{board_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    content = await file.read()  # Async read - non-blocking
    with open(file_path, "wb") as buffer:
        buffer.write(content)

    attachment = Attachment(
        board_id=board_id,
        file_path=file_path,
        original_filename=file.filename
    )
    db.add(attachment)
    await db.commit()

    return {"url": f"/uploads/{safe_filename}", "filename": file.filename}

@router.get("/{board_id}/export")
async def export_tasks_csv(
    board_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify ownership
    result = await db.execute(select(Board).where(Board.id == board_id, Board.owner_id == current_user.id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Board not found or not owned")

    # Generator function for memory-efficient streaming
    async def task_generator():
        yield "id,title,status,due_date,created_at\n"
        
        stmt = select(Task).where(Task.board_id == board_id)
        result = await db.execute(stmt)
        tasks = result.scalars().all()
        
        for task in tasks:
            row = f'{task.id},"{task.title}",{task.status},{task.due_date},{task.created_at}\n'
            yield row.encode('utf-8')  # Yield bytes for StreamingResponse

    headers = {"Content-Disposition": f"attachment; filename=board_{board_id}_tasks.csv"}
    return StreamingResponse(task_generator(), media_type="text/csv", headers=headers)
router = APIRouter(prefix="/boards", tags=["Boards"])

@router.post("", response_model=BoardResponse, status_code=201)
async def create_board(
    board_data: BoardCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    board = Board(title=board_data.title, owner_id=current_user.id)
    db.add(board)
    await db.commit()
    await db.refresh(board)
    return board

@router.get("", response_model=PaginatedResponse)
async def list_boards(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Count total owned boards
    count_q = select(func.count(Board.id)).where(Board.owner_id == current_user.id)
    total = (await db.execute(count_q)).scalar()
    
    # Fetch paginated results
    offset = (page - 1) * page_size
    stmt = select(Board).where(Board.owner_id == current_user.id).offset(offset).limit(page_size)
    result = await db.execute(stmt)
    boards = result.scalars().all()
    
    return PaginatedResponse(items=boards, total=total, page=page, page_size=page_size)

@router.get("/{board_id}", response_model=BoardResponse)
async def get_board(
    board_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Board).where(Board.id == board_id))
    board = result.scalar_one_or_none()
    
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    if board.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this board")
        
    return board

@router.delete("/{board_id}", status_code=204)
async def delete_board(
    board_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Board).where(Board.id == board_id))
    board = result.scalar_one_or_none()
    
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    if board.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    await db.delete(board)
    await db.commit()