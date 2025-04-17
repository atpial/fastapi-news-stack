# app/news/routes.py
from fastapi import APIRouter, Depends
from app.auth.security import verify_token

router = APIRouter(prefix="/news", dependencies=[Depends(verify_token)])


@router.get("/")
def get_news():
    return {"message": "News endpoint is protected"}
