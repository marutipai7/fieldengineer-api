import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

redis_client = None


async def get_redis() -> redis.Redis:
    global redis_client

    if redis_client is None:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )

    try:
        await redis_client.ping()
    except Exception as exc:
        logger.warning(f"Redis ping failed, reconnecting: {exc}")
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )
        await redis_client.ping()

    return redis_client


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()