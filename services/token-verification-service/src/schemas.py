"""
Pydantic schemas for token verification service
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TokenVerificationRequest(BaseModel):
    wallet_address: str
    token_id: int
    contract_address: str
    network: str  # ethereum, polygon, arbitrum


class TokenVerificationResponse(BaseModel):
    valid: bool
    tier: Optional[str] = None
    expires_at: Optional[datetime] = None
    network: str
    contract_address: str
    token_id: int
    wallet_address: str


class TokenInfo(BaseModel):
    token_id: int
    tier: str
    network: str
    contract_address: str


class UserTiersResponse(BaseModel):
    wallet_address: str
    tiers: List[TokenInfo]


class TokenDetailsResponse(BaseModel):
    token_id: int
    tier: str
    network: str
    contract_address: str
    owner: Optional[str] = None

