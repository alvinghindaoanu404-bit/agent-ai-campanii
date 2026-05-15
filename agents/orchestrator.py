from services.whatsapp_service import WhatsAppService
from agents.filtering_agent import FilteringAgent
from agents.calendar_agent import CalendarAgent
from agents.notification_agent import NotificationAgent
from utils.logger import setup_logger
from utils.config import Config
from models.event import Event
from datetime import datetime, timedelta
from typing import List, Optional

logger = setup_logger(__name__)

class AgentOrchestrator:
    """Coordinator principal al sistemului multi-agent"""
    
    def __init__(self, recipients: Optional[List[str]] = None):
        """Initializeaza toti agentii"""
        logger.info("🤖 Initializare Agent Orchestrator...")
        
        # Valideaza config
        Config.validate()
        
        # Initializeaza agenți
        self.whatsapp_service = WhatsAppService()
        self.filtering_agent = FilteringAgent()
        self.calendar_agent = CalendarAgent()
        
        # Notification agent cu recipients
        default_recipients = recipients or [Config.SENDER_EMAIL]
        self.notification_agent = NotificationAgent(self.calendar_agent, default_recipients)
        
        logger.info("✅ Orchestrator initializat")
    
    def initialize_whatsapp(self) -> bool:
        """Conecteaza la WhatsApp Web"""
        return self.whatsapp_service.initialize()
    
    def extract_data_from_whatsapp(self, chat_name: str, message_count: int = 50) -> List[str]:
        """Extrage mesaje din WhatsApp"""
        return self.whatsapp_service.get_chat_messages(chat_name, message_count)
    
    def process_pipeline(self, messages: List[str], confidence_threshold: float = 0.7) -> List[Event]:
        """Proceseaza pipeline complet: Filter -> Calendar"""
        logger.info(f"🔄 Incepe processing pipeline cu {len(messages)} mesaje...")
        
        # 1. Filtrare si parsing
        events = self.filtering_agent.filter_messages(messages, confidence_threshold)
        logger.info(f"📊 Step 1 (Filtrare): {len(events)} events valide")
        
        if not events:
            logger.warning("⚠️  Nu s-au gasit events valide")
            return []
        
        # 2. Adaugare in calendar
        results = self.calendar_agent.add_events_to_calendar(events)
        added_count = sum(1 for v in results.values() if v)
        logger.info(f"📊 Step 2 (Calendar): {added_count} events adaugate")
        
        return events
    
    def start_notification_scheduler(self, notification_time: Optional[str] = None):
        """Incepe programarea notificari zilnice"""
        self.notification_agent.schedule_daily_notifications(notification_time)
        self.notification_agent.start_scheduler()
        logger.info("✅ Sistema de notificari pornita")
    
    def get_tomorrow_events(self) -> List[dict]:
        """Obtine events pentru mâine"""
        return self.calendar_agent.get_tomorrow_events()
    
    def send_immediate_notification(self, recipients: Optional[List[str]] = None) -> bool:
        """Trimite notificare imediat"""
        tomorrow = datetime.now() + timedelta(days=1)
        events = self.get_tomorrow_events()
        
        if recipients:
            self.notification_agent.update_recipients(recipients)
        
        return self.notification_agent.send_immediate_notification(events, tomorrow)
    
    def cleanup(self):
        """Cleanup resurse"""
        logger.info("🧹 Cleanup resurse...")
        self.notification_agent.stop_scheduler()
        self.whatsapp_service.close()
        logger.info("✅ Cleanup completat")
    
    def get_status(self) -> dict:
        """Obtine status-ul sistemului"""
        return {
            'timestamp': datetime.now().isoformat(),
            'config_valid': True,
            'notification_scheduler_active': self.notification_agent.is_running,
            'upcoming_events': len(self.calendar_agent.get_upcoming_events(days_ahead=7)),
            'tomorrow_events': len(self.get_tomorrow_events())
        }
