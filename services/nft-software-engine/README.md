# NFT Software Engine

A standalone service that provides APIs for NFT-based software tokenization, enabling any software product to offer tiered access through blockchain tokens while integrating with existing authentication and tier management systems.

## Features

- **Product Management**: Configure products with tiered NFT licensing
- **Blockchain Integration**: Smart contract deployment and NFT minting
- **Token Verification**: Real-time token ownership verification
- **Dashboard Templates**: Reusable Streamlit components
- **Analytics**: Token economy metrics and insights

## Architecture

This service provides RESTful APIs that any software product can integrate with to implement freemium models using NFT licensing. It supports multiple blockchain networks and includes templates for rapid deployment.

## Quick Start

1. Configure environment variables (see `.env.example`)
2. Deploy smart contracts using the included templates
3. Register your product with tier configuration
4. Integrate APIs into your application

## API Documentation

API documentation is available at `/docs` when the service is running.

## Integration

Any software product can integrate with this service by:
1. Making API calls to purchase and verify NFTs
2. Using the provided dashboard templates
3. Implementing wallet connection flows
4. Following the token verification patterns

## License

This service is part of the Marketing Automation Suite.
