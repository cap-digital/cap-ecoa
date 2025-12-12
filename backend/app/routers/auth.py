from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from ..database import get_supabase
from ..schemas.user import (
    UserCreate,
    UserLogin,
    UserUpdate,
    UserResponse,
    TokenResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Token não fornecido")

    token = authorization.replace("Bearer ", "")
    supabase = get_supabase()

    try:
        user = supabase.auth.get_user(token)
        if not user:
            raise HTTPException(status_code=401, detail="Token inválido")
        return user.user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    supabase = get_supabase()

    try:
        # Create user in Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "full_name": user_data.full_name,
                    "political_name": user_data.political_name,
                    "party": user_data.party,
                    "state": user_data.state,
                }
            }
        })

        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Erro ao criar usuário")

        # Create profile in profiles table
        profile_data = {
            "id": auth_response.user.id,
            "full_name": user_data.full_name,
            "political_name": user_data.political_name,
            "party": user_data.party,
            "state": user_data.state,
            "plan_type": "free"
        }

        supabase.table("ecoa_profiles").insert(profile_data).execute()

        return TokenResponse(
            access_token=auth_response.session.access_token,
            user=UserResponse(
                id=auth_response.user.id,
                email=auth_response.user.email,
                full_name=user_data.full_name,
                political_name=user_data.political_name,
                party=user_data.party,
                state=user_data.state,
                plan_type="free"
            )
        )
    except Exception as e:
        if "already registered" in str(e).lower():
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    supabase = get_supabase()

    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })

        if not auth_response.user:
            raise HTTPException(status_code=401, detail="Credenciais inválidas")

        # Get profile data
        profile = supabase.table("ecoa_profiles").select("*").eq(
            "id", auth_response.user.id
        ).single().execute()

        profile_data = profile.data if profile.data else {}

        return TokenResponse(
            access_token=auth_response.session.access_token,
            user=UserResponse(
                id=auth_response.user.id,
                email=auth_response.user.email,
                full_name=profile_data.get("full_name"),
                political_name=profile_data.get("political_name"),
                party=profile_data.get("party"),
                state=profile_data.get("state"),
                avatar_url=profile_data.get("avatar_url"),
                plan_type=profile_data.get("plan_type", "free"),
                created_at=profile_data.get("created_at")
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")


@router.post("/logout")
async def logout(current_user=Depends(get_current_user)):
    supabase = get_supabase()
    try:
        supabase.auth.sign_out()
        return {"message": "Logout realizado com sucesso"}
    except Exception:
        return {"message": "Logout realizado"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    supabase = get_supabase()

    profile = supabase.table("ecoa_profiles").select("*").eq(
        "id", current_user.id
    ).single().execute()

    profile_data = profile.data if profile.data else {}

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=profile_data.get("full_name"),
        political_name=profile_data.get("political_name"),
        party=profile_data.get("party"),
        state=profile_data.get("state"),
        avatar_url=profile_data.get("avatar_url"),
        plan_type=profile_data.get("plan_type", "free"),
        created_at=profile_data.get("created_at")
    )


@router.put("/me", response_model=UserResponse)
async def update_me(user_data: UserUpdate, current_user=Depends(get_current_user)):
    supabase = get_supabase()

    update_data = user_data.model_dump(exclude_unset=True)

    if update_data:
        supabase.table("ecoa_profiles").update(update_data).eq(
            "id", current_user.id
        ).execute()

    return await get_me(current_user)
