"""
Database connection management
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger(__name__)

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{os.getenv('POSTGRES_USER', 'marketing')}:{os.getenv('POSTGRES_PASSWORD', 'marketing_password')}@{os.getenv('POSTGRES_HOST', 'postgres')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('AUTH_DB_NAME', 'auth_db')}"
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=os.getenv("SQL_DEBUG", "false").lower() == "true"
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI to get database session.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database - create tables if they don't exist.
    """
    # #region agent log
    try:
        from ..debug_log import debug_log
        debug_log("debug-session", "startup", "H4", "auth-service/src/database/connection.py:51", "init_db() called, checking database connection", {"database_url": DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else "hidden"})
    except Exception:
        pass
    # #endregion
    try:
        # #region agent log
        try:
            from ..debug_log import debug_log
            debug_log("debug-session", "startup", "H4", "auth-service/src/database/connection.py:56", "Calling Base.metadata.create_all()", {"before_create": True})
        except Exception:
            pass
        # #endregion
        Base.metadata.create_all(bind=engine)
        # #region agent log
        try:
            from ..debug_log import debug_log
            debug_log("debug-session", "startup", "H4", "auth-service/src/database/connection.py:60", "Database tables created successfully", {"after_create": True})
        except Exception:
            pass
        # #endregion
        logger.info("Database initialized")
    except Exception as e:
        # #region agent log
        try:
            from ..debug_log import debug_log
            debug_log("debug-session", "startup", "H4", "auth-service/src/database/connection.py:64", "Database initialization failed", {"error": str(e), "error_type": type(e).__name__})
        except Exception:
            pass
        # #endregion
        raise

