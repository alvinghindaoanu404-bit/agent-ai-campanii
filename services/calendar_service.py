import os
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.auth.oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google_auth_httplib2 import AuthorizedHttp
import googleapiclient.discovery
import pickle
from utils.logger import setup_logger
from utils.config import Config
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from models.event import Event

logger = setup_logger(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarService:
    """Serviciu Google Calendar API"""
    
    def __init__(self):
        self.service = self._authenticate()
        self.calendar_id = Config.CALENDAR_ID
    
    def _authenticate(self):
        """Autentificare cu Google Calendar API"""
        try:
            creds = None
            
            # Verifica token salvat
            if os.path.exists(Config.TOKEN_FILE):
                with open(Config.TOKEN_FILE, 'rb') as token:
                    creds = pickle.load(token)
            
            # Daca nu exista sau este invalid, cere login
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        Config.CREDENTIALS_FILE, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Salveaza tokenul
                with open(Config.TOKEN_FILE, 'wb') as token:
                    pickle.dump(creds, token)
            
            service = googleapiclient.discovery.build('calendar', 'v3', credentials=creds)
            logger.info("✅ Conectat la Google Calendar API")
            return service
            
        except Exception as e:
            logger.error(f"❌ Eroare autentificare Google Calendar: {str(e)}")
            raise
    
    def create_event(self, event: Event) -> Optional[str]:
        """Creaza event in Google Calendar"""
        try:
            event_body = {
                'summary': event.title,
                'description': f"{event.description}\n\nTip: {event.campaign_type}",
                'start': {
                    'dateTime': event.start_time.isoformat(),
                    'timeZone': Config.NOTIFICATION_TIMEZONE,
                },
                'end': {
                    'dateTime': (event.end_time or event.start_time + timedelta(hours=1)).isoformat(),
                    'timeZone': Config.NOTIFICATION_TIMEZONE,
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # Email 1 zi inainte
                        {'method': 'popup', 'minutes': 15},       # Popup 15 min inainte
                    ]
                }
            }
            
            if event.location:
                event_body['location'] = event.location
            
            if event.attendees:
                event_body['attendees'] = [{'email': email} for email in event.attendees]
            
            result = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event_body
            ).execute()
            
            event.calendar_event_id = result['id']
            logger.info(f"📅 Event creat: {event.title} (ID: {result['id']})")
            return result['id']
            
        except Exception as e:
            logger.error(f"❌ Eroare creare event: {str(e)}")
            return None
    
    def get_events_for_date(self, date: datetime, calendar_id: Optional[str] = None) -> List[Dict]:
        """Obtine events pentru o anumita data"""
        try:
            cal_id = calendar_id or self.calendar_id
            
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
            end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()
            
            result = self.service.events().list(
                calendarId=cal_id,
                timeMin=start_of_day,
                timeMax=end_of_day,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = result.get('items', [])
            logger.info(f"📅 Gasit {len(events)} events pentru {date.strftime('%Y-%m-%d')}")
            return events
            
        except Exception as e:
            logger.error(f"❌ Eroare obtinere events: {str(e)}")
            return []
    
    def get_upcoming_events(self, days_ahead: int = 7) -> List[Dict]:
        """Obtine events viitoare"""
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            future = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'
            
            result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=now,
                timeMax=future,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = result.get('items', [])
            logger.info(f"📅 Gasit {len(events)} events viitoare")
            return events
            
        except Exception as e:
            logger.error(f"❌ Eroare obtinere events viitoare: {str(e)}")
            return []
    
    def delete_event(self, event_id: str) -> bool:
        """Sterge un event"""
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            logger.info(f"🗑️  Event sters: {event_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Eroare stergere event: {str(e)}")
            return False
