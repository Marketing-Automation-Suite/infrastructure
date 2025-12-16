# Auth Service

Centralized authentication and user management service for the Marketing Automation Platform.

## Features

- Email/password authentication
- Wallet address linking (MetaMask, WalletConnect)
- JWT token generation and validation
- Session management
- User tier tracking (free, bronze, silver, gold)
- Subscription management (traditional + token-based)

## API Endpoints

### Authentication
- `POST /v1/auth/register` - Register new user
- `POST /v1/auth/login` - Login with email/password
- `POST /v1/auth/logout` - Logout (invalidate token)
- `POST /v1/auth/refresh` - Refresh JWT token
- `GET /v1/auth/me` - Get current user info

### Wallet Management
- `POST /v1/wallet/link` - Link wallet address to user
- `POST /v1/wallet/verify` - Verify wallet signature
- `GET /v1/wallet/addresses` - Get user's linked wallets

### User Management
- `GET /v1/users/:id` - Get user by ID
- `PUT /v1/users/:id` - Update user
- `GET /v1/users/:id/tier` - Get user tier

### Subscriptions
- `GET /v1/subscriptions` - Get user subscriptions
- `POST /v1/subscriptions` - Create subscription
- `PUT /v1/subscriptions/:id` - Update subscription
- `DELETE /v1/subscriptions/:id` - Cancel subscription

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET` - Secret key for JWT signing
- `JWT_EXPIRATION` - JWT expiration time (default: 24h)
- `REDIS_URL` - Redis connection string (optional, for session storage)

## Database

Uses PostgreSQL with the following tables:
- `users` - User accounts
- `subscriptions` - User subscriptions (traditional + token)
- `token_verifications` - Cached token verifications

