from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bot.db import SessionLocal

from api.auth import verify_access_token

security = HTTPBearer()

async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()



def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    payload = verify_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return payload