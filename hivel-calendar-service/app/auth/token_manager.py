"""
Token manager for Google Calendar integration.
Uses database functions from events.py for storage.
"""

from datetime import datetime, timedelta
from app.auth import oauth
from app.database.events import (
    get_integration_tokens,
    save_integration_tokens
)
from app.core.logger import get_logger

logger = get_logger(__name__)


def get_tokens(org_id):
    """Get tokens from database."""
    logger.debug(f"[TOKEN] Retrieving tokens for org {org_id}")
    tokens = get_integration_tokens(org_id)
    if tokens:
        logger.debug(f"[TOKEN] ✅ Tokens found for org {org_id}")
    else:
        logger.warning(f"[TOKEN] ⚠️ No tokens found for org {org_id}")
    return tokens


def save_tokens(org_id, tokens, email=None):
    """
    Save tokens to database.
    
    Args:
        org_id: Organization ID
        tokens: Dict with access_token, refresh_token, expires_in
        email: User's email (optional)
    """
    logger.info(f"[TOKEN] Saving tokens for org {org_id}, email={email}")
    access_token = tokens.get('access_token')
    refresh_token = tokens.get('refresh_token')
    expires_in = tokens.get('expires_in', 3600)  # Default 1 hour (in seconds)
    
    result = save_integration_tokens(
        org_id=org_id,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        email=email
    )
    logger.info(f"[TOKEN] ✅ Tokens saved successfully for org {org_id}")
    return result


def get_valid_token(org_id):
    """
    Get a valid access token, refreshing if expired.
    
    Returns:
        Valid access token string
    
    Raises:
        Exception if no tokens found or refresh fails
    """
    logger.info(f"[TOKEN] Getting valid token for org {org_id}")
    
    tokens = get_tokens(org_id)
    
    if not tokens:
        logger.error(f"[TOKEN] ❌ No tokens found for org {org_id}")
        raise Exception(f"No tokens found for organization {org_id}. Please authenticate first.")
    
    # Calculate expiry from expires_in + access_token_generation_date
    expires_in = tokens.get('expires_in', 3600)
    generation_date = tokens.get('access_token_generation_date')
    
    is_expired = False
    if generation_date:
        expires_at = generation_date + timedelta(seconds=expires_in)
        # Check if expired or about to expire (within 5 minutes)
        is_expired = expires_at < datetime.now() + timedelta(minutes=5)
        logger.debug(f"[TOKEN] Token expires at {expires_at}, is_expired={is_expired}")
    
    if is_expired:
        logger.info(f"[TOKEN] Token expired for org {org_id}, refreshing...")
        
        refresh_token = tokens.get('refresh_token')
        if not refresh_token:
            logger.error(f"[TOKEN] ❌ No refresh token found for org {org_id}")
            raise Exception(f"No refresh token found for org {org_id}. Re-authentication required.")
        
        # Get new tokens from Google
        logger.info(f"[TOKEN] Calling Google OAuth to refresh token")
        new_tokens = oauth.refresh_access_token(refresh_token)
        logger.info(f"[TOKEN] ✅ Token refreshed successfully")
        
        # Save the new tokens (refresh_token might not be returned, keep old one)
        if not new_tokens.get('refresh_token'):
            new_tokens['refresh_token'] = refresh_token
        
        save_tokens(org_id, new_tokens, email=tokens.get('email'))
        
        return new_tokens['access_token']
    
    logger.info(f"[TOKEN] ✅ Token is valid for org {org_id}")
    return tokens['token']
