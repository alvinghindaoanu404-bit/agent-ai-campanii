# Agent AI - Campaign Manager System

## 📋 Descriere

Sistem multi-agent AI care automatizează gestionarea campaniilor și evenimentelor din WhatsApp:

1. **WhatsApp Scraper Agent** - Extrage mesaje cu date despre campanii din WhatsApp Web
2. **Filtering Agent** - Validează și parsează datele folosind AI
3. **Calendar Agent** - Stochează evenimentele în Google Calendar
4. **Notification Agent** - Trimite notificări zilnice cu evenimentele de mâine

## 🏗️ Arhitectura

```
agent-ai-campanii/
├── agents/                  # Agenții AI
│   ├── filtering_agent.py   # Parse + validare mesaje
│   ├── calendar_agent.py    # Gestionare Google Calendar
│   ├── notification_agent.py # Notificări email zilnice
│   └── orchestrator.py      # Coordinare agenți
├── services/               # Servicii de integrare
│   ├── whatsapp_service.py # Extragere WhatsApp Web
│   ├── calendar_service.py # Google Calendar API
│   └── email_service.py    # SMTP + email template
├── models/                 # Modele de date
│   └── event.py           # Pydantic models
├── utils/                  # Utilitare
│   ├── config.py          # Variabile mediu
│   └── logger.py          # Logging
├── main.py                # Entry point
├── requirements.txt       # Dependențe
├── .env.example           # Template .env
└── README.md              # Documentație
```

## 🚀 Instalare

### 1. Clone repository și instaleaza dependențele
```bash
git clone https://github.com/alvinghindaoanu404-bit/agent-ai-campanii.git
cd agent-ai-campanii
pip install -r requirements.txt
```

### 2. Configurare variabile de mediu
```bash
cp .env.example .env
# Edit .env with your credentials
```

#### Variabile necesare:

**Google Calendar:**
- Descarcă `credentials.json` din [Google Cloud Console](https://console.cloud.google.com/)
- Setează `CALENDAR_ID` (obții din Google Calendar settings)

**Email (Gmail):**
- `SENDER_EMAIL` - Gmail address
- `SENDER_PASSWORD` - [App Password](https://support.google.com/accounts/answer/185833) (2FA trebuie activat)

**OpenAI:**
- `OPENAI_API_KEY` - Din [OpenAI Dashboard](https://platform.openai.com/api-keys)

**WhatsApp (opțional):**
- `WHATSAPP_PHONE_NUMBER` - Telefon WhatsApp cu + și cod țară

### 3. Setup Google Calendar API
```bash
# Plasează credentials.json în root directory
# Prima rulare va deschide browser pentru autentificare
```

### 4. Rulare
```bash
python main.py
```

## 📖 Utilizare

### Mod automat (cu notificări zilnice)
```python
from agents.orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator()
orchestrator.start_notification_scheduler()  # Trimite notificări zilnic la ora setata
```

### Procesare manuală WhatsApp
```python
orchestrator.initialize_whatsapp()  # Deschide browser, scan QR
messages = orchestrator.extract_data_from_whatsapp("Campanii", message_count=50)
events = orchestrator.process_pipeline(messages)
```

### Trimitere notificări manuale
```python
tomorrow_events = orchestrator.get_tomorrow_events()
orchestrator.notification_agent.send_immediate_notification(
    tomorrow_events, 
    datetime.now() + timedelta(days=1)
)
```

## 🤖 Cum funcționează

### 1. **WhatsApp Scraper Agent**
- Conectare la WhatsApp Web cu Selenium
- Scanare QR code
- Extrage mesajele din chat-urile specificate
- Returnează lista de texte brute

### 2. **Filtering Agent** (LangChain + GPT-4)
Parseaza fiecare mesaj cu AI pentru a extrage:
- Titlu eveniment
- Dată și ora
- Locație
- Descriere
- Tip campanie (promotion, announcement, meeting, etc.)

Filtrul validează:
- ✅ Are mesajul informații despre event/campanie?
- ✅ Data și ora sunt valide?
- ✅ Titlu și descriere sunt suficiente?
- 📊 Confidence score (0-1)

### 3. **Calendar Agent**
- Preia evenimentele filtrate
- Creează calendar events în Google Calendar cu:
  - Reminder email cu 1 zi înainte
  - Reminder popup cu 15 minute înainte
  - Link direct în calendar

### 4. **Notification Agent**
- Rulează zilnic la ora setata (default 09:00)
- Citește Google Calendar
- Extrage evenimentele pentru ziua următoare
- Trimite email HTML frumos formatat cu:
  - Titlu și descriere
  - Ora evenimentului
  - Locație (dacă disponibilă)
  - Tip campanie

## 📧 Template Email

Email-ul trimis conține:
```
📅 Campanie/Eveniment pentru mâine

• Titlu Campanie
  ⏰ Ora: 10:00 - 18:00
  📍 Locație: Online
  📝 Descriere: Detalii
  🏷️ Tip: promotion
```

## ⚙️ Configurare avansată

### Schimbă ora notificărilor
```python
# În .env
NOTIFICATION_TIME=14:30  # Format HH:MM
```

### Ajustare confidence threshold
```python
events = orchestrator.process_pipeline(
    messages, 
    confidence_threshold=0.8  # Default 0.7, mai strict = mai puține false positives
)
```

### Whatsapp QR timeout
```python
# În .env
WHATSAPP_QR_TIMEOUT=60  # Secunde pentru scan QR
```

## 🐛 Troubleshooting

### Gmail reject email
- Activează 2FA pe Gmail
- Genereaza [App Password](https://support.google.com/accounts/answer/185833)
- Foloseste App Password în `SENDER_PASSWORD`

### Google Calendar auth failed
- Sterge `token.json`
- Genereaza nou `credentials.json` din Google Cloud
- Prima rulare va cere din nou permisiuni

### WhatsApp QR code nu apare
- Verifica: `WHATSAPP_QR_TIMEOUT` in .env
- Sterge cache: `rm -rf /tmp/whatsapp_chrome`
- Chrome trebuie instalat

### LLM errors
- Verifica API key OpenAI valid
- Verifica quota și billing
- Teste cu alt model: `OPENAI_MODEL=gpt-3.5-turbo`

## 📊 Logging

Logs se salvează în `agent_ai.log` și în console.
Schimbă level:
```python
# În .env
LOG_LEVEL=DEBUG  # INFO, DEBUG, WARNING, ERROR
```

## 🔒 Security Best Practices

1. ✅ Nu comite `.env` la git (este în `.gitignore`)
2. ✅ Folosite App Passwords pentru Gmail, nu password-ul real
3. ✅ Restrânge permisiunile Google Calendar API
4. ✅ Rotate API keys periodic
5. ✅ Foloseste environment variables, nu hardcode credentials

## 📝 Exemple

### Exemplu: Procesa campanii din WhatsApp
```python
from agents.orchestrator import AgentOrchestrator
from datetime import datetime, timedelta

orch = AgentOrchestrator()

# Conectare WhatsApp
if not orch.initialize_whatsapp():
    exit(1)

# Extrage mesaje
messages = orch.extract_data_from_whatsapp("Marketing Team", message_count=100)

# Proceseaza
events = orch.process_pipeline(messages, confidence_threshold=0.75)

# Verifica ce s-a adăugat
for event in events:
    print(f"✅ {event.title} - {event.start_time}")

# Cleanup
orch.cleanup()
```

### Exemplu: Citeste events din calendar
```python
from agents.calendar_agent import CalendarAgent
from datetime import datetime, timedelta

cal = CalendarAgent()

# Events pentru următoarele 7 zile
upcoming = cal.get_upcoming_events(days_ahead=7)
for event in upcoming:
    print(f"📅 {event['summary']}: {event['start']['dateTime']}")

# Events de mâine
tomorrow = datetime.now() + timedelta(days=1)
tomorrow_events = cal.get_events_for_date(tomorrow)
```

## 🤝 Contribuții

Contributions sunt welcome! Deschide issue sau pull request.

## 📄 Licență

MIT License - vezi LICENSE file

## 📞 Support

Pentru probleme, deschide issue pe GitHub.

---

**Built with ❤️ using LangChain, OpenAI, Google Calendar API & Selenium**
