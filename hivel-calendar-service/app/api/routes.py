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
from app.core.logger import get_logger

load_dotenv()

# Get logger from centralized module
logger = get_logger(__name__)

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
        logger.info(f"[CALLBACK] Received callback, state={state}")
        org_id = int(state)
        
        # Exchange code for tokens
        logger.info(f"[CALLBACK] Exchanging code for tokens")
        tokens = oauth.exchange_code_for_tokens(code)
        logger.info(f"[CALLBACK] ✅ Got tokens")
        
        # Fetch user email from Google
        logger.info(f"[CALLBACK] Fetching user email")
        user_info = oauth.get_user_info(tokens.get('access_token'))
        user_email = user_info.get('email')
        logger.info(f"[CALLBACK] ✅ User email: {user_email}")
        
        # Store tokens with email (with AES encryption)
        token_manager.save_tokens(org_id, tokens, email=user_email)
        logger.info(f"[CALLBACK] ✅ Tokens saved for org {org_id}")
        
        # Redirect to frontend success page
        return RedirectResponse(
            url=f"{FRONTEND_SUCCESS_URL}?org_id={org_id}&status=success"
        )
        
    except Exception as e:
        logger.error(f"[CALLBACK] ❌ Error: {e}")
        import traceback
        logger.error(f"[CALLBACK] Traceback:\n{traceback.format_exc()}")
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
    end_date: str = None,
    save_to_db: bool = False  # Set True to save to database
):
    """
    Fetch calendar events for an organization.
    Only fetches from users the Marketplace admin permitted.
    
    Example: GET /calendar/sync?org_id=123&start_date=2024-01-01T00:00:00Z&save_to_db=true
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
        
        # Optionally save to database
        saved_count = 0
        if save_to_db:
            from app.database.events import save_events
            # TESTING: Limit to first 5 events
            test_events = events[:5]
            saved_count = save_events(test_events, org_id)
        
        return {
            "status": "success",
            "org_id": org_id,
            "events_count": len(events),
            "saved_to_db": saved_count if save_to_db else "skipped",
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
# AUTH-SVC COMPATIBLE SYNC ENDPOINT
# ============================================

from pydantic import BaseModel
from typing import Optional

class SyncQueryParams(BaseModel):
    orgId: int
    userIntegrationId: Optional[int] = None
    startDate: str
    endDate: str
    initialSync: bool = True

class SyncRequest(BaseModel):
    queryStringParameters: SyncQueryParams


@router.post("/initial-sync")
def initial_sync(request: SyncRequest):
    """
    Initial sync endpoint called by auth-svc.
    Matches the payload format expected by GoogleCalendarOAuthService.java
    
    Payload format:
    {
        "queryStringParameters": {
            "orgId": 123,
            "userIntegrationId": 456,
            "startDate": "2026-11-24T00:00:01Z",
            "endDate": "2026-01-24T00:00:01Z",
            "initialSync": true
        }
    }
    """
    params = request.queryStringParameters
    org_id = params.orgId
    start_date = params.startDate
    end_date = params.endDate
    
    logger.info(f"[SYNC START] org_id={org_id}, start_date={start_date}, end_date={end_date}, initial_sync={params.initialSync}")
    
    try:
        # Step 1: Get access token
        logger.info(f"[STEP 1] Getting access token for org {org_id}")
        access_token = token_manager.get_valid_token(org_id)
        logger.info(f"[STEP 1] ✅ Access token retrieved successfully")
        
        # Step 2: Fetch events from Google Calendar
        logger.info(f"[STEP 2] Fetching events from Google Calendar API")
        events = calendar_service.fetch_data(org_id, access_token, start_date, end_date)
        logger.info(f"[STEP 2] ✅ Fetched {len(events)} events from Google Calendar")
        
        # Step 3: Save to database
        logger.info(f"[STEP 3] Saving events to database")
        from app.database.events import save_events
        saved_count = save_events(events, org_id)
        logger.info(f"[STEP 3] ✅ Saved {saved_count}/{len(events)} events to database")
        
        # Success
        logger.info(f"[SYNC COMPLETE] org_id={org_id}, events_fetched={len(events)}, events_saved={saved_count}")
        
        return {
            "status": "success",
            "org_id": org_id,
            "events_fetched": len(events),
            "events_saved": saved_count,
            "initial_sync": params.initialSync
        }
        
    except Exception as e:
        logger.error(f"[SYNC ERROR] org_id={org_id}, error={str(e)}")
        import traceback
        logger.error(f"[SYNC ERROR] Traceback:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# HEALTH CHECK
# ============================================

@router.get("/health")
def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "service": "hivel-calendar"}
