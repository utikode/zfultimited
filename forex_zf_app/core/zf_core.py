"""
ZF-Core: Main Controller for Buku Besar Forex ZF V16.4-OMNI-WARROOM
Coordinates all engines: Math, Data, AI, Execution, Storage, Monitor
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class ZFCore:
    def __init__(self):
        logger.info("Initializing ZF-Core V16.4-OMNI-WARROOM...")
        self.config = self._load_config()
        self.is_mt5_connected = False
        self.active_pairs = []
        self.market_data = {}
        self.predictions = {"up": [], "down": []}
        self.scan_status = "Idle"
        
        # Initialize Engines (Lazy loading or Mock for now)
        self.math_engine = MathEngineMock()
        self.data_engine = DataEngineMock()
        self.ai_engine = AIEngineMock(self.config)
        self.storage_engine = StorageEngine()
        self.monitor_engine = MonitorEngine()
        
        # Try Connect MT5
        self._connect_mt5()
        
        logger.info("ZF-Core initialized successfully.")

    def _load_config(self) -> dict:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        return {
            "gemini_api_key": "",
            "finnhub_api_key": "",
            "telegram_token": "",
            "telegram_chat_id": "",
            "risk_per_trade": 1.0,
            "max_daily_loss": 5.0
        }

    def _connect_mt5(self):
        try:
            import MetaTrader5 as mt5
            if not mt5.initialize():
                logger.warning("MT5 Initialization failed. Running in Simulation Mode.")
                self.is_mt5_connected = False
            else:
                logger.info("Connected to MetaTrader 5")
                self.is_mt5_connected = True
                # Get symbols
                symbols = mt5.symbols_get()
                if symbols:
                    self.active_pairs = [s.name for s in symbols if s.name in self._get_major_pairs()]
                else:
                    self.active_pairs = self._get_major_pairs()
        except ImportError:
            logger.warning("MetaTrader5 library not found. Running in Simulation Mode.")
            self.is_mt5_connected = False
            self.active_pairs = self._get_major_pairs()

    def _get_major_pairs(self) -> List[str]:
        return [
            "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", 
            "USDCAD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY",
            "AUDJPY", "CADJPY", "CHFJPY", "NZDJPY", "GBPAUD",
            "GBPCAD", "GBPCHF", "EURAUD", "EURCAD", "EURCHF",
            "AUDCAD", "AUDCHF", "AUDNZD", "CADCHF", "NZDCAD",
            "NZDCHF", "XAUUSD", "XAGUSD", "USOIL", "UKOIL"
        ]

    def save_config(self, new_config: dict):
        config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'config.json')
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        self.config.update(new_config)
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=4)
        logger.info("Settings saved successfully")
        
        # Update engines with new config
        if hasattr(self, 'ai_engine'):
            self.ai_engine.update_config(self.config)

    def get_config(self) -> dict:
        return self.config

    def scan_market(self, callback=None):
        """Main Scan Function: Fetch Data -> Analyze -> Predict"""
        self.scan_status = "Scanning..."
        logger.info("Starting market scan...")
        
        try:
            # 1. Fetch Data (Simulated or Real)
            data = self.data_engine.fetch_market_data(self.active_pairs)
            
            # 2. Calculate Math Metrics
            math_metrics = self.math_engine.calculate_all(data)
            
            # 3. AI Analysis & Prediction
            predictions = self.ai_engine.analyze_and_predict(math_metrics, self.config)
            
            self.predictions = predictions
            self.scan_status = "Completed"
            logger.info(f"Scan completed. Found {len(predictions['up'])} Up, {len(predictions['down'])} Down.")
            
            if callback:
                callback(predictions)
                
            return predictions
            
        except Exception as e:
            logger.error(f"Scan failed: {str(e)}")
            self.scan_status = "Failed"
            if callback:
                callback({"error": str(e)})
            return None

    def execute_trade(self, symbol, action, volume, sl, tp, magic=0):
        """Execute Trade via MT5 or Simulation"""
        if self.is_mt5_connected:
            return self._execute_mt5(symbol, action, volume, sl, tp, magic)
        else:
            return self._simulate_execution(symbol, action, volume, sl, tp)

    def _execute_mt5(self, symbol, action, volume, sl, tp, magic):
        try:
            import MetaTrader5 as mt5
            order_type = mt5.ORDER_TYPE_BUY if action == "BUY" else mt5.ORDER_TYPE_SELL
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": order_type,
                "price": mt5.symbol_info_tick(symbol).ask if action == "BUY" else mt5.symbol_info_tick(symbol).bid,
                "sl": sl,
                "tp": tp,
                "deviation": 20,
                "magic": magic,
                "comment": "ZF-Core AI",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Order failed: {result.comment}")
                return False
            logger.info(f"Order executed: {symbol} {action} {volume}")
            return True
        except Exception as e:
            logger.error(f"MT5 Execution error: {e}")
            return False

    def _simulate_execution(self, symbol, action, volume, sl, tp):
        logger.info(f"[SIMULATION] Executing: {symbol} {action} Vol:{volume} SL:{sl} TP:{tp}")
        # Store in journal
        trade_log = {
            "time": datetime.now().isoformat(),
            "symbol": symbol,
            "action": action,
            "volume": volume,
            "sl": sl,
            "tp": tp,
            "status": "Simulated"
        }
        self.storage_engine.save_trade(trade_log)
        return True

    def get_monitor_status(self):
        return self.monitor_engine.get_status(self.is_mt5_connected)

# --- Mock Engines for Stability ---

class MathEngineMock:
    def calculate_all(self, data):
        # Simulate calculation of Drift, ZF-Score, etc.
        results = {}
        for pair, info in data.items():
            price = info.get('price', 1.1000)
            pure_price = price * (1 + (0.0005 - (hash(pair) % 100)/10000)) # Mock Pure Price
            drift = abs(price - pure_price) / pure_price * 100
            zf_score = min(0.99, max(0.1, (drift / 2.0))) # Mock ZF Score
            
            results[pair] = {
                "price": price,
                "pure_price": pure_price,
                "drift": drift,
                "zf_score": zf_score,
                "volume": info.get('volume', 1000)
            }
        return results

class DataEngineMock:
    def fetch_market_data(self, pairs):
        data = {}
        for pair in pairs:
            # Mock live data if MT5 connected, else random walk
            base = 1.1000 if 'EUR' in pair else 1.3000 if 'GBP' in pair else 110.00
            noise = (hash(str(time.time()) + pair) % 1000) / 100000.0
            data[pair] = {
                "price": base + noise,
                "volume": 1000 + (hash(pair) % 500),
                "bid": base + noise - 0.0001,
                "ask": base + noise + 0.0001
            }
        return data

class AIEngineMock:
    def __init__(self, config):
        self.config = config
    
    def update_config(self, config):
        self.config = config

    def analyze_and_predict(self, metrics, config):
        # If API keys missing, fallback to simple logic
        if not config.get('gemini_api_key'):
            return self._fallback_prediction(metrics)
        
        # TODO: Implement real Gemini call here
        # For now, return fallback to ensure UI works
        return self._fallback_prediction(metrics)

    def _fallback_prediction(self, metrics):
        up_list = []
        down_list = []
        
        sorted_items = sorted(metrics.items(), key=lambda x: x[1]['zf_score'], reverse=True)
        
        for pair, data in sorted_items[:10]:
            # Simple logic: High Drift + Low ZF Score (Stable) -> Reversion Up?
            # Or High ZF Score -> Crash Down?
            if data['zf_score'] > 0.7:
                direction = "DOWN"
                target = data['price'] * (1 - data['drift']/100 * 0.8)
                down_list.append({
                    "pair": pair,
                    "current": data['price'],
                    "target": target,
                    "score": data['zf_score'],
                    "reason": "High Tension (Reversal)"
                })
            else:
                direction = "UP"
                target = data['pure_price'] # Mean reversion
                up_list.append({
                    "pair": pair,
                    "current": data['price'],
                    "target": target,
                    "score": data['zf_score'],
                    "reason": "Resonance Stable"
                })
        
        return {"up": up_list[:10], "down": down_list[:10]}

class StorageEngine:
    def __init__(self):
        self.file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'journal.json')
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def save_trade(self, trade_data):
        try:
            history = []
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r') as f:
                    history = json.load(f)
            history.append(trade_data)
            
            # Prune old data (> 30 days)
            cutoff = (datetime.now() - timedelta(days=30)).isoformat()
            history = [t for t in history if t['time'] > cutoff]
            
            with open(self.file_path, 'w') as f:
                json.dump(history, f, indent=4)
        except Exception as e:
            logger.error(f"Storage error: {e}")

    def get_history(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                return json.load(f)
        return []

class MonitorEngine:
    def get_status(self, mt5_connected):
        return {
            "mt5_status": "Connected" if mt5_connected else "Disconnected (Simulation)",
            "api_status": "Configured", # Check keys later
            "uptime": str(datetime.now()),
            "cpu_load": "Low", # Mock
            "memory_load": "Normal"
        }
