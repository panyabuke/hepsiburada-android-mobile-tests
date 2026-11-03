"""WHITE BOX: utils/price.py içindeki parse_price fonksiyonunun tüm kod yolları test edilir.

Hepsiburada'nın kaynak koduna erişimimiz olmadığı için white box testler, kaynağını gördüğümüz
test altyapısı kodu (fiyat ayrıştırıcı) ve uygulamanın iç bileşenleri (bkz. test_uygulama_ic_yapisi.py)
üzerinde yapılır. Bu testler cihaz/Appium gerektirmez.

Kod yolları:
  1) str olmayan girdi        -> ValueError
  2) regex eşleşmeyen metin   -> ValueError
  3) kuruşsuz fiyat           -> fraction None dalı
  4) kuruşlu fiyat            -> fraction dalı
  5) tek haneli kuruş         -> ljust ile tamamlama dalı
  6) binlik ayraçlı fiyat     -> '.' temizleme
  7) bölünmez boşluk (\xa0)   -> replace dalı
"""
import pytest

from utils.price import parse_price

pytestmark = pytest.mark.whitebox


@pytest.mark.pozitif
@pytest.mark.parametrize("metin, beklenen", [
    ("899 TL", 899.0),            # yol 3
    ("755,53 TL", 755.53),        # yol 4
    ("12,5 TL", 12.5),            # yol 5
    ("1.159 TL", 1159.0),         # yol 6
    ("3.099,90 TL", 3099.9),      # yol 4 + 6
    ("1.250\xa0TL", 1250.0),      # yol 7
])
def test_gecerli_fiyat_metni_yanlis_sayiya_cevrilmemeli(metin, beklenen):
    """[OLUMLU] Geçerli fiyat metinleri doğru sayıya çevrilmeli, hiçbir dalda yanlış değer üretilmemeli."""
    assert parse_price(metin) == beklenen


@pytest.mark.negatif
@pytest.mark.parametrize("metin", ["", "TL", "abc TL", "755,53", "755,535 TL", "-5 TL", "1,000.50 TL"])
def test_gecersiz_fiyat_metni_sessizce_kabul_edilmemeli(metin):
    """[OLUMSUZ] Geçersiz fiyat metinleri sessizce kabul edilmemeli, ValueError fırlatılmalı (yol 2)."""
    with pytest.raises(ValueError):
        parse_price(metin)


@pytest.mark.negatif
@pytest.mark.parametrize("deger", [None, 755.53, ["755 TL"]])
def test_metin_olmayan_girdi_fiyat_olarak_islenmemeli(deger):
    """[OLUMSUZ] str olmayan girdiler işlenmemeli, ValueError fırlatılmalı (yol 1)."""
    with pytest.raises(ValueError):
        parse_price(deger)
