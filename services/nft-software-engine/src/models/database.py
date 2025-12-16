"""
SQLAlchemy database models for NFT Software Engine
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

Base = declarative_base()


class TierType(enum.Enum):
    """Tier enumeration"""
    FREE = "free"
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class ContractType(enum.Enum):
    """Contract type enumeration"""
    TIERED = "tiered"
    BUNDLE = "bundle"
    COMMUNITY = "community"


class TransactionStatus(enum.Enum):
    """Transaction status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PaymentMethod(enum.Enum):
    """Payment method enumeration"""
    CRYPTO = "crypto"
    STRIPE = "stripe"
    BANK_TRANSFER = "bank_transfer"


class Product(Base):
    """Product model for NFT tokenized software"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    website = Column(String(255))
    logo_url = Column(String(500))
    network = Column(String(50), default="polygon", index=True)
    currency = Column(String(20), default="MATIC")
    
    # Contract configuration
    contract_address = Column(String(255), index=True)
    contract_type = Column(Enum(ContractType), default=ContractType.TIERED)
    base_uri = Column(String(500))
    royalty_fee = Column(Integer, default=250)  # basis points (2.5%)
    transfer_enabled = Column(Boolean, default=True)
    
    # Metadata
    features = Column(JSON)  # Tier-based feature mapping
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tiers = relationship("Tier", back_populates="product", cascade="all, delete-orphan")
    contracts = relationship("NFTContract", back_populates="product", cascade="all, delete-orphan")
    transactions = relationship("TokenTransaction", back_populates="product")


class Tier(Base):
    """Tier configuration for products"""
    __tablename__ = "tiers"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    tier_type = Column(Enum(TierType), nullable=False, index=True)
    price = Column(Float)  # Price in ETH/Token
    max_supply = Column(Integer)
    features = Column(JSON)  # List of available features
    limits = Column(JSON)  # Usage limits (contacts, workflows, etc.)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="tiers")
    transactions = relationship("TokenTransaction", back_populates="tier")


class NFTContract(Base):
    """Deployed smart contract model"""
    __tablename__ = "nft_contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    contract_address = Column(String(255), nullable=False, unique=True, index=True)
    contract_type = Column(Enum(ContractType), nullable=False)
    network = Column(String(50), nullable=False, index=True)
    
    # Deployment info
    transaction_hash = Column(String(255), index=True)
    block_number = Column(Integer)
    gas_used = Column(Integer)
    deployment_cost = Column(Float)
    
    # Contract metadata
    name = Column(String(255))
    symbol = Column(String(100))
    base_uri = Column(String(500))
    total_supply = Column(Integer)
    
    # Status
    verified = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="contracts")


class TokenTransaction(Base):
    """Token purchase and transfer transactions"""
    __tablename__ = "token_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    tier_id = Column(Integer, ForeignKey("tiers.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    wallet_address = Column(String(255), nullable=False, index=True)
    
    # Transaction details
    token_id = Column(String(255), index=True)
    transaction_hash = Column(String(255), index=True)
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.CRYPTO)
    amount = Column(Float)  # Payment amount in USD
    crypto_amount = Column(Float)  # Crypto payment amount
    crypto_currency = Column(String(20))
    
    # Status
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING, index=True)
    gas_fee = Column(Float)
    block_number = Column(Integer)
    
    # Metadata
    metadata_uri = Column(String(500))
    purchase_ip = Column(String(45))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="transactions")
    tier = relationship("Tier", back_populates="transactions")
    user = relationship("User", back_populates="transactions")


class User(Base):
    """User model for NFT token holders"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    username = Column(String(100), unique=True, index=True, nullable=True)
    
    # Authentication
    password_hash = Column(String(255))
    email_verified = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    
    # Profile
    first_name = Column(String(100))
    last_name = Column(String(100))
    avatar_url = Column(String(500))
    
    # Preferences
    preferred_wallet = Column(String(255))
    notification_settings = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    wallets = relationship("Wallet", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("TokenTransaction", back_populates="user")


class Wallet(Base):
    """User wallet model"""
    __tablename__ = "wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    address = Column(String(255), nullable=False, unique=True, index=True)
    network = Column(String(50), default="polygon", index=True)
    
    # Wallet metadata
    label = Column(String(100))
    wallet_type = Column(String(50), default="web3")  # web3, hardware, etc.
    is_primary = Column(Boolean, default=False)
    
    # Connection status
    connected_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used = Column(DateTime(timezone=True), onupdate=func.now())
    active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="wallets")
