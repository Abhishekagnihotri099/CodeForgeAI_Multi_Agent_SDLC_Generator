import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
from datetime import datetime


def setup_logging(project_name=None):
    """
    Setup comprehensive logging with both console and file handlers.
    Logs are saved to logs/{project_name}_{timestamp}.log
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Create a unique log file name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if project_name:
        log_filename = logs_dir / f"{project_name}_{timestamp}.log"
    else:
        log_filename = logs_dir / f"codegen_{timestamp}.log"
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    simple_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S"
    )
    
    # Console Handler - INFO and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # File Handler - DEBUG and above with rotation (10MB per file, keep 5 backups)
    file_handler = RotatingFileHandler(
        log_filename,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Log the initialization
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info(f"Logging initialized - Log file: {log_filename}")
    logger.info("=" * 80)
    
    return str(log_filename)