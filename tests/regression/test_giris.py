"""REGRESYON: Giriş (login) ekranı."""
import os
import uuid

import pytest
from appium.webdriver.common.appiumby import AppiumBy

from pages.login_page import LoginPage

# Yeni cihazdan girişte istenebilen SMS / e-posta doğrulama kodu ekranı
DOGRULAMA_KODU = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textMatches("(?i).*(doğrulama kodu|kodu gir|tek kullanımlık).*")')

pytestmark = pytest.mark.regression


def giris_ekranini_ac(app):
    """Hesabım sekmesindeki 'Giriş yap' bağlantısıyla giriş ekranına gider."""
    return app.open_account().open_login()


@pytest.mark.pozitif
def test_giris_ekrani_eposta_sifre_ve_giris_butonu_olmadan_acilmamali(app, adim):
    """[OLUMLU] Giriş ekranı açıldığında e-posta, şifre alanları ve Giriş yap butonu eksik olmamalı."""
    page = giris_ekranini_ac(app)
    adim("Giriş ekranı açıldı")
    assert page.is_visible(page.EMAIL_AREA), "E-posta alanı yok"
    assert page.is_visible(page.PASSWORD_AREA), "Şifre alanı yok"
    assert page.is_visible(page.LOGIN_BUTTON), "Giriş yap butonu yok"


hesap_tanimli = pytest.mark.skipif(not (os.getenv("HB_EMAIL") and os.getenv("HB_PASSWORD")),
                                   reason="HB_EMAIL ve HB_PASSWORD .env dosyasında tanımlı değil")


@pytest.fixture
def oturumu_kapat(app):
    """Güvenlik ağı: test yarıda kalıp hesapta açık oturum bıraktıysa hesaptan çıkar.

    Uygulama oturumu hatırlıyor; çıkış yapılmazsa sonraki 'misafir kullanıcı' testleri bozulur.
    Olumlu test çıkışı zaten kendi adımlarında yapar; o durumda burada çıkış gerekmez.
    """
    yield app
    home = app.restart()
    hesap = home.open_account()
    if hesap.is_logged_in():
        hesap.logout()
    assert hesap.is_guest(10) or hesap.is_visible(hesap.LOGIN_LINK, 5), "Test sonrası hesaptan çıkılamadı"


def dogrulama_kodu_isteniyor(page) -> bool:
    return page.is_visible(DOGRULAMA_KODU, 3)


@pytest.mark.pozitif
@pytest.mark.hesap
@hesap_tanimli
def test_gecerli_bilgilerle_giris_yapan_kullanici_giris_ekraninda_kalmamali(oturumu_kapat, adim):
    """[OLUMLU] Doğru bilgilerle giriş yapan kullanıcı giriş ekranında kalmamalı; çıkış yaptıktan sonra Hesabım'da yeniden misafir kullanıcı görünmeli.

    Akış: Giriş yap -> Hesabım (giriş yapılmış) -> Çıkış yap -> Hesabım (Misafir kullanıcı).
    Not: Çıkıştan sonra uygulama Hesabım'da kalmaz; misafir görünümü Hesabım yeniden açılınca görünür.
    """
    page = giris_ekranini_ac(oturumu_kapat)
    page.login(os.environ["HB_EMAIL"], os.environ["HB_PASSWORD"])
    adim("1-Doğru e-posta ve şifreyle Giriş yap'a basıldı")
    if dogrulama_kodu_isteniyor(page):
        pytest.fail("Hepsiburada doğrulama kodu (SMS/e-posta) istedi. İlk girişi emülatörde bir kez elle "
                    "yapıp kodu girin, sonra testi tekrar çalıştırın (README > 6.6).")
    assert page.is_absent(page.LOGIN_BUTTON, 15) or LoginPage.AUTH_ACTIVITY not in page.activity, \
        "Geçerli bilgilere rağmen giriş ekranında kalındı"

    hesap = oturumu_kapat.restart().open_account()
    adim("2-Hesabım: giriş yapılmış")
    assert hesap.is_logged_in(), "Giriş sonrası Hesabım sayfası hâlâ misafir kullanıcı gösteriyor"

    hesap.logout()
    adim("3-Çıkış yapıldı, Hesabım yeniden açıldı: Misafir kullanıcı")
    assert hesap.is_guest(10), "Çıkış sonrası Hesabım'da 'Misafir kullanıcı' görünmüyor"


@pytest.mark.negatif
@pytest.mark.hesap
@hesap_tanimli
def test_dogru_eposta_yanlis_sifreyle_giris_yapilamamali(oturumu_kapat, adim):
    """[OLUMSUZ] Kayıtlı e-posta ile yanlış şifre girildiğinde kullanıcı hata mesajı görmeli, giriş ekranından çıkmamalı ve hesaba girilmemeli."""
    page = giris_ekranini_ac(oturumu_kapat)
    # Gerçek şifre değil; her çalıştırmada farklı, kesinlikle yanlış bir değer
    page.login(os.environ["HB_EMAIL"], f"YanlisSifre-{uuid.uuid4().hex[:8]}")
    # Ekran görüntüsü, yükleme bitip uygulamanın hata mesajı göründükten sonra alınır
    mesaj = page.hata_mesajini_bekle()
    adim(f"Yanlış şifre sonrası hata mesajı: '{mesaj}'" if mesaj
         else "Yanlış şifre sonrası ekran (tanınan bir hata mesajı bulunamadı)")
    # Uygulamanın mesajı (3 Kasım 2026): "E-posta adresi veya şifre hatalı."
    assert mesaj, "Yanlış şifrede kullanıcıya hata mesajı gösterilmedi"
    assert page.is_open(), "Yanlış şifreyle giriş ekranından çıkıldı"
    hesap = oturumu_kapat.restart().open_account()
    assert not hesap.is_logged_in(), "Yanlış şifreyle hesaba girildi"


@pytest.mark.negatif
def test_bos_bilgilerle_giris_yapilamamali(app, adim):
    """[OLUMSUZ] E-posta ve şifre boşken Giriş yap'a basıldığında kullanıcı giriş ekranından çıkmamalı."""
    page = giris_ekranini_ac(app)
    page.submit()
    adim("Boş formla Giriş yap'a basıldı")
    assert page.is_open(), "Boş bilgilerle giriş ekranından çıkıldı"


@pytest.mark.negatif
def test_gecersiz_eposta_formatiyla_giris_yapilamamali(app, adim):
    """[OLUMSUZ] Geçersiz biçimdeki e-posta ile Giriş yap'a basıldığında kullanıcı giriş ekranından çıkmamalı."""
    page = giris_ekranini_ac(app)
    page.type_email("gecersiz-eposta").submit()
    adim("Geçersiz e-posta ile Giriş yap'a basıldı")
    assert page.is_open(), "Geçersiz e-posta ile giriş ekranından çıkıldı"
