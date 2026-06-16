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



logger = logging.getLogger(__name__)

app = FastAPI(title="FieldEngineer API")

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