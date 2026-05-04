from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware  # <-- Add this import
from sqlalchemy.orm import Session
from pydantic import HttpUrl
from typing import Optional

from app.database import engine, Base, get_db, cache, URLMapping
from app.utils import id_worker, URLConverter

# Initialize FastAPI
app = FastAPI(title="URL Shortener Pro")

# --- ADD THIS CORS BLOCK ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Allows your React dev server
    allow_credentials=True,
    allow_methods=["*"], # Allows POST, GET, OPTIONS, etc.
    allow_headers=["*"], # Allows all headers
)

# Create database tables on startup
Base.metadata.create_all(bind=engine)

# --- Schemas ---
from pydantic import BaseModel

class URLRequest(BaseModel):
    url: HttpUrl

class URLResponse(BaseModel):
    short_code: str
    short_url: str

# --- Endpoints ---

@app.post("/shorten", response_model=URLResponse)
def create_short_url(request: URLRequest, db: Session = Depends(get_db)):
    """
    1. Generates a unique Snowflake ID.
    2. Encodes it to Base62.
    3. Saves to Postgres.
    4. Prime the Redis cache for immediate use.
    """
    long_url_str = str(request.url)
    
    # Generate Unique ID and Short Code
    snowflake_id = id_worker.generate()
    short_code = URLConverter.encode(snowflake_id)
    
    # Save to PostgreSQL
    new_mapping = URLMapping(
        id=snowflake_id,
        short_code=short_code,
        long_url=long_url_str
    )
    db.add(new_mapping)
    db.commit()
    
    # Cache it in Redis (Key: short_code, Value: long_url)
    # We set no expiration as per the 10-year requirement
    cache.set(short_code, long_url_str)
    
    return {
        "short_code": short_code,
        "short_url": f"http://localhost:8000/{short_code}"
    }

@app.get("/{short_code}")
def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    """
    1. Check Redis Cache first (O(1) time complexity).
    2. If not in cache, check Postgres.
    3. If found in Postgres, update cache and redirect.
    """
    # 1. Try Redis Cache
    cached_url = cache.get(short_code)
    if cached_url:
        return RedirectResponse(url=cached_url)

    # 2. Try PostgreSQL
    db_mapping = db.query(URLMapping).filter(URLMapping.short_code == short_code).first()
    
    if db_mapping:
        # 3. Update Cache for next time
        cache.set(short_code, db_mapping.long_url)
        return RedirectResponse(url=db_mapping.long_url)
    
    # 4. Not found
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="URL not found"
    )

@app.get("/health")
def health_check():
    return {"status": "online"}