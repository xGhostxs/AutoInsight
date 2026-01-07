"""
AutoInsight - İstatistiksel Analiz Modülü
Betimleyici istatistikler, korelasyon, dağılım analizleri
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from scipy import stats

class DataAnalyzer:
    """Kapsamlı veri analizi ve istatistik hesaplamaları."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        self.datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
    def get_basic_stats(self) -> Dict:
        """Temel istatistiksel özet."""
        stats_summary = {
            'shape': {
                'rows': len(self.df),
                'columns': len(self.df.columns)
            },
            'memory_usage_mb': self.df.memory_usage(deep=True).sum() / (1024**2),
            'dtypes': self.df.dtypes.value_counts().to_dict(),
            'numeric_columns': len(self.numeric_cols),
            'categorical_columns': len(self.categorical_cols),
            'datetime_columns': len(self.datetime_cols)
        }
        
        return stats_summary
    
    def descriptive_statistics(self) -> pd.DataFrame:
        """
        Sayısal sütunlar için genişletilmiş betimleyici istatistikler.
        """
        if not self.numeric_cols:
            return pd.DataFrame()
        
        desc = self.df[self.numeric_cols].describe().T
        
        # Ek metrikler
        desc['variance'] = self.df[self.numeric_cols].var()
        desc['skewness'] = self.df[self.numeric_cols].skew()
        desc['kurtosis'] = self.df[self.numeric_cols].kurtosis()
        desc['missing'] = self.df[self.numeric_cols].isna().sum()
        desc['missing_pct'] = (desc['missing'] / len(self.df)) * 100
        
        # Sıralama
        desc = desc[['count', 'missing', 'missing_pct', 'mean', 'std', 'min', 
                     '25%', '50%', '75%', 'max', 'variance', 'skewness', 'kurtosis']]
        
        return desc.round(2)
    
    def categorical_analysis(self) -> Dict:
        """Kategorik sütunlar için dağılım analizi."""
        cat_analysis = {}
        
        for col in self.categorical_cols:
            value_counts = self.df[col].value_counts()
            
            cat_analysis[col] = {
                'unique_count': int(self.df[col].nunique()),
                'top_5_values': value_counts.head(5).to_dict(),
                'most_common': value_counts.index[0] if len(value_counts) > 0 else None,
                'most_common_count': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                'concentration': (value_counts.iloc[0] / len(self.df)) * 100 if len(value_counts) > 0 else 0
            }
        
        return cat_analysis
    
    def correlation_analysis(self, method: str = 'pearson', threshold: float = 0.5) -> Tuple[pd.DataFrame, List]:
        """
        Korelasyon matrisi ve güçlü korelasyonlar.
        
        Args:
            method: 'pearson', 'spearman', veya 'kendall'
            threshold: Güçlü korelasyon eşiği (mutlak değer)
        """
        if len(self.numeric_cols) < 2:
            return pd.DataFrame(), []
        
        corr_matrix = self.df[self.numeric_cols].corr(method=method)
        
        # Güçlü korelasyonları bul
        strong_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) >= threshold:
                    strong_correlations.append({
                        'var1': corr_matrix.columns[i],
                        'var2': corr_matrix.columns[j],
                        'correlation': round(corr_val, 3),
                        'strength': self._correlation_strength(abs(corr_val))
                    })
        
        # Korelasyona göre sırala
        strong_correlations = sorted(strong_correlations, 
                                     key=lambda x: abs(x['correlation']), 
                                     reverse=True)
        
        return corr_matrix, strong_correlations
    
    def _correlation_strength(self, corr: float) -> str:
        """Korelasyon gücünü sınıflandır."""
        if corr >= 0.9:
            return 'Çok Güçlü'
        elif corr >= 0.7:
            return 'Güçlü'
        elif corr >= 0.5:
            return 'Orta'
        elif corr >= 0.3:
            return 'Zayıf'
        else:
            return 'Çok Zayıf'
    
    def variance_analysis(self, top_n: int = 10) -> pd.DataFrame:
        """En yüksek varyansa sahip değişkenleri bulur."""
        if not self.numeric_cols:
            return pd.DataFrame()
        
        variances = self.df[self.numeric_cols].var().sort_values(ascending=False)
        
        # Normalize edilmiş varyans (coefficient of variation)
        cv = (self.df[self.numeric_cols].std() / self.df[self.numeric_cols].mean()).abs()
        
        result = pd.DataFrame({
            'variance': variances,
            'std': self.df[self.numeric_cols].std(),
            'cv': cv
        }).head(top_n)
        
        return result.round(4)
    
    def distribution_tests(self) -> Dict:
        """Normallik testleri (Shapiro-Wilk)."""
        normality = {}
        
        for col in self.numeric_cols:
            # Çok fazla veri varsa sample al (Shapiro-Wilk limiti: 5000)
            sample = self.df[col].dropna()
            if len(sample) > 5000:
                sample = sample.sample(5000, random_state=42)
            
            if len(sample) >= 3:  # Minimum gereksinim
                try:
                    stat, p_value = stats.shapiro(sample)
                    normality[col] = {
                        'statistic': round(stat, 4),
                        'p_value': round(p_value, 4),
                        'is_normal': p_value > 0.05  # %5 anlamlılık seviyesi
                    }
                except:
                    normality[col] = {'error': 'Test yapılamadı'}
        
        return normality
    
    def detect_time_patterns(self) -> Dict:
        """Zaman serisi varsa trend ve mevsimsellik analizi."""
        time_analysis = {}
        
        for dt_col in self.datetime_cols:
            # Tarih sütununu index yap
            temp_df = self.df.set_index(dt_col)
            
            # Sayısal kolonlar için trend analizi
            for num_col in self.numeric_cols[:3]:  # İlk 3 sayısal kolon
                if num_col in temp_df.columns:
                    # Günlük ortalama
                    daily = temp_df[num_col].resample('D').mean()
                    
                    time_analysis[f"{dt_col}_{num_col}"] = {
                        'data_points': len(daily.dropna()),
                        'date_range': f"{daily.index.min()} - {daily.index.max()}",
                        'trend': self._detect_trend(daily.dropna())
                    }
        
        return time_analysis
    
    def _detect_trend(self, series: pd.Series) -> str:
        """Basit trend tespiti."""
        if len(series) < 2:
            return 'Yetersiz veri'
        
        # Linear regression slope
        x = np.arange(len(series))
        slope = np.polyfit(x, series.values, 1)[0]
        
        if abs(slope) < series.std() * 0.01:
            return 'Sabit'
        elif slope > 0:
            return 'Artan'
        else:
            return 'Azalan'
    
    def generate_insights(self) -> List[str]:
        """Otomatik içgörüler üretir."""
        insights = []
        
        # 1. Veri boyutu
        insights.append(f"📊 Veri seti {len(self.df):,} satır ve {len(self.df.columns)} sütundan oluşuyor.")
        
        # 2. Eksik veri
        missing_pct = (self.df.isna().sum().sum() / self.df.size) * 100
        if missing_pct > 5:
            insights.append(f"⚠️  Toplam %{missing_pct:.1f} eksik veri tespit edildi.")
        
        # 3. Kategorik değişkenler
        if self.categorical_cols:
            high_cardinality = [col for col in self.categorical_cols 
                               if self.df[col].nunique() > len(self.df) * 0.8]
            if high_cardinality:
                insights.append(f"🔍 {', '.join(high_cardinality)} sütunları çok fazla benzersiz değer içeriyor (ID olabilir).")
        
        # 4. Korelasyonlar
        if len(self.numeric_cols) >= 2:
            _, strong_corr = self.correlation_analysis(threshold=0.7)
            if strong_corr:
                insights.append(f"🔗 {len(strong_corr)} adet güçlü korelasyon tespit edildi.")
        
        # 5. Varyans
        if self.numeric_cols:
            var_df = self.variance_analysis(top_n=3)
            if not var_df.empty:
                top_var = var_df.index[0]
                insights.append(f"📈 En yüksek değişkenlik '{top_var}' sütununda gözlemlendi.")
        
        return insights


# Test
if __name__ == "__main__":
    pass
