import pytest
from unittest.mock import MagicMock, patch
import requests
from app.main import app
from app.database import get_db
from app.models import News
from datetime import datetime


def get_token(client):
    response = client.post(
        "/token",
        json={"client_id": "blockstak_client", "client_secret": "supersecret"},
    )
    print(response.json())
    return response.json()["data"]["access_token"]


def test_save_latest_news(client, cleanup_db):
    token = get_token(client)

    response = client.post(
        "/news/save-latest", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Top 3 articles saved successfully"
    assert body["error"] is False
    assert len(body["data"]) <= 3
    assert all("title" in a and "url" in a for a in body["data"])


@pytest.fixture
def mock_db_session():
    # Mock the DB session for testing
    mock_session = MagicMock()

    # Mock the query result for count()
    mock_session.query().count.return_value = 5

    # Mock the query result for fetching news articles
    mock_news_list = [
        News(
            id=1,
            title="Test News 1",
            description="Description 1",
            url="http://example.com/1",
            published_at=datetime.fromisoformat("2023-01-01T12:00:00"),
        ),
        News(
            id=2,
            title="Test News 2",
            description="Description 2",
            url="http://example.com/2",
            published_at=datetime.fromisoformat("2025-04-18T14:01:40"),
        ),
        News(
            id=3,
            title="Test News 3",
            description="Description 3",
            url="http://example.com/3",
            published_at=datetime.fromisoformat("2023-03-01T12:00:00"),
        ),
    ]
    mock_session.query().order_by().offset().limit().all.return_value = mock_news_list

    # Return the mocked session
    return mock_session


def test_get_all_news(client, mock_db_session, cleanup_db):
    token = get_token(client)
    app.dependency_overrides[get_db] = lambda: mock_db_session

    response = client.get(
        "/news/all?page=1&page_size=10", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    body = response.json()

    assert body["message"] == "Fetched news articles successfully"
    assert body["error"] is False
    assert body["data"]["total"] == 5
    assert body["data"]["page"] == 1
    assert body["data"]["page_size"] == 10
    assert len(body["data"]["articles"]) == 3

    # Check that the article fields are correct
    for article in body["data"]["articles"]:
        assert "id" in article
        assert "title" in article
        assert "description" in article
        assert "url" in article
        assert "published_at" in article


@patch("requests.get")
def test_get_headlines_by_country(mock_get, client):
    # Sample data returned by the mock API call
    token = get_token(client)
    mock_data = {
        "status": "ok",
        "totalResults": 2,
        "articles": [
            {
                "source": {"id": "1", "name": "Source 1"},
                "author": "Author 1",
                "title": "Headline 1",
                "description": "Description 1",
                "url": "http://example.com/1",
                "publishedAt": "2023-01-01T12:00:00Z",
            },
            {
                "source": {"id": "2", "name": "Source 2"},
                "author": "Author 2",
                "title": "Headline 2",
                "description": "Description 2",
                "url": "http://example.com/2",
                "publishedAt": "2023-02-01T14:00:00Z",
            },
        ],
    }

    # Configure the mock response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_data

    # Send the GET request to the API
    response = client.get(
        "news/headlines/country/us", headers={"Authorization": f"Bearer {token}"}
    )

    # Assertions
    assert response.status_code == 200
    body = response.json()

    # Check if the response contains expected data
    assert body["message"] == "Top headlines for country: us"
    assert body["error"] is False
    assert "data" in body
    assert body["data"]["status"] == "ok"
    assert body["data"]["totalResults"] == 2
    assert len(body["data"]["articles"]) == 2
    assert "title" in body["data"]["articles"][0]
    assert "description" in body["data"]["articles"][0]
    assert "url" in body["data"]["articles"][0]

    # Check the structure of the first article
    assert body["data"]["articles"][0]["title"] == "Headline 1"
    assert body["data"]["articles"][1]["title"] == "Headline 2"


@patch("requests.get")
def test_get_headlines_by_country_error(mock_get, client):
    # Mocking an error response from the News API
    mock_get.return_value.status_code = 500
    mock_get.return_value.raise_for_status.side_effect = (
        requests.exceptions.RequestException("API error")
    )

    # Send the GET request to the API
    response = client.get(
        "news/headlines/country/us",
        headers={"Authorization": f"Bearer {get_token(client)}"},
    )

    # Assertions
    assert response.status_code == 400
    body = response.json()
    assert body["message"] == "Failed to fetch news articles"
    assert body["error"] is True
    assert body["code"] == "HEADLINES_FETCH_FAILED"


@patch("requests.get")
def test_get_headlines_by_source_success(mock_get, client):
    token = get_token(client)
    mock_response_data = {
        "status": "ok",
        "totalResults": 2,
        "articles": [
            {
                "source": {"id": "bbc-news", "name": "BBC News"},
                "author": "BBC",
                "title": "Sample Headline 1",
                "description": "Sample Description 1",
                "url": "http://example.com/1",
                "publishedAt": "2024-01-01T10:00:00Z",
            },
            {
                "source": {"id": "bbc-news", "name": "BBC News"},
                "author": "BBC",
                "title": "Sample Headline 2",
                "description": "Sample Description 2",
                "url": "http://example.com/2",
                "publishedAt": "2024-01-02T11:00:00Z",
            },
        ],
    }

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response_data

    response = client.get(
        "news/headlines/source/bbc-news", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Top headlines for source: bbc-news"
    assert body["error"] is False
    assert body["code"] == "TOP_HEADLINES_FETCHED"
    assert body["data"]["status"] == "ok"
    assert len(body["data"]["articles"]) == 2
    assert body["data"]["articles"][0]["title"] == "Sample Headline 1"


@patch("requests.get")
def test_get_headlines_by_source_api_failure(mock_get, client):
    mock_get.side_effect = requests.exceptions.RequestException("API error")

    response = client.get(
        "news/headlines/source/bbc-news",
        headers={"Authorization": f"Bearer {get_token(client)}"},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["message"] == "Failed to fetch news articles"
    assert body["error"] is True
    assert body["code"] == "HEADLINES_FETCH_FAILED"


@patch("requests.get")
def test_get_headlines_by_source_exception(mock_get, client):
    mock_get.side_effect = Exception("Some unexpected error")

    response = client.get(
        "news/headlines/source/bbc-news",
        headers={"Authorization": f"Bearer {get_token(client)}"},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["message"] == "An unexpected error occurred"
    assert body["error"] is True
    assert body["code"] == "UNEXPECTED_ERROR"


@patch("requests.get")
def test_get_headlines_filter_success(mock_get, client):
    mock_response_data = {
        "status": "ok",
        "totalResults": 1,
        "articles": [
            {
                "source": {"id": "bbc-news", "name": "BBC News"},
                "author": "BBC",
                "title": "Test News",
                "description": "Sample Description",
                "url": "http://example.com",
                "publishedAt": "2024-04-19T12:00:00Z",
            }
        ],
    }

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response_data

    response = client.get(
        "news/headlines/filter?source=bbc-news&country=us",
        headers={"Authorization": f"Bearer {get_token(client)}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["error"] is False
    assert body["code"] == "TOP_HEADLINES_FETCHED"
    assert "articles" in body["data"]
    assert body["data"]["articles"][0]["title"] == "Test News"
    assert "bbc-news" in body["message"]
    assert "us" in body["message"]


@patch("requests.get")
def test_get_headlines_filter_api_error(mock_get, client):
    mock_get.side_effect = requests.exceptions.RequestException("Timeout")

    response = client.get(
        "news/headlines/filter?source=bbc-news&country=us",
        headers={"Authorization": f"Bearer {get_token(client)}"},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error"] is True
    assert body["message"] == "Failed to fetch news articles"
    assert body["code"] == "HEADLINES_FETCH_FAILED"


@patch("requests.get")
def test_get_headlines_filter_unexpected_error(mock_get, client):
    mock_get.side_effect = Exception("Boom")

    response = client.get(
        "news/headlines/filter?source=bbc-news&country=us",
        headers={"Authorization": f"Bearer {get_token(client)}"},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error"] is True
    assert body["message"] == "An unexpected error occurred"
    assert body["code"] == "UNEXPECTED_ERROR"


from datetime import timedelta, datetime, timezone
from jose import jwt
from app.config import settings


def create_token(exp_delta_minutes=15):
    expire = datetime.now(timezone.utc) + timedelta(minutes=exp_delta_minutes)
    payload = {"sub": settings.CLIENT_ID, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def test_protected_news_route_with_valid_token(client):
    token = create_token()
    response = client.get(
        "/news/all?page=1&page_size=10", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["error"] is False
    assert body["code"] == "ALL_NEWS_FETCHED"


def test_protected_news_route_with_expired_token(client):
    expired_token = create_token(exp_delta_minutes=-5)
    response = client.get(
        "/news/all?page=1&page_size=10",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401
    body = response.json()
    assert body["detail"] == "Token has expired"


def test_protected_news_route_with_invalid_token(client):
    invalid_token = "this.is.not.a.valid.token"
    response = client.get(
        "/news/all?page=1&page_size=10",
        headers={"Authorization": f"Bearer {invalid_token}"},
    )
    assert response.status_code == 401
    body = response.json()
    assert body["detail"] == "Invalid token"
