"""Authentication API routes"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, MessageResponse
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.deps import get_current_user
from app.config import get_settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user (only first user or by existing users)"""
    settings = get_settings()

    # Check if any users exist
    result = await db.execute(select(func.count(User.id)))
    user_count = result.scalar()

    # If users exist, require first user status check
    if user_count > 0:
        # Find first user
        result = await db.execute(select(User).where(User.is_first_user == True))
        first_user = result.scalar_one_or_none()

        if first_user is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Registration is closed"
            )

    # Check if username exists
    result = await db.execute(select(User).where(User.username == user_data.username))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    # Create new user
    is_first = user_count == 0
    new_user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        is_first_user=is_first
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Create token
    token = create_access_token(
        data={"sub": new_user.id},
        expires_delta=timedelta(minutes=settings.jwt_expire_minutes)
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.jwt_expire_minutes * 60
    )


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login and get access token"""
    settings = get_settings()

    # Find user
    result = await db.execute(select(User).where(User.username == user_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create token
    token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=settings.jwt_expire_minutes)
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.jwt_expire_minutes * 60
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """Logout (client-side token removal)"""
    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user