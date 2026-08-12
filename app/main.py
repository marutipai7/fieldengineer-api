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
# from app.profile.registration import router as auth_rout
from app.profile.auth.registration import router as auth_router
from app.profile.profile import router as profile_router
from app.profile.address import router as address_router
from app.booking.booking import router as booking_router
from app.help_support.help import router as help_router
from app.booking.lead import router as lead_router
from app.fieldengineer.help import router as field_engineer_help_router
from app.payment_method.payment import router as payment_router
from app.fieldengineer.services import router as field_engineer_services_router
from app.chat.chat import router as chat_router
from app.inappcall.call import router as inappcall_router
from app.fieldengineer.work_preferences import router as work_preference_router

import redis.asyncio as redis

from app.profile.models import User
from app.booking.models import FieldEngineerService
from app.notifications.models import Notification


from app.notifications.routes import router as notifications_router
from app.notifications.redis_listener import start_notification_listener



# logger = logging.getLogger(__name__)

# app = FastAPI(title="FieldEngineer API")



logger = logging.getLogger(__name__)

notification_listener_task = None



@asynccontextmanager
async def lifespan(app: FastAPI):
    global notification_listener_task

    logger.info("🚀 FieldEngineer API starting...")

    redis_client = redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
    )

    try:
        await redis_client.ping()
        logger.info("✅ Redis connected")

        notification_listener_task = asyncio.create_task(
            start_notification_listener(redis_client)
        )
        logger.info("✅ Notification listener task started")
        yield

    finally:
        logger.info("🛑 FieldEngineer API shutting down...")

        if notification_listener_task:
            notification_listener_task.cancel()

            try:
                await notification_listener_task
            except asyncio.CancelledError:
                pass

        await redis_client.close()


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
app.include_router(field_engineer_help_router)
app.include_router(field_engineer_services_router)
app.include_router(work_preference_router)

BASE_DIR = Path(__file__).resolve().parent

UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

@app.get("/config")
def config():
    return {
        "app_name": settings.APP_NAME,
        "database": settings.POSTGRES_DB,
        "email_enabled": settings.EMAIL_ENABLED
    }

@app.get("/db-check")
def db_check():
    try:
        with engine.connect() as conn:
            version = conn.execute(
                text("SELECT version();")
            ).scalar()

        return {
            "success": True,
            "database": "connected",
            "version": version
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/db-url")
def db_url():
    return {"url": settings.database_url}
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(address_router)
app.include_router(booking_router)
app.include_router(help_router)
app.include_router(payment_router)
app.include_router(chat_router)
app.include_router(inappcall_router)
app.include_router(notifications_router)