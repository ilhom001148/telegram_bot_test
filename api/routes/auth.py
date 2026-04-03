from datetime import datetime, timedelta, UTC
from jose import jwt, JWTError

SECRET_KEY = "super-secret-key-12345"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")

        if username is None:
            return None

        return {"username": username}

    except JWTError:
        return None


from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
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
def login(data: LoginRequest, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == data.username).first()
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
def me(current_admin=Depends(get_current_admin)):
    return {
        "username": current_admin["username"]
    }

@router.put("/me")
def update_profile(data: ProfileUpdateRequest, current_admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == current_admin["username"]).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    if data.username:
        # Check if username already exists
        existing = db.query(Admin).filter(Admin.username == data.username, Admin.id != admin.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")
        admin.username = data.username
        
    if data.password:
        admin.hashed_password = hash_password(data.password)
        
    db.commit()
    return {"status": "success", "new_username": admin.username}