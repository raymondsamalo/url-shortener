"""
 app.util.logger
 Logging utility
"""
import logging
import sys
from typing import Optional

def get_module_logger(
    name: str, 
    log_file: Optional[str] = None, 
    level: int = logging.INFO
) -> logging.Logger:
    """
    Creates and configures a unique logger object with line tracking.
    
    Args:
        name: The name of the module (usually pass __name__).
        log_file: Optional path to a file if you want to save logs to disk.
        level: The minimum logging level (e.g., logging.DEBUG, logging.INFO).
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate logs if the root logger is configured elsewhere
    logger.propagate = False
    
    # Only add handlers if they haven't been added yet (prevents duplicates on multiple imports)
    if not logger.handlers:
        # Standard format featuring module name, file name, and line number
        log_format = logging.Formatter(
            fmt="%(asctime)s [%(name)s] [%(filename)s:%(lineno)d] %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # 1. Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_format)
        logger.addHandler(console_handler)
        
        # 2. Optional File Handler
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(log_format)
            logger.addHandler(file_handler)
            
    return logger