import os
from dotenv import load_dotenv
import logging

load_dotenv()

class Config:
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    # Google Calendar
    CALENDAR_ID = os.getenv('CALENDAR_ID')
    CREDENTIALS_FILE = 'credentials.json'
    TOKEN_FILE = 'token.json'
    
    # Email (Gmail SMTP)
    SENDER_EMAIL = os.getenv('SENDER_EMAIL')
    SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    
    # WhatsApp
    WHATSAPP_QR_TIMEOUT = int(os.getenv('WHATSAPP_QR_TIMEOUT', 60))
    WHATSAPP_PHONE_NUMBER = os.getenv('WHATSAPP_PHONE_NUMBER', '+40')
    
    # Notification
    NOTIFICATION_TIME = os.getenv('NOTIFICATION_TIME', '09:00')
    NOTIFICATION_TIMEZONE = os.getenv('NOTIFICATION_TIMEZONE', 'Europe/Bucharest')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'agent_ai.log'
    
    @staticmethod
    def validate():
        """Validare configurare"""
        required = ['OPENAI_API_KEY', 'CALENDAR_ID', 'SENDER_EMAIL', 'SENDER_PASSWORD']
        missing = [key for key in required if not getattr(Config, key, None)]
        
        if missing:
            raise ValueError(f"Missing environment variables: {', '.join(missing)}. Check .env file.")
        
        if not os.path.exists(Config.CREDENTIALS_FILE):
            logging.warning(f"⚠️  {Config.CREDENTIALS_FILE} not found. Google Calendar API will request authentication on first run.")
