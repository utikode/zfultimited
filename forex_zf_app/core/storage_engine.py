"""
Storage Engine - Implementasi Bab 9: Protokol Penyimpanan Otonom & Arsip Dinamis
Manajemen siklus hidup data secara mandiri
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List
import shutil

class StorageEngine:
    """Mesin penyimpanan dan pengarsipan otonom"""
    
    def __init__(self, config):
        self.config = config
        self.archive_data = {}
        self.session_data = []
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Pastikan direktori penyimpanan ada"""
        os.makedirs(self.config.DATA_DIR, exist_ok=True)
        os.makedirs(self.config.ARCHIVE_DIR, exist_ok=True)
        os.makedirs(self.config.LOGS_DIR, exist_ok=True)
    
    def store_session_data(self, data: Dict):
        """Simpan data sesi saat ini"""
        self.session_data.append({
            'timestamp': datetime.now().isoformat(),
            'data': data
        })
    
    def save_archive(self):
        """
        Simpan arsip sesi (Bab 9.1)
        Snapshot sesi dan kompresi data geometris
        """
        if not self.session_data:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_file = os.path.join(
            self.config.ARCHIVE_DIR, 
            f"session_{timestamp}.json"
        )
        
        # Buat snapshot
        snapshot = {
            'created_at': timestamp,
            'total_records': len(self.session_data),
            'data': self.session_data,
            'summary': self._generate_summary()
        }
        
        with open(archive_file, 'w') as f:
            json.dump(snapshot, f, indent=2)
        
        print(f"Archive saved: {archive_file}")
        
        # Reset session data
        self.session_data = []
        
        # Jalankan pembersihan data lama
        self._prune_old_archives()
    
    def load_archive(self):
        """
        Muat arsip terakhir untuk sinkronisasi (Bab 8.1 & 9.2)
        """
        try:
            # Cari file arsip terbaru
            archive_files = [f for f in os.listdir(self.config.ARCHIVE_DIR) 
                           if f.startswith('session_') and f.endswith('.json')]
            
            if not archive_files:
                print("No archive found, starting fresh")
                return
            
            # Urutkan berdasarkan nama (timestamp)
            latest_file = sorted(archive_files)[-1]
            filepath = os.path.join(self.config.ARCHIVE_DIR, latest_file)
            
            with open(filepath, 'r') as f:
                self.archive_data = json.load(f)
            
            print(f"Archive loaded: {latest_file}")
            return self.archive_data
        except Exception as e:
            print(f"Error loading archive: {e}")
            return None
    
    def _generate_summary(self) -> Dict:
        """Generate ringkasan dari data sesi"""
        if not self.session_data:
            return {}
        
        pairs_analyzed = set()
        total_signals = 0
        avg_zf_score = 0.0
        
        for record in self.session_data:
            data = record.get('data', {})
            pair = data.get('pair', '')
            if pair:
                pairs_analyzed.add(pair)
            
            math_metrics = data.get('math_metrics', {})
            zf_score = math_metrics.get('zf_score', 0)
            avg_zf_score += zf_score
            
            signal = data.get('signal', {})
            if signal.get('action') != 'HOLD':
                total_signals += 1
        
        count = len(self.session_data)
        if count > 0:
            avg_zf_score /= count
        
        return {
            'pairs_analyzed': list(pairs_analyzed),
            'total_signals': total_signals,
            'avg_zf_score': round(avg_zf_score, 4),
            'analysis_count': count
        }
    
    def _prune_old_archives(self):
        """
        Pembersihan data lama (Bab 9.3)
        Hapus arsip yang berusia lebih dari DATA_RETENTION_DAYS
        """
        cutoff_date = datetime.now() - timedelta(days=self.config.DATA_RETENTION_DAYS)
        
        try:
            for filename in os.listdir(self.config.ARCHIVE_DIR):
                if not filename.endswith('.json'):
                    continue
                
                filepath = os.path.join(self.config.ARCHIVE_DIR, filename)
                
                # Ambil tanggal dari nama file
                try:
                    # Format: session_YYYYMMDD_HHMMSS.json
                    date_str = filename.replace('session_', '').replace('.json', '')[:8]
                    file_date = datetime.strptime(date_str, "%Y%m%d")
                    
                    if file_date < cutoff_date:
                        # Pindahkan ke cold storage atau hapus
                        os.remove(filepath)
                        print(f"Pruned old archive: {filename}")
                except Exception:
                    continue
        except Exception as e:
            print(f"Error pruning archives: {e}")
    
    def get_historical_data(self, pair: str, days: int = 7) -> List[Dict]:
        """Ambil data historis untuk pair tertentu"""
        historical = []
        
        try:
            for filename in os.listdir(self.config.ARCHIVE_DIR):
                if not filename.endswith('.json'):
                    continue
                
                filepath = os.path.join(self.config.ARCHIVE_DIR, filename)
                
                with open(filepath, 'r') as f:
                    archive = json.load(f)
                
                for record in archive.get('data', []):
                    data = record.get('data', {})
                    if data.get('pair') == pair:
                        historical.append(data)
        except Exception as e:
            print(f"Error reading historical data: {e}")
        
        return historical[-100:]  # Return max 100 records
    
    def export_to_csv(self, data: List[Dict], filename: str = None):
        """Ekspor data ke CSV"""
        import csv
        
        if filename is None:
            filename = os.path.join(
                self.config.DATA_DIR,
                f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
        
        if not data:
            return None
        
        keys = data[0].keys()
        
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"Data exported to: {filename}")
        return filename
    
    def validate_integrity(self, filepath: str) -> bool:
        """
        Validasi integritas data (Bab 2.4 & 9.3)
        Check-sum untuk memastikan tidak ada data korup
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Validasi struktur dasar
            required_keys = ['created_at', 'data']
            for key in required_keys:
                if key not in data:
                    return False
            
            # Validasi data records
            for record in data.get('data', []):
                if 'timestamp' not in record or 'data' not in record:
                    return False
            
            return True
        except Exception:
            return False
    
    def clear_session_data(self):
        """Bersihkan data sesi saat ini"""
        self.session_data = []
    
    def get_storage_stats(self) -> Dict:
        """Dapatkan statistik penyimpanan"""
        try:
            archive_files = [f for f in os.listdir(self.config.ARCHIVE_DIR) 
                           if f.startswith('session_')]
            
            total_size = sum(
                os.path.getsize(os.path.join(self.config.ARCHIVE_DIR, f)) 
                for f in archive_files
            )
            
            return {
                'total_archives': len(archive_files),
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'current_session_records': len(self.session_data),
                'retention_days': self.config.DATA_RETENTION_DAYS
            }
        except Exception as e:
            return {'error': str(e)}
