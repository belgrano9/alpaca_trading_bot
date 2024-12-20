# File: src/utils/logger.py

"""Logging configuration utilities for the trading platform."""

import logging
from pathlib import Path
from typing import Optional

def setup_logger(
    name: str = "",
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    format: str = '%(asctime)s - %(levelname)s - %(message)s'
) -> logging.Logger:
    """
    Configure logging with console and optional file output.
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Optional path for log file
        format: Log message format
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    formatter = logging.Formatter(format)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger