"""
Execution Engine - Implementasi Bab 5 & 6: Protokol Eksekusi & Mitigasi Anomali
Eksekusi organik yang meniru perilaku manual trader
"""

import time
import random
from typing import Dict, Optional
from datetime import datetime

class ExecutionEngine:
    """Mesin eksekusi trading dengan protokol organik"""
    
    def __init__(self, config):
        self.config = config
        self.daily_loss = 0.0
        self.daily_profit = 0.0
        self.circuit_breaker_active = False
        self.last_execution_time = None
    
    def execute_organic(self, signal: Dict, pair: str) -> Dict:
        """
        Eksekusi trading dengan perilaku organik (meniru manual trader)
        """
        if self.circuit_breaker_active:
            return {'status': 'BLOCKED', 'reason': 'Circuit Breaker Active'}
        
        # Cek circuit breaker
        if self._check_circuit_breaker():
            return {'status': 'BLOCKED', 'reason': 'Daily Loss Limit Reached'}
        
        # Delay acak untuk meniru manusia (1-5 detik)
        delay = random.uniform(1.0, 5.0)
        time.sleep(delay)
        
        # Split order untuk eksekusi bertahap
        lot_size = self._calculate_dynamic_lot_size(signal)
        orders = self._split_order(lot_size, signal['strength'])
        
        executed_orders = []
        for order in orders:
            result = self._place_single_order(pair, order['type'], order['lot'])
            if result['success']:
                executed_orders.append(result)
            
            # Delay antar order (0.5-2 detik)
            if len(orders) > 1:
                time.sleep(random.uniform(0.5, 2.0))
        
        self.last_execution_time = datetime.now()
        
        return {
            'status': 'EXECUTED',
            'pair': pair,
            'signal': signal,
            'orders': executed_orders,
            'timestamp': datetime.now().isoformat()
        }
    
    def simulate_trade(self, signal: Dict, pair: str) -> Dict:
        """Simulasi trading tanpa eksekusi nyata"""
        lot_size = self._calculate_dynamic_lot_size(signal)
        
        # Simulasi hasil
        is_profitable = random.random() < signal['strength']
        profit_pips = random.uniform(10, 50) if is_profitable else random.uniform(-30, -5)
        
        return {
            'status': 'SIMULATED',
            'pair': pair,
            'action': signal['action'],
            'lot_size': lot_size,
            'entry': signal.get('entry_price', 0),
            'tp': signal.get('tp_price', 0),
            'sl': signal.get('sl_price', 0),
            'result': 'PROFIT' if is_profitable else 'LOSS',
            'profit_pips': profit_pips,
            'timestamp': datetime.now().isoformat()
        }
    
    def request_confirmation(self, signal: Dict, pair: str) -> Dict:
        """Minta konfirmasi manual dari user (Human-in-the-Loop)"""
        return {
            'status': 'PENDING_CONFIRMATION',
            'pair': pair,
            'signal': signal,
            'message': 'Menunggu konfirmasi manual untuk eksekusi',
            'requires_action': True
        }
    
    def _calculate_dynamic_lot_size(self, signal: Dict) -> float:
        """
        Hitung ukuran lot dinamis berdasarkan ZF-Score dan risiko
        Implementasi Bab 5.3: Alokasi Modal Berbasis ZF-Score
        """
        base_lot = self.config.DEFAULT_LOT_SIZE
        strength = signal.get('strength', 0.5)
        
        # Multiplier berdasarkan kekuatan sinyal
        if strength > 0.8:
            multiplier = 2.0  # Volume besar untuk kondisi kritis
        elif strength > 0.6:
            multiplier = 1.5
        elif strength > 0.4:
            multiplier = 1.0
        else:
            multiplier = 0.5  # Volume minimal
        
        # Batasi maksimal lot
        dynamic_lot = base_lot * multiplier
        return min(dynamic_lot, base_lot * 3.0)
    
    def _split_order(self, total_lot: float, strength: float) -> list:
        """Split order menjadi beberapa bagian kecil untuk eksekusi organik"""
        if strength > 0.8:
            # Untuk sinyal kuat, split menjadi 3 bagian
            return [
                {'type': 'MARKET', 'lot': total_lot * 0.5},
                {'type': 'MARKET', 'lot': total_lot * 0.3},
                {'type': 'MARKET', 'lot': total_lot * 0.2}
            ]
        elif strength > 0.6:
            # Split menjadi 2 bagian
            return [
                {'type': 'MARKET', 'lot': total_lot * 0.6},
                {'type': 'MARKET', 'lot': total_lot * 0.4}
            ]
        else:
            # Single order untuk sinyal lemah
            return [{'type': 'MARKET', 'lot': total_lot}]
    
    def _place_single_order(self, pair: str, order_type: str, lot: float) -> Dict:
        """Place single order ke MT5"""
        try:
            import MetaTrader5 as mt5
            
            if not mt5.terminal_info().connected:
                return {'success': False, 'error': 'MT5 not connected'}
            
            # Tentukan tipe order
            action = mt5.TRADE_ACTION_DEAL
            position_type = mt5.ORDER_TYPE_BUY if 'BUY' in str(order_type) else mt5.ORDER_TYPE_SELL
            
            # Ambil harga saat ini
            tick = mt5.symbol_info_tick(pair)
            price = tick.ask if position_type == mt5.ORDER_TYPE_BUY else tick.bid
            
            # Buat request order
            request = {
                "action": action,
                "symbol": pair,
                "volume": lot,
                "type": position_type,
                "price": price,
                "deviation": 20,
                "magic": 0,  # Magic number 0 untuk menyamarkan sebagai manual
                "comment": "ZF-Core Organic",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Kirim order
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                return {
                    'success': True,
                    'order_id': result.order,
                    'lot': lot,
                    'price': price
                }
            else:
                return {
                    'success': False,
                    'error': f"Order failed: {result.comment}"
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _check_circuit_breaker(self) -> bool:
        """
        Protokol Circuit Breaker (Bab 6.1)
        Hentikan trading jika loss harian melebihi batas
        """
        max_loss = self.config.MAX_DAILY_LOSS_PERCENT
        
        # Reset daily loss jika hari baru
        today = datetime.now().date()
        last_date = getattr(self, '_last_reset_date', None)
        
        if last_date != today:
            self.daily_loss = 0.0
            self.daily_profit = 0.0
            self._last_reset_date = today
            self.circuit_breaker_active = False
        
        # Cek apakah sudah mencapai batas loss
        if self.daily_loss >= max_loss:
            self.circuit_breaker_active = True
            return True
        
        return False
    
    def update_pnl(self, profit_loss: float):
        """Update PnL harian untuk circuit breaker"""
        if profit_loss > 0:
            self.daily_profit += profit_loss
        else:
            self.daily_loss += abs(profit_loss)
    
    def activate_circuit_breaker(self, reason: str = "Manual activation"):
        """Aktifkan circuit breaker secara manual"""
        self.circuit_breaker_active = True
        print(f"Circuit Breaker activated: {reason}")
    
    def reset_circuit_breaker(self):
        """Reset circuit breaker"""
        self.circuit_breaker_active = False
        self.daily_loss = 0.0
        print("Circuit Breaker reset")
