from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import timedelta

from ..database import get_db
from ..models import User, PlanType
from ..services.auth import (
    get_password_hash,
    create_access_token,
    authenticate_user,
    get_current_user
)
from ..schemas.user import (
    UserCreate,
    UserLogin,
    UserUpdate,
    UserResponse,
    TokenResponse
)
from ..config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        political_name=user_data.political_name,
        party=user_data.party,
        state=user_data.state,
        plan_type=PlanType.FREE,
        is_active=True,
        is_verified=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate JWT token
    access_token = create_access_token(
        data={"sub": new_user.id},
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return TokenResponse(
        access_token=access_token,
        user=UserResponse(
            id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
            political_name=new_user.political_name,
            party=new_user.party,
            state=new_user.state,
            plan_type=new_user.plan_type.value,
            created_at=new_user.created_at
        )
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, credentials.email, credentials.password)

    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return TokenResponse(
        access_token=access_token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            political_name=user.political_name,
            party=user.party,
            state=user.state,
            avatar_url=user.avatar_url,
            plan_type=user.plan_type.value,
            created_at=user.created_at
        )
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    # JWT é stateless, então logout é feito no cliente removendo o token
    return {"message": "Logout realizado com sucesso"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        political_name=current_user.political_name,
        party=current_user.party,
        state=current_user.state,
        avatar_url=current_user.avatar_url,
        plan_type=current_user.plan_type.value,
        created_at=current_user.created_at
    )


@router.put("/me", response_model=UserResponse)
async def update_me(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    update_data = user_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        political_name=current_user.political_name,
        party=current_user.party,
        state=current_user.state,
        avatar_url=current_user.avatar_url,
        plan_type=current_user.plan_type.value,
        created_at=current_user.created_at
    )
