"""
Main FastAPI application for NFT Software Engine
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .config.settings import Settings
from .api.v1 import products, nft, contracts, analytics
from .core.database import init_db
from .core.auth import verify_token


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager"""
    logger.info("Starting NFT Software Engine...")
    
    # Initialize database
    await init_db()
    
    logger.info("NFT Software Engine started successfully")
    
    yield
    
    # Cleanup
    logger.info("Shutting down NFT Software Engine...")


# Create FastAPI application
app = FastAPI(
    title="NFT Software Engine",
    description="Standalone service for NFT-based software tokenization",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "nft-software-engine"}


@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "NFT Software Engine",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


# API v1 routes
app.include_router(
    products.router,
    prefix="/api/v1/products",
    tags=["Products"]
)

app.include_router(
    nft.router,
    prefix="/api/v1/nft",
    tags=["NFTs"]
)

app.include_router(
    contracts.router,
    prefix="/api/v1/contracts",
    tags=["Contracts"]
)

app.include_router(
    analytics.router,
    prefix="/api/v1/analytics",
    tags=["Analytics"]
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
