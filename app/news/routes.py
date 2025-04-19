# app/news/routes.py
import requests
from datetime import date, datetime
from fastapi import APIRouter, Depends, Query, status, HTTPException
from app.auth.security import verify_token
from app.config import settings
from app.global_utils import get_response
from app.constants import NEWS_API_URL_EVERYTHING, NEWS_API_TOP_HEADLINES
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import News
from sqlalchemy.exc import SQLAlchemyError


router = APIRouter(prefix="/news", dependencies=[Depends(verify_token)])


@router.get("/")
def get_news(
    q: str = Query(default="apple", description="Search term for the news"),
    page=None,
    page_size=None,
    from_date: date = Query(default=date.today(), alias="from"),
    to_date: date = Query(default=date.today(), alias="to"),
):
    """
    Get news articles from the News API.
    """
    params = {
        "q": q,
        "sortBy": "popularity",
        "from": from_date.isoformat(),
        "to": to_date.isoformat(),
        "apiKey": settings.API_KEY,
    }

    if page:
        params["page"] = int(page)
    if page_size:
        params["pageSize"] = int(page_size)

    try:
        response = requests.get(NEWS_API_URL_EVERYTHING, params=params)
        response.raise_for_status()
        return get_response(
            data=response.json(),
            message="News articles fetched successfully",
            status=status.HTTP_200_OK,
            error=False,
            code="NEWS_FETCHED",
        )
    except requests.exceptions.RequestException as e:
        return get_response(
            data={},
            message="Failed to fetch news articles",
            status=status.HTTP_400_BAD_REQUEST,
            error=True,
            code="NEWS_FETCH_FAILED",
        )
    except Exception as e:
        return get_response(
            data={},
            message="An unexpected error occurred",
            status=status.HTTP_400_BAD_REQUEST,
            error=True,
            code="UNEXPECTED_ERROR",
        )


@router.post("/save-latest")
def save_latest_news(db: Session = Depends(get_db)):
    url = NEWS_API_URL_EVERYTHING
    params = {
        "q": "apple",
        "sortBy": "publishedAt",
        "pageSize": 3,  # Only fetch top 3
        "apiKey": settings.API_KEY,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        articles = response.json().get("articles", [])[:3]

        if not articles:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No articles found"
            )

        saved_articles = []

        with db.begin():
            for article in articles:
                existing = db.query(News).filter(News.url == article["url"]).first()
                if existing:
                    continue
                news = News(
                    title=article.get("title"),
                    description=article.get("description"),
                    url=article.get("url"),
                    published_at=datetime.fromisoformat(
                        article.get("publishedAt").replace("Z", "+00:00")
                    ),
                )
                db.add(news)
                saved_articles.append(news)

        return get_response(
            message="Top 3 articles saved successfully",
            status=status.HTTP_200_OK,
            error=False,
            code="ARTICLES_SAVED",
            data=[
                {
                    "title": a.title,
                    "url": a.url,
                    "published_at": a.published_at.isoformat(),
                }
                for a in saved_articles
            ],
        )

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail="Failed to fetch news")
    except SQLAlchemyError as e:
        db.rollback()
        return get_response(
            message="Database error occurred",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error=True,
            code="DB_ERROR",
        )
    except Exception as e:
        db.rollback()
        return get_response(
            message="An unexpected error occurred",
            status=status.HTTP_400_BAD_REQUEST,
            error=True,
            code="UNEXPECTED_ERROR",
        )


@router.get("/all")
def get_all_news(page: int = 1, page_size: int = 10, db: Session = Depends(get_db)):
    try:
        offset = (page - 1) * page_size
        total = db.query(News).count()
        news_list = (
            db.query(News)
            .order_by(News.published_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return get_response(
            message="Fetched news articles successfully",
            status=status.HTTP_200_OK,
            error=False,
            code="ALL_NEWS_FETCHED",
            data={
                "total": total,
                "page": page,
                "page_size": page_size,
                "articles": [
                    {
                        "id": news.id,
                        "title": news.title,
                        "description": news.description,
                        "url": news.url,
                        "published_at": news.published_at.isoformat(),
                    }
                    for news in news_list
                ],
            },
        )
    except Exception as e:
        return get_response(
            message=f"An unexpected error occurred: {str(e)}",
            status=status.HTTP_400_BAD_REQUEST,
            error=True,
            code="UNEXPECTED_ERROR",
        )


@router.get("/headlines/country/{country_code}")
def get_headlines_by_country(country_code: str, db: Session = Depends(get_db)):
    """
    Get news articles from the News API.
    """
    params = {
        "country": country_code.lower(),
        "apiKey": settings.API_KEY,
    }

    try:
        response = requests.get(NEWS_API_TOP_HEADLINES, params=params)
        response.raise_for_status()
        return get_response(
            data=response.json(),
            message=f"Top headlines for country: {country_code.lower()}",
            status=status.HTTP_200_OK,
            error=False,
            code="TOP_HEADLINES_FETCHED",
        )
    except requests.exceptions.RequestException as e:
        return get_response(
            message="Failed to fetch news articles",
            status=status.HTTP_400_BAD_REQUEST,
            error=True,
            code="HEADLINES_FETCH_FAILED",
        )
    except Exception as e:
        return get_response(
            message="An unexpected error occurred",
            status=status.HTTP_400_BAD_REQUEST,
            error=True,
            code="UNEXPECTED_ERROR",
        )


@router.get("/headlines/source/{source_id}")
def get_headlines_by_source(source_id: str, db: Session = Depends(get_db)):
    """
    Get news articles from the News API.
    """
    params = {
        "sources": source_id.lower(),
        "apiKey": settings.API_KEY,
    }

    try:
        response = requests.get(NEWS_API_TOP_HEADLINES, params=params)
        response.raise_for_status()
        return get_response(
            data=response.json(),
            message=f"Top headlines for source: {source_id.lower()}",
            status=status.HTTP_200_OK,
            error=False,
            code="TOP_HEADLINES_FETCHED",
        )
    except requests.exceptions.RequestException as e:
        return get_response(
            message="Failed to fetch news articles",
            status=status.HTTP_400_BAD_REQUEST,
            error=True,
            code="HEADLINES_FETCH_FAILED",
        )
    except Exception as e:
        return get_response(
            message="An unexpected error occurred",
            status=status.HTTP_400_BAD_REQUEST,
            error=True,
            code="UNEXPECTED_ERROR",
        )


@router.get("/headlines/filter")
def get_headlines_by_source(source: str, country: str):
    """
    Get news articles from the News API.
    """
    params = {
        "source": source.lower(),
        "country": country.lower(),
        "apiKey": settings.API_KEY,
    }

    try:
        response = requests.get(NEWS_API_TOP_HEADLINES, params=params)
        response.raise_for_status()
        return get_response(
            data=response.json(),
            message=f"Top headlines for country: {country.lower()}, source: {source.lower()}",
            status=status.HTTP_200_OK,
            error=False,
            code="TOP_HEADLINES_FETCHED",
        )
    except requests.exceptions.RequestException as e:
        return get_response(
            message="Failed to fetch news articles",
            status=status.HTTP_400_BAD_REQUEST,
            error=True,
            code="HEADLINES_FETCH_FAILED",
        )
    except Exception as e:
        return get_response(
            message="An unexpected error occurred",
            status=status.HTTP_400_BAD_REQUEST,
            error=True,
            code="UNEXPECTED_ERROR",
        )
