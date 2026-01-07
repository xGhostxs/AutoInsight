"""
AutoInsight - Veri Temizleme ve Ön İşleme Modülü
Eksik veriler, tip dönüşümleri, outlier tespiti
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class DataCleaner:
    """Veri kalitesi iyileştirmeleri ve temizleme işlemleri."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.cleaning_report = {}
        
    def analyze_missing(self) -> Dict:
        """Eksik veri analizi yapar."""
        missing_stats = {
            'total_cells': self.df.size,
            'missing_cells': self.df.isna().sum().sum(),
            'missing_percentage': (self.df.isna().sum().sum() / self.df.size) * 100,
            'columns_with_missing': {}
        }
        
        for col in self.df.columns:
            missing_count = self.df[col].isna().sum()
            if missing_count > 0:
                missing_stats['columns_with_missing'][col] = {
                    'count': int(missing_count),
                    'percentage': (missing_count / len(self.df)) * 100
                }
        
        self.cleaning_report['missing_analysis'] = missing_stats
        return missing_stats
    
    def detect_column_types(self) -> Dict:
        """Sütun tiplerini otomatik tespit eder."""
        type_info = {
            'numeric': [],
            'categorical': [],
            'datetime': [],
            'text': []
        }
        
        for col in self.df.columns:
            # Datetime kontrolü
            if pd.api.types.is_datetime64_any_dtype(self.df[col]):
                type_info['datetime'].append(col)
            # Sayısal kontrol
            elif pd.api.types.is_numeric_dtype(self.df[col]):
                type_info['numeric'].append(col)
            # Kategorik kontrol (unique < %5 veya < 20)
            elif self.df[col].nunique() < len(self.df) * 0.05 or self.df[col].nunique() < 20:
                type_info['categorical'].append(col)
            # Metin
            else:
                type_info['text'].append(col)
        
        self.cleaning_report['column_types'] = type_info
        return type_info
    
    def handle_missing(self, strategy: str = 'auto', threshold: float = 0.5):
        """
        Eksik verileri yönetir.
        
        Args:
            strategy: 'auto', 'drop', 'mean', 'median', 'mode', 'forward_fill'
            threshold: Bu oranın üstünde eksik değer varsa sütunu sil (0-1)
        """
        original_shape = self.df.shape
        
        # Çok fazla eksik değeri olan sütunları çıkar
        missing_ratio = self.df.isna().sum() / len(self.df)
        cols_to_drop = missing_ratio[missing_ratio > threshold].index.tolist()
        
        if cols_to_drop:
            self.df = self.df.drop(columns=cols_to_drop)
            print(f"🗑️  {len(cols_to_drop)} sütun silindi (>{threshold*100}% eksik): {cols_to_drop}")
        
        # Kalan eksik değerleri doldur
        if strategy == 'auto':
            for col in self.df.columns:
                if self.df[col].isna().any():
                    if pd.api.types.is_numeric_dtype(self.df[col]):
                        # Sayısal: median ile doldur
                        self.df[col].fillna(self.df[col].median(), inplace=True)
                    else:
                        # Kategorik: mode ile doldur
                        self.df[col].fillna(self.df[col].mode()[0] if not self.df[col].mode().empty else 'Unknown', inplace=True)
        
        elif strategy == 'drop':
            self.df.dropna(inplace=True)
        
        elif strategy in ['mean', 'median']:
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            if strategy == 'mean':
                self.df[numeric_cols] = self.df[numeric_cols].fillna(self.df[numeric_cols].mean())
            else:
                self.df[numeric_cols] = self.df[numeric_cols].fillna(self.df[numeric_cols].median())
        
        elif strategy == 'mode':
            for col in self.df.columns:
                if self.df[col].isna().any():
                    mode_val = self.df[col].mode()[0] if not self.df[col].mode().empty else None
                    self.df[col].fillna(mode_val, inplace=True)
        
        elif strategy == 'forward_fill':
            self.df.fillna(method='ffill', inplace=True)
        
        new_shape = self.df.shape
        print(f"✅ Temizleme tamamlandı: {original_shape} → {new_shape}")
        
        self.cleaning_report['missing_handling'] = {
            'strategy': strategy,
            'threshold': threshold,
            'dropped_columns': cols_to_drop,
            'original_shape': original_shape,
            'new_shape': new_shape
        }
    
    def detect_outliers(self, method: str = 'iqr') -> Dict:
        """
        Outlier (aykırı değer) tespiti yapar.
        
        Args:
            method: 'iqr' (Interquartile Range) veya 'zscore'
        """
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        outliers = {}
        
        for col in numeric_cols:
            if method == 'iqr':
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                outlier_mask = (self.df[col] < lower) | (self.df[col] > upper)
            
            elif method == 'zscore':
                z_scores = np.abs((self.df[col] - self.df[col].mean()) / self.df[col].std())
                outlier_mask = z_scores > 3
            
            outlier_count = outlier_mask.sum()
            if outlier_count > 0:
                outliers[col] = {
                    'count': int(outlier_count),
                    'percentage': (outlier_count / len(self.df)) * 100
                }
        
        self.cleaning_report['outliers'] = outliers
        return outliers
    
    def convert_dtypes(self):
        """Veri tiplerini optimize eder (memory tasarrufu)."""
        for col in self.df.select_dtypes(include=['int64']).columns:
            self.df[col] = pd.to_numeric(self.df[col], downcast='integer')
        
        for col in self.df.select_dtypes(include=['float64']).columns:
            self.df[col] = pd.to_numeric(self.df[col], downcast='float')
        
        print("💾 Veri tipleri optimize edildi (memory tasarrufu)")
    
    def get_cleaned_data(self) -> pd.DataFrame:
        """Temizlenmiş DataFrame'i döndürür."""
        return self.df
    
    def get_report(self) -> Dict:
        """Temizleme raporunu döndürür."""
        return self.cleaning_report


# Test
if __name__ == "__main__":
    # Örnek kullanım
    # cleaner = DataCleaner(df)
    # cleaner.analyze_missing()
    # cleaner.handle_missing(strategy='auto')
    # cleaner.detect_outliers()
    # cleaned_df = cleaner.get_cleaned_data()
    pass
