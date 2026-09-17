# fastapi_app/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models import User
from ..auth import get_password_hash, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/signup", status_code=201)
async def signup(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check existing
    result = await db.execute(select(User).where((User.username == user_data.username) | (User.email == user_data.email)))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Username or email already exists")
    
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"id": new_user.id, "username": new_user.username, "email": new_user.email}

@router.post("/login")
async def login(username: str, password: str, db: AsyncSession = Depends(get_db)):
    # Note: For benchmark simplicity we use query params or form data. 
    # In production use OAuth2PasswordRequestForm. Here we keep it simple for curl testing.
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
        
    token = create_access_token(data={"sub": user.username})
    return TokenResponse(access_token=token)

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "email": current_user.email}