"""
SQLAlchemy models for Auth Service
"""

from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Integer, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .connection import Base
import uuid


class User(Base):
    """User accounts"""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    wallet_address = Column(String(42), nullable=True, index=True)  # Ethereum address (0x...)
    tier = Column(String(20), default='free', nullable=False)  # free, bronze, silver, gold
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    token_verifications = relationship("TokenVerification", back_populates="user", cascade="all, delete-orphan")


class Subscription(Base):
    """User subscriptions (traditional + token)"""
    
    __tablename__ = "subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    tier = Column(String(20), nullable=False)  # free, bronze, silver, gold
    source = Column(String(20), nullable=False)  # 'token' or 'traditional'
    token_id = Column(Integer, nullable=True)  # ERC-721 token ID if source='token'
    token_contract_address = Column(String(42), nullable=True)  # Contract address
    token_network = Column(String(20), nullable=True)  # ethereum, polygon, arbitrum
    expires_at = Column(TIMESTAMP, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")


class TokenVerification(Base):
    """Token verification cache"""
    
    __tablename__ = "token_verifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    wallet_address = Column(String(42), nullable=False, index=True)
    token_id = Column(Integer, nullable=False)
    contract_address = Column(String(42), nullable=False)
    network = Column(String(20), nullable=False)  # ethereum, polygon, arbitrum
    tier = Column(String(20), nullable=False)
    verified_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    expires_at = Column(TIMESTAMP, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="token_verifications")
    
    __table_args__ = (
        {"schema": None},  # Use default schema
    )

