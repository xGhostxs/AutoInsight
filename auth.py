"""
AutoInsight - Kullanıcı Kimlik Doğrulama
Firebase Authentication veya basit session bazlı sistem
"""

import streamlit as st
import hashlib
import json
import os
from datetime import datetime
from student_verification import StudentVerification

# Firebase kullanımı (opsiyonel)
try:
    import firebase_admin
    from firebase_admin import credentials, auth, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

class AuthManager:
    """Kullanıcı kimlik doğrulama yöneticisi."""
    
    def __init__(self, use_firebase=False):
        self.use_firebase = use_firebase and FIREBASE_AVAILABLE
        self.db = None
        
        if self.use_firebase:
            # Firebase'i başlat
            if not firebase_admin._apps:
                # Firebase config buraya gelecek
                pass
        else:
            # Basit dosya bazlı kullanıcı sistemi
            self.users_file = 'users_db.json'
            self._ensure_users_file()
    
    def _ensure_users_file(self):
        """Kullanıcı dosyasını oluştur."""
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({}, f)
    
    def _hash_password(self, password: str) -> str:
        """Şifreyi hashle."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _load_users(self) -> dict:
        """Kullanıcıları yükle."""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_users(self, users: dict):
        """Kullanıcıları kaydet."""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2, default=str)
    
    def register_user(self, email: str, password: str, name: str) -> tuple:
        """
        Yeni kullanıcı kaydı.
        
        Returns:
            (success: bool, message: str, user_data: dict)
        """
        try:
            if self.use_firebase:
                return self._register_firebase(email, password, name)
            else:
                return self._register_local(email, password, name)
        except Exception as e:
            return False, f"❌ Kayıt hatası: {str(e)}", {}
    
    def _register_local(self, email: str, password: str, name: str) -> tuple:
        """Yerel dosya sisteminde kayıt."""
        users = self._load_users()
        
        # E-mail kontrolü
        if email in users:
            return False, "❌ Bu e-mail zaten kayıtlı!", {}
        
        # Şifre uzunluk kontrolü
        if len(password) < 6:
            return False, "❌ Şifre en az 6 karakter olmalı!", {}
        
        # Öğrenci e-mail kontrolü
        is_student, university, _ = StudentVerification.is_student_email(email)
        
        # Kullanıcı oluştur
        user_data = {
            'email': email,
            'password': self._hash_password(password),
            'name': name,
            'package': 'free',
            'is_student': is_student,
            'university': university if is_student else '',
            'student_verified': is_student,
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'usage': {
                'analyses_count': 0,
                'monthly_analyses': 0,
                'last_analysis': None
            }
        }
        
        users[email] = user_data
        self._save_users(users)
        
        # Başarı mesajı
        if is_student:
            message = f"✅ Kayıt başarılı! 🎓 {university} öğrencisi olarak %45-48 indirim hakkı kazandınız!"
        else:
            message = "✅ Kayıt başarılı! Şimdi giriş yapabilirsiniz."
        
        return True, message, user_data
    
    def _register_firebase(self, email: str, password: str, name: str) -> tuple:
        """Firebase'de kayıt."""
        # Öğrenci kontrolü
        is_student, university, _ = StudentVerification.is_student_email(email)
        
        # Firebase kullanıcısı oluştur
        user = auth.create_user(
            email=email,
            password=password,
            display_name=name
        )
        
        # Firestore'da profil oluştur
        self.db.collection('users').document(user.uid).set({
            'email': email,
            'name': name,
            'package': 'free',
            'is_student': is_student,
            'university': university if is_student else '',
            'student_verified': is_student,
            'created_at': datetime.now(),
            'usage': {
                'analyses_count': 0,
                'monthly_analyses': 0,
                'last_analysis': None
            }
        })
        
        user_data = {
            'email': email,
            'name': name,
            'package': 'free',
            'is_student': is_student,
            'university': university
        }
        
        if is_student:
            message = f"✅ Kayıt başarılı! 🎓 {university} öğrencisi olarak %45-48 indirim hakkı kazandınız!"
        else:
            message = "✅ Kayıt başarılı!"
        
        return True, message, user_data
    
    def login_user(self, email: str, password: str) -> tuple:
        """
        Kullanıcı girişi.
        
        Returns:
            (success: bool, message: str, user_data: dict)
        """
        try:
            if self.use_firebase:
                return self._login_firebase(email, password)
            else:
                return self._login_local(email, password)
        except Exception as e:
            return False, f"❌ Giriş hatası: {str(e)}", {}
    
    def _login_local(self, email: str, password: str) -> tuple:
        """Yerel sistemde giriş."""
        users = self._load_users()
        
        if email not in users:
            return False, "❌ E-mail veya şifre hatalı!", {}
        
        user = users[email]
        
        if user['password'] != self._hash_password(password):
            return False, "❌ E-mail veya şifre hatalı!", {}
        
        # Son giriş zamanını güncelle
        user['last_login'] = datetime.now().isoformat()
        users[email] = user
        self._save_users(users)
        
        return True, "✅ Giriş başarılı!", user
    
    def _login_firebase(self, email: str, password: str) -> tuple:
        """Firebase'de giriş."""
        import requests
        
        # Firebase REST API ile giriş
        FIREBASE_API_KEY = "YOUR_FIREBASE_API_KEY"
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
        
        data = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        response = requests.post(url, json=data)
        result = response.json()
        
        if 'idToken' in result:
            # Kullanıcı bilgilerini Firestore'dan al
            user_docs = self.db.collection('users').where('email', '==', email).limit(1).get()
            
            if user_docs:
                user_data = user_docs[0].to_dict()
                return True, "✅ Giriş başarılı!", user_data
        
        return False, "❌ E-mail veya şifre hatalı!", {}
    
    def get_user_data(self, email: str) -> dict:
        """Kullanıcı verilerini getir."""
        if self.use_firebase:
            try:
                user_docs = self.db.collection('users').where('email', '==', email).limit(1).get()
                if user_docs:
                    return user_docs[0].to_dict()
            except:
                pass
        else:
            users = self._load_users()
            return users.get(email, {})
        
        return {}
    
    def update_user_package(self, email: str, package: str) -> bool:
        """Kullanıcının paketini güncelle."""
        try:
            if self.use_firebase:
                user_docs = self.db.collection('users').where('email', '==', email).limit(1).stream()
                for doc in user_docs:
                    doc.reference.update({'package': package})
                return True
            else:
                users = self._load_users()
                if email in users:
                    users[email]['package'] = package
                    self._save_users(users)
                    return True
        except:
            pass
        
        return False
    
    def increment_analysis_count(self, email: str):
        """Analiz sayacını artır."""
        try:
            if self.use_firebase:
                user_docs = self.db.collection('users').where('email', '==', email).limit(1).stream()
                for doc in user_docs:
                    user_data = doc.to_dict()
                    usage = user_data.get('usage', {})
                    usage['analyses_count'] = usage.get('analyses_count', 0) + 1
                    usage['monthly_analyses'] = usage.get('monthly_analyses', 0) + 1
                    usage['last_analysis'] = datetime.now()
                    doc.reference.update({'usage': usage})
            else:
                users = self._load_users()
                if email in users:
                    users[email]['usage']['analyses_count'] += 1
                    users[email]['usage']['monthly_analyses'] += 1
                    users[email]['usage']['last_analysis'] = datetime.now().isoformat()
                    self._save_users(users)
        except:
            pass


def show_auth_page():
    """Giriş/Kayıt sayfası."""
    st.markdown("""
    <style>
    .auth-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("📊 AutoInsight")
        st.markdown("### Otomatik Veri Analizi")
        st.markdown("---")
    
    tab1, tab2 = st.tabs(["🔐 Giriş Yap", "✨ Kayıt Ol"])
    
    auth_manager = AuthManager(use_firebase=False)
    
    # GİRİŞ YAPMA
    with tab1:
        st.subheader("Hesabınıza Giriş Yapın")
        
        login_email = st.text_input("E-mail", key="login_email", placeholder="ornek@email.com")
        login_password = st.text_input("Şifre", type="password", key="login_password")
        
        remember_me = st.checkbox("Beni Hatırla")
        
        col_login1, col_login2 = st.columns(2)
        
        with col_login1:
            if st.button("Giriş Yap", type="primary", use_container_width=True):
                if login_email and login_password:
                    success, message, user_data = auth_manager.login_user(login_email, login_password)
                    
                    if success:
                        # Session state'e kaydet
                        st.session_state['logged_in'] = True
                        st.session_state['user_email'] = user_data['email']
                        st.session_state['user_name'] = user_data['name']
                        st.session_state['package'] = user_data.get('package', 'free')
                        st.session_state['is_student'] = user_data.get('is_student', False)
                        st.session_state['university'] = user_data.get('university', '')
                        st.session_state['total_analyses'] = user_data.get('usage', {}).get('analyses_count', 0)
                        st.session_state['monthly_analyses'] = user_data.get('usage', {}).get('monthly_analyses', 0)
                        
                        st.success(message)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("⚠️ Lütfen tüm alanları doldurun")
        
        with col_login2:
            if st.button("Şifremi Unuttum", use_container_width=True):
                st.info("📧 Şifre sıfırlama linki e-mailinize gönderilecek.")
    
    # KAYIT OLMA
    with tab2:
        st.subheader("Yeni Hesap Oluştur")
        
        register_name = st.text_input("Ad Soyad *", key="register_name", placeholder="Ahmet Yılmaz")
        register_email = st.text_input("E-mail *", key="register_email", placeholder="ornek@email.com")
        
        # Öğrenci e-mail kontrolü (anlık)
        if register_email:
            is_student, university, msg = StudentVerification.is_student_email(register_email)
            if is_student:
                st.success(f"🎓 {msg} - {university}")
                st.info("💰 %45-48 öğrenci indiriminden otomatik yararlanacaksınız!")
        
        register_password = st.text_input("Şifre * (min 6 karakter)", type="password", key="register_password")
        register_password2 = st.text_input("Şifre Tekrar *", type="password", key="register_password2")
        
        agree_terms = st.checkbox("Kullanım koşullarını ve gizlilik politikasını kabul ediyorum")
        
        if st.button("Kayıt Ol", type="primary", use_container_width=True):
            if not (register_name and register_email and register_password and register_password2):
                st.error("❌ Lütfen tüm zorunlu alanları doldurun!")
            elif register_password != register_password2:
                st.error("❌ Şifreler eşleşmiyor!")
            elif len(register_password) < 6:
                st.error("❌ Şifre en az 6 karakter olmalı!")
            elif not agree_terms:
                st.warning("⚠️ Kullanım koşullarını kabul etmelisiniz")
            else:
                success, message, user_data = auth_manager.register_user(
                    register_email,
                    register_password,
                    register_name
                )
                
                if success:
                    st.success(message)
                    st.balloons()
                    st.info("👉 Şimdi 'Giriş Yap' sekmesinden giriş yapabilirsiniz!")
                else:
                    st.error(message)
    
    # Footer
    st.markdown("---")
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        st.caption("📚 [Dokümantasyon](#)")
    with col_f2:
        st.caption("💬 [Destek](#)")
    with col_f3:
        st.caption("🎓 [Öğrenci İndirimi](#)")