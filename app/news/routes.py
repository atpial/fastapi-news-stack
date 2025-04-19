# app/news/routes.py
import requests
from datetime import date
from fastapi import APIRouter, Depends, Query, status
from app.auth.security import verify_token
from app.config import settings
from app.global_utils import get_response
from app.constants import NEWS_API_URL_EVERYTHING


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
