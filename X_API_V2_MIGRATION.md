# X API v2 Migration Guide

## Overview

This project has been updated to use **X API v2** (formerly Twitter API v2) with the latest authentication methods and best practices as documented at https://developer.x.com/en/docs/x-api.

## Key Changes

### 1. Authentication Method

**X API v2 Filtered Stream** uses **OAuth 2.0 Bearer Token (App-Only)** authentication:
- ✅ Only requires `TWITTER_BEARER_TOKEN` environment variable
- ✅ Simpler authentication flow
- ✅ No need for OAuth 1.0a credentials for streaming

**How to get your Bearer Token:**
1. Go to https://developer.x.com/en/portal/dashboard
2. Create or select your App (must be associated with a Project)
3. Navigate to "Keys and tokens" tab
4. Generate Bearer Token under "Authentication Tokens"

### 2. API Endpoints

- **Old**: `https://stream.twitter.com/1.1/statuses/filter.json`
- **New**: `https://api.x.com/2/tweets/search/stream`

The new endpoint is automatically used by `tweepy.StreamingClient`.

### 3. Updated Class Names

For clarity and X API v2 alignment:
- `XStreamListener` - Stream listener for X API v2
- `XStreamManager` - Stream manager with rule management

### 4. Access Levels & Pricing

X API v2 has tiered access levels:

| Tier | Monthly Cost | Posts Read Limit | Filtered Stream |
|------|-------------|------------------|-----------------|
| **Free** | $0 | 100 reads/month | ❌ Not available |
| **Basic** | $200 | 10,000 posts/month | ✅ Available |
| **Pro** | $5,000 | 1,000,000 posts/month | ✅ Available |
| **Enterprise** | Custom | Unlimited | ✅ Full features |

**Recommendation**: Pro tier for production use.

### 5. Enhanced Features

X API v2 provides:
- ✅ Multiple persistent filtering rules (no need to reconnect to change rules)
- ✅ Enhanced data objects with more fields
- ✅ Better conversation threading (`conversation_id`)
- ✅ Improved metrics and analytics
- ✅ More detailed error responses

### 6. Field Selection

X API v2 only returns `id` and `text` by default. Request additional fields using:

```python
stream.filter(
    tweet_fields=['author_id', 'created_at', 'lang', 'public_metrics', 'conversation_id'],
    expansions=['author_id'],
    user_fields=['username', 'name', 'verified']
)
```

### 7. Error Handling

Enhanced error handling for X API v2:
- Rate limit detection (HTTP 429)
- Connection error handling
- Request error logging with status codes

## Setup Steps

1. Sign up at https://developer.x.com/
2. Create a Project and App
3. Generate Bearer Token
4. Choose appropriate access tier (Basic minimum for filtered stream)
5. Follow the Quick Start guide in README.md

## Rate Limits

X API v2 rate limits by access tier:

- **Basic**: 10,000 posts/month
- **Pro**: 1,000,000 posts/month
- **Enterprise**: Custom limits

Monitor your usage in the developer portal.

## References

- [X API v2 Documentation](https://developer.x.com/en/docs/x-api)
- [Filtered Stream Introduction](https://docs.x.com/x-api/posts/filtered-stream/introduction)
- [Migration Guide](https://developer.x.com/en/docs/twitter-api/migrate)
- [Access Levels & Pricing](https://developer.x.com/en/docs/x-api)

## Support

If you encounter issues:
1. Check the [X API Status](https://api.twitterstat.us/)
2. Review error messages in logs
3. Verify Bearer Token is valid
4. Ensure your access tier includes filtered stream
5. Check rate limits in developer portal

## Implementation

The codebase uses modern X API v2 standards:
- ✅ Clean class naming aligned with X API v2 (`XStreamListener`, `XStreamManager`)
- ✅ Bearer Token authentication as primary method
- ✅ OAuth 1.0a credentials optional (only for v1.1 endpoints if needed)
