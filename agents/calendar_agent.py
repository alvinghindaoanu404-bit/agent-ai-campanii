from services.calendar_service import CalendarService
from models.event import Event
from utils.logger import setup_logger
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logger = setup_logger(__name__)

class CalendarAgent:
    """Agent pentru gestionare Google Calendar"""
    
    def __init__(self):
        self.calendar_service = CalendarService()
        self.events_registry = {}  # {event_id: Event}
    
    def add_events_to_calendar(self, events: List[Event]) -> Dict[str, bool]:
        """Adauga events in Google Calendar"""
        logger.info(f"📅 Adaugare {len(events)} events in calendar...")
        
        results = {}
        for event in events:
            event_id = self.calendar_service.create_event(event)
            if event_id:
                results[event.title] = True
                self.events_registry[event_id] = event
            else:
                results[event.title] = False
        
        success_count = sum(1 for v in results.values() if v)
        logger.info(f"✅ Adaugate {success_count}/{len(events)} events in calendar")
        return results
    
    def get_tomorrow_events(self) -> List[Dict]:
        """Obtine events pentru mâine"""
        tomorrow = datetime.now() + timedelta(days=1)
        events = self.calendar_service.get_events_for_date(tomorrow)
        logger.info(f"📅 Gasit {len(events)} events pentru mâine")
        return events
    
    def get_events_for_date(self, date: datetime) -> List[Dict]:
        """Obtine events pentru o data specificata"""
        events = self.calendar_service.get_events_for_date(date)
        return events
    
    def get_upcoming_events(self, days_ahead: int = 7) -> List[Dict]:
        """Obtine events viitoare"""
        return self.calendar_service.get_upcoming_events(days_ahead)
    
    def delete_event(self, event_id: str) -> bool:
        """Sterge un event"""
        success = self.calendar_service.delete_event(event_id)
        if success and event_id in self.events_registry:
            del self.events_registry[event_id]
        return success
