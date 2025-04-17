from fastapi import APIRouter, Form
from app.config import settings

router = APIRouter()


@router.post("/token")
def get_token(client_id: str = Form(...), client_secret: str = Form(...)):
    if client_id == settings.CLIENT_ID and client_secret == settings.CLIENT_SECRET:
        return {"access_token": client_secret, "token_type": "bearer"}
    return {"error": "Invalid credentials"}
