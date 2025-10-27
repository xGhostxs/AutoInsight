"""
AutoInsight - Komut Satırı Arayüzü (CLI)
Terminal üzerinden hızlı analiz
"""


import argparse
import sys
import os
from datetime import datetime
from core.loader import DataLoader
from core.cleaner import DataCleaner
from core.analyzer import DataAnalyzer
from core.visualizer import DataVisualizer
from core.reporter import ReportGenerator


def print_header():
    """CLI başlığını yazdır."""
    print("\n" + "="*60)
    print("📊 AutoInsight - Otomatik Veri Analiz Sistemi")
    print("="*60 + "\n")


def print_separator():
    """Ayırıcı çizgi."""
    print("-" * 60)


def analyze_file(filepath: str, package: str = 'free', 
                output_dir: str = 'outputs', 
                generate_pdf: bool = False,
                cleaning_strategy: str = 'auto'):
    """
    Dosya analizi yapar.
    
    Args:
        filepath: Analiz edilecek dosya yolu
        package: Paket tipi (free/pro/business)
        output_dir: Çıktı klasörü
        generate_pdf: PDF raporu oluştur mu?
        cleaning_strategy: Veri temizleme stratejisi
    """
    print_header()
    
    try:
        # 1. VERİ YÜKLEME
        print("📂 Veri yükleniyor...")
        loader = DataLoader(package=package)
        df, metadata = loader.load_data(filepath)
        
        print(f"✅ {metadata['rows']:,} satır × {metadata['columns']} sütun yüklendi")
        print(f"💾 Dosya boyutu: {metadata['size_mb']:.2f} MB")
        print_separator()
        
        # 2. VERİ TEMİZLEME
        print("\n🧹 Veri temizleniyor...")
        cleaner = DataCleaner(df)
        
        # Eksik veri analizi
        missing_stats = cleaner.analyze_missing()
        print(f"⚠️  Toplam eksik veri: %{missing_stats['missing_percentage']:.2f}")
        
        # Temizleme
        cleaner.handle_missing(strategy=cleaning_strategy, threshold=0.5)
        cleaner.detect_outliers()
        
        cleaned_df = cleaner.get_cleaned_data()
        print(f"✅ Temizleme tamamlandı: {len(cleaned_df):,} satır kaldı")
        print_separator()
        
        # 3. ANALİZ
        print("\n🔍 Analiz yapılıyor...")
        analyzer = DataAnalyzer(cleaned_df)
        
        # İstatistikler
        desc_stats = analyzer.descriptive_statistics()
        cat_analysis = analyzer.categorical_analysis()
        corr_matrix, strong_corr = analyzer.correlation_analysis(threshold=0.5)
        insights = analyzer.generate_insights()
        
        # İçgörüleri yazdır
        print("\n💡 Otomatik İçgörüler:")
        for insight in insights:
            print(f"  • {insight}")
        
        # Güçlü korelasyonları yazdır
        if strong_corr:
            print(f"\n🔗 {len(strong_corr)} güçlü korelasyon bulundu:")
            for corr in strong_corr[:5]:  # İlk 5
                print(f"  • {corr['var1']} ↔ {corr['var2']}: "
                      f"{corr['correlation']:.3f} ({corr['strength']})")
        
        print_separator()
        
        # 4. GÖRSELLEŞTİRME
        print("\n🎨 Grafikler oluşturuluyor...")
        os.makedirs(output_dir, exist_ok=True)
        
        visualizer = DataVisualizer(cleaned_df, save_dir=output_dir)
        plots = visualizer.generate_all_plots()
        
        print(f"✅ {len([p for p in plots.values() if p])} görsel oluşturuldu")
        print_separator()
        
        # 5. PDF RAPOR (sadece Pro/Business)
        if generate_pdf:
            if package == 'free':
                print("\n⚠️  PDF rapor özelliği sadece Pro ve Business paketlerinde mevcuttur!")
            else:
                print("\n📄 PDF raporu oluşturuluyor...")
                
                reporter = ReportGenerator(package=package)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                pdf_filename = f"{output_dir}/AutoInsight_Report_{timestamp}.pdf"
                
                reporter.generate_report(
                    filename=pdf_filename,
                    metadata=metadata,
                    stats=desc_stats,
                    insights=insights,
                    plots=plots,
                    cat_analysis=cat_analysis,
                    correlation_info=strong_corr
                )
                
                print(f"✅ PDF raporu: {pdf_filename}")
        
        # ÖZET
        print("\n" + "="*60)
        print("✅ ANALİZ TAMAMLANDI!")
        print("="*60)
        print(f"\n📁 Çıktı klasörü: {output_dir}/")
        print(f"📊 Grafikler: {len([p for p in plots.values() if p])} adet")
        if generate_pdf and package != 'free':
            print(f"📄 PDF raporu: Oluşturuldu")
        print()
        
    except Exception as e:
        print(f"\n❌ HATA: {str(e)}")
        sys.exit(1)


def main():
    """CLI ana fonksiyonu."""
    parser.add_argument('--output', '-o',
                       default='outputs',
                       help='Çıktı klasörü (default: outputs)')
    
    parser.add_argument('--pdf',
                       action='store_true',
                       help='PDF raporu oluştur (Pro/Business gerekli)')
    
    parser.add_argument('--strategy', '-s',
                       choices=['auto', 'drop', 'mean', 'median', 'mode'],
                       default='auto',
                       help='Eksik veri temizleme stratejisi (default: auto)')
    
    parser.add_argument('--version', '-v',
                       action='version',
                       version='AutoInsight v1.0.0')
    
    # Argümanları parse et
    args = parser.parse_args()
    
    # Dosya kontrolü
    if not os.path.exists(args.file):
        print(f"❌ HATA: Dosya bulunamadı: {args.file}")
        sys.exit(1)
    
    # Analizi başlat
    analyze_file(
        filepath=args.file,
        package=args.package,
        output_dir=args.output,
        generate_pdf=args.pdf,
        cleaning_strategy=args.strategy
    )


if __name__ == "__main__":
    main()
    parser = argparse.ArgumentParser(
        description='AutoInsight - Otomatik Veri Analiz Sistemi',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  # Basit analiz
  python cli.py data.csv
  
  # Pro paket ile PDF raporu
  python cli.py data.xlsx --package pro --pdf
  
  # Özel çıktı klasörü
  python cli.py data.json --output my_analysis --strategy median
  
  # Business paket, tüm özellikler
  python cli.py large_data.csv --package business --pdf --strategy auto
        """
    )
    
    # Zorunlu argümanlar
    parser.add_argument('file', 
                       help='Analiz edilecek veri dosyası (CSV, Excel, JSON)')
    
    # Opsiyonel argümanlar
    parser.add_argument('--package', '-p',
                       choices=['free', 'pro', 'business'],
                       default='free',
                       help='Paket tipi (default: free)')
    
    parser