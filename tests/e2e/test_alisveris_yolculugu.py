"""UÇTAN UCA: Her ürün kategorisinde bir kullanıcının en basit alışveriş yolculuğu, her adımı ekran
görüntüsüyle kaydedilerek test edilir.

Akış: Ana sayfa -> Arama -> Ürün -> (Renk/beden seçimi) -> Sepete ekle -> Sepet -> Ödemeye Geç -> Giriş/Misafir adımı
Gerçek sipariş verilmez; test ödeme bilgisi istenen adımdan önce durur.
"""
import pytest

from config.urun_kategorileri import KATEGORILER, kategori_parametreleri
from pages import flows
from utils.urun_profili import BEDEN, COKLU, INDIRIMLI, RENK, STANDART, STOKTA_OLMAYAN

pytestmark = pytest.mark.e2e


@pytest.mark.pozitif
@pytest.mark.parametrize("kategori", kategori_parametreleri(STANDART, RENK, BEDEN, COKLU, INDIRIMLI))
def test_misafir_kullanici_alisveris_adimlarinin_hicbirinde_takilmamali(bos_sepet, adim, kategori):
    """[OLUMLU] Misafir kullanıcı, kategorideki bir ürünle ana sayfadan ödeme adımına kadar hiçbir adımda takılmamalı."""
    adim("1-Ana sayfa açıldı")

    product, profil, kart = flows.kategoride_urun_ac(bos_sepet, kategori)
    adim(f"2-{KATEGORILER[kategori]['aciklama']} bulundu: {kart.strip()[:40]}")

    for grup in profil.secim_gruplari():
        secilen = product.baska_secenek_sec(grup.ad)
        adim(f"3-{grup.ad}: '{secilen}' seçildi")

    product.add_to_cart()
    adim("4-Ürün sepete eklendi")

    cart = product.go_to_cart()
    assert cart.item_count() == 1, "Sepette 1 ürün yok"
    adim("5-Sepet açıldı")

    login = cart.checkout().wait_loaded()
    assert login.is_open(), "Ödemeye Geç sonrası giriş/misafir adımı açılmadı"
    adim("6-Ödeme öncesi giriş/misafir adımı")
    login.go_back()


@pytest.mark.negatif
@pytest.mark.parametrize("kategori", kategori_parametreleri(STANDART, RENK, BEDEN, COKLU, INDIRIMLI))
def test_sepete_eklemeden_ilerleyen_kullanici_odeme_adimina_ulasmamali(bos_sepet, adim, kategori):
    """[OLUMSUZ] Kullanıcı ürünü bulup seçeneklerini seçse de 'Sepete ekle'ye basmadan sepete geçerse ödeme adımına ilerleyememeli."""
    adim("1-Ana sayfa açıldı")

    product, profil, kart = flows.kategoride_urun_ac(bos_sepet, kategori)
    adim(f"2-{KATEGORILER[kategori]['aciklama']} bulundu: {kart.strip()[:40]}")

    for grup in profil.secim_gruplari():
        secilen = product.baska_secenek_sec(grup.ad)
        adim(f"3-{grup.ad}: '{secilen}' seçildi")

    cart = product.open_cart_from_toolbar()
    adim("4-'Sepete ekle'ye basılmadan sepete geçildi")
    assert cart.is_empty(), "Sepete eklenmeyen ürün sepette görünüyor"
    assert cart.is_absent(cart.CHECKOUT, 3), "Boş sepette 'Ödemeye Geç' butonu var"


@pytest.mark.negatif
@pytest.mark.parametrize("kategori", kategori_parametreleri(STOKTA_OLMAYAN))
def test_stokta_olmayan_secenekle_alisveris_sepete_ulasmamali(bos_sepet, adim, kategori):
    """[OLUMSUZ] Kullanıcı stokta olmayan seçeneği seçtiğinde ürünü sepete ekleyememeli ve sepeti boş kalmalı."""
    adim("1-Ana sayfa açıldı")
    product, _, _ = flows.kategoride_urun_ac(bos_sepet, kategori)
    adim("2-Ürün sayfası açıldı")
    secenek = product.stokta_olmayan_secenegi_sec()
    adim(f"3-Stokta olmayan '{secenek}' seçildi")
    assert product.is_absent(product.ADD_TO_CART, 3), "Stokta olmayan seçenekte 'Sepete ekle' görünüyor"
    cart = product.open_cart_from_toolbar()
    adim("4-Sepet boş")
    assert cart.is_empty(), "Stokta olmayan ürün sepete düştü"


@pytest.mark.negatif
def test_sepet_bosken_kullanici_odeme_adimina_gecememeli(bos_sepet, adim):
    """[OLUMSUZ] Sepete ürün eklenmeden kullanıcı ödeme adımına geçememeli."""
    adim("1-Ana sayfa (sepet boş)")
    cart = bos_sepet.open_cart()
    adim("2-Boş sepet açıldı")
    assert cart.is_empty(), "Sepet boş değil"
    assert cart.is_absent(cart.CHECKOUT, 3), "Boş sepette ödemeye geçiş butonu var"
