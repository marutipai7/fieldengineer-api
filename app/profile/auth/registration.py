from fastapi import APIRouter, Depends, UploadFile, File, Request, HTTPException

router = APIRouter(
    prefix="/auth",
    tags=["Registration"]
)