import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from utils.logger import setup_logger
from utils.config import Config
from datetime import datetime
from typing import List, Dict, Optional

logger = setup_logger(__name__)

EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html dir="ltr" lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .header h1 { margin: 0; font-size: 24px; }
        .event { border-left: 4px solid #667eea; padding: 15px; margin: 15px 0; background-color: #f9f9f9; border-radius: 3px; }
        .event-title { font-size: 18px; font-weight: bold; color: #333; margin-bottom: 10px; }
        .event-detail { margin: 8px 0; color: #666; }
        .event-detail strong { color: #333; }
        .badge { display: inline-block; background-color: #667eea; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px; margin-top: 10px; }
        .footer { text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #999; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📅 Campanii și Evenimente pentru {{ date }}</h1>
            <p>Iată ce se întâmplă mâine</p>
        </div>
        
        {% if events %}
            {% for event in events %}
            <div class="event">
                <div class="event-title">{{ event.title }}</div>
                <div class="event-detail">⏰ <strong>Ora:</strong> {{ event.start_time }} {% if event.end_time %}- {{ event.end_time }}{% endif %}</div>
                {% if event.location %}
                <div class="event-detail">📍 <strong>Locație:</strong> {{ event.location }}</div>
                {% endif %}
                <div class="event-detail">📝 <strong>Descriere:</strong> {{ event.description }}</div>
                <div class="event-detail"><span class="badge">{{ event.type }}</span></div>
            </div>
            {% endfor %}
        {% else %}
            <p style="text-align: center; color: #999; padding: 20px;">Nu sunt campanii sau evenimente programate pentru mâine.</p>
        {% endif %}
        
        <div class="footer">
            <p>📧 Email generat automat de Agent AI Campaign Manager</p>
            <p>© {{ year }} - Toate drepturile rezervate</p>
        </div>
    </div>
</body>
</html>
"""

class EmailService:
    """Serviciu pentru trimitere email-uri"""
    
    def __init__(self):
        self.sender_email = Config.SENDER_EMAIL
        self.sender_password = Config.SENDER_PASSWORD
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
    
    def send_email(self, recipient: str, subject: str, html_content: str) -> bool:
        """Trimite email HTML"""
        try:
            # Creare mesaj
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = recipient
            
            # Attach HTML
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Conectare SMTP si trimitere
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient, message.as_string())
            
            logger.info(f"📧 Email trimis catre {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Eroare trimitere email: {str(e)}")
            return False
    
    def send_campaign_notification(self, recipients: List[str], events: List[Dict], date: datetime) -> bool:
        """Trimite notificare cu campanii/evenimente pentru o data"""
        try:
            # Formeaza datele pentru template
            formatted_events = []
            for event in events:
                start_time = event.get('start', {}).get('dateTime', event.get('start', {}).get('date', ''))
                end_time = event.get('end', {}).get('dateTime', event.get('end', {}).get('date', ''))
                
                formatted_events.append({
                    'title': event.get('summary', 'Fără titlu'),
                    'start_time': start_time[:5] if 'T' in start_time else start_time,
                    'end_time': end_time[:5] if 'T' in end_time else end_time,
                    'location': event.get('location', 'Nu este specificată'),
                    'description': event.get('description', 'Fără descriere').split('\n')[0],
                    'type': event.get('description', '').split('Tip: ')[-1] if 'Tip: ' in event.get('description', '') else 'event'
                })
            
            # Render template
            template = Template(EMAIL_TEMPLATE)
            html_content = template.render(
                date=date.strftime('%d %B %Y'),
                events=formatted_events,
                year=datetime.now().year
            )
            
            # Trimite la fiecare recipient
            success_count = 0
            for recipient in recipients:
                if self.send_email(
                    recipient,
                    f"📅 Campanii și Evenimente - {date.strftime('%d.%m.%Y')}",
                    html_content
                ):
                    success_count += 1
            
            logger.info(f"✅ Notificări trimise: {success_count}/{len(recipients)}")
            return success_count == len(recipients)
            
        except Exception as e:
            logger.error(f"❌ Eroare trimitere notificări: {str(e)}")
            return False
