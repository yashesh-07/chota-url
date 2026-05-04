import os
import redis
from sqlalchemy import create_engine, Column, BigInteger, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# 1. Fetch configurations from .env
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# 2. SQLAlchemy Setup (PostgreSQL)
# We use 'check_same_thread' only for SQLite; for Postgres it's not needed.
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 3. Redis Setup (Caching)
# decode_responses=True ensures we get Python strings instead of bytes
cache = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0, 
    decode_responses=True
)

# 4. Database Model
class URLMapping(Base):
    __tablename__ = "url_mappings"
    
    # We use BigInteger for 'id' to match our 64-bit Snowflake ID
    id = Column(BigInteger, primary_key=True, index=True)
    short_code = Column(String(12), unique=True, index=True)
    long_url = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# 5. Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()