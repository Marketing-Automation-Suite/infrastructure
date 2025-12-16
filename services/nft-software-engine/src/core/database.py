"""
Database initialization and operations for NFT Software Engine
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from .models.database import Base

logger = logging.getLogger(__name__)

# Global database engine and session maker
engine = None
SessionLocal = None


def init_db(database_url: str = None):
    """Initialize database connection and create tables"""
    global engine, SessionLocal
    
    if not database_url:
        from ..config.settings import settings
        database_url = settings.DATABASE_URL
    
    try:
        # Create engine based on database URL
        if "sqlite" in database_url:
            engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=settings.DEBUG if hasattr(settings, 'DEBUG') else False
            )
        else:
            engine = create_engine(
                database_url,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=settings.DEBUG if hasattr(settings, 'DEBUG') else False
            )
        
        # Create session maker
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info(f"Database initialized successfully: {database_url}")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_db() -> Session:
    """Get database session"""
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db_session() -> Session:
    """Create a new database session"""
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return SessionLocal()


def close_db():
    """Close database connections"""
    global engine, SessionLocal
    
    if engine:
        engine.dispose()
        logger.info("Database connections closed")
    
    engine = None
    SessionLocal = None


# Import settings for database config
try:
    from ..config.settings import settings
except ImportError:
    settings = None
