import logging
import os
from datetime import datetime

# Path to the log file
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'system.log')

# Ensure data directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def setup_logger():
    """Sets up the application logger to write to both console and a file."""
    logger = logging.getLogger('sentiment_engine')
    logger.setLevel(logging.INFO)
    
    # Create file handler
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

# Create a shared logger instance
logger = setup_logger()

def get_recent_logs(limit=50):
    """Reads the last N lines from the log file."""
    if not os.path.exists(LOG_FILE):
        return []
    
    try:
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
            return [line.strip() for line in lines[-limit:]]
    except Exception as e:
        return [f"Error reading logs: {str(e)}"]
