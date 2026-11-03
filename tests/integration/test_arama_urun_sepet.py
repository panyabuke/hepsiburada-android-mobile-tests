"""ENTEGRASYON: Arama, ürün detayı ve sepet modüllerinin birbirine doğru veri aktarması test edilir."""
import re

import pytest
from selenium.webdriver.support.ui import WebDriverWait

from pages import flows
from utils.price import parse_price

pytestmark = [pytest.mark.integration, pytest.mark.standart]
# Sepete eklenen ürün: 'standart' kategorisinden (seçeneksiz, indirimsiz) bir ürün, bkz. pages/flows.py


def _normalize(text: str) -> str:
    return re.sub(r"\s+", "", text.replace("\xa0", " ")).lower()


@pytest.mark.pozitif
def test_aramada_secilen_urun_sepete_farkli_urun_olarak_eklenmemeli(bos_sepet, adim):
    """[OLUMLU] Arama sonucunda seçilen ürün sepete eklendiğinde sepette farklı bir ürün görünmemeli."""
    cart, card_text = flows.sepete_urun_ekle(bos_sepet)
    adim("Sepetteki ürün")
    names = cart.item_names()
    assert len(names) == 1, f"Sepette beklenmeyen ürün sayısı: {names}"
    # Sepetteki ad kısaltılmış olabilir; ilk 20 karakter karttaki metinde geçmeli
    assert _normalize(names[0])[:20] in _normalize(card_text), \
        f"Sepetteki ürün ({names[0]!r}) seçilen ürünle ({card_text!r}) eşleşmiyor"


@pytest.mark.pozitif
def test_urun_sayfasindaki_fiyat_sepette_farkli_gorunmemeli(bos_sepet, adim):
    """[OLUMLU] Ürün sayfasında görülen fiyat sepete geçildiğinde değişmemeli."""
    product, _ = flows.urun_ac(bos_sepet)
    urun_fiyati = parse_price(product.price_text())
    adim(f"Ürün sayfası fiyatı: {urun_fiyati}")
    product.add_to_cart()
    cart = product.go_to_cart()
    sepet_fiyati = parse_price(cart.first_item_price_text())
    adim(f"Sepetteki fiyat: {sepet_fiyati}")
    assert sepet_fiyati == urun_fiyati, f"Ürün sayfası {urun_fiyati} TL, sepet {sepet_fiyati} TL"


@pytest.mark.negatif
def test_urun_adedi_artirildiginda_sepet_toplami_tek_urun_fiyatinda_kalmamali(bos_sepet, adim):
    """[OLUMSUZ] Sepette ürün adedi artırıldığında toplam fiyat güncellenmeli; tek ürünün fiyatında kalmamalı."""
    cart, _ = flows.sepete_urun_ekle(bos_sepet)
    birim = parse_price(cart.first_item_price_text())
    once = parse_price(cart.total_price_text())
    adim(f"1 adet: birim {birim} TL, toplam {once} TL")
    adet = cart.increase_first_item_quantity()
    # Toplam, adet değiştikten kısa süre sonra yeniden hesaplanıyor
    WebDriverWait(cart.driver, 15).until(lambda _: parse_price(cart.total_price_text()) != once)
    sonra = parse_price(cart.total_price_text())
    adim(f"{adet} adet: toplam {sonra} TL")
    assert sonra > once, f"Adet {adet} olduğu halde toplam {once} TL -> {sonra} TL"


@pytest.mark.negatif
def test_alisverise_devam_et_secildiginde_kullanici_sepete_yonlendirilmemeli(bos_sepet, adim):
    """[OLUMSUZ] Sepete ekledikten sonra 'Alışverişe devam et' seçilirse sepet ekranı açılmamalı, ancak ürün sepetten düşmemeli."""
    product, _ = flows.urun_ac(bos_sepet)
    product.add_to_cart()
    product.continue_shopping()
    adim("'Alışverişe devam et' sonrası ekran")
    from pages.cart_page import CartPage
    assert CartPage(product.driver).is_absent(CartPage.HEADER, 3), "Kullanıcı sepete yönlendirildi"
    cart = bos_sepet.back_to_tabs().open_cart()
    adim("Sepet kontrolü")
    assert cart.item_count() == 1, "Alışverişe devam edildiğinde ürün sepetten düştü"
