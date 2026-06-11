# Buku Besar Forex ZF - V16.4 OMNI-WARROOM

Aplikasi trading forex canggih berbasis protokol **Zuhri Formalism (ZF-Core)** yang menggabungkan analisis matematika murni, AI (Google Gemini), data eksternal (Finnhub), dan eksekusi otomatis melalui MetaTrader 5. Dirancang untuk beroperasi secara "organik" agar tidak terdeteksi sebagai EA oleh broker.

## Fitur Utama

### 1. Core Engine (ZF-Core)
- **Matematika Resonansi:** Menghitung *Topological Drift*, *ZF-Score*, dan titik ekuilibrium.
- **AI Hybrid:** Integrasi Google Gemini untuk analisis sentimen dan konfirmasi sinyal.
- **Data Eksternal:** Tarik data order book & sentimen via Finnhub API.
- **Eksekusi Organik:** Simulasi perilaku manusia (delay acak, split order).

### 2. Dashboard & Prediksi
- **Scan Pasar:** Analisis 30+ pasangan mata uang secara simultan.
- **Tabel Prediksi:** Top 10 prediksi NAIK dan TURUN dalam 10 hari.
- **War Room:** Kontrol trading otomatis dan visualisasi data.

### 3. Manajemen Risiko & Penyimpanan
- **Circuit Breaker:** Stop otomatis jika kerugian harian melebihi batas.
- **Archival Vault:** Pencatatan jurnal trading otomatis (JSON) dengan pembersihan data >30 hari.
- **Notifikasi Telegram:** Alert real-time ke smartphone Anda.

### 4. Antarmuka Pengguna (GUI)
- Modern Dark Mode menggunakan `CustomTkinter`.
- Tab navigasi: Dashboard, Predictions, War Room, Settings, Journal.
- Konfigurasi API Key mudah dengan deteksi otomatis Chat ID Telegram.

## Instalasi

### Prasyarat
- **OS:** Windows 10/11 (Wajib untuk MetaTrader 5).
- **Python:** Versi 3.9 atau lebih baru.
- **MetaTrader 5:** Terinstal dan login ke akun (Demo/Real).
- **API Keys:** 
  - [Google Gemini API](https://aistudio.google.com/app/apikey)
  - [Finnhub API](https://finnhub.io/)
  - [Telegram Bot Token](https://t.me/BotFather)

### Langkah Instalasi

1. **Clone atau Download Repository**
   ```bash
   cd path/to/forex_zf_app
   ```

2. **Install Dependensi**
   ```bash
   pip install -r requirements.txt
   ```

3. **Jalankan Aplikasi**
   ```bash
   python main.py
   ```

## Cara Penggunaan

### 1. Konfigurasi Awal
- Buka tab **Settings**.
- Masukkan **Google Gemini API Key**, **Finnhub API Key**, dan **Telegram Bot Token**.
- Klik **Auto-Detect Chat ID** (Pastikan sudah kirim `/start` ke bot Telegram Anda).
- Atur **Risk Per Trade** dan **Max Daily Loss**.
- Klik **Save Configuration**.

### 2. Scan Pasar
- Buka tab **Dashboard**.
- Klik tombol **SCAN MARKET NOW**.
- Tunggu proses scanning (data akan diambil dari MT5/API/Simulasi).
- Hasil prediksi akan muncul di tab **Predictions** (Tabel Hijau untuk NAIK, Merah untuk TURUN).

### 3. Eksekusi Trading
- **Manual:** Pilih sinyal dari tabel, tentukan entry, dan eksekusi via MT5.
- **Otomatis:** Aktifkan switch **Auto Trading** di tab **War Room** (Hati-hati, pastikan konfigurasi risiko sudah benar).

### 4. Monitoring
- Cek **Journal** untuk riwayat trading.
- Pantau notifikasi Telegram untuk alert penting.

## Struktur Folder Modular

```
forex_zf_app/
├── core/           # Logika inti (ZFCore, Engines)
│   ├── __init__.py
│   └── zf_core.py
├── gui/            # Antarmuka pengguna
│   ├── __init__.py
│   └── main_gui.py
├── utils/          # Fungsi bantuan
├── data/           # Penyimpanan config & journal
└── __init__.py
main.py             # Entry point aplikasi
requirements.txt    # Daftar dependensi
README.md           # Dokumentasi ini
```

## Protokol Zuhri Formalism (Ringkasan)

Aplikasi ini mengimplementasikan 9 Bab Buku Besar Forex ZF:
1. **Ontologi Pasar:** Aset sebagai entitas resonansi.
2. **Mekanika Data:** Sinkronisasi & normalisasi data.
3. **Analisis Order Book:** Deteksi spoofing & likuiditas.
4. **Formulasi Matematis:** Rumus Drift, Decay, ZF-Score.
5. **Protokol Eksekusi:** Entry/Exit deterministik.
6. **Mitigasi Anomali:** Circuit breaker & mode dingin.
7. **Akuisisi Multi-Asset:** Scan 200+ pairs.
8. **Validasi Silang:** Cross-check historis vs real-time.
9. **Penyimpanan Otonom:** Archiving & pruning data.

## Peringatan Risiko

> **DISCLAIMER:** Trading forex mengandung risiko tinggi. Aplikasi ini adalah alat bantu analisis dan eksekusi. Kinerja masa lalu tidak menjamin hasil masa depan. Gunakan hanya dana yang Anda rela kehilangan. Pengembang tidak bertanggung jawab atas kerugian finansial.

## Troubleshooting

- **Error `CTkLabelFrame`:** Sudah diperbaiki dengan menggunakan `tk.LabelFrame` standar.
- **Scan Tidak Muncul:** Pastikan API Key valid atau biarkan kosong untuk mode simulasi (fallback matematika).
- **MT5 Tidak Terkoneksi:** Pastikan terminal MT5 terbuka dan login. Jika tidak, aplikasi otomatis masuk **Mode Simulasi**.
- **Telegram Gagal:** Pastikan sudah kirim pesan `/start` ke bot sebelum klik "Auto-Detect".

## Lisensi

Proyek ini untuk tujuan edukasi dan riset pribadi.

---
**Jaga Ibadahmu - Ttd, Arsitek Utama (ZF-Core V16.4)**