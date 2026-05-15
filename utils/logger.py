import logging
from utils.config import Config
import os

def setup_logger(name=__name__):
    """Configurare logging centralizat"""
    
    # Get log level
    log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # File handler
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    file_handler = logging.FileHandler('logs/agent_ai.log')
    file_handler.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger
