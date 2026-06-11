"""
Buku Besar Forex ZF - Core Engine
Zuhri Formalism V16.4-OMNI-WARROOM
"""

from .math_engine import MathEngine
from .data_engine import DataEngine
from .ai_engine import AIEngine
from .execution_engine import ExecutionEngine
from .storage_engine import StorageEngine
from .system_monitor import SystemMonitor

class ZFCore:
    """Mesin Utama ZF-Core yang mengintegrasikan semua modul"""
    
    def __init__(self, config):
        self.config = config
        self.math_engine = MathEngine(config)
        self.data_engine = DataEngine(config)
        self.ai_engine = AIEngine(config)
        self.execution_engine = ExecutionEngine(config)
        self.storage_engine = StorageEngine(config)
        self.system_monitor = SystemMonitor(config)
        
        self.is_running = False
    
    def initialize(self):
        """Inisialisasi semua komponen"""
        print("Initializing ZF-Core V16.4-OMNI-WARROOM...")
        self.data_engine.connect_mt5()
        self.storage_engine.load_archive()
        self.system_monitor.start()
        self.is_running = True
        print("ZF-Core initialized successfully.")
    
    def shutdown(self):
        """Shutdown semua komponen dengan aman"""
        print("Shutting down ZF-Core...")
        self.is_running = False
        self.system_monitor.stop()
        self.data_engine.disconnect_mt5()
        self.storage_engine.save_archive()
        print("ZF-Core shutdown complete.")
    
    def run_analysis_cycle(self, pairs: list):
        """Jalankan satu siklus analisis lengkap"""
        if not self.is_running:
            return None
        
        results = []
        for pair in pairs:
            # 1. Ambil data
            market_data = self.data_engine.get_market_data(pair)
            orderbook_data = self.data_engine.get_orderbook_data(pair)
            
            # 2. Hitung metrik matematika
            math_metrics = self.math_engine.calculate(market_data, orderbook_data)
            
            # 3. Analisis AI
            ai_analysis = self.ai_engine.analyze(pair, market_data, math_metrics)
            
            # 4. Gabungkan hasil
            result = {
                'pair': pair,
                'timestamp': market_data.get('timestamp'),
                'math_metrics': math_metrics,
                'ai_analysis': ai_analysis,
                'trading_style': self.determine_trading_style(math_metrics, ai_analysis),
                'signal': self.generate_signal(math_metrics, ai_analysis)
            }
            results.append(result)
            
            # 5. Simpan ke arsip
            self.storage_engine.store_session_data(result)
        
        return results
    
    def determine_trading_style(self, math_metrics: dict, ai_analysis: dict) -> str:
        """Tentukan gaya trading berdasarkan kondisi pasar"""
        zf_score = math_metrics.get('zf_score', 0)
        drift = math_metrics.get('drift', 0)
        ai_confidence = ai_analysis.get('confidence', 0)
        
        if drift > 5.0 and ai_confidence > 0.8:
            return "SCALPING"
        elif drift > 3.0 and zf_score > 0.7:
            return "DAY_TRADING"
        elif drift > 2.0 and zf_score > 0.6:
            return "SWING_TRADING"
        else:
            return "LONG_POSITION"
    
    def generate_signal(self, math_metrics: dict, ai_analysis: dict) -> dict:
        """Generate sinyal trading"""
        zf_score = math_metrics.get('zf_score', 0)
        drift = math_metrics.get('drift', 0)
        direction = ai_analysis.get('direction', 'NEUTRAL')
        
        signal = {
            'action': 'HOLD',
            'strength': 0,
            'entry': None,
            'tp': None,
            'sl': None,
            'reason': ''
        }
        
        if zf_score > 0.8 and drift > 3.0:
            signal['strength'] = min(zf_score, 1.0)
            signal['action'] = 'SELL' if direction == 'BEARISH' else 'BUY'
            signal['reason'] = f"High ZF-Score ({zf_score:.2f}) + Significant Drift ({drift:.2f}%)"
        elif zf_score > 0.6 and drift > 2.0:
            signal['strength'] = min(zf_score * 0.8, 0.8)
            signal['action'] = 'SELL' if direction == 'BEARISH' else 'BUY'
            signal['reason'] = f"Moderate ZF-Score ({zf_score:.2f}) + Drift ({drift:.2f}%)"
        
        return signal
    
    def execute_trade(self, signal: dict, pair: str):
        """Eksekusi trading dengan protokol organik"""
        if self.config.TRADING_MODE == "SIMULATION":
            return self.execution_engine.simulate_trade(signal, pair)
        elif self.config.TRADING_MODE == "AUTO":
            if self.config.ENABLE_HUMAN_IN_LOOP and signal['strength'] > 0.7:
                return self.execution_engine.request_confirmation(signal, pair)
            return self.execution_engine.execute_organic(signal, pair)
        return None

__all__ = ['ZFCore']
