"""
Auth Service - FastAPI Application
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import logging

from .database.connection import get_db, init_db
from .database.models import User, Subscription, TokenVerification
from .auth.jwt import create_access_token, get_password_hash, verify_password
from .auth.dependencies import get_current_user, get_optional_current_user
from .schemas import (
    UserResponse, UserCreate, UserUpdate,
    Token, LoginRequest, RegisterRequest,
    WalletLinkRequest, WalletVerifyRequest,
    SubscriptionResponse, SubscriptionCreate
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Auth Service",
    version="1.0.0",
    description="Centralized authentication and user management"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    # #region agent log
    from .debug_log import debug_log
    debug_log("debug-session", "startup", "H2", "auth-service/src/server.py:41", "Auth service startup initiated", {"event": "startup"})
    # #endregion
    try:
        # #region agent log
        debug_log("debug-session", "startup", "H4", "auth-service/src/server.py:45", "Calling init_db()", {"before_init": True})
        # #endregion
        init_db()
        # #region agent log
        debug_log("debug-session", "startup", "H4", "auth-service/src/server.py:49", "init_db() completed successfully", {"after_init": True})
        # #endregion
        logger.info("Auth Service started")
        # #region agent log
        debug_log("debug-session", "startup", "H2", "auth-service/src/server.py:52", "Auth service startup successful", {"status": "success"})
        # #endregion
    except Exception as e:
        # #region agent log
        debug_log("debug-session", "startup", "H2,H4", "auth-service/src/server.py:55", "Auth service startup failed", {"error": str(e), "error_type": type(e).__name__})
        # #endregion
        logger.error(f"Error during startup: {str(e)}")
        raise


@app.get("/health")
async def health():
    """Health check"""
    # #region agent log
    from .debug_log import debug_log
    debug_log("debug-session", "health", "H2,H3", "auth-service/src/server.py:52", "Health check endpoint called", {"service": "auth-service"})
    # #endregion
    return {"status": "healthy", "service": "auth-service"}


# Authentication endpoints
@app.post("/v1/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        email=request.email,
        password_hash=get_password_hash(request.password),
        wallet_address=request.wallet_address,
        tier='free'
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"User registered: {user.email}")
    return user


@app.post("/v1/auth/login", response_model=Token)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login with email and password"""
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 86400  # 24 hours
    }


@app.post("/v1/auth/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """Logout (client should discard token)"""
    # In a production system, you might want to blacklist the token
    # For now, we just return success
    return {"message": "Logged out successfully"}


@app.post("/v1/auth/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_user)
):
    """Refresh access token"""
    access_token = create_access_token(data={"sub": str(current_user.id), "email": current_user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 86400
    }


@app.get("/v1/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user


# Wallet management endpoints
@app.post("/v1/wallet/link")
async def link_wallet(
    request: WalletLinkRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Link wallet address to user account"""
    # TODO: Verify signature
    # For now, we'll just link the address
    current_user.wallet_address = request.wallet_address
    db.commit()
    db.refresh(current_user)
    
    return {"message": "Wallet linked successfully", "wallet_address": current_user.wallet_address}


@app.post("/v1/wallet/verify")
async def verify_wallet(
    request: WalletVerifyRequest,
    db: Session = Depends(get_db)
):
    """Verify wallet signature"""
    # TODO: Implement signature verification
    # This should verify that the user controls the wallet
    return {"verified": True, "wallet_address": request.wallet_address}


@app.get("/v1/wallet/addresses")
async def get_wallet_addresses(
    current_user: User = Depends(get_current_user)
):
    """Get user's linked wallet addresses"""
    addresses = []
    if current_user.wallet_address:
        addresses.append(current_user.wallet_address)
    return {"addresses": addresses}


# User management endpoints
@app.get("/v1/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user by ID (users can only view their own profile)"""
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )
    return current_user


@app.put("/v1/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user (users can only update their own profile)"""
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    # Update fields
    if user_update.email is not None:
        current_user.email = user_update.email
    if user_update.wallet_address is not None:
        current_user.wallet_address = user_update.wallet_address
    if user_update.tier is not None:
        current_user.tier = user_update.tier
    
    db.commit()
    db.refresh(current_user)
    return current_user


@app.get("/v1/users/{user_id}/tier")
async def get_user_tier(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user tier"""
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Get highest active subscription tier
    active_subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.is_active == True
    ).order_by(
        Subscription.created_at.desc()
    ).first()
    
    tier = active_subscription.tier if active_subscription else current_user.tier
    
    return {"user_id": user_id, "tier": tier}


# Subscription endpoints
@app.get("/v1/subscriptions", response_model=List[SubscriptionResponse])
async def get_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's subscriptions"""
    subscriptions = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).all()
    return subscriptions


@app.post("/v1/subscriptions", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new subscription"""
    # Update user tier if this is higher
    tier_order = {'free': 0, 'bronze': 1, 'silver': 2, 'gold': 3}
    if tier_order.get(subscription.tier, 0) > tier_order.get(current_user.tier, 0):
        current_user.tier = subscription.tier
    
    new_subscription = Subscription(
        user_id=current_user.id,
        tier=subscription.tier,
        source=subscription.source,
        token_id=subscription.token_id,
        token_contract_address=subscription.token_contract_address,
        token_network=subscription.token_network,
        expires_at=subscription.expires_at,
        is_active=True
    )
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)
    
    return new_subscription


@app.put("/v1/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: str,
    subscription: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update subscription"""
    sub = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id
    ).first()
    
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    # Update fields
    sub.tier = subscription.tier
    sub.source = subscription.source
    sub.token_id = subscription.token_id
    sub.token_contract_address = subscription.token_contract_address
    sub.token_network = subscription.token_network
    sub.expires_at = subscription.expires_at
    
    db.commit()
    db.refresh(sub)
    return sub


@app.delete("/v1/subscriptions/{subscription_id}")
async def cancel_subscription(
    subscription_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel subscription"""
    sub = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id
    ).first()
    
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    sub.is_active = False
    db.commit()
    
    return {"message": "Subscription cancelled"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

