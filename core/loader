"""
AutoInsight - Veri Yükleme Modülü
Desteklenen formatlar: CSV, Excel, JSON, Parquet
"""

import pandas as pd
import os
from typing import Tuple, Optional
import chardet

class DataLoader:
    """Farklı formatlardaki veri dosyalarını yükler ve standardize eder."""
    
    SUPPORTED_FORMATS = {
        '.csv': 'csv',
        '.xlsx': 'excel',
        '.xls': 'excel',
        '.json': 'json',
        '.parquet': 'parquet',
        '.txt': 'csv'  # tab/comma separated olarak dene
    }
    
    # Paket limitleri (MB)
    LIMITS = {
        'free': 2.5,
        'pro': 25,
        'business': 200
    }
    
    def __init__(self, package: str = 'free'):
        """
        Args:
            package: 'free', 'pro', veya 'business'
        """
        self.package = package.lower()
        self.max_size_mb = self.LIMITS.get(self.package, 1)
        
    def check_file_size(self, filepath: str) -> Tuple[bool, float]:
        """
        Dosya boyutunu kontrol eder.
        
        Returns:
            (izin_verildi_mi, dosya_boyutu_mb)
        """
        size_bytes = os.path.getsize(filepath)
        size_mb = size_bytes / (1024 * 1024)
        
        return size_mb <= self.max_size_mb, size_mb
    
    def detect_encoding(self, filepath: str) -> str:
        """CSV dosyaları için encoding tespiti yapar."""
        with open(filepath, 'rb') as f:
            result = chardet.detect(f.read(100000))  # ilk 100KB
        return result['encoding'] or 'utf-8'
    
    def load_data(self, filepath: str, **kwargs) -> Tuple[pd.DataFrame, dict]:
        """
        Veri dosyasını yükler ve metadata döndürür.
        
        Args:
            filepath: Dosya yolu
            **kwargs: Pandas okuma fonksiyonlarına iletilecek ek parametreler
            
        Returns:
            (DataFrame, metadata_dict)
        """
        # Dosya varlığı kontrolü
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Dosya bulunamadı: {filepath}")
        
        # Boyut kontrolü
        allowed, size_mb = self.check_file_size(filepath)
        if not allowed:
            raise ValueError(
                f"❌ Dosya boyutu ({size_mb:.2f} MB), {self.package.upper()} "
                f"paket limitini ({self.max_size_mb} MB) aşıyor!"
            )
        
        # Format tespiti
        ext = os.path.splitext(filepath)[1].lower()
        if ext not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Desteklenmeyen format: {ext}")
        
        file_format = self.SUPPORTED_FORMATS[ext]
        
        # Veri yükleme
        print(f"📂 Yükleniyor: {os.path.basename(filepath)} ({size_mb:.2f} MB)")
        
        try:
            if file_format == 'csv':
                encoding = self.detect_encoding(filepath)
                df = pd.read_csv(filepath, encoding=encoding, **kwargs)
                
            elif file_format == 'excel':
                df = pd.read_excel(filepath, **kwargs)
                
            elif file_format == 'json':
                df = pd.read_json(filepath, **kwargs)
                
            elif file_format == 'parquet':
                df = pd.read_parquet(filepath, **kwargs)
            
            # Metadata
            metadata = {
                'filename': os.path.basename(filepath),
                'format': file_format,
                'size_mb': size_mb,
                'rows': len(df),
                'columns': len(df.columns),
                'package': self.package,
                'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024**2)
            }
            
            print(f"✅ Yükleme başarılı: {metadata['rows']:,} satır × {metadata['columns']} sütun")
            
            return df, metadata
            
        except Exception as e:
            raise Exception(f"❌ Dosya okunurken hata: {str(e)}")
    
    def get_sample(self, df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
        """İlk n satırı döndürür."""
        return df.head(n)


# Test fonksiyonu
if __name__ == "__main__":
    loader = DataLoader(package='pro')
    
    # Örnek kullanım
    # df, meta = loader.load_data('examples/sample_data.csv')
    # print(meta)
    # print(loader.get_sample(df, 3))
