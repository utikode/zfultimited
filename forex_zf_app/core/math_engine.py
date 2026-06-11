"""
Math Engine - Implementasi Bab 4: Formulasi Matematis Resonansi
"""

import numpy as np
from typing import Dict, Optional

class MathEngine:
    """Mesin kalkulasi matematis ZF-Core"""
    
    def __init__(self, config):
        self.config = config
        self.lambda_coefficient = 0.15  # Koefisien elastisitas default
    
    def calculate(self, market_data: Dict, orderbook_data: Dict) -> Dict:
        """Hitung semua metrik matematika dari data pasar"""
        p_market = market_data.get('price', 0)
        p_pure = self.calculate_pure_price(market_data, orderbook_data)
        
        # Topological Drift
        drift = self.calculate_topological_drift(p_market, p_pure)
        
        # Decay Energy
        decay = self.calculate_decay_energy(drift, market_data.get('time_window', 10))
        
        # ZF-Score
        zf_score = self.calculate_zf_score(market_data, orderbook_data, drift)
        
        # Inflection Point Detection
        inflection = self.detect_inflection_point(market_data.get('price_history', []))
        
        return {
            'p_market': p_market,
            'p_pure': p_pure,
            'drift': drift,
            'decay': decay,
            'zf_score': zf_score,
            'inflection_point': inflection,
            'lambda': self.lambda_coefficient,
            'timestamp': market_data.get('timestamp')
        }
    
    def calculate_pure_price(self, market_data: Dict, orderbook_data: Dict) -> float:
        """
        Hitung harga resonansi murni (P_pure)
        Berdasarkan rata-rata tertimbang likuiditas terintegrasi
        """
        bids = orderbook_data.get('bids', [])
        asks = orderbook_data.get('asks', [])
        
        if not bids or not asks:
            return market_data.get('price', 0)
        
        # Weighted average dari bid dan ask
        total_bid_volume = sum([b[1] for b in bids])
        total_ask_volume = sum([a[1] for a in asks])
        
        if total_bid_volume == 0 or total_ask_volume == 0:
            return market_data.get('price', 0)
        
        weighted_bid = sum([b[0] * b[1] for b in bids]) / total_bid_volume
        weighted_ask = sum([a[0] * a[1] for a in asks]) / total_ask_volume
        
        # P_pure adalah titik tengah tertimbang
        p_pure = (weighted_bid + weighted_ask) / 2
        return p_pure
    
    def calculate_topological_drift(self, p_market: float, p_pure: float) -> float:
        """
        Rumus: Dres = (|Pmarket - Ppure|) / Ppure * 100
        """
        if p_pure == 0:
            return 0.0
        drift = (abs(p_market - p_pure) / p_pure) * 100
        return round(drift, 4)
    
    def calculate_decay_energy(self, drift: float, time_window: int) -> float:
        """
        Rumus: Decay_t = Integral (0 ke t) [lambda * Dres] dt
        Simplifikasi: lambda * drift * t
        """
        decay = self.lambda_coefficient * drift * time_window
        return round(decay, 4)
    
    def calculate_zf_score(self, market_data: Dict, orderbook_data: Dict, drift: float) -> float:
        """
        Rumus: ZFscore = (Vabs / Vtotal) * tanh(Dres)
        """
        v_abs = market_data.get('volume_abnormal', 0)
        v_total = market_data.get('volume_total', 1)
        
        if v_total == 0:
            return 0.0
        
        volume_ratio = v_abs / v_total
        tanh_drift = np.tanh(drift / 100)  # Normalisasi drift
        
        zf_score = volume_ratio * tanh_drift
        return min(max(zf_score, 0.0), 1.0)  # Clamp antara 0-1
    
    def detect_inflection_point(self, price_history: list) -> bool:
        """
        Deteksi titik balik resonansi
        Ketika turunan kedua ≈ 0: d2P / dt2 = 0
        """
        if len(price_history) < 3:
            return False
        
        # Hitung turunan pertama
        first_derivative = [price_history[i+1] - price_history[i] 
                           for i in range(len(price_history)-1)]
        
        if len(first_derivative) < 2:
            return False
        
        # Hitung turunan kedua
        second_derivative = [first_derivative[i+1] - first_derivative[i] 
                            for i in range(len(first_derivative)-1)]
        
        # Cek jika turunan kedua mendekati nol
        if second_derivative:
            latest_second_deriv = abs(second_derivative[-1])
            return latest_second_deriv < 0.0001  # Threshold sangat kecil
        
        return False
    
    def update_lambda(self, new_value: float):
        """Update koefisien elastisitas berdasarkan kalibrasi"""
        self.lambda_coefficient = max(0.01, min(new_value, 1.0))
