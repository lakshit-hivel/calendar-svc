"""
OAuth functions for Google Calendar Marketplace integration.
Functional style matching existing Hivel code.
"""

import os
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from dotenv import load_dotenv
from app.core.logger import get_logger

load_dotenv()

logger = get_logger(__name__)

# Config (loaded from environment)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8000/auth/callback")
SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid"  # Google adds this automatically, we need to include it
]


def get_client_config():
    """Get OAuth client config dict."""
    return {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REDIRECT_URI]
        }
    }


def get_authorization_url(org_id):
    """
    Generate the URL where admin clicks to start OAuth.
    
    Args:
        org_id: Your internal organization ID
        
    Returns:
        Authorization URL string
    """
    logger.info(f"[OAUTH] Generating authorization URL for org {org_id}")
    
    flow = Flow.from_client_config(
        get_client_config(),
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent',
        state=str(org_id)  # Pass org_id through OAuth flow
    )
    
    logger.info(f"[OAUTH] ✅ Authorization URL generated for org {org_id}")
    return authorization_url


def exchange_code_for_tokens(authorization_code):
    """
    Exchange authorization code for tokens.
    Called when Google redirects back to callback URL.
    
    Args:
        authorization_code: The code from callback URL
        
    Returns:
        Dictionary with access_token, refresh_token, expiry
    """
    logger.info(f"[OAUTH] Exchanging authorization code for tokens")
    
    try:
        flow = Flow.from_client_config(
            get_client_config(),
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        
        flow.fetch_token(code=authorization_code)
        credentials = flow.credentials
        
        logger.info(f"[OAUTH] ✅ Successfully exchanged code for tokens")
        
        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "expiry": credentials.expiry.isoformat() if credentials.expiry else None
        }
    except Exception as e:
        logger.error(f"[OAUTH] ❌ Failed to exchange code for tokens: {e}")
        raise


def refresh_access_token(refresh_token):
    """
    Get new access token using refresh token.
    
    Args:
        refresh_token: The stored refresh token
        
    Returns:
        Dictionary with new access_token, refresh_token, expiry
    """
    logger.info(f"[OAUTH] Refreshing access token using refresh token")
    
    try:
        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET
        )
        
        credentials.refresh(Request())
        
        logger.info(f"[OAUTH] ✅ Successfully refreshed access token")
        
        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token or refresh_token,
            "expiry": credentials.expiry.isoformat() if credentials.expiry else None
        }
    except Exception as e:
        logger.error(f"[OAUTH] ❌ Failed to refresh access token: {e}")
        raise


def get_user_info(access_token):
    """
    Fetch user info (email) from Google using access token.
    
    Args:
        access_token: Valid OAuth access token
        
    Returns:
        Dictionary with email and other user info
    """
    import requests
    
    logger.info("[OAUTH] Fetching user info from Google")
    
    try:
        response = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        response.raise_for_status()
        user_info = response.json()
        
        logger.info(f"[OAUTH] ✅ Got user info, email={user_info.get('email')}")
        
        return {
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "picture": user_info.get("picture")
        }
    except Exception as e:
        logger.error(f"[OAUTH] ❌ Failed to fetch user info: {e}")
        return {"email": None, "name": None, "picture": None}
