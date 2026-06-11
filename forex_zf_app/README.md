# 📘 Buku Besar Forex ZF
## Zuhri Formalism V16.4-OMNI-WARROOM

Sistem trading forex otonom berbasis AI yang mengimplementasikan protokol Zuhri Formalism dengan integrasi Google Gemini dan Finnhub untuk analisis dinamis.

## ✨ Fitur Utama

### Core Engine (Bab 1-9 Terimplementasi)
- **BAB 1:** Ontologi Pasar - Definisi dan Struktur
- **BAB 2:** Mekanika Data - Penarikan dan Sinkronisasi
- **BAB 3:** Analisis Order Book - Pemetaan Kekuatan
- **BAB 4:** Formulasi Matematis Resonansi (ZF-Core)
- **BAB 5:** Protokol Eksekusi - Dari Teori ke Tindakan
- **BAB 6:** Protokol Mitigasi Anomali & Mode Dingin
- **BAB 7:** Akuisisi Data & Manajemen Multi-Asset
- **BAB 8:** Validasi Silang & Analisis Anomali Deterministik
- **BAB 9:** Penyimpanan Otonom & Arsip Dinamis

### Fitur Tambahan
- 🤖 **AI Gemini Integration** - Analisis dinamis dengan Google Gemini
- 📊 **Finnhub API** - Data sentimen pasar real-time
- 📈 **TradingView Chart** - Visualisasi grafik custom
- 🎯 **Dynamic Position Sizing** - Manajemen risiko otomatis
- 📱 **Telegram Notifications** - Notifikasi multi-channel
- 🧪 **Backtesting Engine** - Uji strategi pada data historis
- 🖥️ **System Health Monitor** - Monitoring kinerja real-time
- 🏛️ **War Room Dashboard** - Visualisasi 3D/heatmap

## 🚀 Instalasi

### Prasyarat
- Python 3.8+
- Windows (untuk MetaTrader 5)
- MetaTrader 5 terminal terinstal

### Langkah Instalasi

```bash
# Clone atau download repository
cd forex_zf_app

# Install dependencies
pip install -r requirements.txt

# Jalankan aplikasi
python main.py
```

## ⚙️ Konfigurasi

### 1. Setup API Keys
Buka tab "Pengaturan" di aplikasi dan masukkan:
- **Google Gemini API Key** - Dapatkan dari https://makersuite.google.com/app/apikey
- **Finnhub API Key** - Dapatkan dari https://finnhub.io/dashboard
- **Telegram Bot Token** (opsional) - Buat bot via @BotFather

### 2. Koneksi MetaTrader 5
1. Instal MT5 dari broker Anda
2. Login ke akun Demo/Real
3. Aktifkan "Algo Trading" (ikon Play)
4. Centang "Allow DLL imports" di Tools > Options > Expert Advisors

### 3. Mode Operasi
- **SIMULATION** - Testing tanpa uang asli (default jika MT5 tidak terdeteksi)
- **AUTO** - Trading otomatis penuh
- **MANUAL** - Memerlukan konfirmasi manusia (Human-in-the-Loop)

## 📖 Cara Penggunaan

1. **Jalankan Aplikasi**
   ```bash
   python main.py
   ```

2. **Konfigurasi API Keys** di tab Pengaturan

3. **Scan Market** untuk melihat prediksi AI

4. **Monitor Dashboard** untuk sinyal trading

5. **Eksekusi** otomatis atau manual sesuai mode

## 🏗️ Struktur Modular

```
forex_zf_app/
├── config/
│   └── __init__.py       # Konfigurasi global
├── core/
│   ├── __init__.py       # ZFCore engine utama
│   ├── math_engine.py    # Bab 4: Formulasi Matematis
│   ├── data_engine.py    # Bab 2 & 7: Data & Akuisisi
│   ├── ai_engine.py      # Integrasi Gemini & Finnhub
│   ├── execution_engine.py # Bab 5 & 6: Eksekusi
│   ├── storage_engine.py # Bab 9: Penyimpanan
│   └── system_monitor.py # Monitor kesehatan
├── gui/
│   └── main_gui.py       # Antarmuka pengguna
├── main.py               # Entry point
├── requirements.txt      # Dependencies
└── README.md            # Dokumentasi ini
```

## ⚠️ Peringatan Risiko

**PERINGATAN PENTING:** Trading forex melibatkan risiko tinggi dan dapat mengakibatkan kehilangan seluruh modal Anda. Sistem ini disediakan untuk tujuan edukasi dan riset saja.

- Gunakan akun DEMO untuk testing awal
- Jangan trade dengan uang yang tidak siap hilang
- Past performance tidak menjamin hasil masa depan
- Konsultasikan dengan profesional keuangan sebelum trading real

## 📝 Lisensi

Proyek ini dikembangkan untuk komunitas Zuhri Formalism.

## 🤝 Kontribusi

Silakan submit issue atau pull request untuk perbaikan.

---

**Jaga Ibadahmu** - Ttd, Arsitek Utama (ZF-Core V16.4-OMNI-WARROOM)