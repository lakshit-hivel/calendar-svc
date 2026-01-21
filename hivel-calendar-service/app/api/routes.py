"""
FastAPI routes for the calendar integration.
Uses functional modules for auth, tokens, and calendar.
"""

import os
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta
from dotenv import load_dotenv

from app.auth import oauth
from app.auth import token_manager
from app.calendar import service as calendar_service

load_dotenv()

# Config
FRONTEND_SUCCESS_URL = os.getenv("FRONTEND_SUCCESS_URL", "http://localhost:3000")

router = APIRouter()


# ============================================
# OAUTH ENDPOINTS
# ============================================

@router.get("/auth/start")
def start_oauth(org_id: int):
    """
    Start OAuth flow.
    Frontend calls this, we return the Google authorization URL.
    
    Example: GET /auth/start?org_id=123
    """
    authorization_url = oauth.get_authorization_url(org_id)
    return {"authorization_url": authorization_url}


@router.get("/auth/callback")
def oauth_callback(
    code: str = Query(...),
    state: str = Query(...)  # Contains org_id
):
    """
    OAuth callback.
    Google redirects here after admin approves.
    We exchange code for tokens and store them (with AES encryption).
    """
    try:
        org_id = int(state)
        
        # Exchange code for tokens
        tokens = oauth.exchange_code_for_tokens(code)
        
        # Store tokens (with AES encryption)
        token_manager.save_tokens(org_id, tokens)
        
        # Redirect to frontend success page
        return RedirectResponse(
            url=f"{FRONTEND_SUCCESS_URL}?org_id={org_id}&status=success"
        )
        
    except Exception as e:
        return RedirectResponse(
            url=f"{FRONTEND_SUCCESS_URL}?status=error&message={str(e)}"
        )


# ============================================
# CALENDAR ENDPOINTS
# ============================================

@router.get("/calendar/sync")
def sync_calendar(
    org_id: int,
    start_date: str = None,
    end_date: str = None
):
    """
    Fetch calendar events for an organization.
    Only fetches from users the Marketplace admin permitted.
    
    Example: GET /calendar/sync?org_id=123&start_date=2024-01-01T00:00:00Z
    """
    try:
        # Get valid access token (auto-refreshes if expired)
        access_token = token_manager.get_valid_token(org_id)
        
        # Default date range
        if not start_date:
            start_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%dT00:00:00Z")
        if not end_date:
            end_date = datetime.utcnow().strftime("%Y-%m-%dT23:59:59Z")
        
        # Fetch all events
        events = calendar_service.fetch_data(org_id, access_token, start_date, end_date)
        
        return {
            "status": "success",
            "org_id": org_id,
            "events_count": len(events),
            "events": events
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calendar/users")
def get_accessible_users(org_id: int):
    """
    List all calendars we can access for this org.
    For Marketplace app, shows ONLY users the admin scoped.
    
    Example: GET /calendar/users?org_id=123
    """
    try:
        access_token = token_manager.get_valid_token(org_id)
        service = calendar_service.build_calendar_service(access_token)
        calendars = calendar_service.fetch_all_calendar_list(service)
        
        return {
            "status": "success",
            "org_id": org_id,
            "accessible_calendars": calendars,
            "count": len(calendars)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# HEALTH CHECK
# ============================================

@router.get("/health")
def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "service": "hivel-calendar"}
