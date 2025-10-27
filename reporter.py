"""
AutoInsight - PDF Rapor Oluşturma Modülü
Profesyonel PDF raporları üretir (sadece Pro ve Business paketlerde)
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import pandas as pd
from typing import Dict, List
import os

class ReportGenerator:
    """PDF rapor oluşturucu sınıfı."""
    
    def __init__(self, package: str = 'pro'):
        self.package = package.lower()
        
        if self.package not in ['pro', 'business']:
            raise ValueError("PDF raporları sadece Pro ve Business paketlerinde kullanılabilir!")
        
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Özel stil tanımlamaları."""
        # Başlık stilleri
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a365d'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c5282'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=10
        ))
    
    def generate_report(self, filename: str, metadata: Dict, stats: pd.DataFrame,
                       insights: List[str], plots: Dict, cat_analysis: Dict = None,
                       correlation_info: List = None):
        """
        Kapsamlı PDF raporu oluşturur.
        
        Args:
            filename: Çıktı dosya adı
            metadata: Veri seti meta bilgileri
            stats: Betimleyici istatistikler DataFrame
            insights: Otomatik içgörüler listesi
            plots: Grafik dosya yolları dict
            cat_analysis: Kategorik analiz sonuçları
            correlation_info: Güçlü korelasyonlar listesi
        """
        doc = SimpleDocTemplate(filename, pagesize=A4,
                               rightMargin=50, leftMargin=50,
                               topMargin=50, bottomMargin=50)
        
        story = []
        
        # ============ KAPAK SAYFA ============
        story.append(Spacer(1, 1.5*inch))
        
        title = Paragraph("AutoInsight<br/>Veri Analiz Raporu", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        # Meta bilgiler
        meta_text = f"""
        <b>Dosya:</b> {metadata.get('filename', 'N/A')}<br/>
        <b>Tarih:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>
        <b>Paket:</b> {self.package.upper()}<br/>
        <b>Boyut:</b> {metadata.get('rows', 0):,} satır × {metadata.get('columns', 0)} sütun<br/>
        <b>Hafıza:</b> {metadata.get('memory_usage_mb', 0):.2f} MB
        """
        story.append(Paragraph(meta_text, self.styles['CustomBody']))
        story.append(PageBreak())
        
        # ============ YÖNETİCİ ÖZETİ ============
        story.append(Paragraph("📊 Yönetici Özeti", self.styles['CustomHeading2']))
        
        for insight in insights[:5]:  # İlk 5 içgörü
            story.append(Paragraph(f"• {insight}", self.styles['CustomBody']))
        
        story.append(Spacer(1, 0.3*inch))
        story.append(PageBreak())
        
        # ============ BETİMLEYİCİ İSTATİSTİKLER ============
        story.append(Paragraph("📈 Betimleyici İstatistikler", self.styles['CustomHeading2']))
        
        if not stats.empty:
            # İstatistik tablosunu hazırla
            table_data = [['Değişken', 'Ortalama', 'Std', 'Min', 'Maks', 'Eksik %']]
            
            for idx, row in stats.head(15).iterrows():  # İlk 15 değişken
                table_data.append([
                    str(idx)[:20],  # Sütun adı (max 20 karakter)
                    f"{row['mean']:.2f}" if pd.notna(row['mean']) else '-',
                    f"{row['std']:.2f}" if pd.notna(row['std']) else '-',
                    f"{row['min']:.2f}" if pd.notna(row['min']) else '-',
                    f"{row['max']:.2f}" if pd.notna(row['max']) else '-',
                    f"{row['missing_pct']:.1f}%" if pd.notna(row['missing_pct']) else '-'
                ])
            
            table = Table(table_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            
            story.append(table)
        
        story.append(PageBreak())
        
        # ============ KATEGORİK ANALİZ ============
        if cat_analysis:
            story.append(Paragraph("📋 Kategorik Değişken Analizi", self.styles['CustomHeading2']))
            
            for col, info in list(cat_analysis.items())[:5]:  # İlk 5 kategorik değişken
                story.append(Paragraph(f"<b>{col}</b>", self.styles['CustomBody']))
                story.append(Paragraph(
                    f"Benzersiz değer sayısı: {info['unique_count']}<br/>"
                    f"En sık: {info['most_common']} ({info['concentration']:.1f}%)",
                    self.styles['CustomBody']
                ))
                story.append(Spacer(1, 0.1*inch))
            
            story.append(PageBreak())
        
        # ============ KORELASYON ANALİZİ ============
        if correlation_info and len(correlation_info) > 0:
            story.append(Paragraph("🔗 Güçlü Korelasyonlar", self.styles['CustomHeading2']))
            
            for corr in correlation_info[:10]:  # İlk 10 korelasyon
                story.append(Paragraph(
                    f"• <b>{corr['var1']}</b> ↔ <b>{corr['var2']}</b>: "
                    f"{corr['correlation']:.3f} ({corr['strength']})",
                    self.styles['CustomBody']
                ))
            
            story.append(PageBreak())
        
        # ============ GÖRSELLEŞTİRMELER ============
        story.append(Paragraph("📊 Görselleştirmeler", self.styles['CustomHeading2']))
        
        for plot_name, plot_path in plots.items():
            if plot_path and os.path.exists(plot_path):
                try:
                    # Resmi ekle (sayfa genişliğine sığacak şekilde)
                    img = Image(plot_path, width=6.5*inch, height=4.5*inch)
                    story.append(img)
                    story.append(Spacer(1, 0.2*inch))
                    
                    # Her 2 grafikten sonra sayfa atla
                    if list(plots.keys()).index(plot_name) % 2 == 1:
                        story.append(PageBreak())
                except:
                    pass
        
        # ============ FOOTER ============
        story.append(PageBreak())
        story.append(Spacer(1, 2*inch))
        footer_text = f"""
        <para align=center>
        <i>Bu rapor AutoInsight tarafından otomatik olarak oluşturulmuştur.</i><br/>
        <i>Paket: {self.package.upper()} | Tarih: {datetime.now().strftime('%d/%m/%Y')}</i>
        </para>
        """
        story.append(Paragraph(footer_text, self.styles['BodyText']))
        
        # PDF'i oluştur
        doc.build(story)
        print(f"\n✅ PDF raporu oluşturuldu: {filename}")
        
        return filename


# Test
if __name__ == "__main__":
    pass