"""
AI Engine - Integrasi Google Gemini & Finnhub untuk Analisis Dinamis
Implementasi Bab 7 & 8: Analisis AI & Validasi Silang
"""

import json
from typing import Dict, Optional
import requests

class AIEngine:
    """Mesin analisis AI dengan Gemini dan Finnhub"""
    
    def __init__(self, config):
        self.config = config
        self.gemini_client = None
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Inisialisasi klien Gemini"""
        if self.config.GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.config.GEMINI_API_KEY)
                self.gemini_client = genai.GenerativeModel('gemini-pro')
            except Exception as e:
                print(f"Gemini initialization error: {e}")
                self.gemini_client = None
    
    def analyze(self, pair: str, market_data: Dict, math_metrics: Dict) -> Dict:
        """Analisis komprehensif menggunakan AI dan data eksternal"""
        
        # 1. Ambil data dari Finnhub (jika tersedia)
        finnhub_data = self._fetch_finnhub_data(pair)
        
        # 2. Buat prompt untuk Gemini
        prompt = self._create_analysis_prompt(pair, market_data, math_metrics, finnhub_data)
        
        # 3. Minta analisis dari Gemini
        ai_analysis = self._query_gemini(prompt)
        
        # 4. Parse hasil AI
        return self._parse_ai_response(ai_analysis, math_metrics)
    
    def _fetch_finnhub_data(self, pair: str) -> Dict:
        """Ambil data sentimen dan berita dari Finnhub"""
        if not self.config.FINNHUB_API_KEY:
            return {'sentiment': 'NEUTRAL', 'news_count': 0}
        
        try:
            # Mapping pair forex ke simbol Finnhub
            symbol_map = {
                'EURUSD': 'FOREX:EURUSD',
                'GBPUSD': 'FOREX:GBPUSD',
                'USDJPY': 'FOREX:USDJPY',
                'USDCHF': 'FOREX:USDCHF',
                'AUDUSD': 'FOREX:AUDUSD',
                'USDCAD': 'FOREX:USDCAD',
                'NZDUSD': 'FOREX:NZDUSD'
            }
            
            symbol = symbol_map.get(pair, '')
            if not symbol:
                return {'sentiment': 'NEUTRAL', 'news_count': 0}
            
            # Ambil news/sentiment dari Finnhub
            url = "https://finnhub.io/api/v1/news"
            params = {
                'category': 'forex',
                'token': self.config.FINNHUB_API_KEY
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                news = response.json()[:5]  # Ambil 5 berita terbaru
                
                # Analisis sentimen sederhana dari judul
                bullish_keywords = ['rise', 'gain', 'up', 'bullish', 'strength', 'rally']
                bearish_keywords = ['fall', 'drop', 'down', 'bearish', 'weakness', 'decline']
                
                bullish_count = 0
                bearish_count = 0
                
                for article in news:
                    title = article.get('headline', '').lower()
                    if any(word in title for word in bullish_keywords):
                        bullish_count += 1
                    elif any(word in title for word in bearish_keywords):
                        bearish_count += 1
                
                total = bullish_count + bearish_count
                if total == 0:
                    sentiment = 'NEUTRAL'
                elif bullish_count > bearish_count:
                    sentiment = 'BULLISH'
                else:
                    sentiment = 'BEARISH'
                
                return {
                    'sentiment': sentiment,
                    'news_count': len(news),
                    'bullish_count': bullish_count,
                    'bearish_count': bearish_count
                }
            
            return {'sentiment': 'NEUTRAL', 'news_count': 0}
        except Exception as e:
            print(f"Finnhub fetch error: {e}")
            return {'sentiment': 'NEUTRAL', 'news_count': 0}
    
    def _create_analysis_prompt(self, pair: str, market_data: Dict, 
                                math_metrics: Dict, finnhub_data: Dict) -> str:
        """Buat prompt analisis untuk Gemini"""
        return f"""
Anda adalah asisten trading ahli untuk sistem ZF-Core (Zuhri Formalism).
Analisis pasangan mata uang: {pair}

DATA MATEMATIKA (ZF-Core):
- Harga Pasar: {math_metrics.get('p_market', 0)}
- Harga Murni: {math_metrics.get('p_pure', 0)}
- Topological Drift: {math_metrics.get('drift', 0):.2f}%
- Decay Energy: {math_metrics.get('decay', 0):.2f}
- ZF-Score: {math_metrics.get('zf_score', 0):.2f} (0-1 scale)
- Inflection Point: {'Ya' if math_metrics.get('inflection_point') else 'Tidak'}

DATA PASAR:
- Volume Total: {market_data.get('volume_total', 0)}
- Volume Abnormal: {market_data.get('volume_abnormal', 0)}

DATA SENTIMEN (Finnhub):
- Sentimen Berita: {finnhub_data.get('sentiment', 'NEUTRAL')}
- Jumlah Berita: {finnhub_data.get('news_count', 0)}

TUGAS ANDA:
1. Tentukan arah pasar (BULLISH/BEARISH/NEUTRAL)
2. Berikan tingkat kepercayaan (0.0-1.0)
3. Identifikasi gaya trading terbaik (SCALPING/DAY_TRADING/SWING_TRADING/LONG_POSITION)
4. Berikan rekomendasi entry, TP, dan SL
5. Deteksi potensi risiko atau anomali

FORMAT RESPON (JSON saja, tanpa teks lain):
{{
    "direction": "BULLISH/BEARISH/NEUTRAL",
    "confidence": 0.0-1.0,
    "trading_style": "SCALPING/DAY_TRADING/SWING_TRADING/LONG_POSITION",
    "entry_price": 0.0,
    "tp_price": 0.0,
    "sl_price": 0.0,
    "reasoning": "penjelasan singkat",
    "risk_level": "LOW/MEDIUM/HIGH"
}}
"""
    
    def _query_gemini(self, prompt: str) -> Optional[str]:
        """Kirim query ke Gemini"""
        if not self.gemini_client:
            return None
        
        try:
            response = self.gemini_client.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini query error: {e}")
            return None
    
    def _parse_ai_response(self, ai_response: Optional[str], 
                          math_metrics: Dict) -> Dict:
        """Parse respons AI menjadi struktur data"""
        default_response = {
            'direction': 'NEUTRAL',
            'confidence': 0.5,
            'trading_style': 'DAY_TRADING',
            'entry_price': math_metrics.get('p_market', 0),
            'tp_price': 0,
            'sl_price': 0,
            'reasoning': 'AI tidak tersedia atau error',
            'risk_level': 'MEDIUM'
        }
        
        if not ai_response:
            return default_response
        
        try:
            # Ekstrak JSON dari respons
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                return default_response
            
            json_str = ai_response[start_idx:end_idx]
            parsed = json.loads(json_str)
            
            return {
                'direction': parsed.get('direction', 'NEUTRAL'),
                'confidence': float(parsed.get('confidence', 0.5)),
                'trading_style': parsed.get('trading_style', 'DAY_TRADING'),
                'entry_price': float(parsed.get('entry_price', math_metrics.get('p_market', 0))),
                'tp_price': float(parsed.get('tp_price', 0)),
                'sl_price': float(parsed.get('sl_price', 0)),
                'reasoning': parsed.get('reasoning', ''),
                'risk_level': parsed.get('risk_level', 'MEDIUM')
            }
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            return default_response
    
    def update_api_key(self, new_key: str):
        """Update API key Gemini"""
        self.config.GEMINI_API_KEY = new_key
        self._initialize_gemini()
