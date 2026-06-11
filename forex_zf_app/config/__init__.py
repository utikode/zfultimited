"""
Buku Besar Forex ZF - Core Configuration
Zuhri Formalism V16.4-OMNI-WARROOM
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Konfigurasi Utama Aplikasi"""
    
    # API Keys
    GEMINI_API_KEY: str = ""
    FINNHUB_API_KEY: str = ""
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    
    # MT5 Settings
    MT5_LOGIN: int = 0
    MT5_PASSWORD: str = ""
    MT5_SERVER: str = ""
    MT5_PATH: Optional[str] = None
    
    # Trading Settings
    DEFAULT_LOT_SIZE: float = 0.01
    MAX_DAILY_LOSS_PERCENT: float = 2.0
    ENABLE_HUMAN_IN_LOOP: bool = True
    TRADING_MODE: str = "AUTO"  # AUTO, MANUAL, SIMULATION
    
    # Data Settings
    DATA_RETENTION_DAYS: int = 30
    SCAN_INTERVAL_SECONDS: int = 120  # 2 menit
    SCANS_PER_CYCLE: int = 3  # 3x dalam 4 jam
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    LOGS_DIR: str = os.path.join(BASE_DIR, "logs")
    ARCHIVE_DIR: str = os.path.join(BASE_DIR, "archive")
    
    def __post_init__(self):
        """Initialize directories"""
        for directory in [self.DATA_DIR, self.LOGS_DIR, self.ARCHIVE_DIR]:
            os.makedirs(directory, exist_ok=True)
    
    def save_to_file(self, filepath: str = None):
        """Simpan konfigurasi ke file"""
        if filepath is None:
            filepath = os.path.join(self.BASE_DIR, "config", "settings.json")
        
        import json
        with open(filepath, 'w') as f:
            json.dump({
                'GEMINI_API_KEY': self.GEMINI_API_KEY,
                'FINNHUB_API_KEY': self.FINNHUB_API_KEY,
                'TELEGRAM_BOT_TOKEN': self.TELEGRAM_BOT_TOKEN,
                'TELEGRAM_CHAT_ID': self.TELEGRAM_CHAT_ID,
                'MT5_LOGIN': self.MT5_LOGIN,
                'MT5_SERVER': self.MT5_SERVER,
                'DEFAULT_LOT_SIZE': self.DEFAULT_LOT_SIZE,
                'MAX_DAILY_LOSS_PERCENT': self.MAX_DAILY_LOSS_PERCENT,
                'ENABLE_HUMAN_IN_LOOP': self.ENABLE_HUMAN_IN_LOOP,
                'TRADING_MODE': self.TRADING_MODE,
                'DATA_RETENTION_DAYS': self.DATA_RETENTION_DAYS,
            }, f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str = None):
        """Muat konfigurasi dari file"""
        if filepath is None:
            filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                   "config", "settings.json")
        
        import json
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
            return cls(**data)
        return cls()

# Global config instance
config = Config()
