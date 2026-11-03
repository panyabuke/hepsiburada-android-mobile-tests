"""BLACK BOX (kategoriler): Renk/beden seçimine verilen girdilere göre ekranın tepkisi test edilir.

Uygulamanın iç yapısı bilinmeden, yalnızca dokunma (girdi) ve ekranda görünen seçim (çıktı) kullanılır.
Denklik sınıfları:
  - seçili olmayan bir seçeneğe dokunma  -> o seçenek seçilir, diğeri bırakılır
  - zaten seçili olan seçeneğe dokunma   -> seçim değişmez (seçim kaldırılmaz)
"""
import pytest

from config.urun_kategorileri import kategori_parametreleri
from pages import flows
from utils.urun_profili import BEDEN, RENK

pytestmark = pytest.mark.blackbox


def _grup(profil, kategori):
    return profil.renk_grubu if kategori == RENK else profil.beden_grubu


@pytest.mark.pozitif
@pytest.mark.parametrize("kategori", kategori_parametreleri(RENK, BEDEN))
def test_seceneklere_art_arda_dokunuldugunda_birden_fazla_secim_kalmamali(app, adim, kategori):
    """[OLUMLU] Seçenekler arasında art arda geçiş yapıldığında her seferinde yalnızca son dokunulan seçenek seçili olmalı."""
    product, profil, _ = flows.kategoride_urun_ac(app, kategori)
    grup = _grup(profil, kategori).ad
    for tur in range(1, 3):
        secilen = product.baska_secenek_sec(grup)
        adim(f"{tur}. geçiş: '{secilen}'")
        secililer = [s.ad for s in product.profil().gruplar[grup].secenekler if s.secili]
        assert secililer == [secilen], f"{tur}. geçişten sonra seçili olanlar: {secililer}"


@pytest.mark.negatif
@pytest.mark.parametrize("kategori", kategori_parametreleri(RENK, BEDEN))
def test_secili_secenege_tekrar_dokunuldugunda_secim_kaldirilmamali(app, adim, kategori):
    """[OLUMSUZ] Zaten seçili olan seçeneğe tekrar dokunulduğunda seçim kalkmamalı ve 'Sepete ekle' kaybolmamalı."""
    product, profil, _ = flows.kategoride_urun_ac(app, kategori)
    grup = _grup(profil, kategori)
    product.secili_secenege_dokun(grup.secili_deger)
    adim(f"Seçili '{grup.secili_deger}' seçeneğine tekrar dokunuldu")
    yeni = product.profil().gruplar[grup.ad]
    assert yeni.secili_deger == grup.secili_deger, f"Seçim '{yeni.secili_deger}' oldu"
    assert [s.ad for s in yeni.secenekler if s.secili] == [grup.secili_deger], "Seçim kaldırıldı"
    assert product.is_visible(product.ADD_TO_CART, 5), "'Sepete ekle' butonu kayboldu"
