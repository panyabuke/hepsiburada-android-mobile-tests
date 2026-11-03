"""BİLİNEN HATALAR: Testlerin uygulamada bulduğu hataları yeniden üreten testler.

Her hatanın ayrıntılı raporu ve ekran görüntüleri proje kökündeki `hatalar/<hata-no>/` klasöründedir.
Testler `xfail(strict=True)` ile işaretlidir:
  - Hata devam ettiği sürece sonuç XFAIL olur (beklenen başarısızlık, çalıştırmayı durdurmaz).
  - Hata düzeltilirse test XPASS olur ve strict olduğu için BAŞARISIZ sayılır; bu, hata kaydının
    kapatılması ve işaretin kaldırılması gerektiğini haber verir.
"""
import pytest

from pages import flows
from utils.price import parse_price
from utils.urun_profili import INDIRIMLI

pytestmark = pytest.mark.bilinen_hata


@pytest.mark.indirimli
@pytest.mark.negatif
@pytest.mark.xfail(strict=True, reason="HB-001: Ürün sayfasında Premium fiyatı misafire satış fiyatı gibi gösteriliyor")
def test_hb001_urun_sayfasindaki_fiyat_misafirin_sepet_fiyatindan_dusuk_gosterilmemeli(bos_sepet, adim):
    """[OLUMSUZ] HB-001: Misafir kullanıcıya ürün sayfasında gösterilen fiyat, sepette ödeyeceği fiyattan düşük olmamalı."""
    product, profil, _ = flows.kategoride_urun_ac(bos_sepet, INDIRIMLI)
    gosterilen = profil.satis_fiyati
    premium = product.en_uste_don().profil(kaydir=False).premium_teklif_fiyati
    adim(f"Ürün sayfası: gösterilen {gosterilen} TL, Premium bandı {premium} TL")
    if premium != gosterilen:
        pytest.skip("Bu üründe gösterilen fiyat Premium fiyatı değil; HB-001 bu ürünle yeniden üretilemez")
    product.add_to_cart()
    cart = product.go_to_cart()
    sepet = parse_price(cart.first_item_price_text())
    adim(f"Sepet: {sepet} TL")
    assert sepet <= gosterilen, f"Ürün sayfasında {gosterilen} TL gösterildi, sepette {sepet} TL"
