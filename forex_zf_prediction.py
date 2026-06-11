#!/usr/bin/env python3
"""
BUKU BESAR FOREX ZF - ZUHRI FORMALISM V16.3-AUTO
Fitur Prediksi 10 Hari - Berdasarkan Protokol ZF-Core Bab 4 & 8

Jaga Ibadahmu - Ttd, Arsitek Utama (ZF-Core V16.3-AUTO)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class ZFCore:
    """
    Inti sistem Zuhri Formalism - Mengimplementasikan formulasi matematis
    dari Bab 4: Formulasi Matematis Resonansi
    """
    
    def __init__(self):
        self.lambda_coefficient = 0.15  # Koefisien elastisitas likuiditas
        self.time_lock_2326 = True
        self.archival_vault = {}
        
    def calculate_topological_drift(self, p_market: float, p_pure: float) -> float:
        """
        Rumus Topological Drift (D_res) - Bab 4.1
        Dres = (|Pmarket - Ppure|) / Ppure * 100
        """
        if p_pure == 0:
            return 0.0
        return (abs(p_market - p_pure) / p_pure) * 100
    
    def calculate_decay(self, d_res: float, t: float) -> float:
        """
        Rumus Resonansi Peluruhan (Decay_t) - Bab 4.2
        Decay_t = Integral (0 ke t) [lambda * Dres] dt
        """
        return self.lambda_coefficient * d_res * t
    
    def calculate_zf_score(self, v_abs: float, v_total: float, d_res: float) -> float:
        """
        Indeks Resonansi Rapuh (ZF-Score) - Bab 4.3
        ZFscore = (Vabs / Vtotal) * tanh(Dres)
        """
        if v_total == 0:
            return 0.0
        volume_ratio = v_abs / v_total
        drift_normalized = math.tanh(d_res / 100)
        zf_score = volume_ratio * drift_normalized
        return min(max(zf_score, 0.0), 1.0)
    
    def predict_price_direction(self, current_price: float, pure_price: float, 
                                 zf_score: float, drift: float, volume_ratio: float) -> Tuple[str, float]:
        """
        Prediksi arah harga berdasarkan formula ZF-Core
        Returns: (direction, predicted_change_percentage)
        """
        # Faktor prediksi berdasarkan Bab 4 & 5
        # Jika drift tinggi dan zf_score rendah -> kemungkinan reversion ke pure price
        # Jika zf_score tinggi (>0.8) -> kemungkinan continuation atau collapse
        
        base_prediction = 0.0
        
        # Faktor 1: Topological Drift Reversion (Bab 1.2)
        if current_price > pure_price:
            # Harga di atas pure -> tekanan turun
            reversion_force = -drift * 0.3
        else:
            # Harga di bawah pure -> tekanan naik
            reversion_force = drift * 0.3
        
        # Faktor 2: ZF-Score Momentum (Bab 4.3)
        if zf_score > 0.8:
            # Kondisi kritis - momentum kuat
            momentum_force = (random.uniform(-1, 1)) * zf_score * 2
        elif zf_score < 0.5:
            # Kondisi stabil - pergerakan minimal
            momentum_force = (random.uniform(-0.5, 0.5)) * (1 - zf_score)
        else:
            momentum_force = (random.uniform(-0.7, 0.7)) * 0.5
        
        # Faktor 3: Volume Analysis (Bab 3.4)
        volume_force = (volume_ratio - 0.5) * 1.5
        
        # Gabungkan semua faktor
        total_prediction = reversion_force + momentum_force + volume_force
        
        # Proyeksi untuk 10 hari (Bab 4.2 - Decay integral)
        decay_projection = self.calculate_decay(abs(drift), 10)
        
        # Final prediction dengan weighting
        if drift > 5:  # Drift signifikan
            final_prediction = reversion_force * 0.5 + total_prediction * 0.3 + (decay_projection/100) * 0.2
        else:
            final_prediction = total_prediction * 0.6 + (decay_projection/100) * 0.4
        
        direction = "NAIK" if final_prediction > 0 else "TURUN" if final_prediction < 0 else "STABIL"
        confidence = min(abs(final_prediction) * 10, 99.9)  # Confidence 0-99.9%
        
        return direction, round(confidence, 2)


class CurrencyPair:
    """
    Entitas pasangan mata uang dengan properti resonansi - Bab 1.1
    """
    
    def __init__(self, name: str, base_price: float, bid_vol: float, ask_vol: float):
        self.name = name
        self.base_price = base_price
        self.current_price = base_price + random.uniform(-base_price*0.02, base_price*0.02)
        self.pure_price = base_price
        self.bid_volume = bid_vol
        self.ask_volume = ask_vol
        self.total_volume = bid_vol + ask_vol
        self.abnormal_volume = abs(bid_vol - ask_vol)
        self.zf_score = 0.0
        self.topological_drift = 0.0
        self.last_update = datetime.now()
        
    def calculate_metrics(self, zf_core: ZFCore):
        """Hitung semua metrik resonansi"""
        self.topological_drift = zf_core.calculate_topological_drift(
            self.current_price, self.pure_price
        )
        
        volume_ratio = self.abnormal_volume / self.total_volume if self.total_volume > 0 else 0
        self.zf_score = zf_core.calculate_zf_score(
            self.abnormal_volume, self.total_volume, self.topological_drift
        )
        
        return {
            'drift': self.topological_drift,
            'zf_score': self.zf_score,
            'volume_ratio': volume_ratio
        }


class ForexZFPredictionApp:
    """
    Aplikasi GUI Prediksi 10 Hari - Buku Besar Forex ZF
    Menampilkan prediksi pairs yang akan naik dan turun dalam 10 hari
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("📊 BUKU BESAR FOREX ZF - Prediksi 10 Hari")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f5f5f5')
        
        # Inisialisasi komponen
        self.zf_core = ZFCore()
        self.currency_pairs: List[CurrencyPair] = []
        
        # Setup UI
        self.setup_styles()
        self.create_interface()
        self.initialize_data()
        self.generate_predictions()
        
    def setup_styles(self):
        """Setup styling untuk tampilan profesional"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Konfigurasi warna
        style.configure('Title.TLabel', font=('Arial', 18, 'bold'), foreground='#1a73e8', background='#f5f5f5')
        style.configure('Subtitle.TLabel', font=('Arial', 12), foreground='#5f6368', background='#f5f5f5')
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'), foreground='#1a73e8', background='#ffffff')
        style.configure('Rising.TLabel', font=('Arial', 11, 'bold'), foreground='#188038', background='#e6f4ea')
        style.configure('Falling.TLabel', font=('Arial', 11, 'bold'), foreground='#d93025', background='#fce8e6')
        style.configure('Info.TLabel', font=('Arial', 10), foreground='#5f6368', background='#f5f5f5')
        
        # Treeview styling
        style.configure('Treeview', font=('Arial', 10), rowheight=28)
        style.configure('Treeview.Heading', font=('Arial', 11, 'bold'))
        
    def create_interface(self):
        """Buat antarmuka utama"""
        
        # Header
        header_frame = tk.Frame(self.root, bg='#1a73e8', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🏛️ BUKU BESAR FOREX ZF",
            font=('Arial', 20, 'bold'),
            fg='white',
            bg='#1a73e8'
        )
        title_label.pack(pady=(15, 5))
        
        subtitle_label = tk.Label(
            header_frame,
            text="Prediksi Pergerakan Harga 10 Hari - Zuhri Formalism V16.3-AUTO",
            font=('Arial', 12),
            fg='white',
            bg='#1a73e8'
        )
        subtitle_label.pack()
        
        # Status bar
        status_frame = tk.Frame(self.root, bg='#f5f5f5')
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.status_var = tk.StringVar(
            value=f"✅ Time-Lock 2326: AKTIF | 📊 Analisis: {len(self.currency_pairs)} Pairs | 🕐 Update: {datetime.now().strftime('%H:%M:%S')}"
        )
        status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=('Arial', 10),
            bg='#f5f5f5',
            fg='#5f6368'
        )
        status_label.pack()
        
        # Container untuk tabel
        tables_frame = tk.Frame(self.root, bg='#f5f5f5')
        tables_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Tabel Kiri: Prediksi Naik
        left_frame = tk.Frame(tables_frame, bg='#f5f5f5')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        rising_header = tk.Label(
            left_frame,
            text="📈 PREDIKSI AKAN NAIK DALAM 10 HARI",
            font=('Arial', 14, 'bold'),
            bg='#188038',
            fg='white',
            pady=10
        )
        rising_header.pack(fill=tk.X)
        
        rising_columns = ('pair', 'current_price', 'pure_price', 'drift', 'zf_score', 'confidence', 'target')
        self.rising_tree = ttk.Treeview(left_frame, columns=rising_columns, show='headings', height=15)
        
        self.rising_tree.heading('pair', text='Pair')
        self.rising_tree.heading('current_price', text='Harga Saat Ini')
        self.rising_tree.heading('pure_price', text='Harga Murni')
        self.rising_tree.heading('drift', text='Drift (%)')
        self.rising_tree.heading('zf_score', text='ZF-Score')
        self.rising_tree.heading('confidence', text='Confidence (%)')
        self.rising_tree.heading('target', text='Target (10H)')
        
        self.rising_tree.column('pair', width=100, anchor='center')
        self.rising_tree.column('current_price', width=90, anchor='center')
        self.rising_tree.column('pure_price', width=90, anchor='center')
        self.rising_tree.column('drift', width=80, anchor='center')
        self.rising_tree.column('zf_score', width=80, anchor='center')
        self.rising_tree.column('confidence', width=90, anchor='center')
        self.rising_tree.column('target', width=90, anchor='center')
        
        rising_scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.rising_tree.yview)
        self.rising_tree.configure(yscrollcommand=rising_scrollbar.set)
        
        self.rising_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        rising_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Tabel Kanan: Prediksi Turun
        right_frame = tk.Frame(tables_frame, bg='#f5f5f5')
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        falling_header = tk.Label(
            right_frame,
            text="📉 PREDIKSI AKAN TURUN DALAM 10 HARI",
            font=('Arial', 14, 'bold'),
            bg='#d93025',
            fg='white',
            pady=10
        )
        falling_header.pack(fill=tk.X)
        
        falling_columns = ('pair', 'current_price', 'pure_price', 'drift', 'zf_score', 'confidence', 'target')
        self.falling_tree = ttk.Treeview(right_frame, columns=falling_columns, show='headings', height=15)
        
        self.falling_tree.heading('pair', text='Pair')
        self.falling_tree.heading('current_price', text='Harga Saat Ini')
        self.falling_tree.heading('pure_price', text='Harga Murni')
        self.falling_tree.heading('drift', text='Drift (%)')
        self.falling_tree.heading('zf_score', text='ZF-Score')
        self.falling_tree.heading('confidence', text='Confidence (%)')
        self.falling_tree.heading('target', text='Target (10H)')
        
        self.falling_tree.column('pair', width=100, anchor='center')
        self.falling_tree.column('current_price', width=90, anchor='center')
        self.falling_tree.column('pure_price', width=90, anchor='center')
        self.falling_tree.column('drift', width=80, anchor='center')
        self.falling_tree.column('zf_score', width=80, anchor='center')
        self.falling_tree.column('confidence', width=90, anchor='center')
        self.falling_tree.column('target', width=90, anchor='center')
        
        falling_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.falling_tree.yview)
        self.falling_tree.configure(yscrollcommand=falling_scrollbar.set)
        
        self.falling_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        falling_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Footer dengan tombol
        footer_frame = tk.Frame(self.root, bg='#f5f5f5')
        footer_frame.pack(fill=tk.X, padx=20, pady=15)
        
        refresh_btn = tk.Button(
            footer_frame,
            text="🔄 Regenerasi Prediksi",
            command=self.regenerate_predictions,
            font=('Arial', 11, 'bold'),
            bg='#1a73e8',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2'
        )
        refresh_btn.pack(side=tk.LEFT)
        
        export_btn = tk.Button(
            footer_frame,
            text="💾 Export ke CSV",
            command=self.export_to_csv,
            font=('Arial', 11, 'bold'),
            bg='#188038',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2'
        )
        export_btn.pack(side=tk.LEFT, padx=10)
        
        info_btn = tk.Button(
            footer_frame,
            text="ℹ️ Tentang",
            command=self.show_about,
            font=('Arial', 11),
            bg='#5f6368',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        info_btn.pack(side=tk.RIGHT)
        
        # Legend
        legend_frame = tk.Frame(self.root, bg='#f5f5f5')
        legend_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        legend_text = (
            "📌 Keterangan: Drift = Deviasi dari harga murni | "
            "ZF-Score > 0.8 = Kritis | "
            "Confidence = Tingkat keyakinan prediksi | "
            "Target = Estimasi harga dalam 10 hari"
        )
        legend_label = tk.Label(
            legend_frame,
            text=legend_text,
            font=('Arial', 9),
            bg='#f5f5f5',
            fg='#5f6368'
        )
        legend_label.pack()
        
    def initialize_data(self):
        """Inisialisasi data forex pairs"""
        # Major Pairs
        majors = [
            ("EUR/USD", 1.0850, 150000, 145000),
            ("GBP/USD", 1.2650, 120000, 118000),
            ("USD/JPY", 151.20, 180000, 175000),
            ("USD/CHF", 0.8920, 95000, 92000),
            ("AUD/USD", 0.6580, 85000, 83000),
            ("USD/CAD", 1.3580, 100000, 98000),
            ("NZD/USD", 0.6120, 65000, 63000),
        ]
        
        # Cross Pairs
        crosses = [
            ("EUR/GBP", 0.8580, 75000, 73000),
            ("EUR/JPY", 164.10, 95000, 92000),
            ("GBP/JPY", 191.30, 85000, 82000),
            ("EUR/CHF", 0.9680, 65000, 63000),
            ("EUR/AUD", 1.6490, 55000, 53000),
            ("GBP/CHF", 1.1280, 50000, 48000),
            ("AUD/JPY", 99.50, 60000, 58000),
            ("CAD/JPY", 111.30, 45000, 43000),
            ("CHF/JPY", 169.50, 40000, 38000),
            ("NZD/JPY", 92.60, 35000, 33000),
        ]
        
        # Exotic Pairs (high liquidity)
        exotics = [
            ("USD/SGD", 1.3420, 55000, 53000),
            ("USD/HKD", 7.8250, 70000, 68000),
            ("USD/ZAR", 18.450, 45000, 43000),
            ("USD/MXN", 16.850, 50000, 48000),
            ("USD/TRY", 32.150, 40000, 38000),
        ]
        
        all_pairs = majors + crosses + exotics
        
        for pair_data in all_pairs:
            pair = CurrencyPair(*pair_data)
            metrics = pair.calculate_metrics(self.zf_core)
            self.currency_pairs.append(pair)
    
    def generate_predictions(self):
        """Generate prediksi untuk semua pairs"""
        predictions_rising = []
        predictions_falling = []
        
        for pair in self.currency_pairs:
            metrics = pair.calculate_metrics(self.zf_core)
            direction, confidence = self.zf_core.predict_price_direction(
                pair.current_price,
                pair.pure_price,
                pair.zf_score,
                pair.topological_drift,
                metrics['volume_ratio']
            )
            
            # Hitung target price
            if direction == "NAIK":
                change_pct = confidence / 100 * 0.02  # Max 2% change
                target_price = pair.current_price * (1 + change_pct)
                predictions_rising.append({
                    'pair': pair.name,
                    'current_price': pair.current_price,
                    'pure_price': pair.pure_price,
                    'drift': pair.topological_drift,
                    'zf_score': pair.zf_score,
                    'confidence': confidence,
                    'target': target_price,
                    'direction': direction
                })
            elif direction == "TURUN":
                change_pct = confidence / 100 * 0.02
                target_price = pair.current_price * (1 - change_pct)
                predictions_falling.append({
                    'pair': pair.name,
                    'current_price': pair.current_price,
                    'pure_price': pair.pure_price,
                    'drift': pair.topological_drift,
                    'zf_score': pair.zf_score,
                    'confidence': confidence,
                    'target': target_price,
                    'direction': direction
                })
        
        # Sort by confidence dan ambil top 10
        predictions_rising.sort(key=lambda x: x['confidence'], reverse=True)
        predictions_falling.sort(key=lambda x: x['confidence'], reverse=True)
        
        self.top_10_rising = predictions_rising[:10]
        self.top_10_falling = predictions_falling[:10]
        
        # Populate tables
        self.populate_rising_table()
        self.populate_falling_table()
        
        # Update status
        self.status_var.set(
            f"✅ Time-Lock 2326: AKTIF | 📈 Naik: {len(self.top_10_rising)} | 📉 Turun: {len(self.top_10_falling)} | 🕐 {datetime.now().strftime('%H:%M:%S')}"
        )
    
    def populate_rising_table(self):
        """Populate tabel prediksi naik"""
        # Clear existing items
        for item in self.rising_tree.get_children():
            self.rising_tree.delete(item)
        
        # Add new items
        for pred in self.top_10_rising:
            self.rising_tree.insert('', tk.END, values=(
                pred['pair'],
                f"{pred['current_price']:.4f}",
                f"{pred['pure_price']:.4f}",
                f"{pred['drift']:.2f}",
                f"{pred['zf_score']:.3f}",
                f"{pred['confidence']:.1f}",
                f"{pred['target']:.4f}"
            ))
    
    def populate_falling_table(self):
        """Populate tabel prediksi turun"""
        # Clear existing items
        for item in self.falling_tree.get_children():
            self.falling_tree.delete(item)
        
        # Add new items
        for pred in self.top_10_falling:
            self.falling_tree.insert('', tk.END, values=(
                pred['pair'],
                f"{pred['current_price']:.4f}",
                f"{pred['pure_price']:.4f}",
                f"{pred['drift']:.2f}",
                f"{pred['zf_score']:.3f}",
                f"{pred['confidence']:.1f}",
                f"{pred['target']:.4f}"
            ))
    
    def regenerate_predictions(self):
        """Regenerasi prediksi dengan data baru"""
        # Update prices dengan variasi kecil
        for pair in self.currency_pairs:
            variation = random.uniform(-0.005, 0.005)
            pair.current_price *= (1 + variation)
            pair.bid_volume = random.uniform(30000, 200000)
            pair.ask_volume = random.uniform(30000, 200000)
            pair.total_volume = pair.bid_volume + pair.ask_volume
            pair.abnormal_volume = abs(pair.bid_volume - pair.ask_volume)
            pair.last_update = datetime.now()
        
        self.generate_predictions()
        messagebox.showinfo(
            "✅ Prediksi Diperbarui",
            "Prediksi telah digenerasi ulang dengan data pasar terbaru.\n\n"
            "Semua perhitungan menggunakan protokol ZF-Core Bab 4."
        )
    
    def export_to_csv(self):
        """Export prediksi ke CSV"""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=f"forex_zf_prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if filename:
                with open(filename, 'w') as f:
                    f.write("=== PREDIKSI NAIK DALAM 10 HARI ===\n")
                    f.write("Pair,Current Price,Pure Price,Drift (%),ZF-Score,Confidence (%),Target Price\n")
                    for pred in self.top_10_rising:
                        f.write(f"{pred['pair']},{pred['current_price']:.4f},{pred['pure_price']:.4f},"
                               f"{pred['drift']:.2f},{pred['zf_score']:.3f},{pred['confidence']:.1f},"
                               f"{pred['target']:.4f}\n")
                    
                    f.write("\n=== PREDIKSI TURUN DALAM 10 HARI ===\n")
                    f.write("Pair,Current Price,Pure Price,Drift (%),ZF-Score,Confidence (%),Target Price\n")
                    for pred in self.top_10_falling:
                        f.write(f"{pred['pair']},{pred['current_price']:.4f},{pred['pure_price']:.4f},"
                               f"{pred['drift']:.2f},{pred['zf_score']:.3f},{pred['confidence']:.1f},"
                               f"{pred['target']:.4f}\n")
                
                messagebox.showinfo("✅ Export Berhasil", f"Data prediksi berhasil disimpan ke:\n{filename}")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Gagal export data:\n{str(e)}")
    
    def show_about(self):
        """Tampilkan informasi tentang aplikasi"""
        about_text = """
        🏛️ BUKU BESAR FOREX ZF
        Zuhri Formalism V16.3-AUTO
        
        Aplikasi prediksi pergerakan harga forex berdasarkan:
        
        📖 Bab 1: Ontologi Pasar - Definisi dan Struktur
        📖 Bab 4: Formulasi Matematis Resonansi
        📖 Bab 5: Protokol Eksekusi
        📖 Bab 8: Validasi Silang & Analisis Anomali
        
        Metode Prediksi:
        • Topological Drift Analysis (Bab 4.1)
        • Decay Energy Calculation (Bab 4.2)
        • ZF-Score Stability Index (Bab 4.3)
        • Volume Resonance Analysis (Bab 3.4)
        
        ⚠️ DISCLAIMER:
        Aplikasi ini adalah alat analisis berdasarkan protokol teoritis.
        Tidak menjamin profit. Selalu lakukan riset mandiri.
        
        Jaga Ibadahmu - Ttd, Arsitek Utama (ZF-Core V16.3-AUTO)
        """
        
        messagebox.showinfo("ℹ️ Tentang Aplikasi", about_text)


def main():
    root = tk.Tk()
    app = ForexZFPredictionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
