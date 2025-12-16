"""
Pydantic schemas for API requests and responses
"""

from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


# Enums for schemas
class TierType(str, Enum):
    FREE = "free"
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class ContractType(str, Enum):
    TIERED = "tiered"
    BUNDLE = "bundle"
    COMMUNITY = "community"


class PaymentMethod(str, Enum):
    CRYPTO = "crypto"
    STRIPE = "stripe"
    BANK_TRANSFER = "bank_transfer"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Configuration Schemas
class ProductConfig(BaseModel):
    """Product configuration schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    website: Optional[str] = Field(None, max_length=255)
    logo_url: Optional[str] = Field(None, max_length=500)
    network: str = Field("polygon", max_length=50)
    currency: str = Field("MATIC", max_length=20)
    features: Dict[str, List[str]] = Field(default_factory=dict)


class TierConfig(BaseModel):
    """Tier configuration schema"""
    name: str = Field(..., min_length=1, max_length=100)
    tier_type: TierType
    price: Optional[float] = Field(None, ge=0)
    max_supply: Optional[int] = Field(None, ge=1)
    features: List[str] = Field(default_factory=list)
    limits: Dict[str, Union[int, str]] = Field(default_factory=dict)


class NFTContractConfig(BaseModel):
    """NFT contract configuration schema"""
    contract_address: Optional[str] = Field(None, max_length=255)
    contract_type: ContractType = ContractType.TIERED
    base_uri: str = Field("", max_length=500)
    royalty_fee: int = Field(250, ge=0, le=1000)  # basis points
    transfer_enabled: bool = True


# Request Schemas
class CreateProductRequest(BaseModel):
    """Request to create a new product"""
    product_config: ProductConfig
    tier_configs: List[TierConfig]
    network: str = "polygon"
    
    @validator('tier_configs')
    def validate_tiers(cls, v):
        if not v:
            raise ValueError('At least one tier must be configured')
        return v


class PurchaseNFTRequest(BaseModel):
    """Request to purchase an NFT"""
    product_id: int = Field(..., gt=0)
    tier: str = Field(..., min_length=1)
    wallet_address: str = Field(..., min_length=1)
    payment_method: PaymentMethod = PaymentMethod.CRYPTO
    user_id: Optional[int] = Field(None, gt=0)
    
    @validator('wallet_address')
    def validate_wallet_address(cls, v):
        if not v.startswith('0x') or len(v) != 42:
            raise ValueError('Invalid Ethereum wallet address')
        return v


class VerifyTokenRequest(BaseModel):
    """Request to verify token ownership"""
    wallet_address: str = Field(..., min_length=1)
    product_id: int = Field(..., gt=0)
    tier: Optional[str] = Field(None, min_length=1)
    
    @validator('wallet_address')
    def validate_wallet_address(cls, v):
        if not v.startswith('0x') or len(v) != 42:
            raise ValueError('Invalid Ethereum wallet address')
        return v


class TransferTokenRequest(BaseModel):
    """Request to transfer NFT token"""
    token_id: str = Field(..., min_length=1)
    from_wallet: str = Field(..., min_length=1)
    to_wallet: str = Field(..., min_length=1)
    
    @validator('from_wallet', 'to_wallet')
    def validate_wallet_addresses(cls, v):
        if not v.startswith('0x') or len(v) != 42:
            raise ValueError('Invalid Ethereum wallet address')
        return v


class DeployContractRequest(BaseModel):
    """Request to deploy smart contract"""
    product_id: int = Field(..., gt=0)
    contract_type: ContractType = ContractType.TIERED
    network: str = Field("polygon", max_length=50)
    base_uri: Optional[str] = Field(None, max_length=500)


# Response Schemas
class TokenVerificationResponse(BaseModel):
    """Response for token verification"""
    has_token: bool
    tier: Optional[str] = None
    token_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    features: List[str] = Field(default_factory=list)
    max_supply_reached: bool = False
    transaction_pending: bool = False


class ProductResponse(BaseModel):
    """Product response schema"""
    id: int
    name: str
    description: Optional[str]
    website: Optional[str]
    logo_url: Optional[str]
    network: str
    currency: str
    contract_address: Optional[str]
    contract_type: ContractType
    base_uri: Optional[str]
    royalty_fee: int
    transfer_enabled: bool
    features: Dict[str, List[str]]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TierResponse(BaseModel):
    """Tier response schema"""
    id: int
    product_id: int
    name: str
    tier_type: TierType
    price: Optional[float]
    max_supply: Optional[int]
    features: List[str]
    limits: Dict[str, Union[int, str]]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ContractResponse(BaseModel):
    """Contract response schema"""
    id: int
    product_id: int
    contract_address: str
    contract_type: ContractType
    network: str
    transaction_hash: Optional[str]
    block_number: Optional[int]
    name: Optional[str]
    symbol: Optional[str]
    total_supply: Optional[int]
    verified: bool
    active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TransactionResponse(BaseModel):
    """Transaction response schema"""
    id: int
    product_id: int
    tier_id: int
    wallet_address: str
    token_id: Optional[str]
    transaction_hash: Optional[str]
    payment_method: PaymentMethod
    amount: Optional[float]
    crypto_amount: Optional[float]
    crypto_currency: Optional[str]
    status: TransactionStatus
    gas_fee: Optional[float]
    metadata_uri: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class SmartContractDeployment(BaseModel):
    """Smart contract deployment response"""
    contract_address: str
    network: str
    transaction_hash: str
    block_number: int
    deployed_at: datetime
    gas_used: Optional[int] = None
    deployment_cost: Optional[float] = None


class TokenMetadata(BaseModel):
    """NFT token metadata"""
    name: str
    description: str
    image: str
    attributes: List[Dict[str, str]] = Field(default_factory=list)
    external_url: str = ""


class AnalyticsResponse(BaseModel):
    """Analytics response schema"""
    total_products: int
    total_tokens_minted: int
    total_revenue: float
    active_products: int
    top_products: List[Dict[str, Any]]
    transaction_volume: Dict[str, float]
    network_distribution: Dict[str, int]


class WalletTokensResponse(BaseModel):
    """Wallet tokens response schema"""
    wallet_address: str
    tokens: List[Dict[str, Any]] = Field(default_factory=list)
    total_value: float = 0.0
    network: str = "polygon"


# Database operation schemas
class ProductCreate(BaseModel):
    """Schema for creating a product in database"""
    name: str
    description: Optional[str]
    website: Optional[str]
    logo_url: Optional[str]
    network: str = "polygon"
    currency: str = "MATIC"
    contract_address: Optional[str] = None
    contract_type: ContractType = ContractType.TIERED
    base_uri: Optional[str] = None
    royalty_fee: int = 250
    transfer_enabled: bool = True
    features: Dict[str, List[str]] = Field(default_factory=dict)


class TierCreate(BaseModel):
    """Schema for creating a tier in database"""
    product_id: int
    name: str
    tier_type: TierType
    price: Optional[float]
    max_supply: Optional[int]
    features: List[str] = Field(default_factory=list)
    limits: Dict[str, Union[int, str]] = Field(default_factory=dict)


class TransactionCreate(BaseModel):
    """Schema for creating a transaction in database"""
    product_id: int
    tier_id: int
    user_id: Optional[int]
    wallet_address: str
    token_id: Optional[str]
    transaction_hash: Optional[str]
    payment_method: PaymentMethod = PaymentMethod.CRYPTO
    amount: Optional[float]
    crypto_amount: Optional[float]
    crypto_currency: Optional[str]
    status: TransactionStatus = TransactionStatus.PENDING
    gas_fee: Optional[float]
    metadata_uri: Optional[str]
