"""
AutoInsight - Öğrenci Doğrulama Sistemi
.edu uzantılı e-mailler ve öğrenci kimlik doğrulama
"""

import streamlit as st
import re
from datetime import datetime, timedelta

class StudentVerification:
    """Öğrenci doğrulama ve indirim yönetimi."""
    
    # Türk üniversiteleri e-mail uzantıları
    TURKISH_EDU_DOMAINS = [
        'edu.tr',           # Genel .edu.tr
        'std.yeditepe.edu.tr',
        'stu.khas.edu.tr',
        'ogr.iu.edu.tr',    # İstanbul Üniversitesi
        'std.iyte.edu.tr',  # İzmir Yüksek Teknoloji
        'ogr.deu.edu.tr',   # Dokuz Eylül
        'std.boun.edu.tr',  # Boğaziçi
        'metu.edu.tr',      # ODTÜ
        'itu.edu.tr',       # İTÜ
        'sabanciuniv.edu',  # Sabancı
        'ku.edu.tr',        # Koç
        'bilkent.edu.tr',   # Bilkent
        'hacettepe.edu.tr', # Hacettepe
        'ankara.edu.tr',    # Ankara Üniversitesi
        'gazi.edu.tr',      # Gazi
        'ege.edu.tr',       # Ege
        'marmara.edu.tr',   # Marmara
        'yildiz.edu.tr',    # Yıldız Teknik
        'baskent.edu.tr',   # Başkent
        'atilim.edu.tr',    # Atılım
        'cankaya.edu.tr',   # Çankaya
        'tobb.edu.tr',      # TOBB ETÜ
        'etu.edu.tr',       # TOBB ETÜ alternatif
        'ozyegin.edu.tr',   # Özyeğin
        'bahcesehir.edu.tr',# Bahçeşehir
        'medipol.edu.tr',   # İstanbul Medipol
        'beykent.edu.tr',   # Beykent
        'maltepe.edu.tr',   # Maltepe
        'gelisim.edu.tr',   # İstanbul Gelişim
        'aydin.edu.tr',     # İstanbul Aydın
        'fsm.edu.tr',       # Fatih Sultan Mehmet
        'altinbas.edu.tr',  # Altınbaş
        'uskudar.edu.tr',   # Üsküdar
        'rumeli.edu.tr',    # İstanbul Rumeli
        'dogus.edu.tr',     # Doğuş
        'kemerburgaz.edu.tr', # Kemerburgaz
        'izmir.edu.tr',     # İzmir Ekonomi
        'yasar.edu.tr',     # Yaşar
        'okan.edu.tr',      # Okan
    ]
    
    # Uluslararası .edu uzantıları
    INTERNATIONAL_EDU_DOMAINS = [
        'edu',              # ABD ve diğer ülkeler
        'ac.uk',            # İngiltere
        'edu.au',           # Avustralya
        'edu.cn',           # Çin
        'ac.jp',            # Japonya
        'edu.sg',           # Singapur
        'edu.my',           # Malezya
        'ac.nz',            # Yeni Zelanda
    ]
    
    # Öğrenci indirimleri
    STUDENT_DISCOUNTS = {
        'pro': {
            'original_price': 9,
            'student_price': 4.99,
            'discount_percent': 45
        },
        'business': {
            'original_price': 29,
            'student_price': 14.99,
            'discount_percent': 48
        }
    }
    
    @staticmethod
    def is_student_email(email: str) -> tuple:
        """
        E-mail'in öğrenci e-maili olup olmadığını kontrol eder.
        
        Returns:
            (is_student: bool, university: str, reason: str)
        """
        email = email.lower().strip()
        
        # Türk üniversiteleri kontrolü
        for domain in StudentVerification.TURKISH_EDU_DOMAINS:
            if email.endswith('@' + domain) or '@' + domain in email:
                # Üniversite adını domain'den çıkar
                uni_parts = domain.replace('.edu.tr', '').replace('std.', '').replace('ogr.', '').replace('stu.', '')
                uni_name = uni_parts.split('.')[0].upper()
                return True, uni_name, f"✅ Türk üniversitesi e-maili tespit edildi"
        
        # Uluslararası .edu kontrolü
        for domain in StudentVerification.INTERNATIONAL_EDU_DOMAINS:
            if email.endswith('.' + domain) or '@' + domain in email:
                return True, "International University", f"✅ Uluslararası eğitim kurumu e-maili"
        
        return False, "", "❌ Öğrenci e-maili değil"
    
    @staticmethod
    def verify_with_document(uploaded_file) -> tuple:
        """
        Öğrenci belgesi ile doğrulama (manuel onay gerektirir).
        
        Returns:
            (success: bool, message: str)
        """
        if uploaded_file is not None:
            # Dosya formatı kontrolü
            if uploaded_file.type not in ['image/jpeg', 'image/png', 'application/pdf']:
                return False, "❌ Sadece JPG, PNG veya PDF dosyaları kabul edilir"
            
            # Dosya boyutu kontrolü (max 5MB)
            if uploaded_file.size > 5 * 1024 * 1024:
                return False, "❌ Dosya boyutu 5MB'dan küçük olmalıdır"
            
            # Başvuru kaydet (gerçek uygulamada Firebase/Database'e kaydedilir)
            return True, "✅ Belgeniz alındı! 24 saat içinde incelenecektir."
        
        return False, "❌ Lütfen bir belge yükleyin"
    
    @staticmethod
    def get_student_price(package: str) -> dict:
        """Öğrenci fiyatını getirir."""
        return StudentVerification.STUDENT_DISCOUNTS.get(package, {})
    
    @staticmethod
    def save_student_status(db, user_email: str, is_student: bool, university: str = ""):
        """Kullanıcının öğrenci durumunu kaydeder."""
        try:
            user_docs = db.collection('users').where('email', '==', user_email).limit(1).stream()
            
            for doc in user_docs:
                doc.reference.update({
                    'is_student': is_student,
                    'university': university,
                    'student_verified_at': datetime.now(),
                    'student_discount_active': is_student
                })
            
            return True
        except:
            return False


def show_student_verification_page():
    """Öğrenci doğrulama sayfası."""
    st.title("🎓 Öğrenci İndirimi")
    
    st.markdown("""
    ### 🎉 Öğrencilere Özel %45-48 İndirim!
    
    Üniversite öğrencileri için özel fiyatlarımız:
    - **Pro Paket**: ~~$9/ay~~ → **$4.99/ay** (%45 indirim)
    - **Business Paket**: ~~$29/ay~~ → **$14.99/ay** (%48 indirim)
    
    ---
    
    ### ✅ Kimler Başvurabilir?
    - Lisans/Ön Lisans öğrencileri
    - Yüksek Lisans öğrencileri
    - Doktora öğrencileri
    - Aktif kayıtlı öğrenciler
    """)
    
    st.markdown("---")
    
    # Doğrulama yöntemleri
    verification_method = st.radio(
        "Doğrulama Yöntemi Seçin:",
        ["📧 Üniversite E-maili ile", "📄 Öğrenci Belgesi ile"]
    )
    
    if verification_method == "📧 Üniversite E-maili ile":
        st.subheader("E-mail Doğrulama")
        st.info("💡 .edu veya .edu.tr uzantılı üniversite e-mailinizi kullanın")
        
        student_email = st.text_input("Üniversite E-mailiniz", placeholder="ad.soyad@universite.edu.tr")
        
        if st.button("Doğrula", type="primary"):
            if student_email:
                is_student, university, message = StudentVerification.is_student_email(student_email)
                
                if is_student:
                    st.success(message)
                    st.balloons()
                    
                    # Üniversite bilgisi
                    st.markdown(f"### 🎓 {university}")
                    
                    # İndirimli fiyatlar
                    st.markdown("### 💰 İndirimli Fiyatlarınız")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        pro_price = StudentVerification.get_student_price('pro')
                        st.markdown(f"""
                        **🚀 Pro Paket**
                        
                        - ~~${pro_price['original_price']}/ay~~
                        - **${pro_price['student_price']}/ay**
                        - 🎓 %{pro_price['discount_percent']} öğrenci indirimi
                        
                        **İçerik:**
                        - 25 MB veri limiti
                        - PDF raporlar
                        - Gelişmiş analizler
                        - Öncelikli destek
                        """)
                        if st.button("Pro'ya Geç (Öğrenci)", key="student_pro"):
                            st.session_state['selected_package'] = 'pro_student'
                            st.info("💳 Stripe ödeme sayfasına yönlendiriliyorsunuz...")
                    
                    with col2:
                        business_price = StudentVerification.get_student_price('business')
                        st.markdown(f"""
                        **💼 Business Paket**
                        
                        - ~~${business_price['original_price']}/ay~~
                        - **${business_price['student_price']}/ay**
                        - 🎓 %{business_price['discount_percent']} öğrenci indirimi
                        
                        **İçerik:**
                        - 200 MB veri limiti
                        - Çoklu dosya
                        - API erişimi
                        - Özel destek
                        """)
                        if st.button("Business'a Geç (Öğrenci)", key="student_business"):
                            st.session_state['selected_package'] = 'business_student'
                            st.info("💳 Stripe ödeme sayfasına yönlendiriliyorsunuz...")
                    
                    # Session state'e kaydet
                    st.session_state['is_student'] = True
                    st.session_state['student_email'] = student_email
                    st.session_state['university'] = university
                    
                    st.markdown("---")
                    st.success("✅ Öğrenci durumunuz doğrulandı! Artık indirimli fiyatlardan yararlanabilirsiniz.")
                else:
                    st.error(message)
                    st.warning("📄 Alternatif olarak öğrenci belgeniz ile doğrulama yapabilirsiniz.")
            else:
                st.warning("⚠️ Lütfen e-mail adresinizi girin")
    
    else:  # Belge ile doğrulama
        st.subheader("Öğrenci Belgesi ile Doğrulama")
        
        st.markdown("""
        ### 📋 Kabul Edilen Belgeler:
        - ✅ Öğrenci Kimlik Kartı (her iki yüzü)
        - ✅ Öğrenci belgesi (transkript, kayıt belgesi)
        - ✅ Aktif dönem için geçerli olmalı
        - ✅ Ad soyad ve üniversite bilgileri net görünmeli
        
        **Format:** JPG, PNG veya PDF (Max 5MB)
        """)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Ad Soyad *", key="student_name")
            email = st.text_input("E-mail *", key="student_doc_email")
        
        with col2:
            university = st.text_input("Üniversite *", key="university_name")
            student_no = st.text_input("Öğrenci No", key="student_no")
        
        st.markdown("---")
        
        uploaded_file = st.file_uploader(
            "📎 Öğrenci Belgenizi Yükleyin *",
            type=['jpg', 'jpeg', 'png', 'pdf'],
            help="Belgeniz gizli tutulacak ve sadece doğrulama için kullanılacaktır"
        )
        
        # Önizleme
        if uploaded_file:
            if uploaded_file.type.startswith('image'):
                st.image(uploaded_file, caption="Yüklenen Belge Önizleme", use_container_width=True)
            else:
                st.success(f"✅ PDF yüklendi: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
        
        st.markdown("---")
        
        agree = st.checkbox("Bilgilerimin doğru olduğunu ve belgenin gerçek olduğunu onaylıyorum")
        
        if st.button("📤 Başvuru Gönder", type="primary", disabled=not agree):
            if not (name and email and university and uploaded_file):
                st.error("❌ Lütfen tüm zorunlu alanları doldurun!")
            else:
                success, message = StudentVerification.verify_with_document(uploaded_file)
                
                if success:
                    st.success(message)
                    st.balloons()
                    st.info("📧 Doğrulama sonucu 24 saat içinde e-mailinize gönderilecektir.")
                    
                    # Başvuru bilgilerini göster
                    st.markdown("""
                    ### ⏳ Sonraki Adımlar:
                    
                    1. **İnceleme**: Belgeniz 24 saat içinde incelenecek
                    2. **E-mail**: Onay/Red kararı e-mailinize gönderilecek
                    3. **Aktivasyon**: Onay sonrası öğrenci indirimi otomatik aktif olacak
                    4. **Süre**: Öğrenci indirimi mezuniyet tarihine kadar geçerli
                    
                    ### 📞 Destek
                    Sorularınız için: student@autoinsight.com
                    """)
                else:
                    st.error(message)


def show_student_pricing_banner():
    """Ana sayfada öğrenci indirimi banner'ı."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 🎓 Öğrenci misiniz?
    
    **%45-48 indirim** kazanın!
    
    - Pro: ~~$9~~ → **$4.99/ay**  
    - Business: ~~$29~~ → **$14.99/ay**
    
    .edu veya .edu.tr uzantılı e-mailinizle hemen başvurun!
    """)
    
    if st.sidebar.button("🎓 Öğrenci İndirimi Al", use_container_width=True):
        st.session_state['show_student_page'] = True
        st.rerun()