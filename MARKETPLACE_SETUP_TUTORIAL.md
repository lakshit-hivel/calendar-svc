# Google Workspace Marketplace App: Complete Beginner's Guide

## What Are We Building?

We're going to publish "Hivel Calendar Integration" as an app in Google's Marketplace (like an app store for Google Workspace). When clients install it, they can choose which users' calendars Hivel can access.

---

## Prerequisites

Before you start, you need:
- [ ] A Google account (your work email is fine)
- [ ] Access to Google Cloud Console (free to sign up)
- [ ] A domain for Hivel (e.g., `hivel.ai`)
- [ ] Privacy Policy URL (required for publishing)
- [ ] Terms of Service URL (optional but recommended)

---

## PART 1: Google Cloud Project Setup

### Step 1.1: Go to Google Cloud Console

1. Open your browser
2. Go to: **https://console.cloud.google.com**
3. Sign in with your Google account

### Step 1.2: Create a New Project

1. Click the project dropdown at the top (next to "Google Cloud")
2. Click **"New Project"** in the popup
3. Fill in:
   - **Project name**: `Hivel Calendar Integration`
   - **Organization**: Select your org (or leave as "No organization")
   - **Location**: Leave default
4. Click **"Create"**
5. Wait for the project to be created (about 30 seconds)
6. Make sure this new project is selected in the dropdown

### Step 1.3: Enable Required APIs

1. In the left sidebar, go to **APIs & Services** → **Library**
2. Search for and enable these APIs (click each one → click "Enable"):

| API to Enable | What It's For |
|---------------|---------------|
| **Google Calendar API** | Access calendar data |
| **Google Workspace Marketplace SDK** | Publish to Marketplace |
| **Admin SDK API** | (Optional) List users in groups |

---

## PART 2: OAuth Consent Screen Setup

This is what users see when your app asks for permission.

### Step 2.1: Navigate to OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. You'll see "User Type" selection

### Step 2.2: Select User Type

- Select **"External"** (required for Marketplace apps)
- Click **"Create"**

> ⚠️ "External" means the app can be used by users outside your organization (which is what you want - Chargebee needs to use it)

### Step 2.3: Fill App Information

**Step 1 of 4: OAuth consent screen**

| Field | What to Enter |
|-------|---------------|
| App name | `Hivel Calendar Integration` |
| User support email | Your email (e.g., `support@hivel.ai`) |
| App logo | Upload a 120x120 PNG (optional for now) |
| App home page | `https://hivel.ai` |
| App privacy policy link | `https://hivel.ai/privacy` (REQUIRED) |
| App terms of service link | `https://hivel.ai/terms` |
| Developer contact email | Your email |

Click **"Save and Continue"**

### Step 2.4: Add Scopes

**Step 2 of 4: Scopes**

1. Click **"Add or Remove Scopes"**
2. In the search box, search for each scope and check the box:

| Scope | Description |
|-------|-------------|
| `https://www.googleapis.com/auth/calendar.readonly` | Read calendar events |
| `https://www.googleapis.com/auth/userinfo.email` | Get user email |

3. Click **"Update"**
4. Click **"Save and Continue"**

### Step 2.5: Test Users (Skip for now)

**Step 3 of 4: Test users**

- Skip this for now (you'll add test users later)
- Click **"Save and Continue"**

### Step 2.6: Summary

**Step 4 of 4: Summary**

- Review everything
- Click **"Back to Dashboard"**

---

## PART 3: Create OAuth Credentials

These are the "keys" your app will use.

### Step 3.1: Create OAuth Client ID

1. Go to **APIs & Services** → **Credentials**
2. Click **"+ Create Credentials"** → **"OAuth client ID"**

### Step 3.2: Configure OAuth Client

| Field | What to Enter |
|-------|---------------|
| Application type | **Web application** |
| Name | `Hivel Calendar Web Client` |
| Authorized redirect URIs | `https://your-backend-url.com/oauth/callback` |

> 📝 The redirect URI is where Google sends users after they authorize. Replace with your actual backend URL.

3. Click **"Create"**

### Step 3.3: Save Your Credentials

A popup will show:
- **Client ID**: `123456789-abc...apps.googleusercontent.com`
- **Client Secret**: `GOCSPX-...`

**IMPORTANT**: 
- Click **"Download JSON"** to save these
- Store them securely (treat like passwords!)
- You'll need these in your code

---

## PART 4: Configure Marketplace SDK

This is where you set up the actual Marketplace listing.

### Step 4.1: Enable Marketplace SDK (if not done)

1. Go to **APIs & Services** → **Library**
2. Search for **"Google Workspace Marketplace SDK"**
3. Click it → Click **"Enable"**

### Step 4.2: Configure the SDK

1. Go to **APIs & Services** → **Google Workspace Marketplace SDK**
2. Click **"Configuration"** tab

### Step 4.3: Fill Configuration

**App Configuration:**

| Field | What to Enter |
|-------|---------------|
| App name | `Hivel Calendar Integration` |
| Short description | `Engineering analytics from Google Calendar` |
| App icon | Upload 128x128 PNG |
| Terms of Service URL | `https://hivel.ai/terms` |
| Privacy Policy URL | `https://hivel.ai/privacy` |
| Support URL | `https://hivel.ai/support` |

**OAuth Client Configuration:**

| Field | What to Enter |
|-------|---------------|
| OAuth2 Client ID | Paste the Client ID from Step 3.3 |

**API Configuration:**

| Field | What to Enter |
|-------|---------------|
| Google Calendar API | Check the box |

**Installation Type:**

Select: **"Admin can install app for users in their organization"**

> ⚠️ This is crucial! It allows admins to install for specific users/groups.

Click **"Save"**

---

## PART 5: Create App Listing

This is what appears in the Marketplace.

### Step 5.1: Go to Store Listing

1. Still in Marketplace SDK
2. Click **"Store Listing"** tab

### Step 5.2: Fill Listing Information

**Category:**
- Select: **Productivity**

**Detailed Description:**
```
Hivel Calendar Integration provides engineering analytics by analyzing calendar data.

Key Features:
• Meeting time analytics for engineering teams
• Focus time tracking
• Internal vs external meeting breakdown

This app requests read-only access to Google Calendar to compute metrics displayed in the Hivel dashboard.
```

**Screenshots:**
- Add at least 1 screenshot (1280x800 recommended)
- Show what users get after integrating

**Regions:**
- Select regions where app will be available
- Or select "All regions"

Click **"Save"**

---

## PART 6: Build Fresh Backend Service (From Scratch)

We're building a completely new service. No legacy code, no confusion.

### Step 6.1: Project Structure

Create this folder structure:

```
hivel-calendar-service/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Environment variables
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── oauth.py            # OAuth flow handling
│   │   └── token_manager.py    # Token storage & refresh
│   │
│   ├── calendar/
│   │   ├── __init__.py
│   │   ├── service.py          # Calendar API calls
│   │   └── models.py           # Data models
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py       # DB connection
│   │   └── models.py           # SQLAlchemy models
│   │
│   └── api/
│       ├── __init__.py
│       └── routes.py           # API endpoints
│
├── requirements.txt
├── .env                        # Environment variables (DON'T COMMIT)
├── .env.example                # Template for env vars
└── README.md
```

### Step 6.2: Create requirements.txt

```txt
# requirements.txt

# Web framework
fastapi==0.109.0
uvicorn==0.27.0

# Google APIs
google-auth==2.27.0
google-auth-oauthlib==1.2.0
google-api-python-client==2.116.0

# Database
sqlalchemy==2.0.25
psycopg2-binary==2.9.9

# Environment variables
python-dotenv==1.0.0

# HTTP client
httpx==0.26.0
```

### Step 6.3: Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# or: venv\Scripts\activate  # Windows

# Install packages
pip install -r requirements.txt
```

### Step 6.4: Create .env File

```bash
# .env (DON'T COMMIT THIS FILE!)

# Google OAuth Credentials (from Step 3.3)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-secret-here

# Your backend URL
REDIRECT_URI=https://your-backend.com/auth/callback
FRONTEND_SUCCESS_URL=https://app.hivel.ai/integration-success

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/hivel_calendar

# App settings
DEBUG=true
```

### Step 6.5: Create config.py

```python
# app/config.py

import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET")
    REDIRECT_URI: str = os.getenv("REDIRECT_URI")
    FRONTEND_SUCCESS_URL: str = os.getenv("FRONTEND_SUCCESS_URL")
    
    # Google Calendar Scopes
    SCOPES: list = [
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/userinfo.email"
    ]
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    # Debug
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

settings = Settings()
```

### Step 6.6: Skip Database Models (Use Existing Tables!)

**You already have these tables - no need to create new ones!**

| Table | Purpose |
|-------|---------|
| `insightly.user_integration_details` | OAuth tokens (with AES encryption) |
| `insightly_meeting.gcalendar` | Raw calendar events from Google |
| `insightly_meeting.gcal_event` | Processed meeting data |

### Step 6.7: Create Database Connection (Using psycopg2 like existing code)

```python
# app/database/connection.py

import os
import psycopg2
import psycopg2.extras
from app.config import settings

def get_connection():
    """Get PostgreSQL connection"""
    return psycopg2.connect(
        dbname=settings.POSTGRES_DBNAME,
        user=settings.POSTGRES_USERNAME,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_HOST,
        port=5432
    )
```

Update your `config.py` to include these:

```python
# Add to app/config.py

class Settings:
    # ... existing settings ...
    
    # Database (PostgreSQL)
    POSTGRES_DBNAME: str = os.getenv("POSTGRES_DBNAME")
    POSTGRES_USERNAME: str = os.getenv("POSTGRES_USERNAME")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST")
```

Update your `.env`:

```bash
# Database
POSTGRES_DBNAME=your_db_name
POSTGRES_USERNAME=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=your_host
```


### Step 6.8: Create OAuth Handler (THE IMPORTANT PART)

```python
# app/auth/oauth.py

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from app.config import settings
import json

class GoogleOAuth:
    """Handles all OAuth operations for Marketplace app"""
    
    def __init__(self):
        self.client_config = {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.REDIRECT_URI]
            }
        }
    
    def get_authorization_url(self, org_id: int) -> str:
        """
        Generate the URL where admin clicks to start OAuth.
        Called when client wants to integrate.
        
        Args:
            org_id: Your internal organization ID
            
        Returns:
            URL to redirect admin to
        """
        flow = Flow.from_client_config(
            self.client_config,
            scopes=settings.SCOPES,
            redirect_uri=settings.REDIRECT_URI
        )
        
        # state parameter will be returned in callback
        # Use it to know which org is integrating
        authorization_url, state = flow.authorization_url(
            access_type='offline',      # Get refresh token
            include_granted_scopes='true',
            prompt='consent',           # Always show consent screen
            state=str(org_id)           # Pass org_id through OAuth flow
        )
        
        return authorization_url
    
    def exchange_code_for_tokens(self, authorization_code: str) -> dict:
        """
        Exchange the authorization code for access & refresh tokens.
        Called when Google redirects back to your callback URL.
        
        Args:
            authorization_code: The code from callback URL
            
        Returns:
            Dictionary with tokens
        """
        flow = Flow.from_client_config(
            self.client_config,
            scopes=settings.SCOPES,
            redirect_uri=settings.REDIRECT_URI
        )
        
        # Exchange code for tokens
        flow.fetch_token(code=authorization_code)
        credentials = flow.credentials
        
        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "expiry": credentials.expiry.isoformat() if credentials.expiry else None,
            "scopes": list(credentials.scopes) if credentials.scopes else []
        }
    
    def refresh_access_token(self, refresh_token: str) -> dict:
        """
        Get new access token using refresh token.
        Called when access token expires.
        
        Args:
            refresh_token: The stored refresh token
            
        Returns:
            New tokens dictionary
        """
        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET
        )
        
        # Refresh the token
        credentials.refresh(Request())
        
        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token or refresh_token,
            "expiry": credentials.expiry.isoformat() if credentials.expiry else None
        }

# Create singleton instance
google_oauth = GoogleOAuth()
```

### Step 6.9: Create Token Manager (Using Existing Table with AES Encryption)

```python
# app/auth/token_manager.py

import psycopg2.extras
from datetime import datetime, timedelta
from app.database.connection import get_connection
from app.auth.oauth import google_oauth

class TokenManager:
    """
    Manages storing and retrieving OAuth tokens.
    Uses existing insightly.user_integration_details table with AES encryption.
    """
    
    PROVIDER = 'GOOGLE_CALENDAR'
    
    def get_tokens(self, org_id: int) -> dict:
        """
        Get decrypted tokens from database.
        
        Args:
            org_id: Organization ID
            
        Returns:
            Dictionary with token, refresh_token, expires_at
        """
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        aes_decrypt(uid.accesstoken) as token, 
                        aes_decrypt(uid.refreshtoken) as refresh_token, 
                        COALESCE(
                            uid.access_token_generation_date + 
                            CAST(uid.expiresin || ' minutes' AS INTERVAL), 
                            NOW()
                        ) as expires_at 
                    FROM insightly.user_integration_details uid 
                    WHERE uid.organizationid = %s 
                    AND provider = %s
                """, (org_id, self.PROVIDER))
                
                result = cursor.fetchone()
                if result:
                    return dict(result)
                return None
        finally:
            conn.close()
    
    def save_tokens(self, org_id: int, tokens: dict) -> bool:
        """
        Save tokens with AES encryption.
        
        Args:
            org_id: Organization ID
            tokens: Dictionary with access_token, refresh_token
            
        Returns:
            True if successful
        """
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                # Check if record exists
                cursor.execute("""
                    SELECT id FROM insightly.user_integration_details 
                    WHERE organizationid = %s AND provider = %s
                """, (org_id, self.PROVIDER))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing record
                    cursor.execute("""
                        UPDATE insightly.user_integration_details
                        SET accesstoken = aes_encrypt(%s), 
                            refreshtoken = aes_encrypt(%s),
                            access_token_generation_date = NOW(),
                            expiresin = 60
                        WHERE organizationid = %s AND provider = %s
                    """, (
                        tokens.get("access_token"),
                        tokens.get("refresh_token"),
                        org_id,
                        self.PROVIDER
                    ))
                else:
                    # Insert new record
                    cursor.execute("""
                        INSERT INTO insightly.user_integration_details 
                        (organizationid, provider, accesstoken, refreshtoken, 
                         access_token_generation_date, expiresin)
                        VALUES (%s, %s, aes_encrypt(%s), aes_encrypt(%s), NOW(), 60)
                    """, (
                        org_id,
                        self.PROVIDER,
                        tokens.get("access_token"),
                        tokens.get("refresh_token")
                    ))
                
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_valid_token(self, org_id: int) -> str:
        """
        Get a valid access token, refreshing if needed.
        
        Args:
            org_id: Organization ID
            
        Returns:
            Valid access token string
        """
        tokens = self.get_tokens(org_id)
        
        if not tokens:
            raise Exception(f"No tokens found for organization {org_id}")
        
        # Check if token is expired (with 5 min buffer)
        expires_at = tokens.get("expires_at")
        if expires_at and expires_at < datetime.now() + timedelta(minutes=5):
            # Token expired, refresh it
            print(f"Token expired for org {org_id}, refreshing...")
            new_tokens = google_oauth.refresh_access_token(tokens["refresh_token"])
            
            # Save new tokens
            self.save_tokens(org_id, new_tokens)
            
            return new_tokens["access_token"]
        
        return tokens["token"]

# Create singleton
token_manager = TokenManager()
```


# Create singleton
token_manager = TokenManager()
```

### Step 6.10: Create Calendar Service

```python
# app/calendar/service.py

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta
from typing import List
import json

class CalendarService:
    """Fetches and processes calendar data"""
    
    def __init__(self, access_token: str):
        """
        Initialize with access token.
        
        Args:
            access_token: Valid OAuth access token
        """
        credentials = Credentials(token=access_token)
        self.service = build('calendar', 'v3', credentials=credentials)
    
    def get_all_calendars(self) -> List[str]:
        """
        Get list of all calendar IDs accessible to this token.
        For Marketplace app, this returns ONLY calendars for
        users the admin scoped the app to.
        
        Returns:
            List of calendar email/IDs
        """
        calendars = []
        page_token = None
        
        while True:
            calendar_list = self.service.calendarList().list(
                pageToken=page_token
            ).execute()
            
            for calendar in calendar_list.get('items', []):
                calendars.append(calendar['id'])
            
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break
        
        return calendars
    
    def fetch_events(
        self, 
        calendar_id: str, 
        start_date: datetime = None, 
        end_date: datetime = None
    ) -> List[dict]:
        """
        Fetch events from a specific calendar.
        
        Args:
            calendar_id: Calendar email/ID
            start_date: Start of date range (default: 30 days ago)
            end_date: End of date range (default: today)
            
        Returns:
            List of event dictionaries
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        events = []
        page_token = None
        
        while True:
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=start_date.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime',
                pageToken=page_token
            ).execute()
            
            for event in events_result.get('items', []):
                events.append(self._parse_event(event, calendar_id))
            
            page_token = events_result.get('nextPageToken')
            if not page_token:
                break
        
        return events
    
    def _parse_event(self, event: dict, calendar_id: str) -> dict:
        """Parse raw Google event into our format"""
        
        # Get attendees
        attendees = []
        for attendee in event.get('attendees', []):
            attendees.append({
                'email': attendee.get('email'),
                'response': attendee.get('responseStatus'),
                'organizer': attendee.get('organizer', False)
            })
        
        # Get start/end times
        start = event.get('start', {})
        end = event.get('end', {})
        
        return {
            'google_event_id': event.get('id'),
            'title': event.get('summary', 'No Title'),
            'description': event.get('description'),
            'start_time': start.get('dateTime') or start.get('date'),
            'end_time': end.get('dateTime') or end.get('date'),
            'creator_email': event.get('creator', {}).get('email'),
            'source_calendar': calendar_id,
            'attendees': attendees,
            'meeting_link': event.get('hangoutLink')
        }
    
    def fetch_all_events(
        self, 
        start_date: datetime = None, 
        end_date: datetime = None
    ) -> List[dict]:
        """
        Fetch events from ALL accessible calendars.
        
        For Marketplace app, this automatically only fetches
        from users the admin permitted.
        """
        all_events = []
        
        # Get all accessible calendars
        calendars = self.get_all_calendars()
        print(f"Found {len(calendars)} accessible calendars")
        
        # Fetch events from each
        for calendar_id in calendars:
            try:
                events = self.fetch_events(calendar_id, start_date, end_date)
                all_events.extend(events)
                print(f"  - {calendar_id}: {len(events)} events")
            except Exception as e:
                print(f"  - {calendar_id}: Error - {e}")
        
        return all_events
```

### Step 6.11: Create API Routes

```python
# app/api/routes.py

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from app.auth.oauth import google_oauth
from app.auth.token_manager import token_manager
from app.calendar.service import CalendarService
from app.config import settings
from datetime import datetime

router = APIRouter()

# ============================================
# OAUTH ENDPOINTS (For Marketplace Integration)
# ============================================

@router.get("/auth/start")
def start_oauth(org_id: int):
    """
    Step 1: Start OAuth flow.
    Frontend calls this, we return the Google authorization URL.
    
    Example: GET /auth/start?org_id=123
    """
    authorization_url = google_oauth.get_authorization_url(org_id)
    return {"authorization_url": authorization_url}


@router.get("/auth/callback")
def oauth_callback(
    code: str = Query(...),
    state: str = Query(...)  # Contains org_id
):
    """
    Step 2: OAuth callback.
    Google redirects here after admin approves.
    We exchange code for tokens and store them (with AES encryption).
    
    This URL must match what you set in Google Cloud Console!
    """
    try:
        # Get org_id from state parameter
        org_id = int(state)
        
        # Exchange authorization code for tokens
        tokens = google_oauth.exchange_code_for_tokens(code)
        
        # Store tokens in database (with AES encryption)
        token_manager.save_tokens(org_id, tokens)
        
        # Redirect to frontend success page
        return RedirectResponse(
            url=f"{settings.FRONTEND_SUCCESS_URL}?org_id={org_id}&status=success"
        )
        
    except Exception as e:
        # Redirect to frontend with error
        return RedirectResponse(
            url=f"{settings.FRONTEND_SUCCESS_URL}?status=error&message={str(e)}"
        )


# ============================================
# CALENDAR DATA ENDPOINTS
# ============================================

@router.get("/calendar/sync")
def sync_calendar(
    org_id: int,
    start_date: str = None,  # Format: 2024-01-01
    end_date: str = None
):
    """
    Fetch calendar events for an organization.
    This only fetches from users the Marketplace admin permitted.
    
    Example: GET /calendar/sync?org_id=123&start_date=2024-01-01
    """
    try:
        # Get valid access token (auto-refreshes if needed)
        access_token = token_manager.get_valid_token(org_id)
        
        # Create calendar service
        calendar_service = CalendarService(access_token)
        
        # Parse dates
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        # Fetch all events
        events = calendar_service.fetch_all_events(start, end)
        
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
    List all users whose calendars we can access.
    For Marketplace app, this shows ONLY the users
    the admin scoped the app to.
    
    Example: GET /calendar/users?org_id=123
    """
    try:
        access_token = token_manager.get_valid_token(org_id)
        calendar_service = CalendarService(access_token)
        
        calendars = calendar_service.get_all_calendars()
        
        return {
            "status": "success",
            "org_id": org_id,
            "accessible_users": calendars,
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
```

### Step 6.12: Create Main App

```python
# app/main.py

from fastapi import FastAPI
from app.api.routes import router
from app.database.connection import init_db

# Create FastAPI app
app = FastAPI(
    title="Hivel Calendar Service",
    description="Google Calendar integration via Marketplace",
    version="1.0.0"
)

# Include routes
app.include_router(router)

# Initialize database on startup
@app.on_event("startup")
def startup():
    print("🚀 Starting Hivel Calendar Service...")
    init_db()
    print("✅ Database tables created")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Step 6.13: Run Your Service

```bash
# Make sure you're in the project directory
cd hivel-calendar-service

# Activate virtual environment
source venv/bin/activate

# Run the server
python -m app.main

# Or use uvicorn directly
uvicorn app.main:app --reload --port 8000
```

Your service will be running at `http://localhost:8000`

### Step 6.14: Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Start OAuth (returns Google authorization URL)
curl "http://localhost:8000/auth/start?org_id=1"

# After OAuth completes, sync calendars
curl "http://localhost:8000/calendar/sync?org_id=1"

# List accessible users
curl "http://localhost:8000/calendar/users?org_id=1"
```

---

## PART 7: Testing Before Publishing

### Step 7.1: Local Testing Setup

1. **Update REDIRECT_URI in .env**:
   - For local testing, use ngrok to expose localhost:
   ```bash
   ngrok http 8000
   ```
   - Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)
   - Update `.env`: `REDIRECT_URI=https://abc123.ngrok.io/auth/callback`
   - Also update this URL in Google Cloud Console → Credentials

2. **Add yourself as test user**:
   - Go to Google Cloud Console → OAuth consent screen
   - Under "Test users", add your email

### Step 7.2: Test the Full Flow

1. **Start OAuth**:
   ```bash
   curl "http://localhost:8000/auth/start?org_id=1"
   ```
   Copy the `authorization_url` and open in browser

2. **Approve the app** in Google's consent screen

3. **Check callback** - You should be redirected to your success URL

4. **Verify tokens stored** - Check your database

5. **Fetch calendar data**:
   ```bash
   curl "http://localhost:8000/calendar/sync?org_id=1"
   ```

6. **Check accessible users**:
   ```bash
   curl "http://localhost:8000/calendar/users?org_id=1"
   ```

---

## PART 8: Deploy & Submit for Review

### Step 8.1: Deploy Your Service

Deploy to any cloud provider (AWS, GCP, Heroku, etc.):

```bash
# Example: Deploy to Heroku
heroku create hivel-calendar-service
heroku config:set GOOGLE_CLIENT_ID=...
heroku config:set GOOGLE_CLIENT_SECRET=...
heroku config:set REDIRECT_URI=https://hivel-calendar-service.herokuapp.com/auth/callback
git push heroku main
```

### Step 8.2: Update Redirect URI

1. Go to Google Cloud Console → Credentials
2. Edit your OAuth Client
3. Update Authorized redirect URI to your deployed URL

### Step 8.3: Submit for Review

1. Go to **OAuth consent screen** → Click **"Publish App"**
2. Go to **Marketplace SDK** → **Store Listing** → Click **"Publish"**
3. Wait 1-4 weeks for Google review

---

## PART 9: After Approval - Client Flow

### Step 9.1: What Clients Do

1. Client admin goes to Google Workspace Marketplace
2. Searches for "Hivel Calendar Integration"
3. Clicks **"Admin Install"**
4. **Selects which users/groups** can use the app
5. Clicks **"Install"**
6. Gets redirected to your callback → Tokens stored → Done!

### Step 9.2: What You Get

When you call `/calendar/users?org_id=X`:
- You'll see ONLY the users the admin selected
- Not the whole organization!
- Google enforces this automatically

---

## Quick Reference

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/auth/start?org_id=X` | GET | Get OAuth authorization URL |
| `/auth/callback` | GET | OAuth callback (Google redirects here) |
| `/calendar/sync?org_id=X` | GET | Fetch calendar events |
| `/calendar/users?org_id=X` | GET | List accessible users |

### Environment Variables

| Variable | Description |
|----------|-------------|
| `GOOGLE_CLIENT_ID` | From Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | From Google Cloud Console |
| `REDIRECT_URI` | Your callback URL |
| `FRONTEND_SUCCESS_URL` | Where to redirect after OAuth |
| `DATABASE_URL` | PostgreSQL connection string |

---

## Troubleshooting

### Error: "redirect_uri_mismatch"
- The REDIRECT_URI in your code must EXACTLY match Google Cloud Console
- Check for trailing slashes, http vs https

### Error: "invalid_grant"
- Authorization code expired (they expire in ~10 minutes)
- User revoked access
- Try starting OAuth flow again

### Error: "Access blocked: App not verified"
- Your app is still in testing mode
- Add your email to test users, OR
- Submit for verification

### Error: "No tokens found for organization"
- OAuth hasn't been completed for this org
- Call `/auth/start` first

---

## Timeline Summary

| Phase | What You Do | Duration |
|-------|-------------|----------|
| 1. GCP Setup | Create project, enable APIs | 1 day |
| 2. OAuth Setup | Configure consent screen | 1 day |
| 3. Credentials | Create client ID/secret | 30 min |
| 4. Marketplace SDK | Configure app settings | 1 day |
| 5. Store Listing | Add description, screenshots | 1 day |
| 6. Build Service | Create fresh Python backend | 2-3 days |
| 7. Testing | Test with internal users | 2-3 days |
| 8. Deploy | Deploy to cloud | 1 day |
| 9. Submit | Request publishing | 30 min |
| 10. Review | Wait for Google | 1-4 weeks |
| **Total** | | **2-3 weeks + review time** |
