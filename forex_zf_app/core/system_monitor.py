"""
System Monitor - Monitor Kesehatan Sistem (Fitur Tambahan)
Memantau status koneksi, latensi, dan kinerja komponen
"""

import time
import psutil
from datetime import datetime
from typing import Dict
import threading

class SystemMonitor:
    """Monitor kesehatan sistem real-time"""
    
    def __init__(self, config):
        self.config = config
        self.is_running = False
        self.monitor_thread = None
        self.metrics = {
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'mt5_connected': False,
            'api_status': {
                'gemini': False,
                'finnhub': False,
                'telegram': False
            },
            'latency_ms': 0.0,
            'last_update': None,
            'uptime_seconds': 0
        }
        self.start_time = None
    
    def start(self):
        """Mulai monitoring"""
        self.is_running = True
        self.start_time = datetime.now()
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop(self):
        """Hentikan monitoring"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
    
    def _monitor_loop(self):
        """Loop monitoring utama"""
        while self.is_running:
            try:
                # CPU & Memory usage
                self.metrics['cpu_usage'] = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                self.metrics['memory_usage'] = memory.percent
                
                # MT5 connection status
                try:
                    import MetaTrader5 as mt5
                    self.metrics['mt5_connected'] = mt5.terminal_info().connected if mt5.terminal_info() else False
                except:
                    self.metrics['mt5_connected'] = False
                
                # API status check
                self.metrics['api_status']['gemini'] = bool(self.config.GEMINI_API_KEY)
                self.metrics['api_status']['finnhub'] = bool(self.config.FINNHUB_API_KEY)
                self.metrics['api_status']['telegram'] = bool(self.config.TELEGRAM_BOT_TOKEN)
                
                # Latency measurement (simulasi)
                start = time.time()
                time.sleep(0.01)  # Simulasi network call
                self.metrics['latency_ms'] = round((time.time() - start) * 1000, 2)
                
                # Uptime
                if self.start_time:
                    self.metrics['uptime_seconds'] = (datetime.now() - self.start_time).total_seconds()
                
                self.metrics['last_update'] = datetime.now().isoformat()
                
                time.sleep(5)  # Update setiap 5 detik
            except Exception as e:
                print(f"Monitor error: {e}")
                time.sleep(5)
    
    def get_metrics(self) -> Dict:
        """Dapatkan metrik terkini"""
        return self.metrics.copy()
    
    def get_health_status(self) -> str:
        """Dapatkan status kesehatan keseluruhan"""
        cpu = self.metrics.get('cpu_usage', 0)
        memory = self.metrics.get('memory_usage', 0)
        
        if cpu > 90 or memory > 90:
            return "CRITICAL"
        elif cpu > 70 or memory > 70:
            return "WARNING"
        else:
            return "HEALTHY"
    
    def format_uptime(self) -> str:
        """Format uptime menjadi string yang mudah dibaca"""
        seconds = int(self.metrics.get('uptime_seconds', 0))
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
