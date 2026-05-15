from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class CampaignType(str, Enum):
    """Tipuri de campanii/evenimente"""
    PROMOTION = "promotion"
    ANNOUNCEMENT = "announcement"
    MEETING = "meeting"
    WEBINAR = "webinar"
    SALE = "sale"
    EVENT = "event"
    OTHER = "other"

class Event(BaseModel):
    """Model pentru eveniment/campanie"""
    title: str = Field(..., min_length=1, description="Titlul evenimentului")
    description: str = Field(..., min_length=1, description="Descrierea evenimentului")
    start_time: datetime = Field(..., description="Data și ora de început")
    end_time: Optional[datetime] = Field(None, description="Data și ora de finalizare")
    location: Optional[str] = Field(None, description="Locația evenimentului")
    campaign_type: CampaignType = Field(default=CampaignType.OTHER, description="Tipul campaniei")
    attendees: List[str] = Field(default_factory=list, description="Lista email-uri participanți")
    confidence_score: float = Field(default=1.0, ge=0, le=1, description="Scorul de încredere (0-1)")
    raw_message: Optional[str] = Field(None, description="Mesajul original din WhatsApp")
    created_at: datetime = Field(default_factory=datetime.now)
    calendar_event_id: Optional[str] = Field(None, description="ID din Google Calendar")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Summer Sale 2026",
                "description": "40% off on all products",
                "start_time": "2026-05-20T10:00:00",
                "end_time": "2026-05-20T18:00:00",
                "location": "Online",
                "campaign_type": "sale",
                "attendees": ["customer@example.com"],
                "confidence_score": 0.95
            }
        }

class Campaign(BaseModel):
    """Model pentru campanie (container pentru multiple events)"""
    name: str = Field(..., description="Numele campaniei")
    events: List[Event] = Field(default_factory=list, description="Lista de events din campanie")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
