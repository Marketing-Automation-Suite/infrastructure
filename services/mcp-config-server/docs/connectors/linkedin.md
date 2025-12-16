# LinkedIn Sales Navigator Configuration Guide

## Overview

LinkedIn Sales Navigator provides access to LinkedIn's professional network for lead generation, profile enrichment, and messaging.

## Prerequisites

- LinkedIn account
- LinkedIn Sales Navigator subscription (required for API access)
- LinkedIn Developer account

## Step-by-Step Configuration

### Step 1: Create LinkedIn App

1. Visit [LinkedIn Developers](https://www.linkedin.com/developers/apps)
2. Click "Create app"
3. Fill in the following:
   - App name: Your app name
   - Company: Your company
   - Privacy policy URL: Your privacy policy
   - App logo: Upload a logo
4. Accept terms and submit

### Step 2: Get API Credentials

1. In your app dashboard, go to the "Auth" tab
2. Copy the **Client ID** (this is your API Key)
3. Copy the **Client Secret** (this is your API Secret)
4. Save these securely

### Step 3: Configure OAuth Redirect

1. In the "Auth" tab, add a redirect URL:
   - For development: `http://localhost:8001/oauth/callback`
   - For production: Your production callback URL
2. Request the following permissions:
   - `r_liteprofile` - Read basic profile
   - `r_emailaddress` - Read email address
   - `w_messages` - Send messages (if needed)
3. Save changes

### Step 4: Generate Access Token

1. Use OAuth2 flow to get an access token
2. Or use LinkedIn's token generator for testing
3. Access tokens expire - you may need to refresh them

## Required Credentials

- **api_key**: Your LinkedIn Client ID
- **api_secret**: Your LinkedIn Client Secret
- **access_token**: OAuth2 access token (optional, can be generated)

## Testing Connection

After configuration, the system will automatically test the connection by calling the `/v2/me` endpoint.

## Capabilities

- Generate leads from LinkedIn
- Enrich profiles with LinkedIn data
- Send messages to connections
- Search for people and companies
- Get company information

## Troubleshooting

- **401 Unauthorized**: Check that your access token is valid
- **403 Forbidden**: Verify you have the required permissions
- **Rate Limits**: LinkedIn has rate limits - monitor usage

## Additional Resources

- [LinkedIn API Documentation](https://docs.microsoft.com/en-us/linkedin/)
- [OAuth 2.0 Flow](https://docs.microsoft.com/en-us/linkedin/shared/authentication/authentication)

