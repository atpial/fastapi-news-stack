# app/models.py
from sqlalchemy import Column, String, Integer, DateTime
from app.database import Base


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    url = Column(String)
    published_at = Column(DateTime)
