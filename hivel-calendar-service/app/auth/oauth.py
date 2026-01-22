"""
OAuth functions for Google Calendar Marketplace integration.
Functional style matching existing Hivel code.
"""

import os
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from dotenv import load_dotenv

load_dotenv()

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
    
    print(f"Generated auth URL for org {org_id}")
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
    flow = Flow.from_client_config(
        get_client_config(),
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    
    flow.fetch_token(code=authorization_code)
    credentials = flow.credentials
    
    print("Successfully exchanged code for tokens")
    
    return {
        "access_token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "expiry": credentials.expiry.isoformat() if credentials.expiry else None
    }


def refresh_access_token(refresh_token):
    """
    Get new access token using refresh token.
    
    Args:
        refresh_token: The stored refresh token
        
    Returns:
        Dictionary with new access_token, refresh_token, expiry
    """
    credentials = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET
    )
    
    credentials.refresh(Request())
    
    print("Successfully refreshed access token")
    
    return {
        "access_token": credentials.token,
        "refresh_token": credentials.refresh_token or refresh_token,
        "expiry": credentials.expiry.isoformat() if credentials.expiry else None
    }
