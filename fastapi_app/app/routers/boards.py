import csv
import io
import os

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..database import get_db
from ..models import Attachment, Board, Task, User
from ..schemas import BoardCreate, BoardResponse, PaginatedResponse

router = APIRouter(prefix="/boards", tags=["Boards"])
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("", response_model=BoardResponse, status_code=201)
async def create_board(
    board_data: BoardCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    board = Board(title=board_data.title, owner_id=current_user.id)
    db.add(board)
    await db.commit()
    await db.refresh(board)
    return board


@router.get("", response_model=PaginatedResponse[BoardResponse])
async def list_boards(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    count_query = select(func.count(Board.id)).where(Board.owner_id == current_user.id)
    total = (await db.execute(count_query)).scalar_one()

    offset = (page - 1) * page_size
    query = (
        select(Board)
        .where(Board.owner_id == current_user.id)
        .offset(offset)
        .limit(page_size)
    )
    boards = (await db.execute(query)).scalars().all()
    return PaginatedResponse(items=boards, total=total, page=page, page_size=page_size)


@router.get("/{board_id}", response_model=BoardResponse)
async def get_board(
    board_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    board = (
        await db.execute(select(Board).where(Board.id == board_id))
    ).scalar_one_or_none()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    if board.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this board")
    return board


@router.delete("/{board_id}", status_code=204)
async def delete_board(
    board_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    board = (
        await db.execute(select(Board).where(Board.id == board_id))
    ).scalar_one_or_none()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    if board.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    await db.delete(board)
    await db.commit()


@router.post("/{board_id}/attachment")
async def upload_attachment(
    board_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    board = (
        await db.execute(
            select(Board).where(
                Board.id == board_id, Board.owner_id == current_user.id
            )
        )
    ).scalar_one_or_none()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found or not owned")

    filename = os.path.basename(file.filename or "")
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    safe_filename = f"{board_id}_{filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    db.add(
        Attachment(
            board_id=board_id,
            file_path=file_path,
            original_filename=filename,
        )
    )
    await db.commit()
    return {"url": f"/uploads/{safe_filename}", "filename": filename}


@router.get("/{board_id}/export")
async def export_tasks_csv(
    board_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    board = (
        await db.execute(
            select(Board).where(
                Board.id == board_id, Board.owner_id == current_user.id
            )
        )
    ).scalar_one_or_none()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found or not owned")

    tasks = (
        await db.execute(select(Task).where(Task.board_id == board_id))
    ).scalars().all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "title", "status", "due_date", "created_at"])
    for task in tasks:
        writer.writerow(
            [
                task.id,
                task.title,
                task.status.value,
                task.due_date,
                task.created_at,
            ]
        )
    headers = {"Content-Disposition": f"attachment; filename=board_{board_id}_tasks.csv"}
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers=headers)
