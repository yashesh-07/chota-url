# Chota-URL (URL Shortener Pro)

Chota-URL is a high-performance, scalable URL shortener built with modern web technologies. It is designed to handle a large volume of URL shortening and redirection requests efficiently, leveraging a fast backend and caching mechanism.

## High-Level Architecture

The system is built using a distributed architecture designed for scalability and low latency.

### Tech Stack
- **Frontend:** React.js, Tailwind CSS, Lucide React
- **API Backend:** FastAPI, Python, SQLAlchemy
- **Primary Database:** PostgreSQL
- **Caching Layer:** Redis
- **Containerization:** Docker & Docker Compose

### System Design Components

1. **Snowflake ID Generator:** 
   To ensure uniqueness across a distributed system without single points of failure, the backend implements a Snowflake ID generator. It generates time-sortable, highly concurrent 64-bit integers.
   
2. **Base62 Encoding:**
   The unique 64-bit Snowflake IDs are converted into concise alphanumeric strings using Base62 encoding (A-Z, a-z, 0-9). This keeps the generated URLs as short as possible.

3. **Two-Tier Storage:**
   - **PostgreSQL** serves as the source of truth, storing the permanent mappings of short codes to original long URLs.
   - **Redis** operates as a caching layer to serve read requests (redirects) at sub-millisecond speeds.

### Request Flows

#### 1. Shortening a URL
1. Client sends a request with the original `long_url` to the backend.
2. The Backend generates a unique Snowflake ID.
3. The ID is encoded into a Base62 `short_code`.
4. The `(short_code, long_url)` pair is persisted to PostgreSQL.
5. The pair is immediately injected into the Redis cache to pre-warm it.
6. The compiled short URL is returned to the client.

#### 2. Redirecting a URL
1. Client requests a built URL (e.g., `http://localhost:8000/aB3`).
2. The Backend queries Redis for the `short_code`.
   - **Cache Hit:** If found, an immediate `307 Redirect` to the original URL is issued.
   - **Cache Miss:** If not found in Redis, the backend queries PostgreSQL.
3. If found in PostgreSQL, the mapping is loaded back into Redis, and the redirection is issued.
4. If the code does not exist in the database, a `404 Not Found` error is returned.

## Getting Started

### Prerequisites
- Docker
- Docker Compose

### Running Locally

You can spin up the entire application stack using Docker Compose.

1. Ensure the `.env` file is properly configured with your desired credentials.
2. Run the following command from the root directory:
   ```bash
   docker-compose up --build
   ```
3. The services will be available at:
   - **Frontend UI:** `http://localhost:3000`
   - **API Backend:** `http://localhost:8000`
   - **PostgreSQL DB:** `localhost:5432`
   - **Redis:** `localhost:6379`

### API Endpoints

- `POST /shorten`: Accepts a JSON payload `{"url": "https://example.com"}` and returns the generated short code and URL.
- `GET /{short_code}`: Redirects to the mapped long URL.
- `GET /health`: Returns the health status of the API.