"""REGRESYON: Checkout (ödemeye geçiş).

Gerçek sipariş verilmez: testler ödeme bilgisi girilen adımdan önce durur.
"""
import pytest

from pages import flows

pytestmark = [pytest.mark.regression, pytest.mark.standart]
# Sepete eklenen ürün: 'standart' kategorisinden (seçeneksiz, indirimsiz) bir ürün, bkz. pages/flows.py


@pytest.mark.pozitif
def test_sepette_urun_varken_odemeye_gec_kullaniciyi_sepette_birakmamali(bos_sepet, adim):
    """[OLUMLU] Sepette ürün varken 'Ödemeye Geç'e basıldığında kullanıcı bir sonraki adıma (giriş/misafir) yönlenmeli, sepette kalmamalı."""
    cart, _ = flows.sepete_urun_ekle(bos_sepet)
    adim("Ödemeden önce sepet")
    login = cart.checkout().wait_loaded()
    adim("Ödemeye Geç sonrası ekran")
    assert login.is_open(), "Ödemeye Geç sonrası giriş/misafir ekranı açılmadı"
    assert login.is_visible(login.GUEST_CONTINUE), "'Üye olmadan devam et' seçeneği yok"
    login.go_back()


@pytest.mark.negatif
def test_giris_yapmamis_kullanici_odeme_sayfasina_dogrudan_ulasamamali(bos_sepet, adim):
    """[OLUMSUZ] Misafir kullanıcı 'Ödemeye Geç'e bastığında ödeme sayfası açılmamalı; önce kimlik adımı gelmeli ve sepet kaybolmamalı."""
    cart, _ = flows.sepete_urun_ekle(bos_sepet)
    login = cart.checkout().wait_loaded()
    adim("Misafir kullanıcı kimlik adımında")
    assert "Payment" not in login.activity and "Checkout" not in login.activity, \
        f"Doğrudan ödeme ekranı açıldı: {login.activity}"
    login.go_back()
    cart.wait_loaded()
    adim("Geri dönüldüğünde sepet")
    assert cart.item_count() == 1, "Geri dönüldüğünde sepetteki ürün kayboldu"
