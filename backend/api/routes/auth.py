"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional
from backend.models.database import get_db
from backend.models.user import User, RefreshToken, UserRole
from backend.models.alert import AuditLog
from backend.auth.jwt import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, decode_token
)
from backend.auth.totp import generate_totp_secret, get_totp_uri, generate_qr_code, verify_totp
from backend.auth.dependencies import get_current_user, get_current_active_user
from backend.config import settings

router = APIRouter()
security = HTTPBearer()


class LoginRequest(BaseModel):
    """Login request model"""
    username: str
    password: str
    totp_code: Optional[str] = None


class LoginResponse(BaseModel):
    """Login response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RegisterRequest(BaseModel):
    """Registration request model"""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Refresh token request model"""
    refresh_token: str


class TOTPSetupResponse(BaseModel):
    """TOTP setup response"""
    secret: str
    qr_code: str
    uri: str


class TOTPVerifyRequest(BaseModel):
    """TOTP verification request"""
    totp_code: str


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    req: Request,
    db: Session = Depends(get_db)
):
    """Login endpoint with optional 2FA"""
    user = db.query(User).filter(User.username == request.username).first()
    
    if not user or not verify_password(request.password, user.hashed_password):
        # Track failed login
        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                user.locked_until = datetime.utcnow() + timedelta(minutes=settings.LOCKOUT_DURATION_MINUTES)
            db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account locked until {user.locked_until}"
        )
    
    # Check if 2FA is enabled
    if user.totp_enabled:
        if not request.totp_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA code required"
            )
        if not verify_totp(user.totp_secret, request.totp_code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid 2FA code"
            )
    
    # Reset failed attempts
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id, "username": user.username, "role": user.role.value})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    # Save refresh token
    db_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(db_token)
    
    # Audit log
    audit = AuditLog(
        user_id=user.id,
        action="login",
        ip_address=req.client.host if req.client else None,
        user_agent=req.headers.get("user-agent")
    )
    db.add(audit)
    db.commit()
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "full_name": user.full_name
        }
    )


@router.post("/register", response_model=LoginResponse)
async def register(
    request: RegisterRequest,
    req: Request,
    db: Session = Depends(get_db)
):
    """Register new user (Admin only in production)"""
    # Check if username exists
    if db.query(User).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check if email exists
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Create user
    user = User(
        username=request.username,
        email=request.email,
        hashed_password=get_password_hash(request.password),
        full_name=request.full_name,
        role=UserRole.READ_ONLY,  # Default role
        is_active=True,
        is_verified=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id, "username": user.username, "role": user.role.value})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    # Save refresh token
    db_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(db_token)
    
    # Audit log
    audit = AuditLog(
        user_id=user.id,
        action="register",
        ip_address=req.client.host if req.client else None,
        user_agent=req.headers.get("user-agent")
    )
    db.add(audit)
    db.commit()
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "full_name": user.full_name
        }
    )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token"""
    payload = decode_token(request.refresh_token)
    
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Check if refresh token exists and is valid
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == request.refresh_token,
        RefreshToken.user_id == user_id,
        RefreshToken.revoked == False
    ).first()
    
    if not db_token or db_token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired or revoked"
        )
    
    # Create new tokens
    access_token = create_access_token(data={"sub": user.id, "username": user.username, "role": user.role.value})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    # Revoke old refresh token
    db_token.revoked = True
    
    # Save new refresh token
    db_new_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(db_new_token)
    db.commit()
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "full_name": user.full_name
        }
    )


@router.post("/setup-2fa", response_model=TOTPSetupResponse)
async def setup_2fa(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Setup 2FA for current user"""
    if current_user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA already enabled"
        )
    
    secret = generate_totp_secret()
    current_user.totp_secret = secret
    db.commit()
    
    uri = get_totp_uri(current_user.username, secret)
    qr_code = generate_qr_code(uri)
    
    return TOTPSetupResponse(
        secret=secret,
        qr_code=qr_code,
        uri=uri
    )


@router.post("/verify-2fa")
async def verify_2fa(
    request: TOTPVerifyRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Verify and enable 2FA"""
    if not current_user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA not set up. Call /setup-2fa first"
        )
    
    if not verify_totp(current_user.totp_secret, request.totp_code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid 2FA code"
        )
    
    current_user.totp_enabled = True
    db.commit()
    
    return {"message": "2FA enabled successfully"}


@router.post("/disable-2fa")
async def disable_2fa(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Disable 2FA for current user"""
    current_user.totp_enabled = False
    current_user.totp_secret = None
    db.commit()
    
    return {"message": "2FA disabled successfully"}


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role.value,
        "full_name": current_user.full_name,
        "totp_enabled": current_user.totp_enabled,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Logout and revoke refresh tokens"""
    # Revoke all refresh tokens for user
    db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id,
        RefreshToken.revoked == False
    ).update({"revoked": True})
    db.commit()
    
    return {"message": "Logged out successfully"}

