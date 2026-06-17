import os
# import uuid
from pathlib import Path
from datetime import datetime
import aiofiles
from fastapi import UploadFile, HTTPException
from typing import Optional
from app.config import BASE_URL


# =========================================
# Base Upload Directories
# =========================================
# Get the absolute path to the app directory
APP_DIR = Path(__file__).parent.parent  # Goes up from utils to app directory
BASE_UPLOAD_DIR = APP_DIR / "uploads"
BASE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)