from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from ..database import get_db
from ..models import Board, User
from ..auth import get_current_user
from ..schemas import BoardCreate, BoardResponse, PaginatedResponse

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