"""
GUI Module - Antarmuka Pengguna Buku Besar Forex ZF
Menggunakan CustomTkinter untuk tampilan modern
"""

import customtkinter as ctk
from tkinter import ttk, messagebox
from typing import Callable, Optional
import threading

class MainApp(ctk.CTk):
    """Aplikasi GUI Utama"""
    
    def __init__(self, zf_core):
        super().__init__()
        
        self.zf_core = zf_core
        self.title("Buku Besar Forex ZF V16.4-OMNI-WARROOM")
        self.geometry("1400x900")
        
        # Configure theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main layout
        self._create_menu()
        self._create_main_frame()
        
        # Start auto-refresh
        self._refresh_data()
    
    def _create_menu(self):
        """Buat menu bar"""
        menubar = ctk.CTkFrame(self, height=50)
        menubar.pack(fill="x", padx=10, pady=5)
        
        # Title
        title_label = ctk.CTkLabel(
            menubar, 
            text="📘 BUKU BESAR FOREX ZF", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(side="left", padx=20)
        
        # Status indicator
        self.status_label = ctk.CTkLabel(
            menubar,
            text="● Simulation Mode",
            text_color="yellow"
        )
        self.status_label.pack(side="right", padx=20)
    
    def _create_main_frame(self):
        """Buat frame utama dengan tabs"""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create tabview
        self.tabview = ctk.CTkTabview(main_frame)
        self.tabview.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Add tabs
        self.tab_dashboard = self.tabview.add("Dashboard")
        self.tab_predictions = self.tabview.add("Prediksi AI")
        self.tab_chart = self.tabview.add("Grafik TradingView")
        self.tab_settings = self.tabview.add("Pengaturan")
        self.tab_monitor = self.tabview.add("System Monitor")
        
        # Build each tab
        self._build_dashboard()
        self._build_predictions()
        self._build_chart()
        self._build_settings()
        self._build_monitor()
    
    def _build_dashboard(self):
        """Build dashboard tab"""
        # Header
        header = ctk.CTkLabel(
            self.tab_dashboard,
            text="🎛️ Dashboard War Room",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header.pack(pady=10)
        
        # Control buttons frame
        btn_frame = ctk.CTkFrame(self.tab_dashboard)
        btn_frame.pack(pady=10)
        
        self.btn_scan = ctk.CTkButton(
            btn_frame,
            text="🔍 Scan Market",
            command=self._run_scan,
            width=150
        )
        self.btn_scan.pack(side="left", padx=5)
        
        self.btn_trade = ctk.CTkButton(
            btn_frame,
            text="⚡ Auto Trading",
            command=self._toggle_trading,
            width=150
        )
        self.btn_trade.pack(side="left", padx=5)
        
        self.btn_stop = ctk.CTkButton(
            btn_frame,
            text="🛑 Stop All",
            fg_color="red",
            command=self._stop_all,
            width=150
        )
        self.btn_stop.pack(side="left", padx=5)
        
        # Stats frame
        stats_frame = ctk.CTkFrame(self.tab_dashboard)
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        self.lbl_zf_score = ctk.CTkLabel(stats_frame, text="Avg ZF-Score: 0.00")
        self.lbl_zf_score.pack(side="left", padx=20, pady=10)
        
        self.lbl_signals = ctk.CTkLabel(stats_frame, text="Signals Today: 0")
        self.lbl_signals.pack(side="left", padx=20, pady=10)
        
        self.lbl_pnl = ctk.CTkLabel(stats_frame, text="P&L: $0.00")
        self.lbl_pnl.pack(side="left", padx=20, pady=10)
        
        # Log console
        log_frame = ctk.CTkFrame(self.tab_dashboard)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(log_frame, text="📜 Activity Log").pack(anchor="w", padx=5, pady=5)
        
        self.log_text = ctk.CTkTextbox(log_frame, state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _build_predictions(self):
        """Build predictions tab"""
        header = ctk.CTkLabel(
            self.tab_predictions,
            text="🤖 Prediksi AI (Gemini + Finnhub)",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header.pack(pady=10)
        
        # Refresh button
        btn_refresh = ctk.CTkButton(
            self.tab_predictions,
            text="🔄 Regenerate Predictions",
            command=self._refresh_predictions
        )
        btn_refresh.pack(pady=5)
        
        # Tables frame
        tables_frame = ctk.CTkFrame(self.tab_predictions)
        tables_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Bullish predictions
        bullish_frame = ctk.CTkFrame(tables_frame)
        bullish_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(
            bullish_frame,
            text="📈 PREDIKSI NAIK (10 Hari)",
            font=ctk.CTkFont(weight="bold"),
            text_color="green"
        ).pack(pady=5)
        
        columns = ("Pair", "Price", "Drift%", "ZF-Score", "Confidence", "Target")
        self.tree_bullish = ttk.Treeview(bullish_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree_bullish.heading(col, text=col)
            self.tree_bullish.column(col, width=100)
        self.tree_bullish.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Bearish predictions
        bearish_frame = ctk.CTkFrame(tables_frame)
        bearish_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(
            bearish_frame,
            text="📉 PREDIKSI TURUN (10 Hari)",
            font=ctk.CTkFont(weight="bold"),
            text_color="red"
        ).pack(pady=5)
        
        self.tree_bearish = ttk.Treeview(bearish_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree_bearish.heading(col, text=col)
            self.tree_bearish.column(col, width=100)
        self.tree_bearish.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _build_chart(self):
        """Build chart tab with TradingView widget"""
        header = ctk.CTkLabel(
            self.tab_chart,
            text="📊 Grafik TradingView Custom",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header.pack(pady=10)
        
        # Pair selector
        pair_frame = ctk.CTkFrame(self.tab_chart)
        pair_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(pair_frame, text="Select Pair:").pack(side="left", padx=5)
        
        self.pair_var = ctk.StringVar(value="EURUSD")
        pairs = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD"]
        pair_combo = ctk.CTkComboBox(pair_frame, values=pairs, variable=self.pair_var)
        pair_combo.pack(side="left", padx=5)
        
        pair_combo.configure(command=lambda _: self._update_chart())
        
        # Chart placeholder (akan diimplementasikan dengan iframe atau library plotting)
        chart_frame = ctk.CTkFrame(self.tab_chart)
        chart_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.chart_label = ctk.CTkLabel(
            chart_frame,
            text="TradingView Chart Widget\n(Integrasi iframe TradingView)",
            font=ctk.CTkFont(size=16)
        )
        self.chart_label.pack(expand=True)
    
    def _build_settings(self):
        """Build settings tab"""
        header = ctk.CTkLabel(
            self.tab_settings,
            text="⚙️ Pengaturan",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header.pack(pady=10)
        
        # API Keys section
        api_frame = ctk.CTkLabelFrame(self.tab_settings, text="API Keys")
        api_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(api_frame, text="Gemini API Key:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.entry_gemini = ctk.CTkEntry(api_frame, width=400, show="*")
        self.entry_gemini.grid(row=0, column=1, padx=10, pady=5)
        
        ctk.CTkLabel(api_frame, text="Finnhub API Key:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.entry_finnhub = ctk.CTkEntry(api_frame, width=400, show="*")
        self.entry_finnhub.grid(row=1, column=1, padx=10, pady=5)
        
        ctk.CTkLabel(api_frame, text="Telegram Bot Token:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.entry_telegram = ctk.CTkEntry(api_frame, width=400, show="*")
        self.entry_telegram.grid(row=2, column=1, padx=10, pady=5)
        
        # Trading settings
        trade_frame = ctk.CTkLabelFrame(self.tab_settings, text="Trading Settings")
        trade_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(trade_frame, text="Default Lot Size:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.entry_lot = ctk.CTkEntry(trade_frame, width=100)
        self.entry_lot.insert(0, "0.01")
        self.entry_lot.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(trade_frame, text="Max Daily Loss %:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.entry_max_loss = ctk.CTkEntry(trade_frame, width=100)
        self.entry_max_loss.insert(0, "2.0")
        self.entry_max_loss.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Save button
        btn_save = ctk.CTkButton(
            self.tab_settings,
            text="💾 Save Settings",
            command=self._save_settings
        )
        btn_save.pack(pady=20)
    
    def _build_monitor(self):
        """Build system monitor tab"""
        header = ctk.CTkLabel(
            self.tab_monitor,
            text="🖥️ System Health Monitor",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header.pack(pady=10)
        
        # Metrics frame
        metrics_frame = ctk.CTkFrame(self.tab_monitor)
        metrics_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.lbl_cpu = ctk.CTkLabel(metrics_frame, text="CPU Usage: 0%")
        self.lbl_cpu.pack(pady=5)
        
        self.lbl_memory = ctk.CTkLabel(metrics_frame, text="Memory Usage: 0%")
        self.lbl_memory.pack(pady=5)
        
        self.lbl_mt5 = ctk.CTkLabel(metrics_frame, text="MT5 Connected: No")
        self.lbl_mt5.pack(pady=5)
        
        self.lbl_uptime = ctk.CTkLabel(metrics_frame, text="Uptime: 00:00:00")
        self.lbl_uptime.pack(pady=5)
        
        self.lbl_health = ctk.CTkLabel(metrics_frame, text="Health Status: HEALTHY")
        self.lbl_health.pack(pady=5)
    
    def _log_message(self, message: str):
        """Add message to log"""
        self.log_text.configure(state="normal")
        timestamp = threading.current_thread().name
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
    
    def _run_scan(self):
        """Run market scan"""
        self._log_message("Starting market scan...")
        # Implementasi scan akan dipanggil dari zf_core
    
    def _toggle_trading(self):
        """Toggle auto trading"""
        self._log_message("Auto trading toggled")
    
    def _stop_all(self):
        """Stop all operations"""
        self._log_message("Stopping all operations...")
        if self.zf_core:
            self.zf_core.shutdown()
    
    def _refresh_predictions(self):
        """Refresh predictions table"""
        # Clear existing
        for item in self.tree_bullish.get_children():
            self.tree_bullish.delete(item)
        for item in self.tree_bearish.get_children():
            self.tree_bearish.delete(item)
        
        # Add sample data (akan diganti dengan data real dari zf_core)
        bullish_data = [
            ("EURUSD", "1.0850", "2.5", "0.75", "85%", "1.0920"),
            ("GBPUSD", "1.2650", "3.1", "0.82", "90%", "1.2780"),
        ]
        
        bearish_data = [
            ("USDJPY", "157.50", "2.8", "0.78", "88%", "155.20"),
            ("USDCHF", "0.8950", "2.2", "0.71", "82%", "0.8850"),
        ]
        
        for row in bullish_data:
            self.tree_bullish.insert("", "end", values=row)
        
        for row in bearish_data:
            self.tree_bearish.insert("", "end", values=row)
    
    def _update_chart(self):
        """Update chart for selected pair"""
        pair = self.pair_var.get()
        self._log_message(f"Updating chart for {pair}")
    
    def _save_settings(self):
        """Save settings"""
        gemini_key = self.entry_gemini.get()
        finnhub_key = self.entry_finnhub.get()
        telegram_token = self.entry_telegram.get()
        
        if self.zf_core:
            self.zf_core.config.GEMINI_API_KEY = gemini_key
            self.zf_core.config.FINNHUB_API_KEY = finnhub_key
            self.zf_core.config.TELEGRAM_BOT_TOKEN = telegram_token
            self.zf_core.config.DEFAULT_LOT_SIZE = float(self.entry_lot.get())
            self.zf_core.config.MAX_DAILY_LOSS_PERCENT = float(self.entry_max_loss.get())
            
            # Update AI engine
            self.zf_core.ai_engine.update_api_key(gemini_key)
        
        self._log_message("Settings saved successfully")
        messagebox.showinfo("Success", "Settings saved!")
    
    def _refresh_data(self):
        """Periodic data refresh"""
        if self.zf_core and self.zf_core.is_running:
            metrics = self.zf_core.system_monitor.get_metrics()
            
            # Update monitor tab
            self.lbl_cpu.configure(text=f"CPU Usage: {metrics['cpu_usage']}%")
            self.lbl_memory.configure(text=f"Memory Usage: {metrics['memory_usage']}%")
            self.lbl_mt5.configure(text=f"MT5 Connected: {'Yes' if metrics['mt5_connected'] else 'No'}")
            self.lbl_uptime.configure(text=f"Uptime: {self.zf_core.system_monitor.format_uptime()}")
            self.lbl_health.configure(text=f"Health Status: {self.zf_core.system_monitor.get_health_status()}")
        
        # Schedule next refresh
        self.after(5000, self._refresh_data)
