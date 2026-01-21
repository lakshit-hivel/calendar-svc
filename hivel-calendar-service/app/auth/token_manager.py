"""
Token management functions for Google Calendar integration.
Uses existing insightly.user_integration_details table with AES encryption.
Functional style matching existing Hivel code.
"""

import psycopg
from datetime import datetime, timedelta
from app.database.connection import get_connection
from app.auth import oauth

PROVIDER = 'GOOGLE_CALENDAR'


def get_tokens(org_id):
    """
    Get decrypted tokens from database.
    
    Args:
        org_id: Organization ID
        
    Returns:
        Dictionary with token, refresh_token, expires_at or None
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
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
            """, (org_id, PROVIDER))
            
            result = cursor.fetchone()
            if result:
                return {
                    "token": result[0],
                    "refresh_token": result[1],
                    "expires_at": result[2]
                }
            return None
    finally:
        conn.close()


def save_tokens(org_id, tokens):
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
            """, (org_id, PROVIDER))
            
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
                    PROVIDER
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
                    PROVIDER,
                    tokens.get("access_token"),
                    tokens.get("refresh_token")
                ))
            
            conn.commit()
            print(f"Saved tokens for org {org_id}")
            return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_valid_token(org_id):
    """
    Get a valid access token, refreshing if needed.
    
    Args:
        org_id: Organization ID
        
    Returns:
        Valid access token string
    """
    tokens = get_tokens(org_id)
    
    if not tokens:
        raise Exception(f"No tokens found for organization {org_id}")
    
    # Check if token is expired (with 5 min buffer)
    expires_at = tokens.get("expires_at")
    if expires_at and expires_at < datetime.now() + timedelta(minutes=5):
        # Token expired, refresh it
        print(f"Token expired for org {org_id}, refreshing...")
        new_tokens = oauth.refresh_access_token(tokens["refresh_token"])
        
        # Save new tokens
        save_tokens(org_id, new_tokens)
        
        return new_tokens["access_token"]
    
    return tokens["token"]
