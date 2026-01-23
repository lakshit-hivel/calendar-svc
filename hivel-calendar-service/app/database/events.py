"""
Calendar event storage functions.
Saves events to:
  - insightly_meeting.gcalendar (raw event data)
  - insightly.author (user lookup table)
  - insightly_meeting.gcal_event (normalized event data with author IDs)
Uses SELECT → INSERT/UPDATE pattern.
"""

import json
from datetime import datetime
from app.database.connection import get_connection
from app.core.logger import get_logger

logger = get_logger(__name__)

SCM_PROVIDER = 'googlecalendar'


def get_user(email, org_id, conn):
    """
    Look up an existing author by email.
    
    Args:
        email: User's email address
        org_id: Organization ID
        conn: Database connection
        
    Returns:
        id of existing author, or None if not found
    """
    if not email:
        return None
        
    cursor = None
    
    try:
        cursor = conn.cursor()
        
        # Check if author exists by decrypting stored email and comparing
        check_query = """
            SELECT id FROM insightly.author 
            WHERE aes_decrypt(email) = %(email)s 
              AND scmprovider = %(scmprovider)s 
              AND organizationid = %(organizationid)s
            LIMIT 1
        """
        
        params = {
            'email': email,
            'scmprovider': SCM_PROVIDER,
            'organizationid': org_id
        }
        
        cursor.execute(check_query, params)
        existing = cursor.fetchone()
        
        if existing:
            return existing[0]
        return None
        
    except Exception as e:
        logger.error(f"Error looking up author {email}: {e}")
        raise
    finally:
        if cursor:
            cursor.close()


def insert_user(email, org_id, conn):
    """
    Get existing user or insert a new one.
    
    Args:
        email: User's email address
        org_id: Organization ID
        conn: Database connection
        
    Returns:
        id of author (existing or newly created)
    """
    if not email:
        return None
    
    # First check if user already exists
    existing_id = get_user(email, org_id, conn)
    if existing_id:
        return existing_id
        
    # User doesn't exist, insert new one
    cursor = None
    
    try:
        cursor = conn.cursor()
        
        # Insert query - encrypt email before storing
        insert_query = """
            INSERT INTO insightly.author (
                email, scmprovider, organizationid,
                type, active, archived, createddate, modifieddate
            ) VALUES (
                aes_encrypt(%(email)s), %(scmprovider)s, %(organizationid)s,
                'USER', true, false, NOW(), NOW()
            )
            RETURNING id
        """
        
        params = {
            'email': email,
            'scmprovider': SCM_PROVIDER,
            'organizationid': org_id
        }
        
        cursor.execute(insert_query, params)
        author_id = cursor.fetchone()[0]
        
        conn.commit()
        return author_id
        
    except Exception as e:
        logger.error(f"Error inserting author {email}: {e}")
        conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()


def insert_gcalendar(event_data, conn):
    """
    Insert or update a calendar event in insightly_meeting.gcalendar.
    
    Args:
        event_data: Dictionary with event fields
        conn: Database connection
        
    Returns:
        row_id of inserted/updated record
    """
    cursor = None
    
    try:
        cursor = conn.cursor()
        
        # Check if event exists
        check_query = """
            SELECT row_id FROM insightly_meeting.gcalendar 
            WHERE id = %(id)s AND organizationid = %(organizationid)s
            LIMIT 1
        """
        
        # Insert query
        insert_query = """
            INSERT INTO insightly_meeting.gcalendar (
                id, kind, status, summary,
                creator_email, organizer_email,
                start_date_time, start_timezone,
                end_date_time, end_timezone,
                recurringeventid, eventtype,
                attendees, organizationid, source_email,
                visibility, processing_status,
                createddate, modifieddate
            ) VALUES (
                %(id)s, %(kind)s, %(status)s, %(summary)s,
                %(creator_email)s, %(organizer_email)s,
                %(start_date_time)s, %(start_timezone)s,
                %(end_date_time)s, %(end_timezone)s,
                %(recurringeventid)s, %(eventtype)s,
                %(attendees)s, %(organizationid)s, %(source_email)s,
                %(visibility)s, %(processing_status)s,
                NOW(), NOW()
            )
            RETURNING row_id
        """
        
        # Update query
        update_query = """
            UPDATE insightly_meeting.gcalendar SET
                status = %(status)s,
                summary = %(summary)s,
                creator_email = %(creator_email)s,
                organizer_email = %(organizer_email)s,
                start_date_time = %(start_date_time)s,
                end_date_time = %(end_date_time)s,
                attendees = %(attendees)s,
                source_email = %(source_email)s,
                modifieddate = NOW()
            WHERE id = %(id)s AND organizationid = %(organizationid)s
            RETURNING row_id
        """
        
        # Check if exists
        cursor.execute(check_query, event_data)
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute(update_query, event_data)
            row_id = cursor.fetchone()[0]
        else:
            cursor.execute(insert_query, event_data)
            row_id = cursor.fetchone()[0]
        
        conn.commit()
        return row_id
        
    except Exception as e:
        logger.error(f"Error upserting gcalendar {event_data.get('id')}: {e}")
        conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()


def insert_gcal_event(event_data, conn):
    """
    Insert or update a calendar event in insightly_meeting.gcal_event.
    
    Args:
        event_data: Dictionary with event fields
        conn: Database connection
        
    Returns:
        id of inserted/updated record
    """
    cursor = None
    
    try:
        cursor = conn.cursor()
        
        # Check if event exists
        check_query = """
            SELECT id FROM insightly_meeting.gcal_event 
            WHERE meeting_identifier = %(meeting_identifier)s AND organizationid = %(organizationid)s
            LIMIT 1
        """
        
        # Insert query
        insert_query = """
            INSERT INTO insightly_meeting.gcal_event (
                meeting_identifier, title, description,
                created_by, start_date_time, end_date_time,
                attendees, accepted_by, meeting_type,
                created_on, updated_on, organizationid,
                attendees_data
            ) VALUES (
                %(meeting_identifier)s, %(title)s, %(description)s,
                %(created_by)s, %(start_date_time)s, %(end_date_time)s,
                %(attendees)s, %(accepted_by)s, %(meeting_type)s,
                NOW(), NOW(), %(organizationid)s,
                %(attendees_data)s
            )
            RETURNING id
        """
        
        # Update query
        update_query = """
            UPDATE insightly_meeting.gcal_event SET
                title = %(title)s,
                description = %(description)s,
                start_date_time = %(start_date_time)s,
                end_date_time = %(end_date_time)s,
                attendees = %(attendees)s,
                accepted_by = %(accepted_by)s,
                attendees_data = %(attendees_data)s,
                updated_on = NOW()
            WHERE meeting_identifier = %(meeting_identifier)s AND organizationid = %(organizationid)s
            RETURNING id
        """
        
        # Check if exists
        cursor.execute(check_query, event_data)
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute(update_query, event_data)
            record_id = cursor.fetchone()[0]
        else:
            cursor.execute(insert_query, event_data)
            record_id = cursor.fetchone()[0]
        
        conn.commit()
        return record_id
        
    except Exception as e:
        logger.error(f"Error upserting gcal_event {event_data.get('meeting_identifier')}: {e}")
        conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()


def save_events(events, org_id):
    """
    Save all events to gcalendar, authors, and gcal_event tables.
    
    Flow:
      1. Insert raw event → gcalendar
      2. Upsert creator/attendees → authors (get IDs)
      3. Insert normalized event with author IDs → gcal_event
    
    Args:
        events: List of parsed events from Google Calendar
        org_id: Organization ID
        
    Returns:
        Count of saved events
    """
    conn = get_connection()
    saved_count = 0
    
    try:
        for event in events:
            try:
                # Extract nested fields from raw Google Calendar API format
                start = event.get('start', {})
                end = event.get('end', {})
                creator = event.get('creator', {})
                organizer = event.get('organizer', {})
                
                # Start/end can be dateTime or date (all-day events)
                start_time = start.get('dateTime') or start.get('date')
                end_time = end.get('dateTime') or end.get('date')
                start_timezone = start.get('timeZone', 'UTC')
                end_timezone = end.get('timeZone', 'UTC')
                
                # Creator/organizer emails
                creator_email = creator.get('email')
                organizer_email = organizer.get('email')
                
                # Prepare data for gcalendar table
                raw_attendees = event.get('attendees', [])
                
                # Normalize attendees to match expected DB format (all fields, nulls for missing)
                attendees = []
                for a in raw_attendees:
                    attendees.append({
                        'email': a.get('email'),
                        'responseStatus': a.get('responseStatus'),
                        'organizer': a.get('organizer'),
                        'self': a.get('self'),
                        'displayName': a.get('displayName'),
                        'optional': a.get('optional'),
                        'comment': a.get('comment'),
                        'resource': a.get('resource')
                    })
                
                attendees_json = json.dumps(attendees)
                
                gcalendar_data = {
                    'id': event.get('id'),
                    'kind': event.get('kind', 'calendar#event'),
                    'status': event.get('status', 'confirmed'),
                    'summary': event.get('summary'),
                    'creator_email': creator_email,
                    'organizer_email': organizer_email or creator_email,
                    'start_date_time': start_time,
                    'start_timezone': start_timezone,
                    'end_date_time': end_time,
                    'end_timezone': end_timezone,
                    'recurringeventid': event.get('recurringEventId'),
                    'eventtype': event.get('eventType', 'default'),
                    'attendees': attendees_json,
                    'organizationid': org_id,
                    'source_email': event.get('source_email'),
                    'visibility': event.get('visibility', 'default'),
                    'processing_status': 'COMPLETED'
                }
                
                # Step 1: Insert raw event to gcalendar
                insert_gcalendar(gcalendar_data, conn)
                
                # Step 2: Upsert authors and get IDs
                # Creator
                creator_id = insert_user(
                    creator_email,
                    org_id,
                    conn
                )
                
                # All attendees
                attendee_ids = []
                accepted_ids = []
                for attendee in attendees:
                    author_id = insert_user(
                        attendee.get('email'),
                        org_id,
                        conn
                    )
                    if author_id:
                        attendee_ids.append(str(author_id))
                        # Check if accepted (responseStatus == 'accepted')
                        if attendee.get('responseStatus') == 'accepted':
                            accepted_ids.append(str(author_id))
                
                # Step 3: Prepare data for gcal_event table with author IDs
                gcal_event_data = {
                    'meeting_identifier': event.get('id'),
                    'title': event.get('summary'),
                    'description': event.get('description'),
                    'created_by': creator_id,  # Using author ID
                    'start_date_time': start_time,
                    'end_date_time': end_time,
                    'attendees': '{' + ','.join(attendee_ids) + '}',  # PostgreSQL array format
                    'accepted_by': '{' + ','.join(accepted_ids) + '}',  # PostgreSQL array format
                    'meeting_type': event.get('eventType', 'default'),
                    'organizationid': org_id,
                    'attendees_data': attendees_json  # Keep raw JSON for reference
                }
                
                # Insert normalized event to gcal_event
                insert_gcal_event(gcal_event_data, conn)
                
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Error saving event {event.get('id')}: {e}")
                continue
        
        print(f"✅ Saved {saved_count}/{len(events)} events to database")
        return saved_count
        
    finally:
        conn.close()


INTEGRATION_TYPE = 'GOOGLE_CALENDAR'  # Matches auth-svc provider constant


def save_integration_tokens(org_id, access_token, refresh_token, expires_in, email=None):
    """
    Save tokens to user_integration_details table.
    Uses INSERT on first auth, UPDATE on subsequent.
    
    Args:
        org_id: Organization ID
        access_token: OAuth access token
        refresh_token: OAuth refresh token
        expires_in: Token expiry time (seconds or datetime)
        email: User's email
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if record exists
        check_query = """
            SELECT id FROM insightly.user_integration_details
            WHERE organizationid = %(org_id)s
              AND provider = %(provider)s
            LIMIT 1
        """
        
        cursor.execute(check_query, {
            'org_id': org_id,
            'provider': INTEGRATION_TYPE
        })
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing record
            update_query = """
                UPDATE insightly.user_integration_details
                SET accesstoken = aes_encrypt(%(access_token)s),
                    refreshtoken = aes_encrypt(%(refresh_token)s),
                    expiresin = %(expires_in)s,
                    access_token_generation_date = NOW(),
                    modifieddate = NOW()
                WHERE organizationid = %(org_id)s
                  AND provider = %(provider)s
            """
            cursor.execute(update_query, {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_in': expires_in,
                'org_id': org_id,
                'provider': INTEGRATION_TYPE
            })
            print(f"✅ Updated tokens in DB for org {org_id}")
        else:
            # Insert new record
            insert_query = """
                INSERT INTO insightly.user_integration_details (
                    organizationid, provider, accesstoken, refreshtoken,
                    expiresin, email, access_token_generation_date,
                    createddate, modifieddate
                ) VALUES (
                    %(org_id)s, %(provider)s,
                    aes_encrypt(%(access_token)s), aes_encrypt(%(refresh_token)s),
                    %(expires_in)s, %(email)s, NOW(), NOW(), NOW()
                )
            """
            cursor.execute(insert_query, {
                'org_id': org_id,
                'provider': INTEGRATION_TYPE,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_in': expires_in,
                'email': email
            })
            print(f"✅ Saved tokens in DB for org {org_id}")
        
        conn.commit()
        return True
        
    except Exception as e:
        logger.error(f"Error saving tokens for org {org_id}: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_integration_tokens(org_id):
    """
    Get tokens from user_integration_details table.
    
    Returns:
        dict with token, refresh_token, expires_in, access_token_generation_date, email
        or None if not found
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                aes_decrypt(accesstoken) as token,
                aes_decrypt(refreshtoken) as refresh_token,
                expiresin,
                access_token_generation_date,
                email
            FROM insightly.user_integration_details
            WHERE organizationid = %(org_id)s
              AND provider = %(provider)s
            LIMIT 1
        """
        
        cursor.execute(query, {
            'org_id': org_id,
            'provider': INTEGRATION_TYPE
        })
        
        row = cursor.fetchone()
        
        if row:
            return {
                'token': row[0],
                'refresh_token': row[1],
                'expires_in': row[2],
                'access_token_generation_date': row[3],
                'email': row[4]
            }
        return None
        
    except Exception as e:
        logger.error(f"Error getting tokens for org {org_id}: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
