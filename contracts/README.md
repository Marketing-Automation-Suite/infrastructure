# License Token Contracts

Revenue-guaranteed ERC-721 NFT contracts for the Marketing Automation Platform.

## Contracts

### LicenseToken.sol
Main ERC-721 contract with:
- 10% platform fee on primary sales (guaranteed revenue)
- 10% royalty on secondary sales (EIP-2981 standard)
- Referral reward system with network effect multipliers
- Tier-based pricing (Bronze, Silver, Gold)

### Treasury.sol
Revenue collection and distribution:
- Automatic withdrawal at threshold
- Revenue tracking
- Multi-signature support ready

### UsageFeeCollector.sol
Recurring revenue from usage:
- Credit-based system for API calls
- Premium feature unlocks
- Automatic treasury deposits

## Setup

```bash
npm install
```

## Compile

```bash
npm run compile
```

## Deploy

Set environment variables:
```bash
export PRIVATE_KEY=your_private_key
export ETHEREUM_RPC_URL=your_rpc_url
export POLYGON_RPC_URL=your_rpc_url
export ARBITRUM_RPC_URL=your_rpc_url
```

Deploy to testnets:
```bash
npm run deploy:sepolia
npm run deploy:mumbai
npm run deploy:arbitrum-goerli
```

## Verify

```bash
npm run verify:sepolia
```

## Revenue Guarantees

1. **Primary Sales**: 10% platform fee (hardcoded, cannot be bypassed)
2. **Secondary Sales**: 10% royalty (EIP-2981, works on all marketplaces)
3. **Referral Network**: 10% reward to referrers (viral growth)
4. **Usage Fees**: Recurring revenue from API calls
5. **Treasury**: All revenue automatically collected

## Network Effect Multipliers

- 10+ referrals: 10% bonus
- 50+ referrals: 25% bonus
- 100+ referrals: 50% bonus

