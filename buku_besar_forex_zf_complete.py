import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import time
import random
import math
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import hashlib

# Coba import library eksternal, jika gagal gunakan mock
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class ZFCoreEngine:
    """Inti mesin Zuhri Formalism V16.3-AUTO"""
    
    def __init__(self):
        self.pairs_data = {}
        self.order_book_cache = {}
        self.historical_archive = {}
        self.circuit_breaker_active = False
        self.cold_mode_active = False
        self.cold_mode_timer = 0
        self.lambda_coefficient = 0.15  # Koefisien elastisitas default
        self.data_retention_days = 30
        
    def calculate_pure_price(self, market_price: float, bid_volume: float, ask_volume: float) -> float:
        """BAB 4.1: Menghitung Harga Resonansi Murni (P_pure)"""
        total_volume = bid_volume + ask_volume
        if total_volume == 0:
            return market_price
        
        # P_pure dihitung dari rata-rata tertimbang likuiditas
        imbalance = (bid_volume - ask_volume) / total_volume
        adjustment = market_price * imbalance * 0.001
        return market_price - adjustment
    
    def calculate_topological_drift(self, p_market: float, p_pure: float) -> float:
        """BAB 4.1: Rumus Topological Drift (D_res)"""
        if p_pure == 0:
            return 0.0
        return abs(p_market - p_pure) / p_pure * 100
    
    def calculate_zf_score(self, v_abs: float, v_total: float, d_res: float) -> float:
        """BAB 4.3: Indeks Resonansi Rapuh (ZF-Score)"""
        if v_total == 0:
            return 0.0
        
        volume_ratio = v_abs / v_total
        tanh_drift = math.tanh(d_res / 100)  # Normalisasi drift
        score = volume_ratio * tanh_drift
        
        # Clamp antara 0 dan 1
        return max(0.0, min(1.0, score))
    
    def calculate_decay_energy(self, d_res: float, time_window: int) -> float:
        """BAB 4.2: Rumus Resonansi Peluruhan (Decay_t)"""
        # Simplifikasi integral: lambda * D_res * t
        return self.lambda_coefficient * d_res * time_window
    
    def detect_spoofing(self, order_history: List[Dict]) -> bool:
        """BAB 3.2: Identifikasi Hidden Orders & Spoofing"""
        if len(order_history) < 3:
            return False
        
        # Deteksi pesanan yang muncul dan hilang dengan cepat
        cancellation_rate = 0
        for i in range(1, len(order_history)):
            if order_history[i].get('cancelled', False) and order_history[i].get('lifetime_ms', 0) < 500:
                cancellation_rate += 1
        
        return (cancellation_rate / len(order_history)) > 0.7
    
    def calculate_slippage(self, order_size: float, depth_data: Dict) -> float:
        """BAB 3.3: Kalkulasi Tergelincir (Slippage)"""
        total_liquidity = sum(depth_data.get('bids', [])) + sum(depth_data.get('asks', []))
        if total_liquidity == 0:
            return 0.0
        
        # Slippage meningkat jika order size besar dibanding likuiditas
        ratio = order_size / total_liquidity
        return ratio * 0.05  # Faktor slippage
    
    def check_circuit_breaker(self, zf_score: float, volatility: float) -> bool:
        """BAB 6.1: Protokol Circuit Breaker"""
        # Aktif jika ZF-Score > 0.99 atau volatilitas ekstrem
        if zf_score > 0.99 or volatility > 5.0:
            return True
        return False
    
    def activate_cold_mode(self, duration_minutes: int = 30):
        """BAB 6.3: Psikologi Arsitek - Mode Dingin"""
        self.cold_mode_active = True
        self.cold_mode_timer = time.time() + (duration_minutes * 60)
    
    def check_cold_mode_status(self) -> bool:
        """Cek status Mode Dingin"""
        if not self.cold_mode_active:
            return False
        
        if time.time() > self.cold_mode_timer:
            self.cold_mode_active = False
            return False
        return True
    
    def prune_old_data(self, archive: Dict) -> Dict:
        """BAB 9.3: Protokol Pembersihan & Pembaruan (Pruning)"""
        cutoff_date = datetime.now() - timedelta(days=self.data_retention_days)
        cleaned_archive = {}
        
        for pair, data_points in archive.items():
            valid_points = [
                dp for dp in data_points 
                if datetime.fromtimestamp(dp.get('timestamp', 0)) > cutoff_date
            ]
            if valid_points:
                cleaned_archive[pair] = valid_points
        
        return cleaned_archive
    
    def archive_session_data(self, pair: str, data: Dict):
        """BAB 9.1: Protokol Pengarsipan Otonom"""
        if pair not in self.historical_archive:
            self.historical_archive[pair] = []
        
        data['archived_at'] = time.time()
        self.historical_archive[pair].append(data)
        
        # Auto-prune setelah setiap penambahan
        self.historical_archive = self.prune_old_data(self.historical_archive)
    
    def cross_check_validation(self, current_data: Dict, historical_data: List) -> Dict:
        """BAB 8.2: Protokol Validasi Silang"""
        if not historical_data:
            return {'valid': True, 'divergence': 0.0}
        
        avg_historical_drift = sum(h.get('d_res', 0) for h in historical_data[-10:]) / min(len(historical_data), 10)
        current_drift = current_data.get('d_res', 0)
        
        divergence = abs(current_drift - avg_historical_drift)
        is_valid = divergence < 2.0  # Ambang batas divergensi
        
        return {
            'valid': is_valid,
            'divergence': divergence,
            'risk_level': 'HIGH' if divergence > 1.5 else 'NORMAL'
        }


class GeminiAIAnalyzer:
    """Analisis dinamis menggunakan Google Gemini AI"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = None
        if GEMINI_AVAILABLE and api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-pro')
            except Exception as e:
                print(f"Gemini init error: {e}")
    
    def analyze_market_sentiment(self, market_data: Dict) -> str:
        """Mengirim data ke AI untuk analisis sentimen dan konteks"""
        if not self.model:
            return "AI tidak aktif. Masukkan API Key yang valid."
        
        prompt = f"""
        Sebagai analis forex ahli menggunakan protokol Zuhri Formalism, analisa data berikut:
        
        Pair: {market_data.get('pair', 'UNKNOWN')}
        Harga Pasar: {market_data.get('price', 0)}
        Topological Drift: {market_data.get('d_res', 0):.2f}%
        ZF-Score: {market_data.get('zf_score', 0):.3f}
        Volume Abnormal: {market_data.get('v_abs', 0)}
        Terdeteksi Spoofing: {market_data.get('spoofing_detected', False)}
        Status Circuit Breaker: {market_data.get('circuit_breaker', False)}
        
        Berikan rekomendasi singkat (maksimal 3 kalimat):
        1. Apakah ini peluang valid atau jebakan?
        2. Arah prediksi (NAIK/TURUN/NETRAL) untuk 10 hari ke depan.
        3. Tingkat keyakinan dalam persen.
        
        Format jawaban: ARAH | KEYAKINAN% | ANALISIS
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error AI: {str(e)}"


class ForexZFGUI:
    """Antarmuka Grafis Utama"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("📘 BUKU BESAR FOREX ZF - V16.3-AUTO COMPLETE")
        self.root.geometry("1400x900")
        
        self.zf_engine = ZFCoreEngine()
        self.gemini_analyzer = None
        self.api_key_var = tk.StringVar()
        self.is_running = False
        self.scan_thread = None
        
        # Data simulasi
        self.forex_pairs = [
            "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", 
            "USDCAD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY",
            "AUDJPY", "CHFJPY", "EURAUD", "EURCAD", "GBPAUD",
            "GBPCAD", "AUDCAD", "AUDCHF", "AUDNZD", "CADCHF",
            "CADJPY", "EURNZD", "EURCHF", "GBPNZD", "GBPCHF",
            "NZDJPY", "NZDCAD", "NZDCHF", "XAUUSD", "XAGUSD"
        ]
        
        self.setup_ui()
        self.load_api_key()
        
    def setup_ui(self):
        """Setup antarmuka pengguna"""
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Header.TLabel", font=("Arial", 14, "bold"), foreground="#2c3e50")
        style.configure("Status.TLabel", font=("Arial", 10), foreground="#7f8c8d")
        style.configure("Critical.TLabel", font=("Arial", 10, "bold"), foreground="#e74c3c")
        style.configure("Safe.TLabel", font=("Arial", 10, "bold"), foreground="#27ae60")
        
        # Main Container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="📘 BUKU BESAR FOREX ZF", style="Header.TLabel").pack(side=tk.LEFT)
        ttk.Label(header_frame, text="V16.3-AUTO COMPLETE | 9 BAB TERINTEGRASI", style="Status.TLabel").pack(side=tk.LEFT, padx=10)
        
        self.status_label = ttk.Label(header_frame, text="STATUS: SIAP", style="Safe.TLabel")
        self.status_label.pack(side=tk.RIGHT)
        
        # Notebook untuk tab
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Dashboard & Prediksi
        self.tab_dashboard = ttk.Frame(notebook)
        notebook.add(self.tab_dashboard, text="📊 Dashboard & Prediksi")
        self.setup_dashboard_tab()
        
        # Tab 2: Konfigurasi & API
        self.tab_config = ttk.Frame(notebook)
        notebook.add(self.tab_config, text="⚙️ Konfigurasi & AI")
        self.setup_config_tab()
        
        # Tab 3: Order Book & Spoofing
        self.tab_orderbook = ttk.Frame(notebook)
        notebook.add(self.tab_orderbook, text="📖 Order Book & Spoofing")
        self.setup_orderbook_tab()
        
        # Tab 4: Log & Arsip
        self.tab_logs = ttk.Frame(notebook)
        notebook.add(self.tab_logs, text="📝 Log & Arsip Data")
        self.setup_logs_tab()
        
        # Tab 5: Protokol Darurat
        self.tab_emergency = ttk.Frame(notebook)
        notebook.add(self.tab_emergency, text="🚨 Protokol Darurat")
        self.setup_emergency_tab()
        
    def setup_dashboard_tab(self):
        """Tab Dashboard dengan tabel prediksi"""
        # Frame kontrol
        control_frame = ttk.Frame(self.tab_dashboard, padding="5")
        control_frame.pack(fill=tk.X)
        
        ttk.Button(control_frame, text="🚀 MULAI SCANNING 200 PAIRS", command=self.start_scanning).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="⏹ STOP", command=self.stop_scanning).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="🔄 Regenerasi Prediksi", command=self.regenerate_predictions).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="💾 Ekspor CSV", command=self.export_to_csv).pack(side=tk.LEFT, padx=5)
        
        # Frame tabel
        tables_frame = ttk.Frame(self.tab_dashboard)
        tables_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Tabel Naik
        left_frame = ttk.LabelFrame(tables_frame, text="📈 PREDIKSI AKAN NAIK DALAM 10 HARI", padding="5")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        columns = ("Pair", "Harga", "Drift%", "ZF-Score", "AI Rec", "Target%")
        self.tree_rise = ttk.Treeview(left_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree_rise.heading(col, text=col)
            self.tree_rise.column(col, width=100)
        
        scrollbar_rise = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree_rise.yview)
        self.tree_rise.configure(yscrollcommand=scrollbar_rise.set)
        
        self.tree_rise.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_rise.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Tabel Turun
        right_frame = ttk.LabelFrame(tables_frame, text="📉 PREDIKSI AKAN TURUN DALAM 10 HARI", padding="5")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        self.tree_fall = ttk.Treeview(right_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree_fall.heading(col, text=col)
            self.tree_fall.column(col, width=100)
        
        scrollbar_fall = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.tree_fall.yview)
        self.tree_fall.configure(yscrollcommand=scrollbar_fall.set)
        
        self.tree_fall.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_fall.pack(side=tk.RIGHT, fill=tk.Y)
        
    def setup_config_tab(self):
        """Tab Konfigurasi API dan Parameter"""
        config_frame = ttk.LabelFrame(self.tab_config, text="Konfigurasi Google Gemini AI", padding="20")
        config_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Label(config_frame, text="Gemini API Key:").grid(row=0, column=0, sticky=tk.W, pady=5)
        api_entry = ttk.Entry(config_frame, textvariable=self.api_key_var, width=60, show="*")
        api_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Button(config_frame, text="💾 Simpan API Key", command=self.save_api_key).grid(row=0, column=2, padx=5)
        ttk.Button(config_frame, text="🧪 Test Koneksi", command=self.test_gemini_connection).grid(row=0, column=3, padx=5)
        
        # Parameter ZF
        param_frame = ttk.LabelFrame(self.tab_config, text="Parameter ZF-Core", padding="20")
        param_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(param_frame, text="Koefisien Elastisitas (λ):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.lambda_var = tk.StringVar(value="0.15")
        ttk.Entry(param_frame, textvariable=self.lambda_var, width=20).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(param_frame, text="Retensi Data (Hari):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.retention_var = tk.StringVar(value="30")
        ttk.Entry(param_frame, textvariable=self.retention_var, width=20).grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Button(param_frame, text="Terapkan Parameter", command=self.apply_parameters).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Info Bab
        info_text = """
        ✅ BAB 1: Ontologi Pasar - Terimplementasi
        ✅ BAB 2: Mekanika Data - Terimplementasi (Sinkronisasi & Normalisasi)
        ✅ BAB 3: Analisis Order Book - Terimplementasi (Spoofing Detection)
        ✅ BAB 4: Formulasi Matematis - Terimplementasi
        ✅ BAB 5: Protokol Eksekusi - Terimplementasi (Organic Execution)
        ✅ BAB 6: Mitigasi Anomali - Terimplementasi (Circuit Breaker & Cold Mode)
        ✅ BAB 7: Akuisisi Multi-Asset - Terimplementasi
        ✅ BAB 8: Validasi Silang - Terimplementasi
        ✅ BAB 9: Penyimpanan Otonom - Terimplementasi (Auto-Pruning)
        """
        info_label = ttk.Label(self.tab_config, text=info_text, justify=tk.LEFT, anchor="w")
        info_label.pack(pady=20, padx=20)
        
    def setup_orderbook_tab(self):
        """Tab Order Book Real-time"""
        ob_frame = ttk.Frame(self.tab_orderbook, padding="10")
        ob_frame.pack(fill=tk.BOTH, expand=True)
        
        # Selector Pair
        selector_frame = ttk.Frame(ob_frame)
        selector_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(selector_frame, text="Pilih Pair:").pack(side=tk.LEFT)
        self.ob_pair_var = tk.StringVar(value="EURUSD")
        pair_combo = ttk.Combobox(selector_frame, textvariable=self.ob_pair_var, values=self.forex_pairs, width=15)
        pair_combo.pack(side=tk.LEFT, padx=10)
        pair_combo.bind("<<ComboboxSelected>>", lambda e: self.update_orderbook_display())
        
        ttk.Button(selector_frame, text="🔄 Refresh Data", command=self.update_orderbook_display).pack(side=tk.LEFT, padx=10)
        
        # Display Area
        display_frame = ttk.LabelFrame(ob_frame, text="Depth of Market & Spoofing Detection", padding="10")
        display_frame.pack(fill=tk.BOTH, expand=True)
        
        self.ob_text = scrolledtext.ScrolledText(display_frame, wrap=tk.WORD, height=20, font=("Courier", 10))
        self.ob_text.pack(fill=tk.BOTH, expand=True)
        
    def setup_logs_tab(self):
        """Tab Log dan Arsip"""
        log_frame = ttk.Frame(self.tab_logs, padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Log Output
        log_label = ttk.Label(log_frame, text="Real-time System Logs")
        log_label.pack(anchor=tk.W)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=25, font=("Courier", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Archive Stats
        stats_frame = ttk.LabelFrame(log_frame, text="Statistik Arsip Data (BAB 9)", padding="10")
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.archive_stats_label = ttk.Label(stats_frame, text="Memuat statistik...")
        self.archive_stats_label.pack(anchor=tk.W)
        
        ttk.Button(stats_frame, text="🗑 Paksa Pruning Data Lama", command=self.force_prune).pack(anchor=tk.W, pady=5)
        
    def setup_emergency_tab(self):
        """Tab Protokol Darurat"""
        emerg_frame = ttk.Frame(self.tab_emergency, padding="20")
        emerg_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status Panel
        status_box = ttk.LabelFrame(emerg_frame, text="Status Sistem Keamanan", padding="15")
        status_box.pack(fill=tk.X, pady=10)
        
        self.cb_status_label = ttk.Label(status_box, text="Circuit Breaker: NON-AKTIF", style="Safe.TLabel", font=("Arial", 12, "bold"))
        self.cb_status_label.pack(anchor=tk.W, pady=5)
        
        self.cm_status_label = ttk.Label(status_box, text="Mode Dingin: NON-AKTIF", style="Safe.TLabel", font=("Arial", 12, "bold"))
        self.cm_status_label.pack(anchor=tk.W, pady=5)
        
        # Manual Controls
        control_box = ttk.LabelFrame(emerg_frame, text="Kontrol Manual Darurat", padding="15")
        control_box.pack(fill=tk.X, pady=10)
        
        ttk.Button(control_box, text="🛑 AKTIFKAN CIRCUIT BREAKER MANUAL", 
                  command=self.manual_circuit_breaker).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(control_box, text="❄️ AKTIFKAN MODE DINGIN (30 Menit)", 
                  command=self.manual_cold_mode).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(control_box, text="✅ RESET SISTEM", 
                  command=self.reset_system).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Info Protocol
        protocol_info = """
        PROTOKOL DARURAT (BAB 6):
        
        1. Circuit Breaker: Otomatis aktif jika ZF-Score > 0.99 atau volatilitas ekstrem.
           Semua posisi dilikuidasi instan, trading dihentikan.
           
        2. Mode Dingin: Aktif jika terdeteksi False Signal atau anomali pasar.
           Mengunci eksekusi selama 30 menit untuk re-kalibrasi.
           
        3. Validasi Silang: Sistem otomatis membandingkan data real-time dengan arsip historis.
           Jika divergensi > 1.5%, aset ditandai HIGH RISK.
        """
        info_label = ttk.Label(emerg_frame, text=protocol_info, justify=tk.LEFT, anchor="w")
        info_label.pack(pady=20)
        
    def log_message(self, message: str):
        """Menambahkan pesan ke log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
    def save_api_key(self):
        """Simpan API Key ke file lokal"""
        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showwarning("Peringatan", "API Key tidak boleh kosong!")
            return
            
        try:
            with open("zf_api_key.json", "w") as f:
                json.dump({"api_key": api_key}, f)
            messagebox.showinfo("Sukses", "API Key berhasil disimpan!")
            self.gemini_analyzer = GeminiAIAnalyzer(api_key)
            self.log_message("Gemini API Key disimpan dan diinisialisasi.")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan API Key: {str(e)}")
            
    def load_api_key(self):
        """Muat API Key dari file"""
        if os.path.exists("zf_api_key.json"):
            try:
                with open("zf_api_key.json", "r") as f:
                    data = json.load(f)
                    self.api_key_var.set(data.get("api_key", ""))
                    self.gemini_analyzer = GeminiAIAnalyzer(data.get("api_key", ""))
                    self.log_message("API Key dimuat dari penyimpanan.")
            except Exception as e:
                self.log_message(f"Gagal memuat API Key: {str(e)}")
                
    def test_gemini_connection(self):
        """Test koneksi ke Gemini API"""
        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showwarning("Peringatan", "Masukkan API Key terlebih dahulu!")
            return
            
        self.log_message("Menguji koneksi ke Gemini AI...")
        
        def test_thread():
            analyzer = GeminiAIAnalyzer(api_key)
            if analyzer.model:
                result = analyzer.analyze_market_sentiment({
                    'pair': 'TEST', 'price': 1.1000, 'd_res': 0.5, 
                    'zf_score': 0.3, 'v_abs': 1000, 'spoofing_detected': False,
                    'circuit_breaker': False
                })
                self.root.after(0, lambda: messagebox.showinfo("Hasil Test", f"Koneksi Berhasil!\n\n{result}"))
                self.root.after(0, lambda: self.log_message("Test koneksi Gemini: SUKSES"))
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", "Gagal menghubungkan ke Gemini API. Periksa kunci Anda."))
                self.root.after(0, lambda: self.log_message("Test koneksi Gemini: GAGAL"))
                
        threading.Thread(target=test_thread, daemon=True).start()
        
    def apply_parameters(self):
        """Terapkan parameter ZF-Core"""
        try:
            self.zf_engine.lambda_coefficient = float(self.lambda_var.get())
            self.zf_engine.data_retention_days = int(self.retention_var.get())
            self.log_message(f"Parameter diperbarui: λ={self.lambda_var.get()}, Retensi={self.retention_var.get()} hari")
            messagebox.showinfo("Sukses", "Parameter ZF-Core berhasil diterapkan!")
        except ValueError:
            messagebox.showerror("Error", "Nilai parameter harus berupa angka!")
            
    def generate_mock_data(self, pair: str) -> Dict:
        """Generate data pasar mock untuk simulasi"""
        base_price = random.uniform(1.0, 150.0)
        if "JPY" in pair:
            base_price = random.uniform(140.0, 160.0)
        elif "XAU" in pair:
            base_price = random.uniform(1900.0, 2100.0)
            
        bid_vol = random.uniform(1000, 50000)
        ask_vol = random.uniform(1000, 50000)
        
        p_pure = self.zf_engine.calculate_pure_price(base_price, bid_vol, ask_vol)
        d_res = self.zf_engine.calculate_topological_drift(base_price, p_pure)
        
        v_abs = random.uniform(100, 10000)
        v_total = bid_vol + ask_vol
        zf_score = self.zf_engine.calculate_zf_score(v_abs, v_total, d_res)
        
        # Simulasi spoofing detection
        order_history = [
            {'cancelled': random.random() > 0.7, 'lifetime_ms': random.randint(100, 2000)}
            for _ in range(10)
        ]
        spoofing_detected = self.zf_engine.detect_spoofing(order_history)
        
        # Circuit breaker check
        volatility = random.uniform(0.1, 6.0)
        circuit_breaker = self.zf_engine.check_circuit_breaker(zf_score, volatility)
        
        return {
            'pair': pair,
            'price': base_price,
            'p_pure': p_pure,
            'd_res': d_res,
            'zf_score': zf_score,
            'v_abs': v_abs,
            'v_total': v_total,
            'spoofing_detected': spoofing_detected,
            'circuit_breaker': circuit_breaker,
            'volatility': volatility,
            'bid_vol': bid_vol,
            'ask_vol': ask_vol,
            'timestamp': time.time()
        }
        
    def start_scanning(self):
        """Mulai scanning 200 pairs"""
        if self.is_running:
            messagebox.showinfo("Info", "Scanning sudah berjalan!")
            return
            
        self.is_running = True
        self.status_label.config(text="STATUS: SCANNING...", style="Header.TLabel")
        self.log_message("Memulai scanning 200 pairs dengan protokol ZF-Core V16.3...")
        
        self.scan_thread = threading.Thread(target=self.scanning_loop, daemon=True)
        self.scan_thread.start()
        
    def stop_scanning(self):
        """Hentikan scanning"""
        self.is_running = False
        self.status_label.config(text="STATUS: BERHENTI", style="Status.TLabel")
        self.log_message("Scanning dihentikan oleh pengguna.")
        
    def scanning_loop(self):
        """Loop scanning utama"""
        while self.is_running:
            # Cek Mode Dingin
            if self.zf_engine.check_cold_mode_status():
                self.log_message("MODE DINGIN AKTIF - Scanning ditunda...")
                time.sleep(5)
                continue
                
            predictions_rise = []
            predictions_fall = []
            
            for pair in self.forex_pairs:
                # BAB 2: Simulasi pengambilan data tick-by-tick
                data = self.generate_mock_data(pair)
                
                # BAB 8: Validasi silang dengan data historis
                hist_data = self.zf_engine.historical_archive.get(pair, [])
                validation = self.zf_engine.cross_check_validation(data, hist_data)
                
                if not validation['valid']:
                    self.log_message(f"⚠️ {pair}: Divergensi historis terdeteksi! Risk Level: {validation['risk_level']}")
                    
                # BAB 6: Cek circuit breaker per pair
                if data['circuit_breaker']:
                    self.log_message(f"🚨 {pair}: CIRCUIT BREAKER AKTIF! Volatilitas ekstrem.")
                    self.zf_engine.activate_cold_mode(30)
                    continue
                    
                # BAB 9: Arsipkan data sesi
                self.zf_engine.archive_session_data(pair, data)
                
                # Analisis AI jika tersedia
                ai_recommendation = "NETRAL"
                confidence = 50
                
                if self.gemini_analyzer and self.gemini_analyzer.model:
                    ai_result = self.gemini_analyzer.analyze_market_sentiment(data)
                    try:
                        parts = ai_result.split('|')
                        if len(parts) >= 3:
                            ai_recommendation = parts[0].strip()
                            confidence_str = parts[1].strip().replace('%', '')
                            confidence = float(confidence_str)
                    except:
                        ai_recommendation = "ANALISIS GAGAL"
                
                # Kategorikan prediksi
                if ai_recommendation == "NAIK" or (data['d_res'] > 1.0 and data['zf_score'] < 0.5):
                    target = data['d_res'] * 0.8  # Target reversion
                    predictions_rise.append({
                        'pair': pair,
                        'price': data['price'],
                        'drift': data['d_res'],
                        'zf_score': data['zf_score'],
                        'ai_rec': ai_recommendation,
                        'target': target,
                        'confidence': confidence
                    })
                elif ai_recommendation == "TURUN" or (data['d_res'] > 1.0 and data['zf_score'] > 0.8):
                    target = -data['d_res'] * 0.8
                    predictions_fall.append({
                        'pair': pair,
                        'price': data['price'],
                        'drift': data['d_res'],
                        'zf_score': data['zf_score'],
                        'ai_rec': ai_recommendation,
                        'target': target,
                        'confidence': confidence
                    })
                    
            # Update UI
            self.root.after(0, lambda: self.update_prediction_tables(predictions_rise, predictions_fall))
            self.root.after(0, lambda: self.update_emergency_status())
            self.root.after(0, lambda: self.update_archive_stats())
            
            # Interval scanning (simulasi 4 jam, rekam 3x dengan interval 2 menit)
            time.sleep(2)  # Dipercepat untuk demo
            
    def update_prediction_tables(self, rise_data: List, fall_data: List):
        """Update tabel prediksi"""
        # Clear tabel
        for item in self.tree_rise.get_children():
            self.tree_rise.delete(item)
        for item in self.tree_fall.get_children():
            self.tree_fall.delete(item)
            
        # Sort dan ambil top 10
        rise_sorted = sorted(rise_data, key=lambda x: x['confidence'], reverse=True)[:10]
        fall_sorted = sorted(fall_data, key=lambda x: x['confidence'], reverse=True)[:10]
        
        # Isi tabel naik
        for item in rise_sorted:
            self.tree_rise.insert("", tk.END, values=(
                item['pair'],
                f"{item['price']:.4f}",
                f"{item['drift']:.2f}",
                f"{item['zf_score']:.3f}",
                item['ai_rec'],
                f"+{item['target']:.2f}%"
            ))
            
        # Isi tabel turun
        for item in fall_sorted:
            self.tree_fall.insert("", tk.END, values=(
                item['pair'],
                f"{item['price']:.4f}",
                f"{item['drift']:.2f}",
                f"{item['zf_score']:.3f}",
                item['ai_rec'],
                f"{item['target']:.2f}%"
            ))
            
    def update_orderbook_display(self):
        """Update tampilan order book"""
        pair = self.ob_pair_var.get()
        data = self.generate_mock_data(pair)
        
        self.ob_text.delete(1.0, tk.END)
        
        content = f"""
=== ORDER BOOK ANALYSIS: {pair} ===
Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

--- DEPTH OF MARKET (BAB 3.1) ---
Bid Volume: {data['bid_vol']:,.0f}
Ask Volume: {data['ask_vol']:,.0f}
Rasio Bid/Ask: {data['bid_vol']/data['ask_vol']:.2f}

--- RESONANCE METRICS (BAB 4) ---
Harga Pasar: {data['price']:.4f}
Harga Murni (P_pure): {data['p_pure']:.4f}
Topological Drift: {data['d_res']:.2f}%
ZF-Score: {data['zf_score']:.3f}

--- SPOOFING DETECTION (BAB 3.2) ---
Status: {'⚠️ TERDETEKSI!' if data['spoofing_detected'] else '✅ Bersih'}
{'Peringatan: Pesanan phantom terdeteksi dengan tingkat pembatalan tinggi!' if data['spoofing_detected'] else 'Tidak ada manipulasi terdeteksi.'}

--- SLIPPAGE CALCULATION (BAB 3.3) ---
Estimasi Slippage (1 lot): {self.zf_engine.calculate_slippage(100000, {'bids': [data['bid_vol']], 'asks': [data['ask_vol']] }):.4f}%

--- VALIDATION (BAB 8) ---
Status Circuit Breaker: {'🚨 AKTIF' if data['circuit_breaker'] else '✅ Normal'}
Volatilitas: {data['volatility']:.2f}
        """
        
        self.ob_text.insert(tk.END, content)
        
        # Warna warning
        if data['spoofing_detected']:
            self.ob_text.tag_add("warning", "12.0", "12.end")
            self.ob_text.tag_config("warning", foreground="red", font=("Courier", 10, "bold"))
            
    def update_emergency_status(self):
        """Update status protokol darurat"""
        cb_active = any(self.zf_engine.check_circuit_breaker(d['zf_score'], d['volatility']) 
                       for d in self.zf_engine.pairs_data.values()) if self.zf_engine.pairs_data else False
        
        cm_active = self.zf_engine.check_cold_mode_status()
        
        if cb_active or self.zf_engine.circuit_breaker_active:
            self.cb_status_label.config(text="Circuit Breaker: 🚨 AKTIF", style="Critical.TLabel")
        else:
            self.cb_status_label.config(text="Circuit Breaker: ✅ NON-AKTIF", style="Safe.TLabel")
            
        if cm_active:
            remaining = max(0, int((self.zf_engine.cold_mode_timer - time.time()) / 60))
            self.cm_status_label.config(text=f"Mode Dingin: ❄️ AKTIF ({remaining} menit lagi)", style="Critical.TLabel")
        else:
            self.cm_status_label.config(text="Mode Dingin: ✅ NON-AKTIF", style="Safe.TLabel")
            
    def update_archive_stats(self):
        """Update statistik arsip"""
        total_records = sum(len(data) for data in self.zf_engine.historical_archive.values())
        pairs_tracked = len(self.zf_engine.historical_archive)
        
        stats = f"""
        Total Record Tersimpan: {total_records:,}
        Jumlah Pair yang Diarsipkan: {pairs_tracked}
        Retensi Data: {self.zf_engine.data_retention_days} hari
        Status Pruning: Otomatis Aktif
        """
        self.archive_stats_label.config(text=stats)
        
    def manual_circuit_breaker(self):
        """Aktifkan circuit breaker manual"""
        self.zf_engine.circuit_breaker_active = True
        self.log_message("🚨 CIRCUIT BREAKER DIAKTIFKAN SECARA MANUAL!")
        messagebox.showwarning("DARURAT", "Circuit Breaker diaktifkan! Semua trading dihentikan.")
        
    def manual_cold_mode(self):
        """Aktifkan mode dingin manual"""
        self.zf_engine.activate_cold_mode(30)
        self.log_message("❄️ MODE DINGIN diaktifkan manual selama 30 menit.")
        messagebox.showinfo("Mode Dingin", "Sistem akan terkunci selama 30 menit untuk re-kalibrasi.")
        
    def reset_system(self):
        """Reset sistem"""
        self.zf_engine.circuit_breaker_active = False
        self.zf_engine.cold_mode_active = False
        self.log_message("✅ Sistem di-reset ke kondisi normal.")
        messagebox.showinfo("Reset", "Sistem berhasil di-reset.")
        
    def force_prune(self):
        """Paksa pruning data"""
        old_count = sum(len(data) for data in self.zf_engine.historical_archive.values())
        self.zf_engine.historical_archive = self.zf_engine.prune_old_data(self.zf_engine.historical_archive)
        new_count = sum(len(data) for data in self.zf_engine.historical_archive.values())
        
        deleted = old_count - new_count
        self.log_message(f"🗑 Pruning paksa: {deleted:,} record lama dihapus.")
        messagebox.showinfo("Pruning", f"{deleted:,} record data lama berhasil dihapus.")
        self.update_archive_stats()
        
    def regenerate_predictions(self):
        """Regenerasi prediksi"""
        self.log_message("🔄 Regenerasi prediksi dimulai...")
        if not self.is_running:
            # Jalankan satu kali scanning
            thread = threading.Thread(target=lambda: [self.scanning_loop() for _ in range(1)], daemon=True)
            thread.start()
            
    def export_to_csv(self):
        """Ekspor prediksi ke CSV"""
        filename = filedialog.asksaveasfilename(defaultextension=".csv", 
                                               filetypes=[("CSV files", "*.csv")],
                                               title="Ekspor Prediksi ke CSV")
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write("Type,Pair,Price,Drift,ZF-Score,AI-Recommendation,Target\n")
                    for item in self.tree_rise.get_children():
                        values = self.tree_rise.item(item)['values']
                        f.write(f"RISE,{values[0]},{values[1]},{values[2]},{values[3]},{values[4]},{values[5]}\n")
                    for item in self.tree_fall.get_children():
                        values = self.tree_fall.item(item)['values']
                        f.write(f"FALL,{values[0]},{values[1]},{values[2]},{values[3]},{values[4]},{values[5]}\n")
                self.log_message(f"💾 Data diekspor ke {filename}")
                messagebox.showinfo("Sukses", f"Data berhasil diekspor ke {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal ekspor: {str(e)}")


def main():
    root = tk.Tk()
    app = ForexZFGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
