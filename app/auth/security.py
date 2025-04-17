# app/auth/security.py
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def verify_token(token: str = Depends(oauth2_scheme)):
    if token != settings.CLIENT_SECRET:
        raise HTTPException(status_code=401, detail="Invalid token")
    return token
