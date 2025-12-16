# Payment Service

Handles both traditional (Stripe) and crypto payments for premium tier upgrades.

## Features

- Stripe integration for credit card payments
- Crypto payment processing (ETH, MATIC, ARB)
- Subscription management
- Webhook handlers for payment events
- Integration with smart contracts for token minting

## API Endpoints

### Payments
- `POST /v1/payments/stripe/create-checkout` - Create Stripe checkout session
- `POST /v1/payments/crypto/initiate` - Initiate crypto payment
- `GET /v1/payments/:id` - Get payment status
- `POST /v1/payments/stripe/webhook` - Stripe webhook handler

### Subscriptions
- `GET /v1/subscriptions` - Get user subscriptions
- `POST /v1/subscriptions` - Create subscription
- `DELETE /v1/subscriptions/:id` - Cancel subscription

## Environment Variables

- `STRIPE_SECRET_KEY` - Stripe secret key
- `STRIPE_WEBHOOK_SECRET` - Stripe webhook secret
- `LICENSE_TOKEN_CONTRACT_ETHEREUM` - Contract address on Ethereum
- `LICENSE_TOKEN_CONTRACT_POLYGON` - Contract address on Polygon
- `LICENSE_TOKEN_CONTRACT_ARBITRUM` - Contract address on Arbitrum
- `AUTH_SERVICE_URL` - Auth service URL

