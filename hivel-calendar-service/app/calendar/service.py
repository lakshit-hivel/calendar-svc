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
    Captures ALL fields from the Google Calendar API.
    
    Args:
        event: Raw event from Google API
        source_email: Calendar email this event came from
        
    Returns:
        Parsed event dictionary with all fields
    """
    # Get attendees with full details
    attendees = []
    for attendee in event.get('attendees', []):
        attendees.append({
            'email': attendee.get('email'),
            'displayName': attendee.get('displayName'),
            'responseStatus': attendee.get('responseStatus'),
            'organizer': attendee.get('organizer', False),
            'self': attendee.get('self', False),
            'optional': attendee.get('optional', False),
            'resource': attendee.get('resource', False),
            'comment': attendee.get('comment')
        })
    
    # Get start/end with timezone
    start = event.get('start', {})
    end = event.get('end', {})
    
    # Get creator and organizer
    creator = event.get('creator', {})
    organizer = event.get('organizer', {})
    
    # Get conference data
    conference_data = event.get('conferenceData', {})
    
    return {
        # Core identifiers
        'google_event_id': event.get('id'),
        'kind': event.get('kind'),
        'etag': event.get('etag'),
        'status': event.get('status'),
        'iCalUID': event.get('iCalUID'),
        'sequence': event.get('sequence'),
        
        # Content
        'title': event.get('summary', 'No Title'),
        'description': event.get('description'),
        'location': event.get('location'),
        'colorId': event.get('colorId'),
        
        # Links
        'htmlLink': event.get('htmlLink'),
        'hangoutLink': event.get('hangoutLink'),
        
        # Timestamps
        'created': event.get('created'),
        'updated': event.get('updated'),
        
        # Start/End with timezone
        'start_time': start.get('dateTime') or start.get('date'),
        'start_timezone': start.get('timeZone'),
        'end_time': end.get('dateTime') or end.get('date'),
        'end_timezone': end.get('timeZone'),
        
        # People
        'creator_email': creator.get('email'),
        'creator_displayName': creator.get('displayName'),
        'creator_self': creator.get('self', False),
        'organizer_email': organizer.get('email'),
        'organizer_displayName': organizer.get('displayName'),
        'organizer_self': organizer.get('self', False),
        
        # Attendees
        'attendees': attendees,
        
        # Recurrence
        'recurringEventId': event.get('recurringEventId'),
        'recurrence': event.get('recurrence'),
        'originalStartTime': event.get('originalStartTime'),
        
        # Event properties
        'event_type': event.get('eventType'),
        'visibility': event.get('visibility'),
        'transparency': event.get('transparency'),
        'privateCopy': event.get('privateCopy', False),
        'locked': event.get('locked', False),
        'guestsCanModify': event.get('guestsCanModify', False),
        'guestsCanInviteOthers': event.get('guestsCanInviteOthers', True),
        'guestsCanSeeOtherGuests': event.get('guestsCanSeeOtherGuests', True),
        
        # Conference/Meeting
        'conferenceData': conference_data,
        'conferenceId': conference_data.get('conferenceId') if conference_data else None,
        
        # Reminders
        'reminders': event.get('reminders'),
        
        # Attachments
        'attachments': event.get('attachments'),
        
        # Source calendar
        'source_email': source_email
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
    
    # NOTE:
    # We intentionally return the **raw Google event objects** here,
    # instead of our own parsed/normalized structure.
    # This lets downstream consumers (and the DB layer) work directly
    # with the native Google Calendar fields.
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
                    # Use the raw Google event object and just annotate it
                    # with minimal extra context.
                    raw_event = dict(event)
                    raw_event["source_email"] = email
                    raw_event["org_id"] = org_id
                    all_events.append(raw_event)
                
                if page_token is None:
                    done = True
                    
            except Exception as e:
                logging.error(f"Error fetching from {email}: {e}")
                done = True
    
    print(f"Fetched {len(all_events)} total events")
    return all_events
