from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.profile.models import Country
from app.profile.schemas import (
    CountrySchema,
    CountryCreateSchema,
    CountryUpdateSchema
)

router = APIRouter(
    prefix="/countries",
    tags=["Countries"]
)


@router.get("", response_model=list[CountrySchema])
async def get_all_countries(
    region: str = Query(None, description="Filter by region"),
    search: str = Query(None, description="Search by country name or code"),
    db: Session = Depends(get_db)
):
    """
    Get all countries with optional filtering by region or search term.
    
    Query Parameters:
    - region: Filter by region (e.g., 'Asia', 'Europe', 'Americas')
    - search: Search by country name or code
    """
    query = select(Country)
    
    if region:
        query = query.where(Country.region == region)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            (Country.name.ilike(search_term)) | 
            (Country.code.ilike(search_term))
        )
    
    countries = db.execute(
        query.order_by(Country.name)
    ).scalars().all()
    
    return countries


@router.get("/{country_id}", response_model=CountrySchema)
async def get_country(
    country_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific country by ID."""
    country = db.execute(
        select(Country).where(Country.id == country_id)
    ).scalars().first()
    
    if not country:
        raise HTTPException(
            status_code=404,
            detail="Country not found"
        )
    
    return country


@router.get("/by-code/{country_code}", response_model=CountrySchema)
async def get_country_by_code(
    country_code: str,
    db: Session = Depends(get_db)
):
    """Get a specific country by ISO country code (e.g., 'US', 'IN', 'GB')."""
    country = db.execute(
        select(Country).where(Country.code == country_code.upper())
    ).scalars().first()
    
    if not country:
        raise HTTPException(
            status_code=404,
            detail="Country not found"
        )
    
    return country


@router.post("", response_model=CountrySchema)
async def create_country(
    payload: CountryCreateSchema,
    db: Session = Depends(get_db)
):
    """Create a new country."""
    # Check if country already exists
    existing = db.execute(
        select(Country).where(
            (Country.code == payload.code.upper()) |
            (Country.name == payload.name)
        )
    ).scalars().first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Country with this name or code already exists"
        )
    
    country = Country(
        name=payload.name,
        code=payload.code.upper(),
        phone_code=payload.phone_code,
        region=payload.region
    )
    
    db.add(country)
    db.commit()
    db.refresh(country)
    
    return country


@router.put("/{country_id}", response_model=CountrySchema)
async def update_country(
    country_id: int,
    payload: CountryUpdateSchema,
    db: Session = Depends(get_db)
):
    """Update an existing country."""
    country = db.execute(
        select(Country).where(Country.id == country_id)
    ).scalars().first()
    
    if not country:
        raise HTTPException(
            status_code=404,
            detail="Country not found"
        )
    
    if payload.name:
        country.name = payload.name
    if payload.code:
        country.code = payload.code.upper()
    if payload.phone_code is not None:
        country.phone_code = payload.phone_code
    if payload.region is not None:
        country.region = payload.region
    
    db.commit()
    db.refresh(country)
    
    return country


@router.delete("/{country_id}")
async def delete_country(
    country_id: int,
    db: Session = Depends(get_db)
):
    """Delete a country."""
    country = db.execute(
        select(Country).where(Country.id == country_id)
    ).scalars().first()
    
    if not country:
        raise HTTPException(
            status_code=404,
            detail="Country not found"
        )
    
    db.delete(country)
    db.commit()
    
    return {
        "message": "Country deleted successfully"
    }


@router.get("/regions/list", response_model=list[str])
async def get_regions(
    db: Session = Depends(get_db)
):
    """Get list of all unique regions."""
    regions = db.execute(
        select(Country.region).distinct().where(Country.region.isnot(None))
    ).scalars().all()
    
    return sorted([r for r in regions if r])
