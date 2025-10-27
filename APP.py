"""
AutoInsight - Ana Streamlit Uygulaması
Kullanıcı dostu web arayüzü ile otomatik veri analizi
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime

# Core modülleri import et
from core.loader import DataLoader
from core.cleaner import DataCleaner
from core.analyzer import DataAnalyzer
from core.visualizer import DataVisualizer
from core.reporter import ReportGenerator

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="AutoInsight - Otomatik Veri Analizi",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1a365d;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c5282;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f7fafc;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #3182ce;
    }
    .insight-box {
        background-color: #e6fffa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #38b2ac;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Ana uygulama fonksiyonu."""
    
    # Header
    st.markdown('<p class="main-header">📊 AutoInsight</p>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #718096; font-size: 1.2rem;">'
               'Otomatik Veri Analizi ve Raporlama Sistemi</p>', 
               unsafe_allow_html=True)
    
    # Sidebar - Paket seçimi
    st.sidebar.title("⚙️ Ayarlar")
    
    package = st.sidebar.selectbox(
        "📦 Paket Seçin",
        ["Free", "Pro", "Business"],
        help="Free: 2,5 MB, Pro: 25 MB + PDF, Business: 200 MB + Çoklu Rapor"
    )
    
    # Paket bilgileri
    package_info = {
        "Free": {"limit": "2.5 MB", "pdf": "❌"},
        "Pro": {"limit": "25 MB", "pdf": "✅"},
        "Business": {"limit": "200 MB", "pdf": "✅"}
    }
    
    st.sidebar.info(
        f"**{package} Paketi**\n\n"
        f"📦 Veri Limiti: {package_info[package]['limit']}\n\n"
        f"📄 PDF Rapor: {package_info[package]['pdf']}\n\n"
        
    )
    
    st.sidebar.markdown("---")
    
    # Temizleme ayarları
    with st.sidebar.expander("🧹 Temizleme Ayarları"):
        missing_strategy = st.selectbox(
            "Eksik Veri Stratejisi",
            ["auto", "drop", "mean", "median", "mode"],
            help="auto: Sayısal için median, kategorik için mode"
        )
        
        missing_threshold = st.slider(
            "Eksik Veri Eşiği (%)",
            0, 100, 50,
            help="Bu oranın üstünde eksik veri varsa sütunu sil"
        ) / 100
    
    # Görselleştirme ayarları
    with st.sidebar.expander("📊 Görselleştirme Ayarları"):
        show_distributions = st.checkbox("Dağılım Grafikleri", value=True)
        show_categorical = st.checkbox("Kategorik Grafikler", value=True)
        show_correlation = st.checkbox("Korelasyon Haritası", value=True)
        show_boxplots = st.checkbox("Boxplot Grafikleri", value=False)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("💡 **İpucu:** CSV, Excel, JSON formatları desteklenir.")
    
    # Ana içerik
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Veri Yükleme", "📊 Analiz", "📈 Görselleştirme", "📄 Rapor"])
    
    # TAB 1: Veri Yükleme
    with tab1:
        st.markdown('<p class="sub-header">📂 Veri Dosyanızı Yükleyin</p>', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "CSV, Excel veya JSON dosyası seçin",
            type=['csv', 'xlsx', 'xls', 'json'],
            help=f"Maksimum dosya boyutu: {package_info[package]['limit']}"
        )
        
        if uploaded_file is not None:
            try:
                # Geçici dosya kaydet
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Veri yükle
                loader = DataLoader(package=package.lower())
                df, metadata = loader.load_data(temp_path)
                
                # Session state'e kaydet
                st.session_state['df'] = df
                st.session_state['metadata'] = metadata
                st.session_state['package'] = package.lower()
                
                # Geçici dosyayı sil
                os.remove(temp_path)
                
                # Başarı mesajı
                st.success(f"✅ Dosya başarıyla yüklendi!")
                
                # Meta bilgiler
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📏 Satır Sayısı", f"{metadata['rows']:,}")
                
                with col2:
                    st.metric("📋 Sütun Sayısı", metadata['columns'])
                
                with col3:
                    st.metric("💾 Dosya Boyutu", f"{metadata['size_mb']:.2f} MB")
                
                with col4:
                    st.metric("🧠 Bellek Kullanımı", f"{metadata['memory_usage_mb']:.2f} MB")
                
                # Veri önizleme
                st.markdown("### 👀 Veri Önizleme")
                st.dataframe(df.head(10), use_container_width=True)
                
                # Sütun bilgileri
                st.markdown("### 📊 Sütun Bilgileri")
                col_info = pd.DataFrame({
                    'Sütun': df.columns,
                    'Tip': df.dtypes.astype(str),
                    'Eksik': df.isna().sum(),
                    'Eksik %': (df.isna().sum() / len(df) * 100).round(2),
                    'Benzersiz': df.nunique()
                })
                st.dataframe(col_info, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Hata: {str(e)}")
    
    # TAB 2: Analiz
    with tab2:
        if 'df' not in st.session_state:
            st.warning("⚠️ Lütfen önce bir veri dosyası yükleyin!")
        else:
            st.markdown('<p class="sub-header">🔍 Veri Analizi</p>', unsafe_allow_html=True)
            
            df = st.session_state['df']
            
            # Veri temizleme
            if st.button("🧹 Veriyi Temizle", type="primary"):
                with st.spinner("Veriler temizleniyor..."):
                    cleaner = DataCleaner(df)
                    
                    # Eksik veri analizi
                    missing_stats = cleaner.analyze_missing()
                    cleaner.handle_missing(strategy=missing_strategy, threshold=missing_threshold)
                    
                    # Outlier tespiti
                    outliers = cleaner.detect_outliers()
                    
                    # Temizlenmiş veriyi kaydet
                    cleaned_df = cleaner.get_cleaned_data()
                    st.session_state['cleaned_df'] = cleaned_df
                    st.session_state['cleaning_report'] = cleaner.get_report()
                    
                    st.success("✅ Veri temizleme tamamlandı!")
            
            # Temizleme raporu göster
            if 'cleaning_report' in st.session_state:
                report = st.session_state['cleaning_report']
                
                st.markdown("### 📋 Temizleme Raporu")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Eksik Veri Özeti**")
                    missing = report.get('missing_analysis', {})
                    st.write(f"Toplam hücre: {missing.get('total_cells', 0):,}")
                    st.write(f"Eksik hücre: {missing.get('missing_cells', 0):,}")
                    st.write(f"Eksik oran: %{missing.get('missing_percentage', 0):.2f}")
                
                with col2:
                    st.markdown("**Outlier Özeti**")
                    outliers = report.get('outliers', {})
                    if outliers:
                        total_outliers = sum([v['count'] for v in outliers.values()])
                        st.write(f"Toplam outlier: {total_outliers:,}")
                        st.write(f"Etkilenen sütun: {len(outliers)}")
                    else:
                        st.write("Önemli outlier tespit edilmedi")
            
            # Analiz başlat
            if st.button("📊 Detaylı Analiz Yap", type="primary"):
                with st.spinner("Analiz yapılıyor..."):
                    analysis_df = st.session_state.get('cleaned_df', df)
                    analyzer = DataAnalyzer(analysis_df)
                    
                    # Temel istatistikler
                    basic_stats = analyzer.get_basic_stats()
                    desc_stats = analyzer.descriptive_statistics()
                    cat_analysis = analyzer.categorical_analysis()
                    corr_matrix, strong_corr = analyzer.correlation_analysis(threshold=0.5)
                    insights = analyzer.generate_insights()
                    
                    # Session state'e kaydet
                    st.session_state['desc_stats'] = desc_stats
                    st.session_state['cat_analysis'] = cat_analysis
                    st.session_state['corr_matrix'] = corr_matrix
                    st.session_state['strong_corr'] = strong_corr
                    st.session_state['insights'] = insights
                    
                    st.success("✅ Analiz tamamlandı!")
            
            # Analiz sonuçlarını göster
            if 'insights' in st.session_state:
                st.markdown("### 💡 Otomatik İçgörüler")
                
                for insight in st.session_state['insights']:
                    st.markdown(f'<div class="insight-box">{insight}</div>', 
                              unsafe_allow_html=True)
                
                # Betimleyici istatistikler
                if not st.session_state['desc_stats'].empty:
                    st.markdown("### 📈 Betimleyici İstatistikler")
                    st.dataframe(st.session_state['desc_stats'], use_container_width=True)
                
                # Kategorik analiz
                if st.session_state['cat_analysis']:
                    st.markdown("### 📋 Kategorik Değişkenler")
                    
                    for col, info in list(st.session_state['cat_analysis'].items())[:5]:
                        with st.expander(f"📊 {col}"):
                            st.write(f"**Benzersiz değer sayısı:** {info['unique_count']}")
                            st.write(f"**En sık değer:** {info['most_common']}")
                            st.write(f"**Konsantrasyon:** %{info['concentration']:.1f}")
                            
                            # Top 5 değerleri göster
                            st.write("**En Yaygın 5 Değer:**")
                            for val, count in info['top_5_values'].items():
                                st.write(f"- {val}: {count:,}")
                
                # Güçlü korelasyonlar
                if st.session_state['strong_corr']:
                    st.markdown("### 🔗 Güçlü Korelasyonlar")
                    
                    corr_df = pd.DataFrame(st.session_state['strong_corr'])
                    st.dataframe(corr_df, use_container_width=True)
    
    # TAB 3: Görselleştirme
    with tab3:
        if 'df' not in st.session_state:
            st.warning("⚠️ Lütfen önce bir veri dosyası yükleyin!")
        else:
            st.markdown('<p class="sub-header">📊 Görselleştirmeler</p>', unsafe_allow_html=True)
            
            analysis_df = st.session_state.get('cleaned_df', st.session_state['df'])
            
            if st.button("🎨 Grafikleri Oluştur", type="primary"):
                with st.spinner("Grafikler oluşturuluyor..."):
                    visualizer = DataVisualizer(analysis_df, save_dir='outputs')
                    
                    plots = {}
                    
                    if show_distributions and visualizer.numeric_cols:
                        plots['distributions'] = visualizer.plot_distributions()
                    
                    if show_categorical and visualizer.categorical_cols:
                        plots['categorical'] = visualizer.plot_categorical()
                    
                    if show_correlation and len(visualizer.numeric_cols) >= 2:
                        plots['correlation'] = visualizer.plot_correlation_heatmap()
                    
                    if show_boxplots and visualizer.numeric_cols:
                        plots['boxplots'] = visualizer.plot_boxplots()
                    
                    st.session_state['plots'] = plots
                    st.success(f"✅ {len(plots)} görsel oluşturuldu!")
            
            # Grafikleri göster
            if 'plots' in st.session_state:
                plots = st.session_state['plots']
                
                for plot_name, plot_path in plots.items():
                    if plot_path and os.path.exists(plot_path):
                        st.markdown(f"### 📊 {plot_name.replace('_', ' ').title()}")
                        st.image(plot_path, use_container_width=True)
                        st.markdown("---")
    
    # TAB 4: Rapor
    with tab4:
        if 'df' not in st.session_state:
            st.warning("⚠️ Lütfen önce bir veri dosyası yükleyin!")
        else:
            st.markdown('<p class="sub-header">📄 PDF Rapor Oluştur</p>', unsafe_allow_html=True)
            
            package = st.session_state.get('package', 'free')
            
            if package == 'free':
                st.error("❌ PDF rapor özelliği sadece Pro ve Business paketlerinde mevcuttur!")
                st.info("💡 Pro pakete yükseltmek için lütfen bizimle iletişime geçin.")
            else:
                st.success(f"✅ {package.upper()} paketiniz PDF rapor oluşturmaya uygun!")
                
                # Rapor oluştur
                if st.button("📄 PDF Raporu Oluştur", type="primary"):
                    # Gerekli verileri kontrol et
                    if 'desc_stats' not in st.session_state:
                        st.error("⚠️ Lütfen önce 'Analiz' sekmesinden analiz yapın!")
                    elif 'plots' not in st.session_state:
                        st.error("⚠️ Lütfen önce 'Görselleştirme' sekmesinden grafikleri oluşturun!")
                    else:
                        with st.spinner("PDF raporu oluşturuluyor..."):
                            try:
                                reporter = ReportGenerator(package=package)
                                
                                # Rapor dosya adı
                                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                filename = f"AutoInsight_Report_{timestamp}.pdf"
                                filepath = f"outputs/{filename}"
                                
                                # Raporu oluştur
                                reporter.generate_report(
                                    filename=filepath,
                                    metadata=st.session_state['metadata'],
                                    stats=st.session_state['desc_stats'],
                                    insights=st.session_state.get('insights', []),
                                    plots=st.session_state['plots'],
                                    cat_analysis=st.session_state.get('cat_analysis'),
                                    correlation_info=st.session_state.get('strong_corr')
                                )
                                
                                st.success(f"✅ Rapor başarıyla oluşturuldu: {filename}")
                                
                                # İndir butonu
                                with open(filepath, "rb") as f:
                                    st.download_button(
                                        label="📥 Raporu İndir",
                                        data=f,
                                        file_name=filename,
                                        mime="application/pdf"
                                    )
                                
                            except Exception as e:
                                st.error(f"❌ Rapor oluşturulurken hata: {str(e)}")
                
                # Rapor içeriği hakkında bilgi
                with st.expander("📋 Rapor İçeriği"):
                    st.markdown("""
                    **PDF Raporu şunları içerir:**
                    
                    1. 📊 Yönetici Özeti
                    2. 📈 Betimleyici İstatistikler
                    3. 📋 Kategorik Değişken Analizi
                    4. 🔗 Güçlü Korelasyonlar
                    5. 📊 Tüm Görselleştirmeler
                    6. 💡 Otomatik İçgörüler
                    """)


if __name__ == "__main__":
    # Outputs klasörünü oluştur
    os.makedirs("outputs", exist_ok=True)
    
    
    main()
