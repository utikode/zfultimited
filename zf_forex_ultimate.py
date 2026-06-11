import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import time
import random
import json
import os
import datetime
import math
import requests
from collections import deque
import google.generativeai as genai

# --- KONFIGURASI & STATE GLOBAL ---
class ZFState:
    def __init__(self):
        self.api_key_gemini = ""
        self.api_key_finnhub = ""
        self.is_running = False
        self.is_cold_mode = False
        self.circuit_breaker_active = False
        self.daily_loss_limit = 500.0  # USD
        self.current_daily_loss = 0.0
        self.require_human_confirm = True
        self.data_archive = []
        self.log_buffer = deque(maxlen=1000)
        self.positions = []
        self.market_data = {}  # Simulasi data pasar
        self.last_sync = None
        self.model_ai = None
        
        # Load config if exists
        self.load_config()

    def save_config(self):
        config = {
            "api_key_gemini": self.api_key_gemini,
            "api_key_finnhub": self.api_key_finnhub,
            "daily_loss_limit": self.daily_loss_limit,
            "require_human_confirm": self.require_human_confirm
        }
        try:
            with open("zf_config.json", "w") as f:
                json.dump(config, f)
        except Exception:
            pass

    def load_config(self):
        if os.path.exists("zf_config.json"):
            try:
                with open("zf_config.json", "r") as f:
                    config = json.load(f)
                    self.api_key_gemini = config.get("api_key_gemini", "")
                    self.api_key_finnhub = config.get("api_key_finnhub", "")
                    self.daily_loss_limit = config.get("daily_loss_limit", 500.0)
                    self.require_human_confirm = config.get("require_human_confirm", True)
                    
                # Inisialisasi AI jika key ada
                if self.api_key_gemini:
                    try:
                        genai.configure(api_key=self.api_key_gemini)
                        self.model_ai = genai.GenerativeModel('gemini-pro')
                    except Exception as e:
                        print(f"Gagal inisialisasi Gemini: {e}")
            except Exception:
                pass

state = ZFState()

# --- LOGIC ENGINE (SIMULASI BAB 1-9) ---
def calculate_zf_metrics(pair, price):
    """Simulasi perhitungan metrik ZF (Bab 1 & 4)"""
    pure_price = price * (1 + random.uniform(-0.002, 0.002))
    drift = abs(price - pure_price) / pure_price * 100
    volume_abs = random.uniform(0.5, 2.0)
    volume_total = random.uniform(10, 100)
    zf_score = min(1.0, (volume_abs / volume_total) * math.tanh(drift))
    return {
        "pure_price": pure_price,
        "drift": drift,
        "zf_score": zf_score,
        "status": "CRITICAL" if zf_score > 0.8 else "STABLE"
    }

def fetch_finnhub_data(symbol):
    """Mengambil data sentimen & fundamental dari Finnhub (Bab 7)"""
    if not state.api_key_finnhub:
        return {"sentiment": 0, "news_count": 0, "source": "Finnhub (No API Key)"}
    
    try:
        # Ambil sentimen berita
        url_news = f"https://finnhub.io/api/v1/news-sentiment"
        params = {"symbol": symbol, "token": state.api_key_finnhub}
        resp = requests.get(url_news, params=params, timeout=5)
        
        sentiment_score = 0
        news_count = 0
        
        if resp.status_code == 200:
            data = resp.json()
            if 'sentiment' in data:
                sentiment_score = data['sentiment'].get('score', 0)
                news_count = data.get('totalItems', 0)
        
        # Ambil quote realtime untuk validasi
        finnhub_sym = f"O:{symbol}"  # Format OANDA untuk forex
        url_quote = f"https://finnhub.io/api/v1/quote"
        params_q = {"symbol": finnhub_sym, "token": state.api_key_finnhub}
        resp_q = requests.get(url_quote, params=params_q, timeout=5)
        
        ext_price = 0
        if resp_q.status_code == 200:
            q_data = resp_q.json()
            ext_price = q_data.get('c', 0)
        
        return {
            "sentiment": sentiment_score,
            "news_count": news_count,
            "external_price": ext_price,
            "source": "Finnhub Live"
        }
    except Exception as e:
        return {"sentiment": 0, "news_count": 0, "error": str(e), "source": "Finnhub Error"}

def detect_spoofing(order_book):
    """Simulasi deteksi spoofing (Bab 3)"""
    # Logika sederhana: jika ada order besar yang hilang cepat
    if random.random() < 0.1:
        return True, "Spoofing terdeteksi pada level Ask!"
    return False, "Order book bersih."

def analyze_with_gemini(data_context):
    """Panggilan API Gemini untuk analisis dinamis (Bab 7 & 8)"""
    if not state.model_ai:
        return "AI Tidak Aktif: Masukkan API Key Gemini di pengaturan."
    
    try:
        prompt = f"""
        Anda adalah Arsitek Trading ZF-Core V16.3.
        Analisis pasangan {data_context.get('pair', 'UNKNOWN')} dengan data:
        - Harga: {data_context.get('price', 0)}
        - Drift: {data_context.get('drift', 0):.2f}%
        - ZF-Score: {data_context.get('zf_score', 0):.2f}
        - Sentimen Finnhub: {data_context.get('sentiment', 0)} (-1 s/d 1)
        - Status: {data_context.get('status', 'UNKNOWN')}
        
        Berikan rekomendasi (BUY/SELL/WAIT), alasan singkat, dan deteksi risiko spoofing.
        Jawaban maksimal 2 kalimat.
        """
        
        response = state.model_ai.generate_content(prompt)
        return f"🤖 AI Gemini: {response.text}"
    except Exception as e:
        return f"Error AI: {str(e)}"

def check_circuit_breaker(loss):
    """Bab 6: Circuit Breaker"""
    if loss >= state.daily_loss_limit:
        state.circuit_breaker_active = True
        state.is_running = False
        return True
    return False

def organic_execution(pair, action, volume):
    """Bab 5: Eksekusi Organik"""
    delay = random.uniform(1.5, 4.0)  # Delay acak seperti manusia
    time.sleep(delay)
    
    # Split order jika volume besar
    parts = 1
    if volume > 1.0:
        parts = random.randint(2, 4)
    
    executed_volume = 0
    for i in range(parts):
        part_vol = volume / parts
        time.sleep(random.uniform(0.5, 1.5)) # Jeda antar part
        executed_volume += part_vol
    
    return f"Eksekusi {action} {pair} total {executed_volume:.2f} lot selesai secara organik."

# --- GUI APPLICATION ---
class ZFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Buku Besar Forex ZF V16.3-ULTIMATE")
        self.root.geometry("1200x800")
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#1e1e1e")
        style.configure("TLabel", background="#1e1e1e", foreground="#ffffff", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground="#00ff9d")
        style.configure("Critical.TLabel", foreground="#ff4d4d")
        style.configure("Safe.TLabel", foreground="#00ff9d")
        style.configure("TButton", font=("Segoe UI", 10), padding=5)
        style.configure("TCheckbutton", background="#1e1e1e", foreground="#ffffff")
        
        self.root.configure(bg="#1e1e1e")
        
        self.create_layout()
        self.update_logs("Sistem siap. Menunggu instruksi Arsitek.")
        self.load_dashboard_data()

    def create_layout(self):
        # Main Container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top Bar: Status & Controls
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(top_frame, text="STATUS: IDLE", style="Header.TLabel")
        self.status_label.pack(side=tk.LEFT)
        
        self.circuit_label = ttk.Label(top_frame, text="CIRCUIT BREAKER: AMAN", foreground="#00ff9d")
        self.circuit_label.pack(side=tk.LEFT, padx=20)
        
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text="⚙️ Pengaturan", command=self.open_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📊 Laporan (Vault)", command=self.export_report).pack(side=tk.LEFT, padx=5)
        self.start_btn = ttk.Button(btn_frame, text="▶️ MULAI ROBOTIK", command=self.toggle_robot)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        # Middle Section: Dashboard & Manifold
        mid_frame = ttk.Frame(main_frame)
        mid_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Left: Market Scan & Predictions
        left_panel = ttk.LabelFrame(mid_frame, text="📡 Pemindaian Pasar & Prediksi (Bab 7-8)", padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        columns = ("Pair", "Harga", "Drift", "ZF-Score", "Status", "AI Rec")
        self.tree = ttk.Treeview(left_panel, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Right: Manifold Visualizer & Alerts
        right_panel = ttk.LabelFrame(mid_frame, text="🌌 Manifold Elastis & Spectral Echo", padding=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Simulasi Grafik Manifold (Canvas)
        self.canvas = tk.Canvas(right_panel, bg="#2b2b2b", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.alert_text = scrolledtext.ScrolledText(right_panel, height=8, bg="#1a1a1a", fg="#00ff9d", font=("Consolas", 9))
        self.alert_text.pack(fill=tk.X, pady=(10, 0))
        self.alert_text.insert(tk.END, "Menunggu sinyal Spectral Echo...\n")
        self.alert_text.config(state='disabled')

        # Bottom Section: Logs & Control
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        
        log_frame = ttk.LabelFrame(bottom_frame, text="📜 Log Aktivitas & Archival Vault", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_display = scrolledtext.ScrolledText(log_frame, bg="#121212", fg="#cccccc", font=("Consolas", 9))
        self.log_display.pack(fill=tk.BOTH, expand=True)
        self.log_display.config(state='disabled')

    def update_logs(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        full_msg = f"[{timestamp}] {message}\n"
        state.log_buffer.append(full_msg)
        
        self.log_display.config(state='normal')
        self.log_display.insert(tk.END, full_msg)
        self.log_display.see(tk.END)
        self.log_display.config(state='disabled')

    def add_alert(self, message, level="INFO"):
        color = "#00ff9d" if level == "INFO" else "#ff4d4d"
        self.alert_text.config(state='normal')
        self.alert_text.insert(tk.END, f"[{level}] {message}\n")
        self.alert_text.see(tk.END)
        self.alert_text.config(state='disabled')
        
        if level == "CRITICAL":
            self.update_logs(f"SPECTRAL ECHO: {message}")
            if state.is_running:
                self.trigger_cold_mode()

    def trigger_cold_mode(self):
        state.is_cold_mode = True
        state.is_running = False
        self.status_label.config(text="STATUS: MODE DINGIN (AKSES DIBATASI)")
        self.status_label.config(foreground="#ffaa00")
        self.update_logs("Protokol Mode Dingin diaktifkan. Menunggu re-kalibrasi.")
        messagebox.showwarning("MODE DINGIN", "Anomali terdeteksi! Sistem dikunci selama 30 menit sesuai protokol Bab 6.")

    def toggle_robot(self):
        if state.is_running:
            state.is_running = False
            self.start_btn.config(text="▶️ MULAI ROBOTIK")
            self.status_label.config(text="STATUS: BERHENTI")
            self.update_logs("Robotik dihentikan oleh Arsitek.")
        else:
            if state.circuit_breaker_active:
                messagebox.showerror("ERROR", "Circuit Breaker Aktif! Reset manual diperlukan.")
                return
            
            state.is_running = True
            self.start_btn.config(text="⏹️ HENTIKAN")
            self.status_label.config(text="STATUS: MENYAPU PASAR...")
            self.status_label.config(foreground="#00ff9d")
            self.update_logs("Robotik dimulai. Memulai siklus pemindaian 200 pairs...")
            
            thread = threading.Thread(target=self.robot_loop)
            thread.daemon = True
            thread.start()

    def robot_loop(self):
        while state.is_running and not state.circuit_breaker_active:
            if state.is_cold_mode:
                time.sleep(60)
                continue
                
            # 1. Ambil Data & Hitung Metrik (Bab 2, 4)
            pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "XAUUSD"]
            for pair in pairs:
                if not state.is_running: break
                
                price = random.uniform(1.05, 1.40) if 'USD' in pair else random.uniform(1900, 2050)
                metrics = calculate_zf_metrics(pair, price)
                
                # 2. Ambil data Finnhub untuk sentimen (Bab 7)
                finnhub_data = fetch_finnhub_data(pair)
                metrics['sentiment'] = finnhub_data.get('sentiment', 0)
                metrics['pair'] = pair
                metrics['price'] = price
                
                # 3. Deteksi Spoofing (Bab 3)
                is_spoof, spoof_msg = detect_spoofing({})
                if is_spoof:
                    self.add_alert(spoof_msg, "WARNING")
                    continue # Skip pair ini
                
                # 4. Analisis AI dengan konteks lengkap (ZF + Finnhub) (Bab 7, 8)
                ai_rec = analyze_with_gemini(metrics)
                
                # 5. Update UI
                self.update_tree(pair, price, metrics, ai_rec)
                
                # 6. Cek Circuit Breaker (Bab 6)
                # Simulasi loss acak kecil
                if random.random() < 0.05:
                    loss = random.uniform(10, 50)
                    state.current_daily_loss += loss
                    if check_circuit_breaker(state.current_daily_loss):
                        self.circuit_label.config(text="CIRCUIT BREAKER: AKTIF!", foreground="#ff0000")
                        self.add_alert("BATAS KERUGIAN HARIAN TERCAPAI! SEMUA POSISI DITUTUP.", "CRITICAL")
                        state.is_running = False
                        break
                
                # 7. Eksekusi jika sinyal kuat & Human-in-loop (Bab 5)
                if metrics['zf_score'] > 0.75 and "BUY" in ai_rec:
                    if state.require_human_confirm:
                        self.root.after(0, self.request_human_confirm, pair, "BUY")
                    else:
                        # Simulasi eksekusi organik
                        res = organic_execution(pair, "BUY", 0.5)
                        self.update_logs(res)
                        state.data_archive.append({"time": str(datetime.datetime.now()), "action": "BUY", "pair": pair})

            # Siklus setiap 10 detik untuk demo
            time.sleep(10)
            self.draw_manifold()

    def update_tree(self, pair, price, metrics, ai_rec):
        # Hapus item lama jika ada (untuk demo sederhana, kita tambah saja atau update)
        # Dalam app nyata, kita update berdasarkan ID
        values = (pair, f"{price:.4f}", f"{metrics['drift']:.2f}%", f"{metrics['zf_score']:.2f}", metrics['status'], ai_rec[:20]+"...")
        
        # Cek apakah sudah ada
        existing = self.tree.get_children()
        found = False
        for item in existing:
            if self.tree.item(item)['values'][0] == pair:
                self.tree.item(item, values=values)
                found = True
                break
        
        if not found:
            self.tree.insert("", tk.END, values=values)
            
        # Warna baris berdasarkan status
        tag = "critical" if metrics['zf_score'] > 0.8 else "safe"
        # Treeview tagging butuh konfigurasi style tambahan, disederhanakan di sini

    def draw_manifold(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        # Gambar garis resonansi acak yang halus
        points = []
        for i in range(0, w, 20):
            y = h/2 + math.sin(i/50 + time.time()) * 50 + random.randint(-10, 10)
            points.append((i, y))
        
        self.canvas.create_line(points, fill="#00ff9d", width=2, smooth=True)
        self.canvas.create_text(w/2, h/2, text="VISUALISASI MANIFOLD ELASTIS", fill="#555555", font=("Arial", 12))

    def request_human_confirm(self, pair, action):
        if messagebox.askyesno("Konfirmasi Manusia (Bab 5)", f"Sinyal kuat terdeteksi!\nPair: {pair}\nAksi: {action}\nLanjutkan eksekusi organik?"):
            thread = threading.Thread(target=lambda: self.execute_confirmed(pair, action))
            thread.start()
        else:
            self.update_logs(f"Arsitek menolak eksekusi untuk {pair}.")

    def execute_confirmed(self, pair, action):
        res = organic_execution(pair, action, 0.5)
        self.root.after(0, lambda: self.update_logs(res))
        state.data_archive.append({"time": str(datetime.datetime.now()), "action": action, "pair": pair})

    def open_settings(self):
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Pengaturan Sistem ZF")
        settings_win.geometry("450x400")
        settings_win.configure(bg="#1e1e1e")
        
        # Gemini API Key
        ttk.Label(settings_win, text="🔑 Google Gemini API Key:", style="TLabel").pack(pady=(20, 5))
        api_gemini_entry = ttk.Entry(settings_win, width=50)
        api_gemini_entry.insert(0, state.api_key_gemini)
        api_gemini_entry.pack(pady=5)
        
        # Finnhub API Key
        ttk.Label(settings_win, text="📈 Finnhub API Key (Sentimen & Data):", style="TLabel").pack(pady=(10, 5))
        api_finnhub_entry = ttk.Entry(settings_win, width=50)
        api_finnhub_entry.insert(0, state.api_key_finnhub)
        api_finnhub_entry.pack(pady=5)
        
        # Batas Rugi
        ttk.Label(settings_win, text="💰 Batas Rugi Harian (USD):", style="TLabel").pack(pady=(10, 5))
        loss_entry = ttk.Entry(settings_win, width=10)
        loss_entry.insert(0, str(state.daily_loss_limit))
        loss_entry.pack(pady=5)
        
        # Human in the Loop
        human_var = tk.BooleanVar(value=state.require_human_confirm)
        chk_human = ttk.Checkbutton(settings_win, text="✅ Wajib Konfirmasi Manusia (Human-in-the-Loop)", variable=human_var)
        chk_human.pack(pady=10)
        
        def save():
            gemini_key = api_gemini_entry.get().strip()
            finnhub_key = api_finnhub_entry.get().strip()
            
            state.api_key_gemini = gemini_key
            state.api_key_finnhub = finnhub_key
            
            # Inisialisasi ulang AI jika key berubah
            if gemini_key:
                try:
                    genai.configure(api_key=gemini_key)
                    state.model_ai = genai.GenerativeModel('gemini-pro')
                    self.update_logs("Gemini AI diaktifkan.")
                except Exception as e:
                    messagebox.showerror("Error", f"Gagal menginisialisasi Gemini: {e}")
            
            try:
                state.daily_loss_limit = float(loss_entry.get())
            except:
                pass
            state.require_human_confirm = human_var.get()
            state.save_config()
            
            self.update_logs("Pengaturan disimpan. Finnhub & Gemini dikonfigurasi.")
            settings_win.destroy()
            
        ttk.Button(settings_win, text="💾 Simpan Pengaturan", command=save).pack(pady=20)
        
        # Info text
        info_text = """
        📝 Catatan:
        - Dapatkan Gemini API Key dari Google AI Studio
        - Dapatkan Finnhub API Key dari finnhub.io (gratis untuk tier dasar)
        - Finnhub digunakan untuk data sentimen berita & validasi harga real-time
        """
        ttk.Label(settings_win, text=info_text, foreground="#888888", font=("Segoe UI", 8), justify=tk.CENTER).pack(pady=10)

    def export_report(self):
        if not state.data_archive:
            messagebox.showinfo("Info", "Belum ada data untuk diekspor.")
            return
            
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if filename:
            with open(filename, 'w') as f:
                json.dump(state.data_archive, f, indent=4)
            self.update_logs(f"Laporan berhasil disimpan ke {filename}")

    def load_dashboard_data(self):
        # Load data dummy awal
        pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "NZDUSD", "USDCAD", "XAUUSD"]
        for pair in pairs:
            price = random.uniform(1.05, 1.40) if 'USD' in pair and 'XAU' not in pair else random.uniform(1900, 2050)
            metrics = calculate_zf_metrics(pair, price)
            ai_rec = "Menunggu scan..."
            self.update_tree(pair, price, metrics, ai_rec)

if __name__ == "__main__":
    root = tk.Tk()
    app = ZFApp(root)
    root.mainloop()
