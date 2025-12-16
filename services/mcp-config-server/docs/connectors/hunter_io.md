# Hunter.io Configuration Guide

## Overview

Hunter.io helps you find and verify email addresses for lead generation and outreach.

## Prerequisites

- Hunter.io account (free tier available)

## Step-by-Step Configuration

### Step 1: Create Hunter.io Account

1. Visit [Hunter.io Signup](https://hunter.io/users/sign_up)
2. Create a free or paid account
3. Verify your email address

### Step 2: Get API Key

1. Log in to [Hunter.io](https://hunter.io)
2. Go to **Account** > **API Keys**
3. Copy your API key
4. Save it securely

## Required Credentials

- **api_key**: Your Hunter.io API key

## Testing Connection

The system tests by calling the `/v2/account` endpoint.

## Capabilities

- Verify email addresses
- Find email addresses by name and domain
- Enrich domain information
- Check email deliverability
- Get email confidence scores

## Free Tier Limits

- 25 searches/month
- Basic verification

## Troubleshooting

- **401 Unauthorized**: Verify API key
- **Rate Limits**: Free tier has monthly limits
- **Quota Exceeded**: Upgrade plan or wait for reset

## Additional Resources

- [Hunter.io API Documentation](https://hunter.io/api-documentation)
- [API Key Management](https://hunter.io/user/api_keys)

