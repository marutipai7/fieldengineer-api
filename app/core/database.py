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
use_fake_redis = False


async def get_redis() -> redis.Redis:
    global redis_client
    global use_fake_redis

    if redis_client is None:
        # Try to connect to real Redis first
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )

        try:
            await redis_client.ping()
            logger.info("✅ Connected to real Redis")
        except Exception as exc:
            logger.warning(f"⚠️ Real Redis unavailable ({exc}). Using fakeredis for development.")
            # Fall back to fakeredis
            try:
                import fakeredis.aioredis
                redis_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
                use_fake_redis = True
                logger.info("✅ Using fakeredis (in-process)")
            except Exception as fallback_exc:
                logger.error(f"❌ Failed to initialize fakeredis: {fallback_exc}")
                raise

    return redis_client


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()