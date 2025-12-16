"""
Token Verification Service - FastAPI Application
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import logging
from datetime import datetime, timedelta

from .web3_client import web3_client
from .cache import token_cache
from .schemas import (
    TokenVerificationRequest,
    TokenVerificationResponse,
    UserTiersResponse,
    TokenInfo,
    TokenDetailsResponse
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Token Verification Service",
    version="1.0.0",
    description="Verify ERC-721 token ownership and grant access"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Health check"""
    # #region agent log
    try:
        from .debug_log import debug_log
        debug_log("debug-session", "health", "H2,H3,H5", "token-verification-service/src/server.py:40", "Health check endpoint called", {"service": "token-verification-service"})
    except Exception:
        pass
    # #endregion
    networks_status = {}
    for network in ['ethereum', 'polygon', 'arbitrum']:
        client = web3_client.get_client(network)
        # #region agent log
        try:
            from .debug_log import debug_log
            debug_log("debug-session", "health", "H5", "token-verification-service/src/server.py:44", "Checking network connection in health check", {"network": network, "has_client": client is not None})
        except Exception:
            pass
        # #endregion
        networks_status[network] = client.is_connected() if client else False
    
    result = {
        "status": "healthy",
        "service": "token-verification-service",
        "networks": networks_status,
        "cache_enabled": token_cache.enabled
    }
    # #region agent log
    try:
        from .debug_log import debug_log
        debug_log("debug-session", "health", "H2,H3", "token-verification-service/src/server.py:52", "Health check response prepared", {"networks_status": networks_status, "cache_enabled": token_cache.enabled})
    except Exception:
        pass
    # #endregion
    return result


@app.post("/v1/verify-token", response_model=TokenVerificationResponse)
async def verify_token(request: TokenVerificationRequest):
    """
    Verify token ownership and get tier
    
    Checks if the wallet owns the token and returns the tier.
    Results are cached for 5 minutes.
    """
    # Check cache first
    cached = token_cache.get(
        request.network,
        request.contract_address,
        request.wallet_address,
        request.token_id
    )
    
    if cached:
        logger.info(f"Cache hit for token {request.token_id}")
        return TokenVerificationResponse(**cached)
    
    # Verify ownership
    is_valid = web3_client.verify_token_ownership(
        request.network,
        request.contract_address,
        request.wallet_address,
        request.token_id
    )
    
    if not is_valid:
        response = TokenVerificationResponse(
            valid=False,
            tier=None,
            network=request.network,
            contract_address=request.contract_address,
            token_id=request.token_id,
            wallet_address=request.wallet_address
        )
        return response
    
    # Get tier
    tier = web3_client.get_token_tier(
        request.network,
        request.contract_address,
        request.token_id
    )
    
    # Calculate expiration (tokens don't expire, but cache does)
    expires_at = datetime.utcnow() + timedelta(minutes=5)
    
    response_data = {
        "valid": True,
        "tier": tier,
        "expires_at": expires_at.isoformat(),
        "network": request.network,
        "contract_address": request.contract_address,
        "token_id": request.token_id,
        "wallet_address": request.wallet_address
    }
    
    # Cache the result
    token_cache.set(
        request.network,
        request.contract_address,
        request.wallet_address,
        request.token_id,
        response_data
    )
    
    return TokenVerificationResponse(**response_data)


@app.get("/v1/user-tiers/{wallet_address}", response_model=UserTiersResponse)
async def get_user_tiers(wallet_address: str):
    """
    Get all tiers for a wallet address
    
    Note: This is a simplified implementation. In production, you should:
    1. Use an indexer to track all tokens owned by a wallet
    2. Maintain a database of token ownership
    3. Query multiple networks efficiently
    """
    # For now, return empty list
    # In production, implement proper token enumeration
    # This would require:
    # - Indexing Transfer events
    # - Maintaining a database of token ownership
    # - Querying across all networks
    
    return UserTiersResponse(
        wallet_address=wallet_address,
        tiers=[]
    )


@app.get("/v1/tokens/{token_id}", response_model=TokenDetailsResponse)
async def get_token_details(
    token_id: int,
    network: str,
    contract_address: str
):
    """Get token details"""
    tier = web3_client.get_token_tier(network, contract_address, token_id)
    
    if not tier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    return TokenDetailsResponse(
        token_id=token_id,
        tier=tier,
        network=network,
        contract_address=contract_address,
        owner=None  # Would need to query ownerOf in production
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

