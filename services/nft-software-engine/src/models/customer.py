"""
Customer model for NFT Software Engine
Represents a customer in the system
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class Customer(Base):
    """
    Customer model representing a user in the NFT software licensing system
    """
    __tablename__ = "customers"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Customer identification
    customer_id = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    
    # Customer details
    name = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Additional metadata
    metadata = Column(Text, nullable=True)  # JSON string for additional customer data
    
    # Relationships
    wallets = relationship("Wallet", back_populates="customer", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Customer(id={self.id}, customer_id='{self.customer_id}', email='{self.email}')>"


# Indexes for performance
Index('idx_customer_customer_id', Customer.customer_id)
Index('idx_customer_email', Customer.email)
Index('idx_customer_active', Customer.is_active)
