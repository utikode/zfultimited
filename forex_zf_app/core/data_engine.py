"""
Data Engine - Implementasi Bab 2 & 7: Mekanika Data & Akuisisi Multi-Asset
"""

import time
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

# Import MetaTrader5 dengan fallback untuk simulasi
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("MetaTrader5 not available, running in simulation mode")

class DataEngine:
    """Mesin akuisisi dan manajemen data"""
    
    def __init__(self, config):
        self.config = config
        self.mt5_connected = False
        self.last_data_fetch = {}
    
    def connect_mt5(self) -> bool:
        """Koneksi ke MetaTrader 5"""
        if self.mt5_connected:
            return True
        
        # Cek jika MT5 tidak tersedia
        if not MT5_AVAILABLE:
            print("MT5 module not available, running in simulation mode")
            self.mt5_connected = False
            return False
        
        try:
            # Coba inisialisasi MT5
            if not mt5.initialize():
                print("MT5 initialization failed, running in simulation mode")
                self.mt5_connected = False
                return False
            
            # Cek koneksi
            if not mt5.terminal_info().connected:
                print("MT5 not connected to broker")
                self.mt5_connected = False
                return False
            
            self.mt5_connected = True
            print("Connected to MetaTrader 5")
            return True
        except Exception as e:
            print(f"MT5 connection error: {e}")
            self.mt5_connected = False
            return False
    
    def disconnect_mt5(self):
        """Diskoneksi dari MT5"""
        if self.mt5_connected and MT5_AVAILABLE:
            mt5.shutdown()
            self.mt5_connected = False
    
    def get_market_data(self, pair: str) -> Dict:
        """Ambil data pasar real-time atau simulasi"""
        if self.mt5_connected and pair.endswith(('USD', 'EUR', 'GBP', 'JPY')):
            return self._fetch_mt5_data(pair)
        else:
            return self._generate_simulation_data(pair)
    
    def _fetch_mt5_data(self, pair: str) -> Dict:
        """Ambil data dari MT5"""
        if not MT5_AVAILABLE:
            return self._generate_simulation_data(pair)
            
        try:
            # Mapping pair forex ke simbol MT5
            symbol = pair if pair in ['EURUSD', 'GBPUSD', 'USDJPY'] else pair
            
            # Ambil tick terakhir
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                return self._generate_simulation_data(pair)
            
            # Ambil history untuk kalkulasi
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 100)
            if rates is None or len(rates) == 0:
                return self._generate_simulation_data(pair)
            
            df = pd.DataFrame(rates)
            
            # Hitung volume abnormal
            avg_volume = df['tick_volume'].mean()
            current_volume = df['tick_volume'].iloc[-1]
            volume_abnormal = max(0, current_volume - avg_volume)
            
            return {
                'price': tick.last,
                'bid': tick.bid,
                'ask': tick.ask,
                'volume_total': current_volume,
                'volume_abnormal': volume_abnormal,
                'timestamp': datetime.now().isoformat(),
                'time_window': 10,
                'price_history': df['close'].tolist()[-20:]
            }
        except Exception as e:
            print(f"Error fetching MT5 data for {pair}: {e}")
            return self._generate_simulation_data(pair)
    
    def _generate_simulation_data(self, pair: str) -> Dict:
        """Generate data simulasi untuk testing"""
        import random
        
        # Base prices untuk major pairs
        base_prices = {
            'EURUSD': 1.0850,
            'GBPUSD': 1.2650,
            'USDJPY': 157.50,
            'USDCHF': 0.8950,
            'AUDUSD': 0.6650,
            'USDCAD': 1.3650,
            'NZDUSD': 0.6150,
            'EURGBP': 0.8580,
            'EURJPY': 171.20,
            'GBPJPY': 199.50
        }
        
        base = base_prices.get(pair, 1.0)
        noise = random.uniform(-0.002, 0.002)
        price = base + (base * noise)
        
        # Generate price history
        history = [price * (1 + random.uniform(-0.001, 0.001)) for _ in range(20)]
        
        volume_total = random.randint(100, 1000)
        volume_abnormal = random.randint(0, int(volume_total * 0.3))
        
        return {
            'price': round(price, 5),
            'bid': round(price - 0.0001, 5),
            'ask': round(price + 0.0001, 5),
            'volume_total': volume_total,
            'volume_abnormal': volume_abnormal,
            'timestamp': datetime.now().isoformat(),
            'time_window': 10,
            'price_history': history
        }
    
    def get_orderbook_data(self, pair: str) -> Dict:
        """Ambil data order book (Depth of Market)"""
        if self.mt5_connected:
            return self._fetch_mt5_orderbook(pair)
        else:
            return self._generate_simulation_orderbook(pair)
    
    def _fetch_mt5_orderbook(self, pair: str) -> Dict:
        """Ambil order book dari MT5"""
        if not MT5_AVAILABLE:
            return self._generate_simulation_orderbook(pair)
            
        try:
            book = mt5.order_book(pair)
            if book is None:
                return self._generate_simulation_orderbook(pair)
            
            bids = [(book.buy_price[i], book.buy_volume[i]) 
                   for i in range(len(book.buy_price)) if book.buy_volume[i] > 0]
            asks = [(book.sell_price[i], book.sell_volume[i]) 
                   for i in range(len(book.sell_price)) if book.sell_volume[i] > 0]
            
            return {'bids': bids[:10], 'asks': asks[:10]}
        except:
            return self._generate_simulation_orderbook(pair)
    
    def _generate_simulation_orderbook(self, pair: str) -> Dict:
        """Generate order book simulasi"""
        import random
        
        market_data = self._generate_simulation_data(pair)
        price = market_data['price']
        
        bids = []
        asks = []
        
        for i in range(10):
            bid_price = price - (i * 0.0001)
            ask_price = price + (i * 0.0001)
            bid_volume = random.randint(10, 100) * (10 - i)
            ask_volume = random.randint(10, 100) * (10 - i)
            
            bids.append((round(bid_price, 5), bid_volume))
            asks.append((round(ask_price, 5), ask_volume))
        
        return {'bids': bids, 'asks': asks}
    
    def detect_spoofing(self, orderbook_history: List[Dict]) -> Dict:
        """Deteksi pola spoofing dari history order book"""
        if len(orderbook_history) < 3:
            return {'spoofing_detected': False, 'confidence': 0}
        
        # Analisis pembatalan order yang cepat
        cancellation_rate = 0
        large_orders_appeared = 0
        large_orders_disappeared = 0
        
        for i in range(1, len(orderbook_history)):
            prev_bids = {p: v for p, v in orderbook_history[i-1].get('bids', [])}
            curr_bids = {p: v for p, v in orderbook_history[i].get('bids', [])}
            
            for price, volume in prev_bids.items():
                if volume > 50:  # Order besar
                    large_orders_appeared += 1
                    if price not in curr_bids or curr_bids[price] < volume * 0.3:
                        large_orders_disappeared += 1
        
        if large_orders_appeared > 0:
            cancellation_rate = large_orders_disappeared / large_orders_appeared
        
        spoofing_detected = cancellation_rate > 0.7
        
        return {
            'spoofing_detected': spoofing_detected,
            'confidence': min(cancellation_rate, 1.0),
            'cancellation_rate': cancellation_rate
        }
