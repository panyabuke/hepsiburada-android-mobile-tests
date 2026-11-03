"""SMOKE: Uygulama ayağa kalkıyor mu? Diğer testlere geçmeden önce çalıştırılan hızlı kontrol."""
import pytest

pytestmark = pytest.mark.smoke


@pytest.mark.pozitif
def test_uygulama_acildiginda_ana_sayfa_eksik_yuklenmemeli(app, adim):
    """[OLUMLU] Uygulama açıldığında arama kutusu ve alt menü eksik olmamalı."""
    adim("Uygulama açıldı")
    assert app.is_visible(app.SEARCH_BOX), "Arama kutusu görünmüyor"
    assert app.is_visible(app.BOTTOM_NAV), "Alt menü görünmüyor"
    for menu in (app.NAV_HOME, app.NAV_CART, app.NAV_ACCOUNT):
        assert app.is_visible(menu, 3), f"Alt menüde {menu[1]} eksik"


@pytest.mark.negatif
def test_uygulama_acildiginda_erisim_engeli_veya_hata_ekrani_gorunmemeli(app, adim):
    """[OLUMSUZ] Uygulama açıldığında 'Olağan dışı erişim' ya da 'Yüklenemedi' ekranı gösterilmemeli."""
    adim("Ana sayfa kontrol edildi")
    assert app.is_absent(app.BOT_BLOCK_TEXT, 3), "Otomasyon engeli ekranı çıktı"
    assert app.is_absent(app.ERROR_TEXT, 3), "Sayfa içeriği yüklenemedi"
