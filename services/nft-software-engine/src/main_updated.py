"""
NFT Software Engine - FastAPI Application Entry Point
NFT-based software licensing and distribution system
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import logging
from contextlib import asynccontextmanager
import asyncio

from .core.database import AsyncSessionLocal, get_db
from .services.wallet_service import wallet_service
from .services.token_service import token_service
from .models.customer import Customer
from .models.wallet import Wallet
from .models.tier import Tier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORS Configuration
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "https://dashboard.marketing-automation.com,https://app.marketing-automation.com"
).split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("NFT Software Engine starting up...")
    try:
        # Initialize database connection
        # TODO: Add database initialization checks
        # Initialize blockchain connection
        logger.info("NFT Software Engine started successfully")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("NFT Software Engine shutting down...")


app = FastAPI(
    title="NFT Software Engine",
    version="1.0.0",
    description="NFT-based software licensing and distribution system",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health Check Endpoints
@app.get("/health")
async def health():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "nft-software-engine",
        "version": "1.0.0"
    }


@app.get("/health/ready")
async def readiness(db: AsyncSessionLocal = Depends(get_db)):
    """Readiness probe - check if service can accept requests"""
    try:
        # TODO: Add database connection check
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service not ready")


@app.get("/health/live")
async def liveness():
    """Liveness probe - check if service is alive"""
    return {"status": "alive"}


# API Models
class WalletRequest(BaseModel):
    """Request to generate a new wallet"""
    customer_id: Optional[str] = None
    customer_email: str
    customer_name: Optional[str] = None
    customer_company: Optional[str] = None


class WalletResponse(BaseModel):
    """Wallet generation response"""
    address: str
    customer_id: str
    customer_email: str
    wallet_id: int


class TokenVerificationRequest(BaseModel):
    """Request to verify NFT token ownership"""
    wallet_address: str
    token_id: str
    contract_address: str


class TokenVerificationResponse(BaseModel):
    """Token verification response"""
    verified: bool
    on_chain_verified: bool
    in_database: bool
    recorded_ownership: bool
    token_id: str
    contract_address: str
    tier: Optional[Dict[str, Any]] = None
    token_info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class CustomerTierRequest(BaseModel):
    """Request to get customer tier"""
    wallet_address: str


class CustomerTierResponse(BaseModel):
    """Customer tier response"""
    tier: Optional[Dict[str, Any]] = None
    owned_tokens: int
    wallet_address: str


# API Endpoints
@app.post("/api/v1/wallets", response_model=WalletResponse)
async def create_wallet(request: WalletRequest, db: AsyncSessionLocal = Depends(get_db)):
    """
    Generate a new Ethereum wallet for a customer
    """
    try:
        if not request.customer_id:
            # Generate a customer ID if not provided
            import uuid
            request.customer_id = str(uuid.uuid4())
        
        wallet_info = await wallet_service.create_wallet_for_customer(
            db=db,
            customer_id=request.customer_id,
            customer_email=request.customer_email,
            customer_name=request.customer_name,
            customer_company=request.customer_company
        )
        
        return WalletResponse(**wallet_info)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating wallet: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v1/wallets/{customer_id}")
async def get_customer_wallets(customer_id: str, db: AsyncSessionLocal = Depends(get_db)):
    """
    Get all wallets for a customer
    """
    try:
        wallets = await wallet_service.get_customer_wallets(db=db, customer_id=customer_id)
        return {"wallets": wallets}
    except Exception as e:
        logger.error(f"Error getting customer wallets: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/v1/tokens/verify", response_model=TokenVerificationResponse)
async def verify_token(request: TokenVerificationRequest, db: AsyncSessionLocal = Depends(get_db)):
    """
    Verify NFT token ownership and return tier information
    """
    try:
        result = await token_service.verify_token_ownership(
            db=db,
            wallet_address=request.wallet_address,
            token_id=request.token_id,
            contract_address=request.contract_address
        )
        
        return TokenVerificationResponse(**result)
        
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/v1/customers/tier", response_model=CustomerTierResponse)
async def get_customer_tier(request: CustomerTierRequest, db: AsyncSessionLocal = Depends(get_db)):
    """
    Get the highest tier that a customer owns
    """
    try:
        result = await token_service.get_customer_tier(
            db=db,
            wallet_address=request.wallet_address
        )
        
        if result is None:
            return CustomerTierResponse(
                tier=None,
                owned_tokens=0,
                wallet_address=request.wallet_address
            )
        
        return CustomerTierResponse(**result)
        
    except Exception as e:
        logger.error(f"Error getting customer tier: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v1/tiers")
async def list_tiers(db: AsyncSessionLocal = Depends(get_db)):
    """
    List all available NFT tiers and pricing
    """
    try:
        tiers = await token_service.list_tiers(db=db)
        return {"tiers": tiers}
    except Exception as e:
        logger.error(f"Error listing tiers: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/v1/tokens/ownership")
async def record_token_ownership(
    wallet_address: str,
    token_id: str,
    contract_address: str,
    transaction_hash: Optional[str] = None,
    db: AsyncSessionLocal = Depends(get_db)
):
    """
    Record token ownership in the database
    """
    try:
        success = await token_service.record_token_ownership(
            db=db,
            wallet_address=wallet_address,
            token_id=token_id,
            contract_address=contract_address,
            transaction_hash=transaction_hash
        )
        
        if success:
            return {"status": "success", "message": "Ownership recorded successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to record ownership")
            
    except Exception as e:
        logger.error(f"Error recording token ownership: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Authentication placeholder (to be implemented)
# @app.middleware("http")
# async def authenticate_request(request: Request, call_next):
#     # TODO: Implement authentication middleware
#     return await call_next(request)


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
