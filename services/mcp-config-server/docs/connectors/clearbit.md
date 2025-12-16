# Clearbit Configuration Guide

## Overview

Clearbit provides data enrichment APIs for person and company information.

## Prerequisites

- Clearbit account

## Step-by-Step Configuration

### Step 1: Create Clearbit Account

1. Visit [Clearbit Dashboard](https://dashboard.clearbit.com/signup)
2. Create an account
3. Verify your email address

### Step 2: Get API Key

1. Log in to [Clearbit Dashboard](https://dashboard.clearbit.com)
2. Go to **Settings** > **API**
3. Copy your API key
4. Save it securely

## Required Credentials

- **api_key**: Your Clearbit API key

## Testing Connection

The system tests by attempting a person lookup (404 is acceptable for test).

## Capabilities

- Enrich person data by email
- Enrich company data by domain
- Find companies by name
- Discover company information
- Get comprehensive person profiles

## Free Tier

Limited requests available on free tier.

## Troubleshooting

- **401/403 Unauthorized**: Check API key
- **Rate Limits**: Monitor usage in dashboard
- **Quota Exceeded**: Upgrade plan

## Additional Resources

- [Clearbit API Documentation](https://clearbit.com/docs)
- [Person API](https://clearbit.com/docs#person-api)
- [Company API](https://clearbit.com/docs#company-api)

