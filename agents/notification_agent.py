import schedule
import time
import threading
from datetime import datetime, timedelta
from services.email_service import EmailService
from agents.calendar_agent import CalendarAgent
from utils.logger import setup_logger
from utils.config import Config
from typing import List, Optional

logger = setup_logger(__name__)

class NotificationAgent:
    """Agent pentru trimitere notificari email zilnice"""
    
    def __init__(self, calendar_agent: CalendarAgent, recipients: List[str]):
        self.email_service = EmailService()
        self.calendar_agent = calendar_agent
        self.recipients = recipients
        self.scheduler_thread = None
        self.is_running = False
    
    def send_tomorrow_notifications(self) -> bool:
        """Trimite notificari cu eventos de mâine"""
        try:
            logger.info("📧 Incepe trimitere notificari pentru mâine...")
            
            tomorrow = datetime.now() + timedelta(days=1)
            events = self.calendar_agent.get_events_for_date(tomorrow)
            
            if not events:
                logger.info("ℹ️  Nu sunt events pentru mâine")
                return True
            
            # Trimite notificari
            success = self.email_service.send_campaign_notification(
                self.recipients,
                events,
                tomorrow
            )
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Eroare trimitere notificari: {str(e)}")
            return False
    
    def send_immediate_notification(self, events: List[dict], date: datetime) -> bool:
        """Trimite notificare imediat (manual)"""
        return self.email_service.send_campaign_notification(self.recipients, events, date)
    
    def schedule_daily_notifications(self, notification_time: Optional[str] = None):
        """Programeaza notificari zilnice la ora specificata"""
        time_str = notification_time or Config.NOTIFICATION_TIME
        
        logger.info(f"⏰ Programare notificari zilnice la {time_str}")
        schedule.every().day.at(time_str).do(self.send_tomorrow_notifications)
    
    def start_scheduler(self):
        """Incepe scheduler-ul in background thread"""
        if self.is_running:
            logger.warning("⚠️  Scheduler-ul este deja activ")
            return
        
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("🚀 Scheduler pornit in background")
    
    def _run_scheduler(self):
        """Ruleaza scheduler-ul (background)"""
        logger.info("📅 Scheduler ruleaza 24/7...")
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def stop_scheduler(self):
        """Opreste scheduler-ul"""
        self.is_running = False
        logger.info("⏹️  Scheduler oprit")
    
    def update_recipients(self, recipients: List[str]):
        """Actualizeaza lista de recipients"""
        self.recipients = recipients
        logger.info(f"✅ Recipients actualizati: {len(recipients)}")
