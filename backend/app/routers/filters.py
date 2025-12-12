from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..database import get_supabase
from ..config import settings
from ..schemas.filter import (
    FilterCreate,
    FilterUpdate,
    FilterResponse,
    FilterListResponse
)
from .auth import get_current_user

router = APIRouter(prefix="/filters", tags=["Filters"])


def get_user_plan_limit(plan_type: str) -> int:
    if plan_type == "pro":
        return settings.PRO_PLAN_TERM_LIMIT
    return settings.FREE_PLAN_TERM_LIMIT


@router.get("", response_model=FilterListResponse)
async def list_filters(current_user=Depends(get_current_user)):
    supabase = get_supabase()

    # Get user profile for plan type
    profile = supabase.table("ecoa_profiles").select("plan_type").eq(
        "id", current_user.id
    ).single().execute()

    plan_type = profile.data.get("plan_type", "free") if profile.data else "free"
    plan_limit = get_user_plan_limit(plan_type)

    # Get filters with match counts
    filters_result = supabase.table("ecoa_monitored_terms").select(
        "*, ecoa_news_term_matches(count)"
    ).eq("user_id", current_user.id).order("created_at", desc=True).execute()

    filters = []
    for f in filters_result.data or []:
        match_count = 0
        if f.get("ecoa_news_term_matches"):
            match_count = len(f["ecoa_news_term_matches"])

        filters.append(FilterResponse(
            id=f["id"],
            user_id=f["user_id"],
            term=f["term"],
            is_active=f["is_active"],
            created_at=f["created_at"],
            match_count=match_count
        ))

    return FilterListResponse(
        items=filters,
        total=len(filters),
        limit_reached=len(filters) >= plan_limit,
        plan_limit=plan_limit
    )


@router.post("", response_model=FilterResponse)
async def create_filter(filter_data: FilterCreate, current_user=Depends(get_current_user)):
    supabase = get_supabase()

    # Check plan limit
    profile = supabase.table("ecoa_profiles").select("plan_type").eq(
        "id", current_user.id
    ).single().execute()

    plan_type = profile.data.get("plan_type", "free") if profile.data else "free"
    plan_limit = get_user_plan_limit(plan_type)

    # Count existing filters
    existing = supabase.table("ecoa_monitored_terms").select(
        "id", count="exact"
    ).eq("user_id", current_user.id).execute()

    if existing.count >= plan_limit:
        raise HTTPException(
            status_code=403,
            detail=f"Limite de {plan_limit} termos atingido. Faça upgrade para o plano Pro."
        )

    # Check if term already exists for this user
    existing_term = supabase.table("ecoa_monitored_terms").select("id").eq(
        "user_id", current_user.id
    ).eq("term", filter_data.term.lower()).execute()

    if existing_term.data:
        raise HTTPException(status_code=400, detail="Termo já cadastrado")

    # Create filter
    new_filter = supabase.table("ecoa_monitored_terms").insert({
        "user_id": current_user.id,
        "term": filter_data.term.lower(),
        "is_active": filter_data.is_active
    }).execute()

    if not new_filter.data:
        raise HTTPException(status_code=500, detail="Erro ao criar filtro")

    f = new_filter.data[0]
    return FilterResponse(
        id=f["id"],
        user_id=f["user_id"],
        term=f["term"],
        is_active=f["is_active"],
        created_at=f["created_at"],
        match_count=0
    )


@router.put("/{filter_id}", response_model=FilterResponse)
async def update_filter(
    filter_id: str,
    filter_data: FilterUpdate,
    current_user=Depends(get_current_user)
):
    supabase = get_supabase()

    # Check ownership
    existing = supabase.table("ecoa_monitored_terms").select("*").eq(
        "id", filter_id
    ).eq("user_id", current_user.id).single().execute()

    if not existing.data:
        raise HTTPException(status_code=404, detail="Filtro não encontrado")

    # Update
    update_data = filter_data.model_dump(exclude_unset=True)
    if "term" in update_data:
        update_data["term"] = update_data["term"].lower()

    updated = supabase.table("ecoa_monitored_terms").update(update_data).eq(
        "id", filter_id
    ).execute()

    f = updated.data[0]
    return FilterResponse(
        id=f["id"],
        user_id=f["user_id"],
        term=f["term"],
        is_active=f["is_active"],
        created_at=f["created_at"],
        match_count=0
    )


@router.delete("/{filter_id}")
async def delete_filter(filter_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase()

    # Check ownership
    existing = supabase.table("ecoa_monitored_terms").select("id").eq(
        "id", filter_id
    ).eq("user_id", current_user.id).single().execute()

    if not existing.data:
        raise HTTPException(status_code=404, detail="Filtro não encontrado")

    # Delete related matches first
    supabase.table("ecoa_news_term_matches").delete().eq("term_id", filter_id).execute()

    # Delete filter
    supabase.table("ecoa_monitored_terms").delete().eq("id", filter_id).execute()

    return {"message": "Filtro removido com sucesso"}
