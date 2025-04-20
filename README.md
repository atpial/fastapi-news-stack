
# Project Description

fastapi-news-stack is a backend service that authenticates clients using the OAuth2 Client Credentials Grant flow and provides secure access to news data. The application retrieves top headlines and articles from external APIs, stores them in a MySQL database, and exposes endpoints for fetching, filtering, and searching news content.




## Features

- OAuth2 Client Credentials Grant: Secure token-based authentication for client applications using `client_id` and `client_secret`
- News Ingestion: Fetches and stores top headlines and articles in the database from a third-party news provider.
- Filtered Access: Provides endpoints to retrieve news based on source, and/or category.
- Token-Protected Routes: All core endpoints require a valid access token.
- Configurable Setup: Manage environment settings such as DB credentials and API keys via a .env file.
- Docker-Ready: Easily deployable with Docker, with optional support for connecting to a locally running MySQL server.


## Documentation

- Clone the Repository
```bash
git clone https://github.com/your-username/fastapi-news-api.git
cd fastapi-news-api
```

- Create and Activate a Virtual Environment (For Local Dev)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
- Setup Environment Variables
```bash
cp .env.example .env
```
Then, fill in your actual values:
```ini
API_KEY=your_news_api_key
DATABASE_NAME=your_db_name
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
DATABASE_HOST=your_db_host
DATABASE_PORT=your_db_port
```
make sure mysql in running on your machine.

- Install Dependencies
```bash
pip install -r requirements.txt
```

- Initialize the Database and Bootstrap Credentials
Run the setup tool to:

- Create necessary database tables

- Insert default client credentials and secrets
```bash
python setup.py
```





## Run Locally

Make sure your virtual environment is activated and dependencies are installed.

Then simply run:

```bash
uvicorn app.main:app --reload
```
- App will be live at: http://127.0.0.1:8000

- Interactive Swagger docs: http://127.0.0.1:8000/docs

- Redoc: http://127.0.0.1:8000/redoc


## Run with Docker (App inside container, DB on host)

1. Build the Docker image:
```bash
docker build -t fastapi-news .
```

2. Run the container (replace `.env` with your actual environment file):
```bash
docker run --env-file .env -p 8000:8000 fastapi-news
```
make sure `DATABASE_HOST=host.docker.internal` is set in `.env`

## Run All Tests
Make sure you're in the project root and have the test dependencies installed:

```bash
pip install -r requirements.txt
```

Then run:
```bash
pytest
```

- Run Specific Test File
```bash
pytest tests/test_auth.py
```

## Generate Access Token

Use the `/token` endpoint to generate an access token using your `CLIENT_ID` and `CLIENT_SECRET` from the `.env` file that has been updated after running the setup script.

use `Postman` or `curl` to invoke the api. For postman use the following as body:
```bash
{
  "client_id": "string",
  "client_secret": "string"
}
```
For curl, use the following command:
```bash
curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/json" \
  -d '{"client_id": "your_client_id", "client_secret": "your_client_secret"}'
```

**Response**
```bash
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
  "token_type": "Bearer"
}
```

## Use Secured Endpoints
To access secured routes like /news, include the token in the Authorization header:

**Request**
```bash
curl -X GET http://localhost:8000/news \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response**
```json
{
  "data": [...],
  "message": "News fetched successfully",
  "status": 200,
  "error": false,
  "code": "SUCCESS"
}
```

## API Usage Examples and Descriptions
1. `POST /token` – Generate Access Token
Generates an access token using OAuth2 Client Credentials grant type.

- Request
```bash
curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/json" \
  -d '{"client_id": "your_client_id", "client_secret": "your_client_secret"}'
```
- Response
```json
{
  "access_token": "jwt_token_string",
  "token_type": "Bearer"
}
```

2. `GET /news` – Get All News from the NewsAPI
Retrieves all news from NewsAPI with pagination. Requires Bearer token.
- Request
```bash
curl -X GET http://localhost:8000/news?q=apple&from=2025-04-16&to=2025-04-16 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
- Response
```json
{
    "message": "News articles fetched successfully",
    "error": false,
    "code": "NEWS_FETCHED",
    "data": {
        "status": "ok",
        "totalResults": 1642,
        "articles": [
            {
                "source": {
                    "id": null,
                    "name": "MacRumors"
                },
                "author": "Joe Rossignol",
                "title": "Apple to Enable a Lesser-Known iOS 16 Feature on iPhone Demo Units",
                "description": "In its 2025 Environmental Progress Report released today, Apple revealed that it plans to expand its Clean Energy Charging feature to iPhone and iPad demo units on display at Apple Stores and other retail stores across the United States.\n\n\n\n\n\nIntroduced in th…",
                "url": "https://www.macrumors.com/2025/04/16/demo-iphones-ipads-clean-energy-charging/",
                "urlToImage": "https://images.macrumors.com/t/G87q6Sdfxb-VKyDAmgaltn2wINI=/1600x/article-new/2025/01/iPhone-16-Apple-Store-Levels.jpg",
                "publishedAt": "2025-04-16T19:56:13Z",
                "content": "In its 2025 Environmental Progress Report released today, Apple revealed that it plans to expand its Clean Energy Charging feature to iPhone and iPad demo units on display at Apple Stores and other r… [+1339 chars]"
            },
            ...
        ]
    }
}
```

3. `POST /news/save-latest` – Fetch & Save the Top 3 into the db.
- Request
```bash
curl -X POST http://localhost:8000/news/fetch-and-store \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
- Response
```json
{
    "message": "Top 3 articles saved successfully",
    "error": false,
    "code": "ARTICLES_SAVED",
    "data": []
}
```

4. `GET /news/all` – Get Saved News from DB
Fetches news articles stored in the database for the authenticated client.
- Request
```bash
curl -X GET http://localhost:8000/news/all \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
- Response
```json
{
    "message": "Fetched news articles successfully",
    "error": false,
    "code": "ALL_NEWS_FETCHED",
    "data": {
        "total": 9,
        "page": 1,
        "page_size": 10,
        "articles": [
            {
                "id": 7,
                "title": "Google claims it won half of its monopoly case, and will appeal the rest",
                "description": "Following a federal judge ruling that Google is effectively an unlawful monopoly, the search company say that it will partially appeal.Google insists it half-won its case, despite being ruled to be an unlawful monopolyOn April 17, 2025, US District Judge Leon…",
                "url": "https://appleinsider.com/articles/25/04/18/google-claims-it-won-half-of-its-monopoly-case-and-will-appeal-the-rest",
                "published_at": "2025-04-18T14:01:46"
            },
            ...
        ]
    }
}
```

5. `GET /news/headlines/country/{country_code}` – Get Top Headlines by country code
- Request
```bash
curl -X GET http://localhost:8000/news/headlines/country/us \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
- Response
```json
{
    "message": "Top headlines for country: us",
    "error": false,
    "code": "TOP_HEADLINES_FETCHED",
    "data": {
        "status": "ok",
        "totalResults": 37,
        "articles": [
            {
                "source": {
                    "id": "cnn",
                    "name": "CNN"
                },
                "author": "Taylor Nicioli",
                "title": "Scientists stumble across rare evidence that Earth is peeling underneath the Sierra Nevada - CNN",
                "description": "Scientists found new evidence that Earth’s crust is peeling underneath the Sierra Nevada in California. The process might be how the continents formed, they say.",
                "url": "https://www.cnn.com/2025/04/18/science/lithospheric-foundering-earth-peeling-sierra-nevada/index.html",
                "urlToImage": "https://media.cnn.com/api/v1/images/stellar/prod/gettyimages-2207986235.jpg?c=16x9&q=w_800,c_fill",
                "publishedAt": "2025-04-18T11:30:00Z",
                "content": "Sign up for CNNs Wonder Theory science newsletter. Explore the universe with news on fascinating discoveries, scientific advancements and more.\r\nSeismologist Deborah Kilb was wading through Californi… [+8320 chars]"
            },
            ...
        ]
    }
}
```

6. `GET /news/headlines/source/{source_id}` – Get Top Headlines by source
- Request
```bash
curl -X GET http://localhost:8000/news/headlines/source/cnn \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
- Response
```json
{
    "message": "Top headlines for source: cnn",
    "error": false,
    "code": "TOP_HEADLINES_FETCHED",
    "data": {
        "status": "ok",
        "totalResults": 10,
        "articles": [
            {
                "source": {
                    "id": "cnn",
                    "name": "CNN"
                },
                "author": "Luciana Lopez",
                "title": "Trump’s tariffs could make for closer world relationships. But they may not be the ones he wants",
                "description": "President Donald Trump has repeatedly touted what he calls the return of manufacturing to the United States, hailing companies that have vowed to pour large amounts of money into making everything from computer chips to cars in America.",
                "url": "https://www.cnn.com/2025/04/18/economy/global-trade-relationships-trump-tariffs/index.html",
                "urlToImage": "https://media.cnn.com/api/v1/images/stellar/prod/gettyimages-2209432005-20250417015214599.jpg?c=16x9&q=w_800,c_fill",
                "publishedAt": "2025-04-18T13:34:51Z",
                "content": "President Donald Trump has repeatedly touted what he calls the return of manufacturing to the United States, hailing companies that have vowed to pour large amounts of money into making everything fr… [+5224 chars]"
            },
            ...
        ]
    }
}
```

7. `GET /news/headlines/filter`: Fetch top headlines by filtering both country and source
- Request
```bash
curl -X GET http://localhost:8000/news/headlines/filter?country=us&source=cnn \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
- Response
```json
{
    "message": "Top headlines for country: us, source: techcrunch",
    "error": false,
    "code": "TOP_HEADLINES_FETCHED",
    "data": {
        "status": "ok",
        "totalResults": 35,
        "articles": [
            {
                "source": {
                    "id": "abc-news",
                    "name": "ABC News"
                },
                "author": "ABC News",
                "title": "White House changes COVID.gov web page to page supporting lab leak theory - ABC News",
                "description": null,
                "url":"https://abcnews.go.com/Health/white-house-covid-web-page-page-supporting-lab/story?id\\\=120956514",
                "urlToImage": null,
                "publishedAt": "2025-04-18T23:30:42Z",
                "content": null
            },
            ...
        ]
    }
}
```

## Improvement points:
1. Use `async` for External API Calls
- `async` and `httpx.AsyncClient` instead of `requests` can be used to make non-blocking HTTP calls
2. Dockerize Both App and MySQL Using Docker Compose
- a `docker-compose.yml` file can be used to containerize both the FastAPI app and MySQL together
3. Add Caching for Headlines
- In-memory cache (e.g., `functools.lru_cache` or Redis) can be used to reduce redundant News API calls if the headlines are unlikely to change rapidly