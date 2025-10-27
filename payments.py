"""
AutoInsight - Ödeme Sistemi
Stripe entegrasyonu ile abonelik yönetimi
"""

import streamlit as st
from datetime import datetime, timedelta

# Stripe import (gerçek uygulamada kullanılacak)
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    st.warning("⚠️ Stripe kütüphanesi yüklü değil. Ödeme özellikleri devre dışı.")

# Stripe API Key (Production'da environment variable olarak saklanmalı)
# stripe.api_key = "sk_test_..." # Test key
# stripe.api_key = "sk_live_..." # Production key

class PaymentManager:
    """Ödeme ve abonelik yönetimi."""
    
    # Fiyatlandırma (Stripe Price ID'leri)
    PRICES = {
        'free': {
            'price_id': None,
            'amount': 0,
            'currency': 'usd',
            'display_price': '$0'
        },
        'pro': {
            'price_id': 'price_1Hh1XXX',  # Stripe'dan alınacak
            'amount': 900,  # cent ($9.00)
            'currency': 'usd',
            'display_price': '$9'
        },
        'pro_student': {
            'price_id': 'price_1Hh1StudentXXX',
            'amount': 499,  # cent ($4.99)
            'currency': 'usd',
            'display_price': '$4.99',
            'discount_percent': 45,
            'original_amount': 900
        },
        'business': {
            'price_id': 'price_1Hh2XXX',
            'amount': 2900,  # cent ($29.00)
            'currency': 'usd',
            'display_price': '$29'
        },
        'business_student': {
            'price_id': 'price_1Hh2StudentXXX',
            'amount': 1499,  # cent ($14.99)
            'currency': 'usd',
            'display_price': '$14.99',
            'discount_percent': 48,
            'original_amount': 2900
        }
    }
    
    @staticmethod
    def create_checkout_session(package: str, user_email: str, is_student: bool = False):
        """
        Stripe checkout oturumu oluşturur.
        
        Args:
            package: 'pro' veya 'business'
            user_email: Kullanıcı e-maili
            is_student: Öğrenci indirimi var mı?
        
        Returns:
            checkout_url: Stripe checkout URL'i
        """
        if not STRIPE_AVAILABLE:
            st.error("❌ Ödeme sistemi şu anda kullanılamıyor.")
            return None
        
        try:
            # Öğrenci indirimi kontrolü
            if is_student and package in ['pro', 'business']:
                package_key = f"{package}_student"
            else:
                package_key = package
            
            price_info = PaymentManager.PRICES.get(package_key)
            
            if not price_info or not price_info.get('price_id'):
                st.error("❌ Geçersiz paket seçimi")
                return None
            
            # Stripe Checkout Session oluştur
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_info['price_id'],
                    'quantity': 1,
                }],
                mode='subscription',
                success_url='https://autoinsight.com/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url='https://autoinsight.com/pricing',
                customer_email=user_email,
                metadata={
                    'package': package,
                    'user_email': user_email,
                    'is_student': str(is_student),
                    'discount_percent': price_info.get('discount_percent', 0)
                },
                subscription_data={
                    'metadata': {
                        'package': package,
                        'is_student': str(is_student)
                    }
                },
                # Öğrenci için kupon kodu
                discounts=[{
                    'coupon': 'STUDENT2024'
                }] if is_student else []
            )
            
            return session.url
        
        except Exception as e:
            st.error(f"❌ Ödeme hatası: {str(e)}")
            return None
    
    @staticmethod
    def verify_subscription(user_email: str):
        """
        Kullanıcının aktif aboneliğini kontrol eder.
        
        Returns:
            package_name: 'free', 'pro', 'business', 'pro_student', 'business_student'
        """
        if not STRIPE_AVAILABLE:
            return 'free'
        
        try:
            # Stripe'dan müşteri bilgilerini al
            customers = stripe.Customer.list(email=user_email, limit=1)
            
            if not customers.data:
                return 'free'
            
            customer = customers.data[0]
            subscriptions = stripe.Subscription.list(
                customer=customer.id,
                status='active',
                limit=1
            )
            
            if subscriptions.data:
                # İlk aktif aboneliği al
                sub = subscriptions.data[0]
                package = sub.metadata.get('package', 'free')
                is_student = sub.metadata.get('is_student', 'False') == 'True'
                
                if is_student and package in ['pro', 'business']:
                    return f"{package}_student"
                
                return package
            
            return 'free'
        
        except Exception as e:
            print(f"Subscription verification error: {str(e)}")
            return 'free'
    
    @staticmethod
    def cancel_subscription(user_email: str):
        """
        Aboneliği iptal eder.
        
        Returns:
            success: bool
        """
        if not STRIPE_AVAILABLE:
            return False
        
        try:
            customers = stripe.Customer.list(email=user_email, limit=1)
            
            if customers.data:
                customer = customers.data[0]
                subscriptions = stripe.Subscription.list(
                    customer=customer.id,
                    status='active'
                )
                
                for sub in subscriptions.data:
                    # Aboneliği dönem sonunda iptal et
                    stripe.Subscription.modify(
                        sub.id,
                        cancel_at_period_end=True
                    )
                
                return True
            
            return False
        
        except Exception as e:
            print(f"Subscription cancellation error: {str(e)}")
            return False
    
    @staticmethod
    def get_subscription_info(user_email: str):
        """
        Abonelik detaylarını getirir.
        
        Returns:
            dict: Abonelik bilgileri
        """
        if not STRIPE_AVAILABLE:
            return None
        
        try:
            customers = stripe.Customer.list(email=user_email, limit=1)
            
            if customers.data:
                customer = customers.data[0]
                subscriptions = stripe.Subscription.list(
                    customer=customer.id,
                    status='active',
                    limit=1
                )
                
                if subscriptions.data:
                    sub = subscriptions.data[0]
                    
                    return {
                        'status': sub.status,
                        'current_period_end': datetime.fromtimestamp(sub.current_period_end),
                        'cancel_at_period_end': sub.cancel_at_period_end,
                        'package': sub.metadata.get('package', 'free'),
                        'is_student': sub.metadata.get('is_student', 'False') == 'True'
                    }
            
            return None
        
        except Exception as e:
            print(f"Subscription info error: {str(e)}")
            return None


def show_pricing_page():
    """Fiyatlandırma sayfasını gösterir."""
    st.title("💎 Paket Seç ve Yükselt")
    
    # Öğrenci durumu kontrolü
    is_student = st.session_state.get('is_student', False)
    
    if is_student:
        st.success(f"🎓 Öğrenci hesabı aktif! %45-48 indirimli fiyatları görüyorsunuz.")
        st.markdown(f"**Üniversite:** {st.session_state.get('university', 'N/A')}")
        st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    # FREE PAKET
    with col1:
        st.markdown("### 🆓 Free")
        st.markdown("**$0/ay**")
        st.markdown("""
        **Özellikler:**
        - ✅ 1 MB veri limiti
        - ✅ Temel analizler
        - ✅ Grafikler
        - ✅ Dashboard
        - ❌ PDF raporlar
        - ❌ Öncelikli destek
        """)
        
        current_package = st.session_state.get('package', 'free')
        if current_package == 'free':
            st.info("✅ Mevcut Paket")
        else:
            if st.button("Free'ye Geç", key="downgrade_free"):
                st.session_state['package'] = 'free'
                st.success("✅ Free pakete geçildi!")
                st.rerun()
    
    # PRO PAKET
    with col2:
        st.markdown("### 🚀 Pro")
        
        if is_student:
            pro_price = PaymentManager.PRICES['pro_student']
            st.markdown(f"~~${PaymentManager.PRICES['pro']['amount']/100}/ay~~")
            st.markdown(f"**${pro_price['amount']/100}/ay**")
            st.caption(f"🎓 %{pro_price['discount_percent']} öğrenci indirimi")
        else:
            st.markdown(f"**${PaymentManager.PRICES['pro']['amount']/100}/ay**")
        
        st.markdown("""
        **Özellikler:**
        - ✅ 25 MB veri limiti
        - ✅ **PDF raporlar**
        - ✅ Gelişmiş analizler
        - ✅ Korelasyon analizi
        - ✅ Öncelikli destek
        - ✅ E-mail desteği
        """)
        
        current_package = st.session_state.get('package', 'free')
        if current_package in ['pro', 'pro_student']:
            st.success("✅ Mevcut Paket")
        else:
            if st.button("Pro'ya Geç", key="upgrade_pro", type="primary"):
                user_email = st.session_state.get('user_email', 'demo@example.com')
                package_type = 'pro_student' if is_student else 'pro'
                
                # Demo için
                if STRIPE_AVAILABLE:
                    checkout_url = PaymentManager.create_checkout_session('pro', user_email, is_student)
                    if checkout_url:
                        st.markdown(f"[🔗 Ödeme Sayfasına Git]({checkout_url})")
                else:
                    st.session_state['package'] = package_type
                    st.success("✅ Pro pakete yükseltildi! (Demo)")
                    st.rerun()
    
    # BUSINESS PAKET
    with col3:
        st.markdown("### 💼 Business")
        
        if is_student:
            business_price = PaymentManager.PRICES['business_student']
            st.markdown(f"~~${PaymentManager.PRICES['business']['amount']/100}/ay~~")
            st.markdown(f"**${business_price['amount']/100}/ay**")
            st.caption(f"🎓 %{business_price['discount_percent']} öğrenci indirimi")
        else:
            st.markdown(f"**${PaymentManager.PRICES['business']['amount']/100}/ay**")
        
        st.markdown("""
        **Özellikler:**
        - ✅ 200 MB veri limiti
        - ✅ **Çoklu dosya**
        - ✅ **API erişimi**
        - ✅ Tüm Pro özellikler
        - ✅ Özel destek (24/7)
        - ✅ Öncelikli işleme
        """)
        
        current_package = st.session_state.get('package', 'free')
        if current_package in ['business', 'business_student']:
            st.success("✅ Mevcut Paket")
        else:
            if st.button("Business'a Geç", key="upgrade_business", type="primary"):
                user_email = st.session_state.get('user_email', 'demo@example.com')
                package_type = 'business_student' if is_student else 'business'
                
                # Demo için
                if STRIPE_AVAILABLE:
                    checkout_url = PaymentManager.create_checkout_session('business', user_email, is_student)
                    if checkout_url:
                        st.markdown(f"[🔗 Ödeme Sayfasına Git]({checkout_url})")
                else:
                    st.session_state['package'] = package_type
                    st.success("✅ Business pakete yükseltildi! (Demo)")
                    st.rerun()
    
    st.markdown("---")
    
    # Özellik karşılaştırma tablosu
    st.subheader("📊 Detaylı Karşılaştırma")
    
    import pandas as pd
    
    comparison_data = {
        'Özellik': [
            'Veri Limiti',
            'PDF Rapor',
            'Grafikler',
            'Korelasyon Analizi',
            'Çoklu Dosya',
            'API Erişimi',
            'Destek',
            'Fiyat',
            'Fiyat (Öğrenci)'
        ],
        'Free': [
            '1 MB',
            '❌',
            '✅',
            '✅',
            '❌',
            '❌',
            'E-mail',
            '$0/ay',
            '$0/ay'
        ],
        'Pro': [
            '25 MB',
            '✅',
            '✅',
            '✅',
            '❌',
            '❌',
            'Öncelikli',
            '$9/ay',
            '$4.99/ay'
        ],
        'Business': [
            '200 MB',
            '✅',
            '✅',
            '✅',
            '✅',
            '✅',
            '24/7',
            '$29/ay',
            '$14.99/ay'
        ]
    }
    
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # SSS
    with st.expander("❓ Sıkça Sorulan Sorular"):
        st.markdown("""
        **1. Ödeme nasıl yapılır?**
        - Kredi kartı ile güvenli Stripe ödeme sistemi üzerinden.
        
        **2. İptal edebilir miyim?**
        - Evet, istediğiniz zaman iptal edebilirsiniz. Ödediğiniz dönem sonuna kadar kullanabilirsiniz.
        
        **3. Öğrenci indirimi nasıl alınır?**
        - .edu veya .edu.tr uzantılı e-mailinizle veya öğrenci belgenizle doğrulama yapın.
        
        **4. Paket değişikliği yapabilir miyim?**
        - Evet, istediğiniz zaman yükseltme/düşürme yapabilirsiniz.
        
        **5. Fatura alabilir miyim?**
        - Evet, her ay otomatik olarak e-mailinize fatura gönderilir.
        
        **6. Öğrenci indirimi ne kadar geçerli?**
        - Mezuniyet tarihine kadar veya öğrenci statüsü doğrulandığı sürece.
        """)


def show_subscription_management():
    """Abonelik yönetim sayfası."""
    st.title("⚙️ Abonelik Yönetimi")
    
    user_email = st.session_state.get('user_email', '')
    current_package = st.session_state.get('package', 'free')
    
    # Mevcut paket bilgisi
    st.markdown("### 📦 Mevcut Paketiniz")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        package_names = {
            'free': '🆓 Free',
            'pro': '🚀 Pro',
            'pro_student': '🚀 Pro (Öğrenci)',
            'business': '💼 Business',
            'business_student': '💼 Business (Öğrenci)'
        }
        
        st.markdown(f"## {package_names.get(current_package, 'Free')}")
        
        if current_package != 'free':
            price_info = PaymentManager.PRICES.get(current_package, {})
            st.markdown(f"**Aylık Ücret:** {price_info.get('display_price', '$0')}")
            
            # Abonelik bilgileri (Stripe'dan gelecek)
            if STRIPE_AVAILABLE:
                sub_info = PaymentManager.get_subscription_info(user_email)
                if sub_info:
                    st.markdown(f"**Durum:** {sub_info['status'].upper()}")
                    st.markdown(f"**Yenileme Tarihi:** {sub_info['current_period_end'].strftime('%d/%m/%Y')}")
                    if sub_info['cancel_at_period_end']:
                        st.warning("⚠️ Aboneliğiniz dönem sonunda iptal edilecek.")
    
    with col2:
        if current_package != 'free':
            if st.button("❌ Aboneliği İptal Et", type="secondary"):
                if st.session_state.get('confirm_cancel', False):
                    if STRIPE_AVAILABLE:
                        success = PaymentManager.cancel_subscription(user_email)
                        if success:
                            st.success("✅ Abonelik iptal edildi. Dönem sonuna kadar kullanabilirsiniz.")
                            st.session_state['confirm_cancel'] = False
                        else:
                            st.error("❌ İptal işlemi başarısız.")
                    else:
                        st.session_state['package'] = 'free'
                        st.success("✅ Abonelik iptal edildi.")
                        st.rerun()
                else:
                    st.session_state['confirm_cancel'] = True
                    st.warning("⚠️ İptal etmek istediğinizden emin misiniz? Tekrar butona tıklayın.")
        
        if st.button("💎 Paket Değiştir"):
            st.session_state['show_pricing'] = True
            st.rerun()
    
    st.markdown("---")
    
    # Kullanım istatistikleri
    st.markdown("### 📊 Kullanım İstatistikleri")
    
    usage_col1, usage_col2, usage_col3 = st.columns(3)
    
    with usage_col1:
        st.metric("Toplam Analiz", st.session_state.get('total_analyses', 0))
    
    with usage_col2:
        st.metric("Bu Ay", st.session_state.get('monthly_analyses', 0))
    
    with usage_col3:
        limit_mb = {'free': 1, 'pro': 25, 'pro_student': 25, 'business': 200, 'business_student': 200}
        st.metric("Veri Limiti", f"{limit_mb.get(current_package, 1)} MB")
    
    st.markdown("---")
    
    # Fatura geçmişi
    st.markdown("### 🧾 Fatura Geçmişi")
    
    if current_package == 'free':
        st.info("Free paket kullanıcıları için fatura geçmişi bulunmuyor.")
    else:
        # Demo fatura geçmişi
        import pandas as pd
        invoices = pd.DataFrame({
            'Tarih': ['01/12/2024', '01/11/2024', '01/10/2024'],
            'Paket': ['Pro', 'Pro', 'Pro'],
            'Tutar': ['$9.00', '$9.00', '$9.00'],
            'Durum': ['✅ Ödendi', '✅ Ödendi', '✅ Ödendi']
        })
        
        st.dataframe(invoices, use_container_width=True, hide_index=True)
        
        if st.button("📥 Tüm Faturaları İndir"):
            st.info("Faturalar e-mailinize gönderilecek.")