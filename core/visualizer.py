"""
AutoInsight - Görselleştirme Modülü
Otomatik grafik üretimi: histogram, bar chart, korelasyon, zaman serisi
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Türkçe karakter desteği
plt.rcParams['font.family'] = 'DejaVu Sans'
sns.set_style("whitegrid")
sns.set_palette("husl")

class DataVisualizer:
    """Otomatik veri görselleştirme sınıfı."""
    
    def __init__(self, df: pd.DataFrame, save_dir: str = 'outputs'):
        self.df = df
        self.save_dir = save_dir
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        import os
        os.makedirs(save_dir, exist_ok=True)
    
    def plot_distributions(self, max_cols: int = 9, figsize: Tuple[int, int] = (15, 10)):
        """
        Sayısal değişkenler için histogram/dağılım grafikleri.
        """
        cols_to_plot = self.numeric_cols[:max_cols]
        if not cols_to_plot:
            print("⚠️  Görselleştirilecek sayısal sütun bulunamadı.")
            return None
        
        n_cols = min(3, len(cols_to_plot))
        n_rows = int(np.ceil(len(cols_to_plot) / n_cols))
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        axes = axes.flatten() if len(cols_to_plot) > 1 else [axes]
        
        for idx, col in enumerate(cols_to_plot):
            ax = axes[idx]
            data = self.df[col].dropna()
            
            # Histogram + KDE
            ax.hist(data, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
            ax2 = ax.twinx()
            data.plot(kind='kde', ax=ax2, color='red', linewidth=2)
            
            # İstatistikler
            mean_val = data.mean()
            median_val = data.median()
            
            ax.axvline(mean_val, color='green', linestyle='--', linewidth=2, label=f'Ort: {mean_val:.2f}')
            ax.axvline(median_val, color='orange', linestyle='--', linewidth=2, label=f'Med: {median_val:.2f}')
            
            ax.set_title(f'{col}\n(n={len(data):,})', fontsize=11, fontweight='bold')
            ax.set_xlabel('')
            ax.set_ylabel('Frekans', fontsize=9)
            ax2.set_ylabel('Yoğunluk', fontsize=9)
            ax.legend(loc='upper right', fontsize=8)
            ax.grid(alpha=0.3)
        
        # Boş subplotları gizle
        for idx in range(len(cols_to_plot), len(axes)):
            axes[idx].set_visible(False)
        
        plt.tight_layout()
        filepath = f'{self.save_dir}/distributions.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Dağılım grafikleri kaydedildi: {filepath}")
        return filepath
    
    def plot_categorical(self, max_cols: int = 6, top_n: int = 10, figsize: Tuple[int, int] = (15, 8)):
        """
        Kategorik değişkenler için bar chart.
        """
        cols_to_plot = self.categorical_cols[:max_cols]
        if not cols_to_plot:
            print("⚠️  Görselleştirilecek kategorik sütun bulunamadı.")
            return None
        
        n_cols = min(3, len(cols_to_plot))
        n_rows = int(np.ceil(len(cols_to_plot) / n_cols))
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        axes = axes.flatten() if len(cols_to_plot) > 1 else [axes]
        
        for idx, col in enumerate(cols_to_plot):
            ax = axes[idx]
            
            # En çok tekrar eden top_n değeri al
            value_counts = self.df[col].value_counts().head(top_n)
            
            # Bar chart
            value_counts.plot(kind='barh', ax=ax, color='coral', edgecolor='black')
            
            ax.set_title(f'{col}\n({self.df[col].nunique()} benzersiz değer)', 
                        fontsize=11, fontweight='bold')
            ax.set_xlabel('Frekans', fontsize=9)
            ax.set_ylabel('')
            ax.grid(axis='x', alpha=0.3)
            
            # Yüzde bilgisi ekle
            total = len(self.df)
            for i, (label, value) in enumerate(value_counts.items()):
                pct = (value / total) * 100
                ax.text(value, i, f' {pct:.1f}%', va='center', fontsize=8)
        
        # Boş subplotları gizle
        for idx in range(len(cols_to_plot), len(axes)):
            axes[idx].set_visible(False)
        
        plt.tight_layout()
        filepath = f'{self.save_dir}/categorical.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Kategorik grafikler kaydedildi: {filepath}")
        return filepath
    
    def plot_correlation_heatmap(self, figsize: Tuple[int, int] = (12, 10), method: str = 'pearson'):
        """
        Korelasyon ısı haritası.
        """
        if len(self.numeric_cols) < 2:
            print("⚠️  Korelasyon hesaplamak için en az 2 sayısal sütun gerekli.")
            return None
        
        corr_matrix = self.df[self.numeric_cols].corr(method=method)
        
        # Mask for upper triangle
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
        
        fig, ax = plt.subplots(figsize=figsize)
        
        sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f', 
                   cmap='coolwarm', center=0, square=True,
                   linewidths=1, cbar_kws={"shrink": 0.8},
                   vmin=-1, vmax=1, ax=ax)
        
        ax.set_title(f'Korelasyon Matrisi ({method.capitalize()})', 
                    fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        filepath = f'{self.save_dir}/correlation_heatmap.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Korelasyon haritası kaydedildi: {filepath}")
        return filepath
    
    def plot_boxplots(self, max_cols: int = 9, figsize: Tuple[int, int] = (15, 10)):
        """
        Sayısal değişkenler için boxplot (outlier tespiti).
        """
        cols_to_plot = self.numeric_cols[:max_cols]
        if not cols_to_plot:
            return None
        
        n_cols = min(3, len(cols_to_plot))
        n_rows = int(np.ceil(len(cols_to_plot) / n_cols))
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        axes = axes.flatten() if len(cols_to_plot) > 1 else [axes]
        
        for idx, col in enumerate(cols_to_plot):
            ax = axes[idx]
            data = self.df[col].dropna()
            
            bp = ax.boxplot(data, vert=True, patch_artist=True,
                           boxprops=dict(facecolor='lightblue', alpha=0.7),
                           medianprops=dict(color='red', linewidth=2),
                           flierprops=dict(marker='o', markerfacecolor='red', markersize=4, alpha=0.5))
            
            # İstatistikler
            q1, median, q3 = np.percentile(data, [25, 50, 75])
            iqr = q3 - q1
            
            ax.set_title(f'{col}', fontsize=11, fontweight='bold')
            ax.set_ylabel('Değer', fontsize=9)
            ax.grid(axis='y', alpha=0.3)
            ax.text(1.15, median, f'Med: {median:.1f}', va='center', fontsize=8)
        
        for idx in range(len(cols_to_plot), len(axes)):
            axes[idx].set_visible(False)
        
        plt.tight_layout()
        filepath = f'{self.save_dir}/boxplots.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Boxplot grafikleri kaydedildi: {filepath}")
        return filepath
    
    def plot_time_series(self, date_col: str, value_cols: List[str] = None, 
                        figsize: Tuple[int, int] = (14, 6)):
        """
        Zaman serisi grafiği.
        """
        if date_col not in self.df.columns:
            print(f"⚠️  '{date_col}' sütunu bulunamadı.")
            return None
        
        # Tarih sütununu datetime'a çevir
        if not pd.api.types.is_datetime64_any_dtype(self.df[date_col]):
            try:
                df_copy = self.df.copy()
                df_copy[date_col] = pd.to_datetime(df_copy[date_col])
            except:
                print(f"⚠️  '{date_col}' tarih formatına çevrilemedi.")
                return None
        else:
            df_copy = self.df.copy()
        
        # Değer sütunları belirtilmemişse ilk 3 sayısal sütunu al
        if value_cols is None:
            value_cols = self.numeric_cols[:3]
        
        if not value_cols:
            print("⚠️  Görselleştirilecek sayısal sütun bulunamadı.")
            return None
        
        df_copy = df_copy.sort_values(date_col)
        
        fig, ax = plt.subplots(figsize=figsize)
        
        for col in value_cols:
            if col in df_copy.columns:
                ax.plot(df_copy[date_col], df_copy[col], marker='o', 
                       markersize=3, linewidth=2, label=col, alpha=0.8)
        
        ax.set_title('Zaman Serisi Analizi', fontsize=14, fontweight='bold')
        ax.set_xlabel('Tarih', fontsize=11)
        ax.set_ylabel('Değer', fontsize=11)
        ax.legend(loc='best', fontsize=10)
        ax.grid(alpha=0.3)
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        filepath = f'{self.save_dir}/time_series.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Zaman serisi grafiği kaydedildi: {filepath}")
        return filepath
    
    def plot_scatter_matrix(self, cols: List[str] = None, max_cols: int = 5, 
                           figsize: Tuple[int, int] = (12, 12)):
        """
        Scatter plot matrisi (değişkenler arası ilişki).
        """
        if cols is None:
            cols = self.numeric_cols[:max_cols]
        
        if len(cols) < 2:
            print("⚠️  En az 2 sayısal sütun gerekli.")
            return None
        
        fig = plt.figure(figsize=figsize)
        pd.plotting.scatter_matrix(self.df[cols], alpha=0.6, figsize=figsize, 
                                  diagonal='kde', color='steelblue', 
                                  hist_kwds={'edgecolor': 'black', 'alpha': 0.7})
        
        plt.suptitle('Scatter Plot Matrisi', fontsize=14, fontweight='bold', y=0.995)
        
        filepath = f'{self.save_dir}/scatter_matrix.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Scatter matrix kaydedildi: {filepath}")
        return filepath
    
    def generate_all_plots(self):
        """Tüm grafikleri otomatik üretir."""
        print("\n🎨 Görselleştirmeler oluşturuluyor...\n")
        
        plots = {}
        
        # 1. Dağılım grafikleri
        if self.numeric_cols:
            plots['distributions'] = self.plot_distributions()
        
        # 2. Kategorik grafikler
        if self.categorical_cols:
            plots['categorical'] = self.plot_categorical()
        
        # 3. Korelasyon
        if len(self.numeric_cols) >= 2:
            plots['correlation'] = self.plot_correlation_heatmap()
        
        # 4. Boxplots
        if self.numeric_cols:
            plots['boxplots'] = self.plot_boxplots()
        
        # 5. Scatter matrix (ilk 5 sütun)
        if len(self.numeric_cols) >= 2:
            plots['scatter_matrix'] = self.plot_scatter_matrix()
        
        print(f"\n✅ Toplam {len([p for p in plots.values() if p])} görsel oluşturuldu.\n")
        
        return plots


# Test
if __name__ == "__main__":
    pass
