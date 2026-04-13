from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.auth import create_access_token, verify_password, hash_password
from api.schemas import LoginRequest, TokenResponse, AdminMeResponse
from api.dependencies import get_current_admin, get_db
from bot.models import Admin
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Auth"])

class ProfileUpdateRequest(BaseModel):
    username: str | None = None
    password: str | None = None

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Admin).filter(Admin.username == data.username))
    admin = result.scalars().first()
    if not admin or not verify_password(data.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    access_token = create_access_token({"sub": admin.username})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=AdminMeResponse)
async def me(current_admin=Depends(get_current_admin)):
    return {
        "username": current_admin["username"]
    }

@router.put("/me")
async def update_profile(data: ProfileUpdateRequest, current_admin=Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Admin).filter(Admin.username == current_admin["username"]))
    admin = result.scalars().first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    if data.username:
        # Check if username already exists
        eb_result = await db.execute(select(Admin).filter(Admin.username == data.username, Admin.id != admin.id))
        existing = eb_result.scalars().first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")
        admin.username = data.username
        
    if data.password:
        admin.hashed_password = hash_password(data.password)
        
    await db.commit()
    return {"status": "success", "new_username": admin.username}