# app/models.py
from sqlalchemy import Column, String, Integer, DateTime, Text
from app.database import Base


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    description = Column(Text)
    url = Column(String(255), unique=True)
    published_at = Column(DateTime)
