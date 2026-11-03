"""ENTEGRASYON (kategoriler): Ürün sayfası ile sepet arasında her kategorinin bilgisi doğru aktarılıyor mu?

Ürün sayfasında seçili olan renk/beden ve satış fiyatı, sepete eklendikten sonra sepet ekranında
aynı (fiyat için: daha yüksek olmayan) değerle görünmeli.
"""
import pytest

from config.urun_kategorileri import kategori_parametreleri
from pages import flows
from utils.price import parse_price
from utils.urun_profili import BEDEN, COKLU, INDIRIMLI, RENK, STANDART

pytestmark = pytest.mark.integration


@pytest.mark.pozitif
@pytest.mark.parametrize("kategori", kategori_parametreleri(STANDART, RENK, BEDEN, COKLU, INDIRIMLI))
def test_kategori_urunu_sepete_farkli_secenek_veya_fiyatla_aktarilmamali(bos_sepet, adim, kategori):
    """[OLUMLU] Ürün sayfasındaki seçili seçenekler sepette aynı görünmeli; sepet fiyatı ürünün liste (eski) fiyatını aşmamalı.

    Esas alınan fiyat sepet fiyatıdır. Ürün sayfasındaki indirimli fiyat bazı ürünlerde Premium üyelik
    fiyatıdır ve misafirin sepet fiyatından düşüktür; bu fark ayrıca kayıtlıdır: hatalar/HB-001.
    """
    product, profil, _ = flows.kategoride_urun_ac(bos_sepet, kategori)
    secililer = [g.secili_deger for g in profil.secim_gruplari()]
    adim(f"Ürün sayfası: seçili {secililer or 'seçenek yok'}, {profil.satis_fiyati} TL")
    product.add_to_cart()
    cart = product.go_to_cart()
    adim("Sepet")
    assert cart.item_count() == 1, "Sepette 1 ürün yok"
    if secililer:
        # Seçenek satırı ("Krem/S") yalnızca seçenekli ürünlerde bulunur
        secenek = cart.first_item_variant_text()
        for deger in secililer:
            assert deger in secenek, f"Seçili '{deger}' sepette yok; sepette: '{secenek}'"
    sepet_fiyati = parse_price(cart.first_item_price_text())
    liste_fiyati = profil.eski_fiyat or profil.satis_fiyati
    assert 0 < sepet_fiyati <= liste_fiyati, f"Sepet {sepet_fiyati} TL, liste fiyatı {liste_fiyati} TL"


@pytest.mark.negatif
@pytest.mark.parametrize("kategori", kategori_parametreleri(STANDART, RENK, BEDEN, COKLU, INDIRIMLI))
def test_kategori_urunu_sepete_eklenmeden_sepette_gorunmemeli(bos_sepet, adim, kategori):
    """[OLUMSUZ] Ürün sayfası açılıp seçenek seçilse bile 'Sepete ekle'ye basılmadıkça ürün sepete düşmemeli."""
    product, profil, _ = flows.kategoride_urun_ac(bos_sepet, kategori)
    if profil.secim_gruplari():
        product.baska_secenek_sec(profil.secim_gruplari()[0].ad)
    adim("Ürün sayfası (sepete eklenmedi)")
    cart = product.open_cart_from_toolbar()
    adim("Sepet")
    assert cart.is_empty(), "Sepete eklenmeyen ürün sepette görünüyor"
