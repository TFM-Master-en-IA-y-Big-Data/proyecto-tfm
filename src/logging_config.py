# src/logging_config.py
"""
Configuración centralizada de logging
"""
import logging
import sys
from datetime import datetime

def setup_logging(name, level="INFO"):
    """
    Setup logging para todos los scripts
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Formato con timestamp
    formatter = logging.Formatter(
        '%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    # File handler (opcional, para auditoría)
    from pathlib import Path
    logs_dir = Path("logs/app")
    logs_dir.mkdir(exist_ok=True)
    
    fh = logging.FileHandler(
        logs_dir / f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    return logger