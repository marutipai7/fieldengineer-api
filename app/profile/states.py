from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.profile.models import State, Country
from app.profile.schemas import (
    StateSchema,
    StateCreateSchema,
    StateUpdateSchema
)

router = APIRouter(
    prefix="/states",
    tags=["States"]
)


@router.get("", response_model=list[StateSchema])
async def get_all_states(
    country_id: int = Query(None, description="Filter by country ID"),
    search: str = Query(None, description="Search by state name or code"),
    db: Session = Depends(get_db)
):
    """
    Get all states with optional filtering by country or search term.
    
    Query Parameters:
    - country_id: Filter by country ID
    - search: Search by state name or code
    """
    query = select(State)
    
    if country_id:
        # Verify country exists
        country = db.execute(
            select(Country).where(Country.id == country_id)
        ).scalars().first()
        
        if not country:
            raise HTTPException(
                status_code=404,
                detail="Country not found"
            )
        
        query = query.where(State.country_id == country_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            (State.name.ilike(search_term)) | 
            (State.code.ilike(search_term))
        )
    
    states = db.execute(
        query.order_by(State.name)
    ).scalars().all()
    
    return states


@router.get("/{state_id}", response_model=StateSchema)
async def get_state(
    state_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific state by ID."""
    state = db.execute(
        select(State).where(State.id == state_id)
    ).scalars().first()
    
    if not state:
        raise HTTPException(
            status_code=404,
            detail="State not found"
        )
    
    return state


@router.get("/by-country/{country_id}", response_model=list[StateSchema])
async def get_states_by_country(
    country_id: int,
    db: Session = Depends(get_db)
):
    """Get all states for a specific country by country ID."""
    # Verify country exists
    country = db.execute(
        select(Country).where(Country.id == country_id)
    ).scalars().first()
    
    if not country:
        raise HTTPException(
            status_code=404,
            detail="Country not found"
        )
    
    states = db.execute(
        select(State)
        .where(State.country_id == country_id)
        .order_by(State.name)
    ).scalars().all()
    
    return states


@router.get("/by-country-code/{country_code}", response_model=list[StateSchema])
async def get_states_by_country_code(
    country_code: str,
    db: Session = Depends(get_db)
):
    """Get all states for a specific country by country code."""
    country = db.execute(
        select(Country).where(Country.code == country_code.upper())
    ).scalars().first()
    
    if not country:
        raise HTTPException(
            status_code=404,
            detail="Country not found"
        )
    
    states = db.execute(
        select(State)
        .where(State.country_id == country.id)
        .order_by(State.name)
    ).scalars().all()
    
    return states


@router.post("", response_model=StateSchema)
async def create_state(
    payload: StateCreateSchema,
    db: Session = Depends(get_db)
):
    """Create a new state."""
    # Verify country exists
    country = db.execute(
        select(Country).where(Country.id == payload.country_id)
    ).scalars().first()
    
    if not country:
        raise HTTPException(
            status_code=404,
            detail="Country not found"
        )
    
    # Check if state already exists for this country
    existing = db.execute(
        select(State).where(
            (State.name == payload.name) &
            (State.country_id == payload.country_id)
        )
    ).scalars().first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="State already exists for this country"
        )
    
    state = State(
        name=payload.name,
        code=payload.code.upper(),
        country_id=payload.country_id
    )
    
    db.add(state)
    db.commit()
    db.refresh(state)
    
    return state


@router.put("/{state_id}", response_model=StateSchema)
async def update_state(
    state_id: int,
    payload: StateUpdateSchema,
    db: Session = Depends(get_db)
):
    """Update a state."""
    state = db.execute(
        select(State).where(State.id == state_id)
    ).scalars().first()
    
    if not state:
        raise HTTPException(
            status_code=404,
            detail="State not found"
        )
    
    # If country_id is being changed, verify new country exists
    if payload.country_id and payload.country_id != state.country_id:
        country = db.execute(
            select(Country).where(Country.id == payload.country_id)
        ).scalars().first()
        
        if not country:
            raise HTTPException(
                status_code=404,
                detail="Country not found"
            )
    
    # If name is being changed, check for duplicates in the same country
    if payload.name and payload.name != state.name:
        country_id = payload.country_id or state.country_id
        existing = db.execute(
            select(State).where(
                (State.name == payload.name) &
                (State.country_id == country_id) &
                (State.id != state_id)
            )
        ).scalars().first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail="State already exists for this country"
            )
    
    if payload.name is not None:
        state.name = payload.name
    
    if payload.code is not None:
        state.code = payload.code.upper()
    
    if payload.country_id is not None:
        state.country_id = payload.country_id
    
    db.commit()
    db.refresh(state)
    
    return state


@router.delete("/{state_id}")
async def delete_state(
    state_id: int,
    db: Session = Depends(get_db)
):
    """Delete a state."""
    state = db.execute(
        select(State).where(State.id == state_id)
    ).scalars().first()
    
    if not state:
        raise HTTPException(
            status_code=404,
            detail="State not found"
        )
    
    db.delete(state)
    db.commit()
    
    return {
        "message": "State deleted successfully"
    }
