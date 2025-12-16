"""
Pydantic schemas for request/response models
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    wallet_address: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    wallet_address: Optional[str] = None
    tier: Optional[str] = None


class UserResponse(UserBase):
    id: UUID
    tier: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(UserCreate):
    pass


# Wallet schemas
class WalletLinkRequest(BaseModel):
    wallet_address: str
    signature: str
    message: str


class WalletVerifyRequest(BaseModel):
    wallet_address: str
    signature: str
    message: str


# Subscription schemas
class SubscriptionBase(BaseModel):
    tier: str
    source: str  # 'token' or 'traditional'
    token_id: Optional[int] = None
    token_contract_address: Optional[str] = None
    token_network: Optional[str] = None
    expires_at: Optional[datetime] = None


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionResponse(SubscriptionBase):
    id: UUID
    user_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

