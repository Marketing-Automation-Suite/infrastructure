"""
Token model for NFT Software Engine
Represents NFT tokens that can be used for software licensing
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class Token(Base):
    """
    Token model representing NFT tokens in the system
    """
    __tablename__ = "tokens"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Token identification
    token_id = Column(String(255), unique=True, index=True, nullable=False)
    contract_address = Column(String(42), nullable=False)  # Ethereum contract address
    
    # Token metadata
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    
    # Tier association
    tier_id = Column(Integer, ForeignKey("tiers.id"), nullable=False)
    tier = relationship("Tier", back_populates="tokens")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Blockchain metadata
    blockchain_network = Column(String(50), default="ethereum", nullable=False)
    token_uri = Column(Text, nullable=True)  # IPFS or other URI
    
    def __repr__(self) -> str:
        return f"<Token(id={self.id}, token_id='{self.token_id}', contract_address='{self.contract_address}')>"


# Indexes for performance
Index('idx_token_id', Token.token_id)
Index('idx_token_contract', Token.contract_address)
Index('idx_token_tier', Token.tier_id)
Index('idx_token_active', Token.is_active)
