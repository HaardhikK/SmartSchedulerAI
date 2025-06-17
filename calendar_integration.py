from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import datetime
import os
import pytz

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Get authenticated Google Calendar service"""
    creds = None
    
    # Load existing token if available
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no valid credentials, request authorization
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Token refresh failed: {e}")
                creds = None
        
        if not creds:
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError("credentials.json not found. Please download it from Google Cloud Console.")
            
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('calendar', 'v3', credentials=creds)

def create_event(summary, start_time, end_time, location="", description=""):
    """Create a calendar event with proper timezone handling"""
    try:
        service = get_calendar_service()
        
        # Debug: Print the actual times being used
        print(f"Creating event: {summary}")
        print(f"Start time: {start_time} (tzinfo: {start_time.tzinfo})")
        print(f"End time: {end_time} (tzinfo: {end_time.tzinfo})")
        
        # FIX: Use proper timezone format for Google Calendar
        event_body = {
            'summary': summary,
            'start': {
                'dateTime': start_time.strftime('%Y-%m-%dT%H:%M:%S'),
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': end_time.strftime('%Y-%m-%dT%H:%M:%S'),
                'timeZone': 'Asia/Kolkata',
            },
        }
        
        # Add optional fields if provided
        if location:
            event_body['location'] = location
        
        if description:
            event_body['description'] = description
        
        # Create the event
        event = service.events().insert(calendarId='primary', body=event_body).execute()
        
        print(f"Event created: {event.get('htmlLink')}")
        return event
        
    except Exception as e:
        print(f"Error creating event: {e}")
        raise e

def get_upcoming_events(max_results=10):
    """Get upcoming events from calendar"""
    try:
        service = get_calendar_service()
        
        # Get current time in IST
        now = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).isoformat()
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        return events
        
    except Exception as e:
        print(f"Error fetching events: {e}")
        return []