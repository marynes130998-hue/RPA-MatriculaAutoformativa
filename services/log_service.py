from services.file_service import base_path
import logging
import os
from datetime import datetime

LOG_DIR = os.path.join(base_path(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Genera nombre: Log_2026-03-26_11-45-30.log
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
LOG_FILE = os.path.join(LOG_DIR, f"Log_{timestamp}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)