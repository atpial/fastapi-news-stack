# app/main.py
from fastapi import FastAPI
from app.auth.routes import router as auth_router
from app.news.routes import router as news_router
from app.database import Base, engine
from app.logger import logger
from contextlib import asynccontextmanager

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("FastAPI app is starting up...")
    yield
    logger.info("FastAPI app is shutting down...")


app = FastAPI(title="News API App", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(news_router)
