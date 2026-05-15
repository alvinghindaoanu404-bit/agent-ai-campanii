#!/usr/bin/env python
"""Entry point pentru Agent AI Campaign Manager"""

import sys
import asyncio
from agents.orchestrator import AgentOrchestrator
from utils.logger import setup_logger
from datetime import datetime, timedelta

logger = setup_logger(__name__)

def example_process_whatsapp():
    """Exemplu: Proceseaza campanii din WhatsApp"""
    logger.info("\n" + "="*60)
    logger.info("📱 EXEMPLU: Procesare WhatsApp")
    logger.info("="*60)
    
    orch = AgentOrchestrator(
        recipients=['client@example.com', 'admin@example.com']
    )
    
    try:
        # 1. Conectare WhatsApp
        logger.info("\n1️⃣  Inițializare WhatsApp...")
        if not orch.initialize_whatsapp():
            logger.error("❌ Nu s-a putut conecta la WhatsApp")
            return
        
        # 2. Extragere mesaje
        logger.info("\n2️⃣  Extragere mesaje din chat...")
        messages = orch.extract_data_from_whatsapp("Marketing Team", message_count=30)
        logger.info(f"✅ Extrase {len(messages)} mesaje")
        
        # 3. Procesare pipeline
        logger.info("\n3️⃣  Procesare pipeline (Filter + Calendar)...")
        events = orch.process_pipeline(messages, confidence_threshold=0.7)
        
        if events:
            logger.info(f"\n✅ Succes! {len(events)} campanii adaugate în calendar")
            for event in events[:3]:  # Afișează primele 3
                logger.info(f"  📌 {event.title} - {event.start_time}")
        else:
            logger.warning("⚠️  Nu s-au gasit campanii valide")
        
    finally:
        orch.cleanup()

def example_send_notification():
    """Exemplu: Trimitere notificare manuala"""
    logger.info("\n" + "="*60)
    logger.info("📧 EXEMPLU: Trimitere Notificare Manuala")
    logger.info("="*60)
    
    orch = AgentOrchestrator(
        recipients=['client@example.com']
    )
    
    try:
        logger.info("\n📧 Trimitere notificare pentru mâine...")
        success = orch.send_immediate_notification()
        
        if success:
            logger.info("✅ Notificare trimisa cu succes!")
        else:
            logger.warning("⚠️  Nu s-a putut trimite notificarea")
    
    finally:
        orch.cleanup()

def example_start_scheduler():
    """Exemplu: Incepe planificator zilnic de notificari"""
    logger.info("\n" + "="*60)
    logger.info("⏰ EXEMPLU: Planificator Zilnic de Notificari")
    logger.info("="*60)
    
    orch = AgentOrchestrator(
        recipients=['client@example.com', 'admin@example.com']
    )
    
    try:
        # Incepe planificator la 09:00 zilnic
        logger.info("\n⏰ Incepe planificator de notificari zilnice la 09:00...")
        orch.start_notification_scheduler("09:00")
        
        # Afiseaza status
        status = orch.get_status()
        logger.info(f"\n📊 Status sistem:")
        logger.info(f"  ✅ Scheduler activ: {status['notification_scheduler_active']}")
        logger.info(f"  📅 Events viitoare (7 zile): {status['upcoming_events']}")
        logger.info(f"  📅 Events mâine: {status['tomorrow_events']}")
        
        # Ruleaza 24 ore (înlocuiește cu input() pentru interactiv)
        logger.info("\n🔄 Scheduler ruleaza în background (CTRL+C pentru ieșire)...")
        try:
            while True:
                asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n⏹️  Oprire scheduler...")
    
    finally:
        orch.cleanup()

def main():
    """Meniu principal"""
    logger.info("\n" + "#"*60)
    logger.info("# 🤖 AGENT AI CAMPAIGN MANAGER - MENIU PRINCIPAL")
    logger.info("#"*60)
    
    examples = {
        '1': ('Proceseaza campanii din WhatsApp', example_process_whatsapp),
        '2': ('Trimite notificare manuala', example_send_notification),
        '3': ('Incepe planificator zilnic', example_start_scheduler),
    }
    
    for key, (desc, _) in examples.items():
        logger.info(f"{key}. {desc}")
    logger.info("0. Ieșire")
    
    choice = input("\nAlege o opțiune (0-3): ").strip()
    
    if choice == '0':
        logger.info("👋 La revedere!")
        sys.exit(0)
    elif choice in examples:
        _, func = examples[choice]
        try:
            func()
        except Exception as e:
            logger.error(f"\n❌ Eroare: {str(e)}")
    else:
        logger.error("\n❌ Opțiune invalida!")
        main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n👋 Programul s-a oprit.")
        sys.exit(0)
