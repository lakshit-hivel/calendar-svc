"""
Calendar data fetching functions.
Functional style matching existing Hivel fetch_new_data.py.
"""

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)


def build_calendar_service(access_token):
    """
    Build Google Calendar service with access token.
    
    Args:
        access_token: Valid OAuth access token
        
    Returns:
        Google Calendar API service
    """
    credentials = Credentials(token=access_token)
    return build('calendar', 'v3', credentials=credentials)


def fetch_all_calendar_list(service):
    """
    Get list of all calendar IDs accessible to this token.
    For Marketplace app, this returns ONLY calendars for
    users the admin scoped the app to.
    
    Args:
        service: Google Calendar API service
        
    Returns:
        List of calendar email/IDs
    """
    calendar_emails = []
    page_token = None
    
    while True:
        try:
            calendar_list = service.calendarList().list(
                pageToken=page_token
            ).execute()
            
            for calendar_entry in calendar_list.get('items', []):
                calendar_emails.append(calendar_entry['id'])
            
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break
        except Exception as ex:
            logging.error(f"Failed to fetch calendars: {ex}")
            break
    
    return calendar_emails


def fetch_calendar_events(service, calendar_email, start_date, end_date, page_token=None):
    """
    Fetch events from a specific calendar.
    
    Args:
        service: Google Calendar API service
        calendar_email: Calendar email/ID
        start_date: Start of date range (ISO format string)
        end_date: End of date range (ISO format string)
        page_token: Optional pagination token
        
    Returns:
        Dictionary with items (events) and pageToken
    """
    events_result = service.events().list(
        calendarId=calendar_email,
        timeMin=start_date,
        timeMax=end_date,
        orderBy="startTime",
        singleEvents=True,
        timeZone="UTC",
        pageToken=page_token
    ).execute()
    
    events = events_result.get("items", [])
    next_page_token = events_result.get("nextPageToken")
    
    return {"items": events, "pageToken": next_page_token}


def parse_event(event, source_email):
    """
    Parse raw Google event into our format.
    
    Args:
        event: Raw event from Google API
        source_email: Calendar email this event came from
        
    Returns:
        Parsed event dictionary
    """
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
        'source_email': source_email,
        'attendees': attendees,
        'meeting_link': event.get('hangoutLink'),
        'event_type': event.get('eventType')
    }


def fetch_data(org_id, access_token, start_date, end_date):
    """
    Fetch all calendar data for an organization.
    Main entry point for calendar sync.
    
    Args:
        org_id: Organization ID
        access_token: Valid OAuth access token
        start_date: Start date (ISO format string)
        end_date: End date (ISO format string)
        
    Returns:
        List of all parsed events
    """
    print(f"Fetching calendar data for org {org_id}...")
    
    # Build service
    service = build_calendar_service(access_token)
    
    # Get all accessible calendars
    user_emails = fetch_all_calendar_list(service)
    print(f"Found {len(user_emails)} accessible calendars")
    
    if not user_emails:
        print("No calendars found!")
        return []
    
    all_events = []
    
    # Fetch events from each calendar
    for email in user_emails:
        logging.info(f"Fetching from: {email}")
        done = False
        page_token = None
        
        while not done:
            try:
                result = fetch_calendar_events(
                    service, email, start_date, end_date, page_token
                )
                events = result.get("items", [])
                page_token = result.get("pageToken")
                
                for event in events:
                    parsed = parse_event(event, email)
                    parsed["org_id"] = org_id
                    all_events.append(parsed)
                
                if page_token is None:
                    done = True
                    
            except Exception as e:
                logging.error(f"Error fetching from {email}: {e}")
                done = True
    
    print(f"Fetched {len(all_events)} total events")
    return all_events
