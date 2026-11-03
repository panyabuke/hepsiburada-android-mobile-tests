"""BLACK BOX: Giriş formu, geçersiz e-posta denklik sınıflarıyla test edilir.

Gerçek bir hesap ya da şifre kullanılmaz; yalnızca geçersiz biçimli e-postalar denenir.
"""
import pytest

pytestmark = pytest.mark.blackbox

GECERSIZ_EPOSTALAR = {
    "at_isareti_yok": "kullaniciornek.com",
    "alan_adi_yok": "kullanici@",
    "kullanici_adi_yok": "@ornek.com",
    "bosluk_iceren": "kul lanici@ornek.com",
}


@pytest.mark.negatif
@pytest.mark.parametrize("eposta", GECERSIZ_EPOSTALAR.values(), ids=GECERSIZ_EPOSTALAR.keys())
def test_gecersiz_bicimli_eposta_ile_giris_ekranindan_cikilmamali(app, adim, eposta):
    """[OLUMSUZ] Geçersiz biçimli e-posta ile Giriş yap'a basıldığında kullanıcı giriş ekranından çıkmamalı."""
    page = app.open_account().open_login()
    page.type_email(eposta).submit()
    adim(f"'{eposta}' ile giriş denendi")
    assert page.is_open(), f"'{eposta}' ile giriş ekranından çıkıldı"


@pytest.mark.pozitif
def test_giris_ekrani_misafir_kullaniciya_kapali_olmamali(app, adim):
    """[OLUMLU] Misafir kullanıcı Hesabım sekmesinden giriş ekranına ulaşabilmeli; erişim engellenmemeli."""
    account = app.open_account()
    assert account.is_guest(), "Kullanıcı misafir değil (önceden giriş yapılmış olabilir)"
    page = account.open_login()
    adim("Misafir kullanıcı giriş ekranında")
    assert page.is_open(), "Giriş ekranı açılmadı"
