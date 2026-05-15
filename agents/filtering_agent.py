from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from utils.logger import setup_logger
from utils.config import Config
from models.event import Event, CampaignType
from typing import List, Optional
from datetime import datetime, timedelta
import json
import re

logger = setup_logger(__name__)

class FilteringAgent:
    """Agent AI pentru filtrare si parsing mesaje WhatsApp"""
    
    SYSTEM_PROMPT = """Tu esti un expert in extragerea informatiilor din mesaje. 
    Analizezi mesajele si extragi urmatoarele date despre campanii/evenimente:
    - Titlu
    - Data si ora (parseaza formate diverse: "maine la 10", "20/05 14:30", etc)
    - Locatie (daca exista)
    - Descriere
    - Tip campanie (promotion, announcement, meeting, webinar, sale, event)
    - Email-uri (daca exista)
    
    Returneaza response in format JSON cu campurile: title, description, start_time (ISO format), end_time (optional, ISO format), location, campaign_type, attendees (lista), confidence_score (0-1).
    
    Daca mesajul nu contine informatii despre campanie/eveniment, returneaza confidence_score = 0.
    Daca informatiile sunt incomplete sau confuze, reduceti confidence_score.
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name=Config.OPENAI_MODEL,
            temperature=0.3,
            openai_api_key=Config.OPENAI_API_KEY
        )
    
    def parse_message(self, message: str) -> Optional[Event]:
        """Parseaza un mesaj si returneaza Event daca contine campanie/eveniment"""
        try:
            logger.debug(f"📝 Parsing mesaj: {message[:100]}...")
            
            # Construieste prompt
            human_message = HumanMessage(
                content=f"""Analizeaza urmatorul mesaj si extrage informatiile despre campanie/eveniment:
                
                Mesaj: {message}
                
                Returneaza doar JSON, fara text aditional."""
            )
            
            # Apeleaza LLM
            response = self.llm([
                SystemMessage(content=self.SYSTEM_PROMPT),
                human_message
            ])
            
            # Extrage JSON
            json_str = response.content
            # Incearca sa gaseasca JSON in response
            json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
            if not json_match:
                logger.warning(f"❌ Nu s-a gasit JSON in response")
                return None
            
            json_str = json_match.group(0)
            data = json.loads(json_str)
            
            # Verifica confidence score
            confidence = data.get('confidence_score', 0)
            if confidence < 0.5:
                logger.debug(f"⚠️  Confidence score prea mic: {confidence}")
                return None
            
            # Converteste in Event
            event = Event(
                title=data.get('title', ''),
                description=data.get('description', ''),
                start_time=datetime.fromisoformat(data.get('start_time')),
                end_time=datetime.fromisoformat(data.get('end_time')) if data.get('end_time') else None,
                location=data.get('location'),
                campaign_type=data.get('campaign_type', 'other'),
                attendees=data.get('attendees', []),
                confidence_score=confidence,
                raw_message=message
            )
            
            logger.info(f"✅ Event parsat: {event.title} (confidence: {confidence})")
            return event
            
        except Exception as e:
            logger.error(f"❌ Eroare parsing mesaj: {str(e)}")
            return None
    
    def filter_messages(self, messages: List[str], confidence_threshold: float = 0.7) -> List[Event]:
        """Filtreaza si parseaza o lista de mesaje"""
        logger.info(f"🔍 Filtrare {len(messages)} mesaje (threshold: {confidence_threshold})...")
        
        events = []
        for i, message in enumerate(messages, 1):
            logger.debug(f"  [{i}/{len(messages)}] Procesare mesaj...")
            event = self.parse_message(message)
            
            if event and event.confidence_score >= confidence_threshold:
                events.append(event)
        
        logger.info(f"✅ Filtrate {len(events)} events valide")
        return events
