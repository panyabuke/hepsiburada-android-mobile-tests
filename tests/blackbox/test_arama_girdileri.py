"""BLACK BOX: Arama alanı, iç yapı bilinmeden yalnızca girdi -> çıktı ilişkisiyle test edilir.

Teknikler:
- Sınır değer analizi: uygulama en az 2 karakter istiyor -> 0, 1 ve 2 karakter denenir.
- Denklik sınıfları: büyük harf, Türkçe karakter, özel karakter, çok uzun metin.
"""
import pytest

from config.capabilities import ANDROID_PACKAGE
from pages import flows

pytestmark = pytest.mark.blackbox


@pytest.mark.negatif
@pytest.mark.parametrize("girdi", ["", "a"], ids=["0_karakter", "1_karakter"])
def test_iki_karakterden_kisa_aramada_sonuc_sayfasi_acilmamali(app, adim, girdi):
    """[OLUMSUZ] 2 karakterden kısa aramada sonuç sayfası açılmamalı, 'en az iki karakter' uyarısı eksik olmamalı."""
    search = app.open_search()
    search.search(girdi)
    uyari_var = search.shows_min_char_warning()  # Toast kaybolmadan, ekran görüntüsünden önce kontrol edilir
    adim(f"'{girdi}' arandı")
    assert uyari_var, "Minimum karakter uyarısı gösterilmedi"
    assert search.is_open(3), "Arama sayfasından çıkıldı"


@pytest.mark.pozitif
def test_tam_iki_karakterli_aramada_sonuc_sayfasi_engellenmemeli(app, adim):
    """[OLUMLU] Sınır değer: tam 2 karakter ('tv') arandığında sonuç sayfası engellenmemeli."""
    results = flows.ara(app, "tv")
    assert results.is_open(), "2 karakterlik arama engellendi"
    adim("'tv' için sonuçlar")
    assert results.result_count() > 0, "2 karakterlik aramada sonuç yok"


@pytest.mark.pozitif
@pytest.mark.parametrize("girdi", ["KULAKLIK", "ütü"], ids=["buyuk_harf", "turkce_karakter"])
def test_buyuk_harf_veya_turkce_karakterli_aramada_sonuc_bos_olmamali(app, adim, girdi):
    """[OLUMLU] Büyük harf ve Türkçe karakter içeren aramalarda sonuç listesi boş olmamalı."""
    results = flows.ara(app, girdi)
    assert results.is_open(), "Sonuç sayfası açılmadı"
    adim(f"'{girdi}' için sonuçlar")
    assert results.result_count() > 0, f"'{girdi}' için sonuç yok"


@pytest.mark.negatif
@pytest.mark.parametrize("girdi", ["%&*!?<>", "a" * 150], ids=["ozel_karakter", "cok_uzun_metin"])
def test_ozel_karakterli_veya_cok_uzun_aramada_uygulama_cokmemeli(app, adim, girdi):
    """[OLUMSUZ] Özel karakter ya da 150 karakterlik aramada uygulama çökmemeli ve ön planda kalmalı."""
    app.open_search().search(girdi)
    adim("Uç değerli arama sonrası ekran")
    assert app.driver.query_app_state(ANDROID_PACKAGE) == 4, "Uygulama ön planda değil (çökmüş olabilir)"
