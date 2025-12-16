# Mailgun Configuration Guide

## Overview

Mailgun provides email API for transactional emails, email validation, and analytics.

## Prerequisites

- Mailgun account
- Domain for sending emails

## Step-by-Step Configuration

### Step 1: Create Mailgun Account

1. Visit [Mailgun Signup](https://signup.mailgun.com)
2. Create an account
3. Verify your email address

### Step 2: Add and Verify Domain

1. Log in to [Mailgun Dashboard](https://app.mailgun.com)
2. Go to **Sending** > **Domains**
3. Click **"Add New Domain"**
4. Enter your domain name
5. Select domain type:
   - **Send Only** (recommended for most use cases)
   - **Send & Receive**
6. Click **"Add Domain"**
7. Add the DNS records provided by Mailgun to your domain:
   - TXT record for verification
   - MX records (if receiving emails)
   - CNAME records for tracking
8. Wait for DNS propagation (can take up to 48 hours)
9. Click **"Verify DNS Settings"**

### Step 3: Get API Key

1. Go to **Account** > **Security** > **API Keys**
2. Copy your **Private API key**
3. Save it securely

## Required Credentials

- **api_key**: Your Mailgun Private API key
- **domain**: Your verified sending domain

## Testing Connection

The system tests by calling the domain endpoint with your API key.

## Capabilities

- Send transactional emails
- Send bulk emails
- Manage mailing lists
- Track email events (opens, clicks, bounces)
- Validate email addresses
- View analytics and logs

## Free Tier Limits

- 5,000 emails/month for first 3 months
- 100 emails/day after trial

## Troubleshooting

- **401 Unauthorized**: Check API key
- **Domain not verified**: Complete DNS setup
- **Rate Limits**: Monitor usage in dashboard

## Additional Resources

- [Mailgun API Documentation](https://documentation.mailgun.com/)
- [Domain Verification Guide](https://documentation.mailgun.com/en/latest/user_manual.html#verifying-your-domain)

