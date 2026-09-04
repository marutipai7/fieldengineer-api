import asyncio
from sqlalchemy import text
import logging
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.core.config import settings
from app.core.database import engine
# Load models BEFORE routers
from app.profile.models import User
from app.booking.models import FieldEngineerService
from app.notifications.models import Notification
# from app.profile.registration import router as auth_rout
from app.profile.auth.registration import router as auth_router
from app.profile.profile import router as profile_router
from app.profile.profile import invite_redirect_router
from app.profile.address import router as address_router
from app.booking.booking import router as booking_router
from app.booking.lead import router as lead_router
from app.payment_method.payment import router as payment_router
from app.fieldengineer.services import router as field_engineer_services_router
from app.chat.chat import router as chat_router
from app.inappcall.call import router as inappcall_router
from app.fieldengineer.work_preferences import router as work_preference_router
# from app.notifications.routers import (
#     router as notification_router,
#     ws_router as notification_ws_router,
# )

#from app.notifications.routes import router as notification_router
from app.notifications.routers import router as notification_router
from app.fieldengineer.services import router as field_engineer_router
import redis.asyncio as redis
from app.notifications.redis_listener import start_notification_listener
from app.settings_support.Support_setting import router as settings_support_router
from app.settings_support.permissions import router as permissions_router
from app.settings_support.models import UserPermission
from app.settings_support.notification import router as notification_settings_router



# logger = logging.getLogger(__name__)

# app = FastAPI(title="FieldEngineer API")



logger = logging.getLogger(__name__)

notification_listener_task = None



@asynccontextmanager
async def lifespan(app: FastAPI):
    global notification_listener_task

    logger.info("🚀 FieldEngineer API starting...")

    redis_client = None

    try:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
        )

        await redis_client.ping()
        logger.info("✅ Redis connected")

        notification_listener_task = asyncio.create_task(
            start_notification_listener(redis_client)
        )
        logger.info("✅ Notification listener task started")

    except Exception as exc:
        logger.warning(
            f"⚠️ Real Redis unavailable ({exc}). "
            "Attempting to use fakeredis for development..."
        )
        try:
            import fakeredis.aioredis
            redis_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
            logger.info("✅ Using fakeredis (in-process)")
            
            notification_listener_task = asyncio.create_task(
                start_notification_listener(redis_client)
            )
            logger.info("✅ Notification listener task started with fakeredis")
        except Exception as fallback_exc:
            logger.warning(
                f"⚠️ Fakeredis also unavailable ({fallback_exc}). "
                "Starting without real-time notifications."
            )
            notification_listener_task = None

    try:
        yield

    finally:
        logger.info("🛑 FieldEngineer API shutting down...")

        if notification_listener_task:
            notification_listener_task.cancel()

            try:
                await notification_listener_task
            except asyncio.CancelledError:
                pass

        if redis_client is not None:
            try:
                await redis_client.close()
            except Exception:
                pass


app = FastAPI(
    title="FieldEngineer API",
    lifespan=lifespan,
)



@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": [
                {
                    "loc": err.get("loc"),
                    "msg": err.get("msg"),
                    "type": err.get("type"),
                }
                for err in exc.errors()
            ]
        },
    )

app.include_router(lead_router)
app.include_router(field_engineer_services_router)
app.include_router(work_preference_router)

BASE_DIR = Path(__file__).resolve().parent.parent

UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")


app.include_router(auth_router)
app.include_router(invite_redirect_router)
app.include_router(profile_router)
app.include_router(address_router)
app.include_router(booking_router)
app.include_router(payment_router)
app.include_router(chat_router)
app.include_router(inappcall_router)
app.include_router(notification_router)
# app.include_router(notification_ws_router)
# app.include_router(field_engineer_router)
app.include_router(notification_router)
app.include_router(settings_support_router)
app.include_router(permissions_router)
app.include_router(notification_settings_router)