from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..config import settings
from ..models import User, MonitoredTerm, NewsTermMatch
from ..services.auth import get_current_user
from ..schemas.filter import (
    FilterCreate,
    FilterUpdate,
    FilterResponse,
    FilterListResponse
)

router = APIRouter(prefix="/filters", tags=["Filters"])


def get_user_plan_limit(plan_type: str) -> int:
    if plan_type == "pro":
        return settings.PRO_PLAN_TERM_LIMIT
    return settings.FREE_PLAN_TERM_LIMIT


@router.get("", response_model=FilterListResponse)
async def list_filters(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    plan_type = current_user.plan_type.value
    plan_limit = get_user_plan_limit(plan_type)

    # Get filters with match counts
    filters_query = db.query(
        MonitoredTerm,
        func.count(NewsTermMatch.id).label('match_count')
    ).outerjoin(
        NewsTermMatch, MonitoredTerm.id == NewsTermMatch.term_id
    ).filter(
        MonitoredTerm.user_id == current_user.id
    ).group_by(MonitoredTerm.id).order_by(MonitoredTerm.created_at.desc())

    filters_result = filters_query.all()

    filters = []
    for term, match_count in filters_result:
        filters.append(FilterResponse(
            id=term.id,
            user_id=term.user_id,
            term=term.term,
            is_active=term.is_active,
            created_at=term.created_at,
            match_count=match_count or 0
        ))

    return FilterListResponse(
        items=filters,
        total=len(filters),
        limit_reached=len(filters) >= plan_limit,
        plan_limit=plan_limit
    )


@router.post("", response_model=FilterResponse)
async def create_filter(
    filter_data: FilterCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    plan_type = current_user.plan_type.value
    plan_limit = get_user_plan_limit(plan_type)

    # Count existing filters
    existing_count = db.query(MonitoredTerm).filter(
        MonitoredTerm.user_id == current_user.id
    ).count()

    if existing_count >= plan_limit:
        raise HTTPException(
            status_code=403,
            detail=f"Limite de {plan_limit} termos atingido. Faça upgrade para o plano Pro."
        )

    # Check if term already exists for this user
    existing_term = db.query(MonitoredTerm).filter(
        MonitoredTerm.user_id == current_user.id,
        MonitoredTerm.term == filter_data.term.lower()
    ).first()

    if existing_term:
        raise HTTPException(status_code=400, detail="Termo já cadastrado")

    # Create filter
    new_filter = MonitoredTerm(
        user_id=current_user.id,
        term=filter_data.term.lower(),
        is_active=filter_data.is_active
    )

    db.add(new_filter)
    db.commit()
    db.refresh(new_filter)

    return FilterResponse(
        id=new_filter.id,
        user_id=new_filter.user_id,
        term=new_filter.term,
        is_active=new_filter.is_active,
        created_at=new_filter.created_at,
        match_count=0
    )


@router.put("/{filter_id}", response_model=FilterResponse)
async def update_filter(
    filter_id: str,
    filter_data: FilterUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check ownership
    existing = db.query(MonitoredTerm).filter(
        MonitoredTerm.id == filter_id,
        MonitoredTerm.user_id == current_user.id
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Filtro não encontrado")

    # Update
    update_data = filter_data.model_dump(exclude_unset=True)
    if "term" in update_data:
        update_data["term"] = update_data["term"].lower()

    for key, value in update_data.items():
        setattr(existing, key, value)

    db.commit()
    db.refresh(existing)

    return FilterResponse(
        id=existing.id,
        user_id=existing.user_id,
        term=existing.term,
        is_active=existing.is_active,
        created_at=existing.created_at,
        match_count=0
    )


@router.delete("/{filter_id}")
async def delete_filter(
    filter_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check ownership
    existing = db.query(MonitoredTerm).filter(
        MonitoredTerm.id == filter_id,
        MonitoredTerm.user_id == current_user.id
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Filtro não encontrado")

    # Delete (cascade will handle related matches)
    db.delete(existing)
    db.commit()

    return {"message": "Filtro removido com sucesso"}
