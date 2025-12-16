"""
Payment Service - Stripe and Crypto Payment Processing
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
import stripe
import os
import logging
from typing import Optional
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')

app = FastAPI(
    title="Payment Service",
    version="1.0.0",
    description="Payment processing for premium tiers"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tier pricing
TIER_PRICES = {
    'bronze': {'usd': 30, 'eth': 0.01},
    'silver': {'usd': 150, 'eth': 0.05},
    'gold': {'usd': 300, 'eth': 0.1}
}

AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://auth-service:8001')


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "service": "payment-service"}


@app.post("/v1/payments/stripe/create-checkout")
async def create_stripe_checkout(
    tier: str,
    user_id: str,
    success_url: str = "http://localhost:8501/upgrade?success=true",
    cancel_url: str = "http://localhost:8501/upgrade?canceled=true"
):
    """Create Stripe checkout session"""
    if tier not in TIER_PRICES:
        raise HTTPException(status_code=400, detail="Invalid tier")
    
    price_usd = TIER_PRICES[tier]['usd']
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'{tier.upper()} Tier License',
                        'description': f'Premium {tier} tier access'
                    },
                    'unit_amount': price_usd * 100,  # Stripe uses cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'user_id': user_id,
                'tier': tier
            }
        )
        
        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id
        }
    except Exception as e:
        logger.error(f"Error creating Stripe checkout: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/payments/stripe/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata'].get('user_id')
        tier = session['metadata'].get('tier')
        
        # Create subscription in auth service
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{AUTH_SERVICE_URL}/v1/subscriptions",
                    json={
                        "tier": tier,
                        "source": "traditional",
                        "expires_at": None  # One-time payment
                    },
                    headers={
                        "X-User-ID": user_id
                    }
                )
            logger.info(f"Subscription created for user {user_id}, tier {tier}")
        except Exception as e:
            logger.error(f"Error creating subscription: {str(e)}")
    
    return {"status": "success"}


@app.post("/v1/payments/crypto/initiate")
async def initiate_crypto_payment(
    tier: str,
    network: str,  # ethereum, polygon, arbitrum
    user_id: str,
    wallet_address: str,
    referrer: Optional[str] = None
):
    """Initiate crypto payment for token purchase"""
    if tier not in TIER_PRICES:
        raise HTTPException(status_code=400, detail="Invalid tier")
    
    if network not in ['ethereum', 'polygon', 'arbitrum']:
        raise HTTPException(status_code=400, detail="Invalid network")
    
    price_eth = TIER_PRICES[tier]['eth']
    
    # Get contract address for network
    contract_addresses = {
        'ethereum': os.getenv('LICENSE_TOKEN_CONTRACT_ETHEREUM', ''),
        'polygon': os.getenv('LICENSE_TOKEN_CONTRACT_POLYGON', ''),
        'arbitrum': os.getenv('LICENSE_TOKEN_CONTRACT_ARBITRUM', '')
    }
    
    contract_address = contract_addresses.get(network)
    if not contract_address:
        raise HTTPException(status_code=500, detail="Contract not configured for network")
    
    # Return payment details for frontend to handle
    return {
        "tier": tier,
        "network": network,
        "price_eth": price_eth,
        "contract_address": contract_address,
        "user_id": user_id,
        "wallet_address": wallet_address,
        "referrer": referrer,
        "instructions": "Use your wallet to call mintLicense() on the contract"
    }


@app.get("/v1/payments/{payment_id}")
async def get_payment_status(payment_id: str):
    """Get payment status"""
    # In production, query database for payment status
    return {
        "payment_id": payment_id,
        "status": "pending",
        "message": "Payment status tracking coming soon"
    }


@app.get("/v1/tiers/pricing")
async def get_tier_pricing():
    """Get tier pricing information"""
    return {
        "tiers": {
            tier: {
                "usd": prices['usd'],
                "eth": prices['eth'],
                "description": f"{tier.upper()} tier access"
            }
            for tier, prices in TIER_PRICES.items()
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)

