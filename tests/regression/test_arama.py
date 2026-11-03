"""REGRESYON: Arama barı."""
import pytest

from pages import flows

pytestmark = pytest.mark.regression


@pytest.mark.pozitif
def test_gecerli_kelimeyle_aramada_sonuc_listesi_bos_olmamali(app, adim):
    """[OLUMLU] 'kulaklık' arandığında sonuç sayısı sıfır olmamalı ve ürünler listelenmeli."""
    results = flows.ara(app, "kulaklık")
    assert results.is_open(), "Sonuç sayfası açılmadı"
    adim("kulaklık için sonuçlar listelendi")
    assert "kulaklık" in results.title().lower(), "Başlıkta aranan kelime yok"
    assert results.result_count() > 0, "Sonuç sayısı 0"
    assert results.listed_products(), "Listede ürün kartı yok"


@pytest.mark.negatif
def test_anlamsiz_kelimeyle_aramada_hicbir_urun_listelenmemeli(app, adim):
    """[OLUMSUZ] Anlamsız bir kelime arandığında sonuç sayısı 0 olmalı ve 'ürün bulunamadı' mesajı eksik olmamalı."""
    results = flows.ara(app, "xqzvbnmklpwr")
    assert results.is_open(), "Sonuç sayfası açılmadı"
    adim("Anlamsız kelime için sonuç ekranı")
    assert results.result_count() == 0, f"Beklenmeyen sonuç sayısı: {results.title()}"
    assert results.shows_no_result(), "'Aramana uygun ürün bulunamadı' mesajı gösterilmedi"
