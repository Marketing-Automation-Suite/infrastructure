# Apollo.io Configuration Guide

## Overview

Apollo.io provides a B2B database for finding contacts, companies, and email addresses.

## Prerequisites

- Apollo.io account (free tier available)

## Step-by-Step Configuration

### Step 1: Create Apollo.io Account

1. Visit [Apollo.io Signup](https://www.apollo.io/signup)
2. Create a free or paid account
3. Verify your email address

### Step 2: Get API Key

1. Log in to [Apollo.io](https://app.apollo.io)
2. Go to **Settings** > **Integrations** > **API**
3. Click **"Generate API Key"** or copy existing key
4. Save it securely

## Required Credentials

- **api_key**: Your Apollo.io API key

## Testing Connection

The system tests by calling the `/v1/auth/health` endpoint.

## Capabilities

- Search for people by criteria
- Search for companies
- Enrich contact information
- Find email addresses
- Create and manage sequences
- Track outreach campaigns

## Free Tier Limits

- Limited credits per month
- Basic search functionality

## Troubleshooting

- **401 Unauthorized**: Verify API key
- **Rate Limits**: Monitor credit usage
- **Quota Exceeded**: Upgrade plan

## Additional Resources

- [Apollo.io API Documentation](https://apolloio.github.io/apollo-api-docs/)
- [API Key Management](https://app.apollo.io/#/settings/integrations/api)

