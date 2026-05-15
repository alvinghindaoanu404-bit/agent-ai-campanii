import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from utils.logger import setup_logger
from utils.config import Config
from typing import List, Optional

logger = setup_logger(__name__)

class WhatsAppService:
    """Serviciu pentru extragere date din WhatsApp Web"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
    
    def initialize(self) -> bool:
        """Inițializare Selenium WebDriver și conectare WhatsApp Web"""
        try:
            logger.info("🚀 Inițializare WhatsApp Web...")
            
            chrome_options = Options()
            # chrome_options.add_argument("--headless")  # Decomment pentru headless
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            
            # User data pentru a se pastra sesiunea
            user_data_dir = os.path.expanduser("~/.wpp_chrome")
            chrome_options.add_argument(f"user-data-dir={user_data_dir}")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 30)
            
            # Deschide WhatsApp Web
            logger.info("📱 Deschidere WhatsApp Web...")
            self.driver.get("https://web.whatsapp.com")
            
            # Asteapta QR code
            logger.info(f"⏳ Asteapta QR code scan (timeout: {Config.WHATSAPP_QR_TIMEOUT}s)...")
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='chat-list-item']"))
                )
                logger.info("✅ WhatsApp conectat cu succes!")
                time.sleep(3)  # Asteapta sa se incarchie complet
                return True
            except:
                logger.warning("⚠️  QR code nu a fost scanat în timp. Încearcă din nou.")
                return False
                
        except Exception as e:
            logger.error(f"❌ Eroare la inițializare WhatsApp: {str(e)}")
            return False
    
    def get_chat_messages(self, chat_name: str, message_count: int = 50) -> List[str]:
        """Extrage mesaje din chat-ul specificat"""
        try:
            logger.info(f"🔍 Căutare chat: {chat_name}")
            
            # Cauta chat-ul
            search_box = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[title='Search input textbox']"))
            )
            search_box.click()
            search_box.send_keys(chat_name)
            time.sleep(2)
            
            # Click pe chat
            chat_item = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='chat-list-item']"))
            )
            chat_item.click()
            logger.info(f"✅ Chat deschis: {chat_name}")
            time.sleep(2)
            
            # Extrage mesajele
            messages = []
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while len(messages) < message_count:
                # Cauta toate mesajele
                message_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, 
                    "[data-testid='msg-container']"
                )
                
                for element in message_elements:
                    try:
                        text = element.text
                        if text and text not in messages:
                            messages.append(text)
                    except:
                        pass
                
                if len(messages) >= message_count:
                    break
                
                # Scroll up pentru mesaje mai vechi
                self.driver.execute_script(
                    "arguments[0].scrollTop = 0",
                    self.driver.find_element(By.CSS_SELECTOR, "[data-testid='chat-list-light']").find_element(By.XPATH, "..")
                )
                time.sleep(1)
                
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            logger.info(f"📨 Extrase {len(messages)} mesaje din {chat_name}")
            return messages[:message_count]
            
        except Exception as e:
            logger.error(f"❌ Eroare la extragere mesaje: {str(e)}")
            return []
    
    def close(self):
        """Inchide browser-ul"""
        if self.driver:
            self.driver.quit()
            logger.info("🔌 WhatsApp Web închis")
