"""
SQLAlchemy models for MCP Configuration Server
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey, JSON, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .connection import Base


class ServiceRegistry(Base):
    """Available services in marketplace"""
    
    __tablename__ = "service_registry"
    
    id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text)
    icon_url = Column(String(500))
    definition_path = Column(String(500))
    connector_class = Column(String(255))
    is_active = Column(Boolean, default=True)
    popularity_score = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    configurations = relationship("ServiceConfiguration", back_populates="service", cascade="all, delete-orphan")
    connectors = relationship("ServiceConnector", back_populates="service", cascade="all, delete-orphan")


class ServiceConfiguration(Base):
    """Encrypted user configurations"""
    
    __tablename__ = "service_configurations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    service_id = Column(String(255), ForeignKey("service_registry.id", ondelete="CASCADE"), nullable=False)
    config_name = Column(String(255), nullable=False)
    encrypted_credentials = Column(LargeBinary, nullable=False)
    settings = Column(JSON)
    status = Column(String(50), default="pending")  # pending, active, failed, disabled
    last_tested_at = Column(TIMESTAMP)
    last_test_result = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    service = relationship("ServiceRegistry", back_populates="configurations")
    connection_tests = relationship("ConnectionTest", back_populates="configuration", cascade="all, delete-orphan")
    
    __table_args__ = (
        {"schema": None},  # Use default schema
    )


class ServiceConnector(Base):
    """Plugin metadata"""
    
    __tablename__ = "service_connectors"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    service_id = Column(String(255), ForeignKey("service_registry.id", ondelete="CASCADE"), nullable=False)
    connector_class = Column(String(255), nullable=False)
    version = Column(String(50))
    capabilities = Column(JSON)
    is_loaded = Column(Boolean, default=False)
    loaded_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    service = relationship("ServiceRegistry", back_populates="connectors")


class ConnectionTest(Base):
    """Connection test history"""
    
    __tablename__ = "connection_tests"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    configuration_id = Column(Integer, ForeignKey("service_configurations.id", ondelete="CASCADE"), nullable=False)
    test_status = Column(String(50), nullable=False)  # success, failed, timeout
    test_result = Column(JSON)
    error_message = Column(Text)
    test_duration_ms = Column(Integer)
    tested_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    configuration = relationship("ServiceConfiguration", back_populates="connection_tests")

