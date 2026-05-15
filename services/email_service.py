"""
Email Service - Handles email notifications.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime
from utils.logger import get_logger
from utils.config import Config

logger = get_logger(__name__)


class EmailService:
    """Service for sending emails."""

    def __init__(self):
        """Initialize email service."""
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.sender_email = Config.EMAIL_SENDER
        self.sender_password = Config.EMAIL_PASSWORD

    def send_notification(
        self, recipient_email: str, subject: str, event_data: dict
    ) -> bool:
        """
        Send notification email.

        Args:
            recipient_email: Recipient email address
            subject: Email subject
            event_data: Event information dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = recipient_email

            # Create HTML body
            html_body = self._create_html_body(event_data)

            # Attach HTML
            message.attach(MIMEText(html_body, "html"))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, message.as_string())

            logger.info(f"Email sent successfully to {recipient_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    def send_bulk_notifications(
        self, recipients: List[str], subject: str, event_data: dict
    ) -> int:
        """
        Send bulk notification emails.

        Args:
            recipients: List of recipient email addresses
            subject: Email subject
            event_data: Event information dictionary

        Returns:
            Number of successful sends
        """
        success_count = 0
        for recipient in recipients:
            if self.send_notification(recipient, subject, event_data):
                success_count += 1

        logger.info(
            f"Bulk notification sent: {success_count}/{len(recipients)} successful"
        )
        return success_count

    @staticmethod
    def _create_html_body(event_data: dict) -> str:
        """
        Create HTML email body.

        Args:
            event_data: Event information

        Returns:
            HTML string
        """
        title = event_data.get("title", "Eveniment")
        description = event_data.get("description", "Fără descriere")
        start_date = event_data.get("start_date", "")
        end_date = event_data.get("end_date", "")
        location = event_data.get("location", "Locație nedefinită")

        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #2c3e50;">Notificare Eveniment</h2>
                    <div style="background-color: #ecf0f1; padding: 20px; border-radius: 8px;">
                        <h3 style="color: #e74c3c; margin-top: 0;">{title}</h3>
                        
                        <p><strong>Descriere:</strong></p>
                        <p>{description}</p>
                        
                        <p><strong>Data și ora start:</strong><br/>{start_date}</p>
                        <p><strong>Data și ora final:</strong><br/>{end_date}</p>
                        <p><strong>Locație:</strong><br/>{location}</p>
                    </div>
                    
                    <p style="color: #7f8c8d; font-size: 12px; margin-top: 20px;">
                        Aceasta este o notificare automată din sistemul de gestionare a campaniilor.
                    </p>
                </div>
            </body>
        </html>
        """
        return html
