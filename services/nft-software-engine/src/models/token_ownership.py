"""
TokenOwnership model for NFT Software Engine
Represents ownership relationship between customers and NFT tokens
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class TokenOwnership(Base):
    """
    TokenOwnership model tracking which customer owns which NFT tokens
    """
    __tablename__ = "token_ownerships"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    token_id = Column(Integer, ForeignKey("tokens.id"), nullable=False)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    
    # Relationships
    customer = relationship("Customer")
    token = relationship("Token")
    wallet = relationship("Wallet")
    
    # Ownership metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Verification status
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_date = Column(DateTime(timezone=True), nullable=True)
    
    # Blockchain transaction hash (when token was transferred)
    transaction_hash = Column(String(66), nullable=True)
    
    def __repr__(self) -> str:
        return f"<TokenOwnership(id={self.id}, customer_id={self.customer_id}, token_id={self.token_id})>"


# Indexes for performance
Index('idx_ownership_customer', TokenOwnership.customer_id)
Index('idx_ownership_token', TokenOwnership.token_id)
Index('idx_ownership_wallet', TokenOwnership.wallet_id)
Index('idx_ownership_verified', TokenOwnership.is_verified)
