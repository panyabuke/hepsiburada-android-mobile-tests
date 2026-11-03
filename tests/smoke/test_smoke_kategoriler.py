"""SMOKE (kategoriler): Her ürün kategorisi için test edilecek bir ürün bulunabiliyor mu?

Kategori testlerine geçmeden önce çalışır. Burada bulunan ürünler (arama kelimesi + sıra)
aynı çalıştırmadaki diğer testlerde yeniden kullanılır.
"""
import pytest

from config.urun_kategorileri import KATEGORILER, kategori_parametreleri
from pages import flows

pytestmark = pytest.mark.smoke


@pytest.mark.pozitif
@pytest.mark.parametrize("kategori", kategori_parametreleri())
def test_kategoriye_uyan_urun_arama_sonuclarinda_eksik_olmamali(app, adim, kategori):
    """[OLUMLU] Her kategori için arama sonuçlarında kategorinin koşulunu sağlayan bir ürün bulunmalı."""
    product, profil, kart = flows.kategoride_urun_ac(app, kategori)
    adim(f"{KATEGORILER[kategori]['aciklama']}: {kart.strip()[:40]}")
    assert kategori in profil.kategoriler(), f"Ürün kategorileri: {profil.kategoriler()}"


@pytest.mark.negatif
@pytest.mark.parametrize("kategori", kategori_parametreleri())
def test_kategori_urun_sayfasi_fiyatsiz_veya_sepete_ekle_butonsuz_acilmamali(app, adim, kategori):
    """[OLUMSUZ] Kategori ürününün sayfası fiyat ve (stoktaki varsayılan seçenekte) 'Sepete ekle' olmadan açılmamalı."""
    product, profil, _ = flows.kategoride_urun_ac(app, kategori)
    adim("Ürün sayfası")
    assert profil.satis_fiyati, "Ürün sayfasında fiyat yok"
    assert product.is_visible(product.ADD_TO_CART, 5), "'Sepete ekle' butonu yok"
    assert product.is_absent(product.COMBINATION_MISSING, 1), "Varsayılan seçenek stokta değil"
