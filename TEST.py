"""
AutoInsight - Test ve Örnek Kullanım Scripti
Sistem testi ve örnek veri setleri ile demo
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

from core.loader import DataLoader
from core.cleaner import DataCleaner
from core.analyzer import DataAnalyzer
from core.visualizer import DataVisualizer
from core.reporter import ReportGenerator


def generate_sample_data(filename='examples/sample_data.csv', n_rows=1000):
    """
    Test için örnek veri seti oluşturur.
    
    Args:
        filename: Kaydedilecek dosya adı
        n_rows: Satır sayısı
    """
    print(f"📊 Örnek veri seti oluşturuluyor ({n_rows} satır)...")
    
    np.random.seed(42)
    
    # Tarih aralığı
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(n_rows)]
    
    # Veri seti
    data = {
        'tarih': dates,
        'satis': np.random.normal(1000, 200, n_rows).astype(int),
        'maliyet': np.random.normal(600, 150, n_rows).astype(int),
        'kar': None,  # Hesaplanacak
        'musteri_sayisi': np.random.poisson(50, n_rows),
        'ortalama_siparis': np.random.normal(150, 30, n_rows).round(2),
        'iade_orani': np.random.uniform(0.02, 0.15, n_rows).round(3),
        'kategori': np.random.choice(['Elektronik', 'Giyim', 'Gıda', 'Ev', 'Spor'], n_rows),
        'bolge': np.random.choice(['Istanbul', 'Ankara', 'Izmir', 'Bursa', 'Antalya'], n_rows),
        'kampanya': np.random.choice([True, False], n_rows, p=[0.3, 0.7]),
        'puan': np.random.uniform(1, 5, n_rows).round(1)
    }
    
    df = pd.DataFrame(data)
    
    # Kar hesapla
    df['kar'] = df['satis'] - df['maliyet']
    
    # Bazı eksik veriler ekle (gerçekçi olsun)
    missing_indices = np.random.choice(df.index, size=int(n_rows * 0.05), replace=False)
    df.loc[missing_indices, 'ortalama_siparis'] = np.nan
    
    missing_indices = np.random.choice(df.index, size=int(n_rows * 0.03), replace=False)
    df.loc[missing_indices, 'puan'] = np.nan
    
    # Bazı outlierlar ekle
    outlier_indices = np.random.choice(df.index, size=int(n_rows * 0.02), replace=False)
    df.loc[outlier_indices, 'satis'] = df.loc[outlier_indices, 'satis'] * 3
    
    # Kaydet
    os.makedirs('examples', exist_ok=True)
    df.to_csv(filename, index=False, encoding='utf-8')
    
    print(f"✅ Örnek veri kaydedildi: {filename}")
    print(f"   • {len(df):,} satır × {len(df.columns)} sütun")
    print(f"   • Eksik veri: %{(df.isna().sum().sum() / df.size * 100):.1f}")
    print(f"   • Kategorik: {len([c for c in df.columns if df[c].dtype == 'object'])}")
    print(f"   • Sayısal: {len(df.select_dtypes(include=[np.number]).columns)}")
    print()
    
    return df


def test_full_pipeline(package='pro'):
    """
    Tüm pipeline'ı test eder.
    
    Args:
        package: Test edilecek paket (free/pro/business)
    """
    print("\n" + "="*70)
    print(f"🧪 AutoInsight Pipeline Testi ({package.upper()} paketi)")
    print("="*70 + "\n")
    
    # 1. Örnek veri oluştur
    sample_file = 'examples/sample_data.csv'
    if not os.path.exists(sample_file):
        generate_sample_data(sample_file)
    
    try:
        # 2. VERİ YÜKLEME TESTİ
        print("📂 Test 1: Veri Yükleme")
        print("-" * 70)
        
        loader = DataLoader(package=package)
        df, metadata = loader.load_data(sample_file)
        
        print(f"✅ Veri yüklendi: {metadata['rows']:,} × {metadata['columns']}")
        print(f"   Dosya boyutu: {metadata['size_mb']:.2f} MB")
        print(f"   Bellek kullanımı: {metadata['memory_usage_mb']:.2f} MB")
        print()
        
        # 3. VERİ TEMİZLEME TESTİ
        print("🧹 Test 2: Veri Temizleme")
        print("-" * 70)
        
        cleaner = DataCleaner(df)
        
        # Eksik veri analizi
        missing_stats = cleaner.analyze_missing()
        print(f"   Eksik veri oranı: %{missing_stats['missing_percentage']:.2f}")
        print(f"   Eksik veri içeren sütunlar: {len(missing_stats['columns_with_missing'])}")
        
        # Temizleme
        cleaner.handle_missing(strategy='auto', threshold=0.5)
        outliers = cleaner.detect_outliers()
        
        cleaned_df = cleaner.get_cleaned_data()
        
        print(f"✅ Temizleme tamamlandı")
        print(f"   Yeni boyut: {len(cleaned_df):,} × {len(cleaned_df.columns)}")
        print(f"   Outlier tespit edilen sütunlar: {len(outliers)}")
        print()
        
        # 4. ANALİZ TESTİ
        print("🔍 Test 3: Veri Analizi")
        print("-" * 70)
        
        analyzer = DataAnalyzer(cleaned_df)
        
        # İstatistikler
        desc_stats = analyzer.descriptive_statistics()
        print(f"   Betimleyici istatistikler: {len(desc_stats)} sayısal değişken")
        
        # Kategorik analiz
        cat_analysis = analyzer.categorical_analysis()
        print(f"   Kategorik analiz: {len(cat_analysis)} kategorik değişken")
        
        # Korelasyon
        corr_matrix, strong_corr = analyzer.correlation_analysis(threshold=0.5)
        print(f"   Korelasyon matrisi: {corr_matrix.shape}")
        print(f"   Güçlü korelasyonlar: {len(strong_corr)}")
        
        # İçgörüler
        insights = analyzer.generate_insights()
        print(f"   Otomatik içgörüler: {len(insights)}")
        
        print(f"✅ Analiz tamamlandı")
        print()
        
        # 5. GÖRSELLEŞTİRME TESTİ
        print("🎨 Test 4: Görselleştirme")
        print("-" * 70)
        
        visualizer = DataVisualizer(cleaned_df, save_dir='test_outputs')
        plots = visualizer.generate_all_plots()
        
        plot_count = len([p for p in plots.values() if p])
        print(f"✅ {plot_count} görsel oluşturuldu")
        print(f"   Klasör: test_outputs/")
        print()
        
        # 6. PDF RAPOR TESTİ (sadece Pro/Business)
        if package != 'free':
            print("📄 Test 5: PDF Rapor Oluşturma")
            print("-" * 70)
            
            reporter = ReportGenerator(package=package)
            report_file = 'test_outputs/test_report.pdf'
            
            reporter.generate_report(
                filename=report_file,
                metadata=metadata,
                stats=desc_stats,
                insights=insights,
                plots=plots,
                cat_analysis=cat_analysis,
                correlation_info=strong_corr
            )
            
            print(f"✅ PDF raporu oluşturuldu: {report_file}")
            print()
        
        # ÖZET
        print("="*70)
        print("✅ TÜM TESTLER BAŞARIYLA TAMAMLANDI!")
        print("="*70)
        print(f"\n📊 Özet:")
        print(f"   • Veri: {len(cleaned_df):,} satır × {len(cleaned_df.columns)} sütun")
        print(f"   • Sayısal değişkenler: {len(analyzer.numeric_cols)}")
        print(f"   • Kategorik değişkenler: {len(analyzer.categorical_cols)}")
        print(f"   • Güçlü korelasyonlar: {len(strong_corr)}")
        print(f"   • Görseller: {plot_count} adet")
        if package != 'free':
            print(f"   • PDF raporu: ✅ Oluşturuldu")
        print()
        
        # İçgörüleri yazdır
        print("💡 Örnek İçgörüler:")
        for insight in insights[:3]:
            print(f"   • {insight}")
        print()
        
    except Exception as e:
        print(f"\n❌ TEST BAŞARISIZ: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def quick_demo():
    """Hızlı demo."""
    print("\n" + "="*70)
    print("🚀 AutoInsight - Hızlı Demo")
    print("="*70 + "\n")
    
    # Örnek veri oluştur
    sample_file = 'examples/sample_data.csv'
    if not os.path.exists(sample_file):
        df = generate_sample_data(sample_file, n_rows=500)
    else:
        print(f"✅ Mevcut örnek veri kullanılıyor: {sample_file}\n")
    
    print("📊 Demo için çalıştırılabilir komutlar:\n")
    print("1. Streamlit Web Arayüzü:")
    print("   streamlit run app.py\n")
    
    print("2. CLI (Komut Satırı):")
    print("   python cli.py examples/sample_data.csv\n")
    
    print("3. Python Scripti:")
    print("   python test_example.py --test pro\n")
    
    print("4. Sadece örnek veri oluştur:")
    print("   python test_example.py --generate\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='AutoInsight Test ve Demo')
    parser.add_argument('--test', '-t',
                       choices=['free', 'pro', 'business'],
                       help='Pipeline testini çalıştır')
    parser.add_argument('--generate', '-g',
                       action='store_true',
                       help='Sadece örnek veri oluştur')
    parser.add_argument('--rows', '-r',
                       type=int,
                       default=1000,
                       help='Örnek veri satır sayısı (default: 1000)')
    
    args = parser.parse_args()
    
    if args.generate:
        generate_sample_data(n_rows=args.rows)
    elif args.test:
        test_full_pipeline(package=args.test)
    else:
        quick_demo()