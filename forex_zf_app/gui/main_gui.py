"""
Main GUI for Buku Besar Forex ZF V16.4-OMNI-WARROOM
Built with CustomTkinter for modern UI
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Set Theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MainApp(ctk.CTk):
    def __init__(self, zf_core):
        super().__init__()
        
        self.zf_core = zf_core
        self.title("Buku Besar Forex ZF - V16.4 OMNI WARROOM")
        self.geometry("1200x800")
        
        # Configure Grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._create_main_frame()
        
    def _create_main_frame(self):
        # Main Tab View
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Add Tabs
        self.tab_dashboard = self.tab_view.add("Dashboard")
        self.tab_predictions = self.tab_view.add("Predictions")
        self.tab_warroom = self.tab_view.add("War Room")
        self.tab_settings = self.tab_view.add("Settings")
        self.tab_journal = self.tab_view.add("Journal")
        
        # Build Content
        self._build_dashboard()
        self._build_predictions()
        self._build_warroom()
        self._build_settings()
        self._build_journal()
        
    def _build_dashboard(self):
        # Header
        header_frame = ctk.CTkFrame(self.tab_dashboard)
        header_frame.pack(fill="x", padx=10, pady=5)
        
        title_label = ctk.CTkLabel(header_frame, text="MARKET DASHBOARD", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(side="left", padx=10)
        
        self.scan_btn = ctk.CTkButton(header_frame, text="SCAN MARKET NOW", command=self._start_scan, fg_color="green")
        self.scan_btn.pack(side="right", padx=10)
        
        self.status_label = ctk.CTkLabel(header_frame, text="Status: Idle", text_color="gray")
        self.status_label.pack(side="right", padx=10)
        
        # Market Info Frame (Using standard LabelFrame for compatibility)
        info_frame = tk.LabelFrame(self.tab_dashboard, text="Market Overview", bg='#2b2b2b', fg='#ffffff')
        info_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Simple Text Display for now
        self.info_text = tk.Text(info_frame, bg='#1a1a1a', fg='#00ff00', font=("Consolas", 12))
        self.info_text.pack(fill="both", expand=True, padx=5, pady=5)
        
    def _build_predictions(self):
        # Split into Up and Down
        paned = ttk.PanedWindow(self.tab_predictions, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True, padx=10, pady=10)
        
        # UP Frame
        up_frame = tk.LabelFrame(paned, text="📈 PREDIKSI NAIK (10 DAYS)", bg='#2b2b2b', fg='#00ff00')
        paned.add(up_frame, weight=1)
        
        columns = ("Pair", "Price", "Target", "Score", "Reason")
        self.up_tree = ttk.Treeview(up_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.up_tree.heading(col, text=col)
            self.up_tree.column(col, width=100)
            
        scrollbar_up = ttk.Scrollbar(up_frame, orient=tk.VERTICAL, command=self.up_tree.yview)
        self.up_tree.configure(yscroll=scrollbar_up.set)
        
        self.up_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar_up.pack(side="right", fill="y", pady=5)
        
        # DOWN Frame
        down_frame = tk.LabelFrame(paned, text="📉 PREDIKSI TURUN (10 DAYS)", bg='#2b2b2b', fg='#ff0000')
        paned.add(down_frame, weight=1)
        
        self.down_tree = ttk.Treeview(down_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.down_tree.heading(col, text=col)
            self.down_tree.column(col, width=100)
            
        scrollbar_down = ttk.Scrollbar(down_frame, orient=tk.VERTICAL, command=self.down_tree.yview)
        self.down_tree.configure(yscroll=scrollbar_down.set)
        
        self.down_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar_down.pack(side="right", fill="y", pady=5)
        
    def _build_warroom(self):
        # War Room: Visualizations & Controls
        control_frame = ctk.CTkFrame(self.tab_warroom)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(control_frame, text="WAR ROOM CONTROL", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
        
        self.auto_toggle = ctk.CTkSwitch(control_frame, text="Auto Trading", command=self._toggle_auto)
        self.auto_toggle.pack(side="right", padx=10)
        
        # Placeholder for Charts/Visuals
        visual_frame = tk.LabelFrame(self.tab_warroom, text="Manifold Visualization (TradingView Integration)", bg='#2b2b2b', fg='#ffffff')
        visual_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.visual_label = ctk.CTkLabel(visual_frame, text="Chart Area - Integration Pending\nSelect a pair from predictions to load chart.")
        self.visual_label.place(relx=0.5, rely=0.5, anchor="center")
        
    def _build_settings(self):
        scroll_frame = ctk.CTkScrollableFrame(self.tab_settings)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # API Keys Section
        api_frame = tk.LabelFrame(scroll_frame, text="API Keys Configuration", bg='#2b2b2b', fg='#ffffff')
        api_frame.pack(fill="x", padx=10, pady=10)
        
        # Gemini
        ctk.CTkLabel(api_frame, text="Google Gemini API Key:", bg='#2b2b2b', fg='white').grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.gemini_entry = ctk.CTkEntry(api_frame, width=400, show="*")
        self.gemini_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Finnhub
        ctk.CTkLabel(api_frame, text="Finnhub API Key:", bg='#2b2b2b', fg='white').grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.finnhub_entry = ctk.CTkEntry(api_frame, width=400, show="*")
        self.finnhub_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Telegram
        ctk.CTkLabel(api_frame, text="Telegram Bot Token:", bg='#2b2b2b', fg='white').grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.tg_token_entry = ctk.CTkEntry(api_frame, width=400, show="*")
        self.tg_token_entry.grid(row=2, column=1, padx=10, pady=5)
        
        ctk.CTkLabel(api_frame, text="Telegram Chat ID:", bg='#2b2b2b', fg='white').grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.tg_chat_entry = ctk.CTkEntry(api_frame, width=400)
        self.tg_chat_entry.grid(row=3, column=1, padx=10, pady=5)
        
        detect_btn = ctk.CTkButton(api_frame, text="Auto-Detect Chat ID", command=self._detect_chat_id, width=150)
        detect_btn.grid(row=4, column=1, sticky="e", padx=10, pady=10)
        
        # Risk Settings
        risk_frame = tk.LabelFrame(scroll_frame, text="Risk Management", bg='#2b2b2b', fg='#ffffff')
        risk_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(risk_frame, text="Risk Per Trade (%):", bg='#2b2b2b', fg='white').grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.risk_entry = ctk.CTkEntry(risk_frame, width=100)
        self.risk_entry.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        ctk.CTkLabel(risk_frame, text="Max Daily Loss (%):", bg='#2b2b2b', fg='white').grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.max_loss_entry = ctk.CTkEntry(risk_frame, width=100)
        self.max_loss_entry.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        # Save Button
        save_btn = ctk.CTkButton(scroll_frame, text="SAVE CONFIGURATION", command=self._save_settings, height=40, fg_color="green")
        save_btn.pack(pady=20)
        
        # Load existing config
        self._load_settings_to_ui()
        
    def _build_journal(self):
        journal_frame = tk.LabelFrame(self.tab_journal, text="Trade History (Archival Vault)", bg='#2b2b2b', fg='#ffffff')
        journal_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("Time", "Symbol", "Action", "Volume", "SL", "TP", "Status")
        self.journal_tree = ttk.Treeview(journal_frame, columns=columns, show="headings", height=20)
        for col in columns:
            self.journal_tree.heading(col, text=col)
            self.journal_tree.column(col, width=100)
            
        scrollbar = ttk.Scrollbar(journal_frame, orient=tk.VERTICAL, command=self.journal_tree.yview)
        self.journal_tree.configure(yscroll=scrollbar.set)
        
        self.journal_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
        
        # Refresh Button
        refresh_btn = ctk.CTkButton(self.tab_journal, text="Refresh Journal", command=self._refresh_journal)
        refresh_btn.pack(pady=10)
        
        self._refresh_journal()
        
    # --- Actions & Logic ---
    
    def _start_scan(self):
        self.scan_btn.configure(state="disabled", text="Scanning...")
        self.status_label.configure(text="Status: Scanning...", text_color="orange")
        
        # Run in thread to avoid freezing UI
        thread = threading.Thread(target=self._run_scan)
        thread.daemon = True
        thread.start()
        
    def _run_scan(self):
        try:
            results = self.zf_core.scan_market(callback=self._update_predictions_ui)
            if not results:
                raise Exception("Scan returned no results")
        except Exception as e:
            logger.error(f"Scan thread error: {e}")
            self.after(0, lambda: messagebox.showerror("Scan Error", str(e)))
        finally:
            self.after(0, self._reset_scan_btn)
            
    def _reset_scan_btn(self):
        self.scan_btn.configure(state="normal", text="SCAN MARKET NOW")
        self.status_label.configure(text="Status: Idle", text_color="gray")
        
    def _update_predictions_ui(self, predictions):
        """Update Treeviews with prediction data"""
        # Clear existing
        for item in self.up_tree.get_children():
            self.up_tree.delete(item)
        for item in self.down_tree.get_children():
            self.down_tree.delete(item)
            
        # Populate UP
        if "up" in predictions:
            for p in predictions["up"]:
                self.up_tree.insert("", "end", values=(
                    p.get("pair", "N/A"),
                    f"{p.get('current', 0):.5f}",
                    f"{p.get('target', 0):.5f}",
                    f"{p.get('score', 0):.2f}",
                    p.get("reason", "")
                ))
                
        # Populate DOWN
        if "down" in predictions:
            for p in predictions["down"]:
                self.down_tree.insert("", "end", values=(
                    p.get("pair", "N/A"),
                    f"{p.get('current', 0):.5f}",
                    f"{p.get('target', 0):.5f}",
                    f"{p.get('score', 0):.2f}",
                    p.get("reason", "")
                ))
                
        # Update Info Text
        self.info_text.delete("1.0", "end")
        self.info_text.insert("end", f"Scan Completed: {datetime.now()}\n")
        self.info_text.insert("end", f"Pairs Analyzed: {len(self.zf_core.active_pairs)}\n")
        self.info_text.insert("end", f"Bullish Signals: {len(predictions.get('up', []))}\n")
        self.info_text.insert("end", f"Bearish Signals: {len(predictions.get('down', []))}\n")
        
    def _load_settings_to_ui(self):
        cfg = self.zf_core.get_config()
        self.gemini_entry.insert(0, cfg.get("gemini_api_key", ""))
        self.finnhub_entry.insert(0, cfg.get("finnhub_api_key", ""))
        self.tg_token_entry.insert(0, cfg.get("telegram_token", ""))
        self.tg_chat_entry.insert(0, cfg.get("telegram_chat_id", ""))
        self.risk_entry.insert(0, str(cfg.get("risk_per_trade", 1.0)))
        self.max_loss_entry.insert(0, str(cfg.get("max_daily_loss", 5.0)))
        
    def _save_settings(self):
        new_config = {
            "gemini_api_key": self.gemini_entry.get(),
            "finnhub_api_key": self.finnhub_entry.get(),
            "telegram_token": self.tg_token_entry.get(),
            "telegram_chat_id": self.tg_chat_entry.get(),
            "risk_per_trade": float(self.risk_entry.get() or 1.0),
            "max_daily_loss": float(self.max_loss_entry.get() or 5.0)
        }
        self.zf_core.save_config(new_config)
        messagebox.showinfo("Success", "Configuration saved successfully!")
        
    def _detect_chat_id(self):
        token = self.tg_token_entry.get().strip()
        if not token:
            messagebox.showwarning("Warning", "Please enter Bot Token first")
            return
            
        # Simple API call to get updates and extract chat_id
        try:
            import requests
            url = f"https://api.telegram.org/bot{token}/getUpdates"
            response = requests.get(url)
            data = response.json()
            
            if data.get("ok"):
                results = data.get("result", [])
                if results:
                    # Get chat_id from last message
                    chat_id = results[-1]["message"]["chat"]["id"]
                    self.tg_chat_entry.delete(0, "end")
                    self.tg_chat_entry.insert(0, str(chat_id))
                    messagebox.showinfo("Success", f"Chat ID detected: {chat_id}")
                else:
                    messagebox.showwarning("Info", "No messages found. Send /start to your bot first.")
            else:
                messagebox.showerror("Error", "Invalid Token or API Error")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def _toggle_auto(self):
        state = "ON" if self.auto_toggle.get() else "OFF"
        logger.info(f"Auto Trading switched {state}")
        
    def _refresh_journal(self):
        # Clear
        for item in self.journal_tree.get_children():
            self.journal_tree.delete(item)
            
        # Load from storage
        history = self.zf_core.storage_engine.get_history()
        for trade in reversed(history): # Newest first
            self.journal_tree.insert("", "end", values=(
                trade.get("time", "")[:19], # Cut microseconds
                trade.get("symbol", ""),
                trade.get("action", ""),
                trade.get("volume", ""),
                trade.get("sl", ""),
                trade.get("tp", ""),
                trade.get("status", "")
            ))

def run_gui(zf_core):
    app = MainApp(zf_core)
    app.mainloop()
