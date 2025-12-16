"""
Tier model for NFT Software Engine
Represents subscription tiers associated with NFT tokens
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class Tier(Base):
    """
    Tier model representing software licensing tiers
    """
    __tablename__ = "tiers"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Tier identification
    name = Column(String(255), unique=True, index=True, nullable=False)
    display_name = Column(String(255), nullable=False)
    
    # Tier details
    price = Column(Integer, nullable=False, default=0)  # Price in cents
    features = Column(Text, nullable=True)  # JSON string of features
    description = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Order for display
    sort_order = Column(Integer, default=0, nullable=False)
    
    # Relationships
    tokens = relationship("Token", back_populates="tier", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Tier(id={self.id}, name='{self.name}', price={self.price})>"


# Indexes for performance
Index('idx_tier_name', Tier.name)
Index('idx_tier_active', Tier.is_active)
Index('idx_tier_sort_order', Tier.sort_order)
