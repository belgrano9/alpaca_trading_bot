# src/utils/file_utils.py

from pathlib import Path
from typing import Optional
from datetime import datetime

from utils.logger import setup_logger

logger = setup_logger(name="file_utils")

def get_latest_signals_file(
    base_dir: str | Path,
    file_pattern: str = "orders_*.json"
) -> Optional[Path]:
    """
    Find the most recent signals file in the specified directory.
    
    Args:
        base_dir: Base directory path where signal files are stored
        file_pattern: Pattern to match signal files (default: "orders_*.json")
        
    Returns:
        Path to the most recent signals file or None if no files found
        
    Raises:
        FileNotFoundError: If the base directory doesn't exist
    """
    try:
        base_path = Path(base_dir)
        if not base_path.exists():
            raise FileNotFoundError(f"Directory not found: {base_dir}")
            
        # Find all matching files
        signal_files = list(base_path.glob(file_pattern))
        
        if not signal_files:
            logger.warning(f"No signal files found matching pattern '{file_pattern}' in {base_dir}")
            return None
            
        # Sort files by modification time (newest first)
        latest_file = max(signal_files, key=lambda p: p.stat().st_mtime)
        
        logger.info(f"Found latest signals file: {latest_file.name}")
        logger.debug(f"Modified: {datetime.fromtimestamp(latest_file.stat().st_mtime)}")
        
        return latest_file
        
    except Exception as e:
        logger.error(f"Error finding latest signals file: {str(e)}")
        raise