# 📊 AutoInsight - Otomatik Veri Analiz Sistemi

AutoInsight, veri dosyalarınızı yükleyerek otomatik olarak analiz eden, görselleştiren ve profesyonel PDF raporları oluşturan bir sistemdir.

## 🚀 Özellikler

### ✅ Tüm Paketlerde
- 📂 Çoklu format desteği (CSV, Excel, JSON, Parquet)
- 🔍 Otomatik veri temizleme
- 📊 Betimleyici istatistikler
- 📈 Korelasyon analizi
- 💡 Otomatik içgörüler
- 🎨 İnteraktif dashboard

### 💎 Pro/Business Paketlerinde
- 📄 Profesyonel PDF raporları
- 📧 E-posta ile rapor gönderimi
- 🔄 Çoklu dosya analizi (Business)
- ☁️ Bulut depolama entegrasyonu (Business)

## 📦 Paket Karşılaştırması

| Özellik | Free | Pro | Business |
|---------|------|-----|----------|
| **Veri Limiti** | 2.5 MB | 25 MB | 200 MB |
| **Dashboard** | ✅ | ✅ | ✅ |
| **PDF Rapor** | ❌ | ✅ | ✅ |
| **Çoklu Dosya** | ❌ | ❌ | ✅ |
| **Fiyat** | Ücretsiz | 3$/ay | 15$/ay |

## 🛠️ Kurulum

### 1. Repoyu klonlayın
```bash
git clone https://github.com/yourusername/autoinsight.git
cd autoinsight
```

### 2. Sanal ortam oluşturun (önerilir)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Gerekli kütüphaneleri yükleyin
```bash
pip install -r requirements.txt
```

## 🎯 Kullanım

### Streamlit Web Arayüzü ile
```bash
streamlit run app.py
```

Tarayıcınızda `http://localhost:8501` adresine gidin.

### Python Scripti olarak

```python
from core.loader import DataLoader
from core.cleaner import DataCleaner
from core.analyzer import DataAnalyzer
from core.visualizer import DataVisualizer
from core.reporter import ReportGenerator

# 1. Veri yükle
loader = DataLoader(package='pro')
df, metadata = loader.load_data('veri.csv')

# 2. Temizle
cleaner = DataCleaner(df)
cleaner.handle_missing(strategy='auto')
cleaned_df = cleaner.get_cleaned_data()

# 3. Analiz et
analyzer = DataAnalyzer(cleaned_df)
desc_stats = analyzer.descriptive_statistics()
insights = analyzer.generate_insights()
corr_matrix, strong_corr = analyzer.correlation_analysis()

# 4. Görselleştir
visualizer = DataVisualizer(cleaned_df)
plots = visualizer.generate_all_plots()

# 5. PDF raporu oluştur (Pro/Business)
reporter = ReportGenerator(package='pro')
reporter.generate_report(
    filename='rapor.pdf',
    metadata=metadata,
    stats=desc_stats,
    insights=insights,
    plots=plots,
    correlation_info=strong_corr
)
```

## 📁 Proje Yapısı

```
autoinsight/
│
├── app.py                    # Streamlit ana uygulaması
├── requirements.txt          # Python bağımlılıkları
├── README.md                # Bu dosya
│
├── core/                    # Ana modüller
│   ├── __init__.py
│   ├── loader.py            # Veri yükleme
│   ├── cleaner.py           # Veri temizleme
│   ├── analyzer.py          # İstatistiksel analiz
│   ├── visualizer.py        # Görselleştirme
│   └── reporter.py          # PDF rapor oluşturma
│
├── examples/                # Örnek veri dosyaları
│   └── sample_data.csv
│
└── outputs/                 # Çıktı dosyaları (otomatik oluşur)
    ├── *.png               # Grafikler
    └── *.pdf               # PDF raporları
```

## 🔧 Ayarlar

### Veri Temizleme Stratejileri

```python
cleaner.handle_missing(strategy='auto')  # Otomatik (önerilen)
cleaner.handle_missing(strategy='drop')  # Eksik satırları sil
cleaner.handle_missing(strategy='mean')  # Ortalama ile doldur
cleaner.handle_missing(strategy='median')  # Medyan ile doldur
```

### Korelasyon Analizi

```python
# Pearson korelasyonu
corr_matrix, strong = analyzer.correlation_analysis(method='pearson', threshold=0.7)

# Spearman korelasyonu (non-linear ilişkiler için)
corr_matrix, strong = analyzer.correlation_analysis(method='spearman', threshold=0.7)
```

### Görselleştirme Özelleştirme

```python
visualizer = DataVisualizer(df, save_dir='my_outputs')

# Sadece dağılım grafikleri
visualizer.plot_distributions(max_cols=12, figsize=(18, 12))

# Korelasyon haritası
visualizer.plot_correlation_heatmap(figsize=(14, 12), method='spearman')

# Tüm grafikleri oluştur
all_plots = visualizer.generate_all_plots()
```

## 📊 Desteklenen Veri Formatları

- ✅ **CSV** (.csv, .txt) - virgül/tab ayırıcılı
- ✅ **Excel** (.xlsx, .xls)
- ✅ **JSON** (.json)
- ✅ **Parquet** (.parquet) - hızlı ve kompakt

## 🎨 Üretilen Grafikler

1. **Dağılım Grafikleri**: Histogram + KDE eğrileri
2. **Kategorik Grafikler**: Bar chart + yüzde göstergesi
3. **Korelasyon Haritası**: Isı haritası (heatmap)
4. **Boxplot Grafikleri**: Outlier tespiti
5. **Zaman Serisi**: Trend analizi (tarih sütunu varsa)
6. **Scatter Matrix**: Değişkenler arası ilişki

## 📄 PDF Rapor İçeriği

1. 📊 **Yönetici Özeti**: Otomatik içgörüler
2. 📈 **Betimleyici İstatistikler**: Ortalama, std, min, max, vb.
3. 📋 **Kategorik Analiz**: En sık değerler, dağılımlar
4. 🔗 **Korelasyon Analizi**: Güçlü ilişkiler
5. 📊 **Görselleştirmeler**: Tüm grafikler yüksek çözünürlükte
6. 💡 **Öneriler**: Veri kalitesi ve gelecek adımlar

## 🔒 Güvenlik ve Gizlilik

- ✅ Verileriniz yalnızca yerel ortamınızda işlenir
- ✅ Harici sunucuya veri gönderilmez
- ✅ Çıktı dosyaları sadece sizin kontrolünüzde

## 🐛 Sorun Giderme

### "Module not found" hatası
```bash
pip install -r requirements.txt --upgrade
```

### Encoding hatası
```bash
# loader.py otomatik encoding tespiti yapar, ancak manuel belirtmek için:
loader.load_data('dosya.csv', encoding='utf-8')
```

### Bellek hatası (büyük dosyalar)
```python
# Sadece ilk N satırı yükle
loader.load_data('dosya.csv', nrows=100000)

# Veya belirli sütunları yükle
loader.load_data('dosya.csv', usecols=['sutun1', 'sutun2'])
```

## 📞 Destek

- 📧 Email: e.cankat.sumer@gmail.com


## 📝 Lisans

MIT License - Detaylar için LICENSE dosyasına bakın.

## 🙏 Katkıda Bulunma

Pull request'ler memnuniyetle karşılanır! Büyük değişiklikler için lütfen önce bir issue açın.

## 🎉 Teşekkürler

AutoInsight'ı kullandığınız için teşekkürler! ⭐ vermeyi unutmayın.

---

**Made with ❤️ by AutoInsight Team**
