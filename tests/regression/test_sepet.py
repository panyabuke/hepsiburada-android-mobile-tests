"""REGRESYON: Sepete ekleme."""
import pytest

from pages import flows

pytestmark = [pytest.mark.regression, pytest.mark.standart]
# Sepete eklenen ürün: 'standart' kategorisinden (seçeneksiz, indirimsiz) bir ürün, bkz. pages/flows.py


@pytest.mark.pozitif
def test_sepete_eklenen_urun_sepette_eksik_olmamali(bos_sepet, adim):
    """[OLUMLU] Bir ürün sepete eklendiğinde sepet boş olmamalı ve 1 ürün göstermeli."""
    cart, _ = flows.sepete_urun_ekle(bos_sepet)
    adim("Ürün eklendikten sonra sepet")
    assert not cart.is_empty(3), "Sepet boş görünüyor"
    assert cart.item_count() == 1, "Sepetteki ürün adedi 1 değil"


@pytest.mark.negatif
def test_sepet_silindiginde_sepette_urun_kalmamali(bos_sepet, adim):
    """[OLUMSUZ] Sepetteki ürünler silindiğinde sepette hiç ürün kalmamalı."""
    cart, _ = flows.sepete_urun_ekle(bos_sepet)
    adim("Silmeden önce sepet")
    cart.clear()
    adim("Silme sonrası sepet")
    assert cart.is_empty(), "'Sepetin şu an boş' mesajı gösterilmedi"
    assert cart.item_names() == [], "Sepette hâlâ ürün var"


@pytest.mark.negatif
def test_bos_sepette_odemeye_gec_butonu_gorunmemeli(bos_sepet, adim):
    """[OLUMSUZ] Sepet boşken 'Ödemeye Geç' butonu gösterilmemeli."""
    cart = bos_sepet.open_cart()
    adim("Boş sepet")
    assert cart.is_empty(), "Sepet boş değil"
    assert cart.is_absent(cart.CHECKOUT, 3), "Boş sepette 'Ödemeye Geç' butonu görünüyor"
