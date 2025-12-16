# Token Verification Service

Service for verifying ERC-721 token ownership and granting access to premium features.

## Features

- Multi-network support (Ethereum, Polygon, Arbitrum)
- Token ownership verification
- Tier extraction from token metadata
- Caching layer for performance
- Real-time verification via Web3 providers

## API Endpoints

### Token Verification
- `POST /v1/verify-token` - Verify token ownership and get tier
- `GET /v1/user-tiers/:wallet_address` - Get all tiers for a wallet
- `GET /v1/tokens/:token_id` - Get token details

### Health
- `GET /health` - Health check

## Environment Variables

- `ETHEREUM_RPC_URL` - Ethereum RPC endpoint
- `POLYGON_RPC_URL` - Polygon RPC endpoint
- `ARBITRUM_RPC_URL` - Arbitrum RPC endpoint
- `LICENSE_TOKEN_CONTRACT_ETHEREUM` - Contract address on Ethereum
- `LICENSE_TOKEN_CONTRACT_POLYGON` - Contract address on Polygon
- `LICENSE_TOKEN_CONTRACT_ARBITRUM` - Contract address on Arbitrum
- `REDIS_URL` - Redis connection string (optional, for caching)

## Supported Networks

- Ethereum (Mainnet & Sepolia)
- Polygon (Mainnet & Mumbai)
- Arbitrum (One & Goerli)

