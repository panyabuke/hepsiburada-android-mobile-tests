"""REGRESYON (kategoriler): Her ürün kategorisinin kendine özgü davranışı test edilir.

Kategoriler: standart, renk seçimli, beden seçimli, çoklu seçimli, indirimli, stokta olmayan.
Her kategori için bir olumlu ve bir olumsuz senaryo vardır.
"""
import pytest

from pages import flows
from utils.price import parse_price
from utils.urun_profili import BEDEN, COKLU, INDIRIMLI, RENK, STANDART, STOKTA_OLMAYAN

pytestmark = pytest.mark.regression


# ---------------- Standart ürün ----------------
@pytest.mark.standart
@pytest.mark.pozitif
def test_standart_urun_secim_yapilmadan_sepete_eklenirken_engellenmemeli(bos_sepet, adim):
    """[OLUMLU] Seçeneği olmayan ürün, hiçbir seçim yapılmadan doğrudan sepete eklenebilmeli."""
    product, _, _ = flows.kategoride_urun_ac(bos_sepet, STANDART)
    adim("Standart ürün sayfası")
    product.add_to_cart()
    cart = product.go_to_cart()
    adim("Sepet")
    assert cart.item_count() == 1, "Standart ürün sepete eklenmedi"


@pytest.mark.standart
@pytest.mark.negatif
def test_standart_urun_sayfasinda_renk_veya_beden_secimi_istenmemeli(app, adim):
    """[OLUMSUZ] Standart ürünün sayfasında seçim yapılacak renk/beden grubu ve 'kombinasyon yok' uyarısı olmamalı."""
    product, profil, _ = flows.kategoride_urun_ac(app, STANDART)
    adim("Standart ürün sayfası")
    assert profil.secim_gruplari() == [], f"Seçim grubu var: {[g.ad for g in profil.secim_gruplari()]}"
    assert product.is_absent(product.COMBINATION_MISSING, 1), "Kombinasyon uyarısı görünüyor"


# ---------------- Renk seçimli ürün ----------------
@pytest.mark.renk_secimli
@pytest.mark.pozitif
def test_secilen_renk_sepette_farkli_gorunmemeli(bos_sepet, adim):
    """[OLUMLU] Varsayılandan farklı bir renk seçilip sepete eklendiğinde sepette seçilen renk görünmeli."""
    product, profil, _ = flows.kategoride_urun_ac(bos_sepet, RENK)
    renk = product.baska_secenek_sec(profil.renk_grubu.ad)
    adim(f"'{renk}' rengi seçildi")
    product.add_to_cart()
    cart = product.go_to_cart()
    adim("Sepet")
    secenek = cart.first_item_variant_text()
    assert renk in secenek, f"Seçilen renk '{renk}', sepette '{secenek}'"


@pytest.mark.renk_secimli
@pytest.mark.negatif
def test_renk_degistirildiginde_onceki_renk_secili_kalmamali(app, adim):
    """[OLUMSUZ] Başka bir renk seçildiğinde önceki renk seçili kalmamalı; aynı anda iki renk seçili olmamalı."""
    product, profil, _ = flows.kategoride_urun_ac(app, RENK)
    grup, eski = profil.renk_grubu.ad, profil.renk_grubu.secili_deger
    yeni = product.baska_secenek_sec(grup)
    adim(f"'{eski}' yerine '{yeni}' seçildi")
    secililer = [s.ad for s in product.profil().gruplar[grup].secenekler if s.secili]
    assert secililer == [yeni], f"Seçili renkler: {secililer}"


# ---------------- Beden seçimli ürün ----------------
@pytest.mark.beden_secimli
@pytest.mark.pozitif
def test_secilen_beden_sepette_farkli_gorunmemeli(bos_sepet, adim):
    """[OLUMLU] Varsayılandan farklı bir beden seçilip sepete eklendiğinde sepette seçilen beden görünmeli."""
    product, profil, _ = flows.kategoride_urun_ac(bos_sepet, BEDEN)
    beden = product.baska_secenek_sec(profil.beden_grubu.ad)
    adim(f"'{beden}' bedeni seçildi")
    product.add_to_cart()
    cart = product.go_to_cart()
    adim("Sepet")
    secenek = cart.first_item_variant_text()
    assert beden in secenek.split("/"), f"Seçilen beden '{beden}', sepette '{secenek}'"


@pytest.mark.beden_secimli
@pytest.mark.negatif
def test_beden_degistirildiginde_onceki_beden_secili_kalmamali(app, adim):
    """[OLUMSUZ] Başka bir beden seçildiğinde önceki beden seçili kalmamalı; aynı anda iki beden seçili olmamalı."""
    product, profil, _ = flows.kategoride_urun_ac(app, BEDEN)
    grup, eski = profil.beden_grubu.ad, profil.beden_grubu.secili_deger
    yeni = product.baska_secenek_sec(grup)
    adim(f"'{eski}' yerine '{yeni}' seçildi")
    secililer = [s.ad for s in product.profil().gruplar[grup].secenekler if s.secili]
    assert secililer == [yeni], f"Seçili bedenler: {secililer}"


# ---------------- Çoklu seçimli ürün ----------------
@pytest.mark.coklu_secimli
@pytest.mark.pozitif
def test_secilen_renk_ve_beden_sepete_eksik_aktarilmamali(bos_sepet, adim):
    """[OLUMLU] Renk ve beden birlikte değiştirilip sepete eklendiğinde sepette ikisi de görünmeli."""
    product, profil, _ = flows.kategoride_urun_ac(bos_sepet, COKLU)
    renk = product.baska_secenek_sec(profil.renk_grubu.ad)
    beden = product.baska_secenek_sec(product.profil().beden_grubu.ad)
    adim(f"Renk '{renk}', beden '{beden}' seçildi")
    product.add_to_cart()
    cart = product.go_to_cart()
    adim("Sepet")
    secenek = cart.first_item_variant_text()
    assert renk in secenek and beden in secenek.split("/"), \
        f"Seçilen '{renk}/{beden}', sepette '{secenek}'"


@pytest.mark.coklu_secimli
@pytest.mark.negatif
def test_coklu_secimde_beden_degisince_renk_secimi_kaybolmamali(app, adim):
    """[OLUMSUZ] Çoklu seçimli üründe yalnızca beden değiştirildiğinde seçili renk değişmemeli."""
    product, profil, _ = flows.kategoride_urun_ac(app, COKLU)
    renk = profil.renk_grubu.secili_deger
    beden = product.baska_secenek_sec(profil.beden_grubu.ad)
    adim(f"Beden '{beden}' seçildi")
    yeni_renk = product.profil().renk_grubu.secili_deger
    assert yeni_renk == renk, f"Beden değişince renk '{renk}' -> '{yeni_renk}' oldu"


# ---------------- İndirimli ürün ----------------
@pytest.mark.indirimli
@pytest.mark.pozitif
def test_indirimli_urunun_satis_fiyati_eski_fiyattan_yuksek_olmamali(app, adim):
    """[OLUMLU] İndirimli üründe satış fiyatı eski fiyattan düşük olmalı ve indirim yüzdesi fiyatlarla uyuşmalı."""
    _, profil, _ = flows.kategoride_urun_ac(app, INDIRIMLI)
    adim(f"Eski {profil.eski_fiyat} TL, satış {profil.satis_fiyati} TL, %{profil.indirim_orani}")
    assert profil.satis_fiyati < profil.eski_fiyat, "Satış fiyatı eski fiyattan düşük değil"
    hesaplanan = round((1 - profil.satis_fiyati / profil.eski_fiyat) * 100)
    # Uygulama yüzdeyi yuvarlayarak gösteriyor; 1 puan fark kabul edilir
    assert abs(hesaplanan - profil.indirim_orani) <= 1, \
        f"Gösterilen indirim %{profil.indirim_orani}, fiyatlardan hesaplanan %{hesaplanan}"


@pytest.mark.indirimli
@pytest.mark.negatif
def test_indirimli_urun_sepette_eski_fiyatindan_gosterilmemeli(bos_sepet, adim):
    """[OLUMSUZ] İndirimli ürün sepete eklendiğinde sepette indirimsiz (eski) fiyattan gösterilmemeli.

    Esas alınan fiyat, kullanıcının ödeyeceği sepet fiyatıdır. Ürün sayfasında gösterilen fiyat bazı
    ürünlerde Premium üyelik fiyatıdır ve sepetten düşüktür: bkz. hatalar/HB-001.
    """
    product, profil, _ = flows.kategoride_urun_ac(bos_sepet, INDIRIMLI)
    product.add_to_cart()
    cart = product.go_to_cart()
    adim("Sepet")
    sepet_fiyati = parse_price(cart.first_item_price_text())
    assert sepet_fiyati < profil.eski_fiyat, f"Sepet {sepet_fiyati} TL, eski fiyat {profil.eski_fiyat} TL"
    # Sepetteki "Bu üründen X TL kazancınız var" tutarı, sepet fiyatıyla eski fiyat arasındaki farka eşit olmalı
    kazanc = cart.first_item_savings()
    if kazanc is not None:
        assert abs(sepet_fiyati + kazanc - profil.eski_fiyat) <= 0.05, \
            f"Sepet {sepet_fiyati} + kazanç {kazanc} ≠ eski fiyat {profil.eski_fiyat}"


# ---------------- Stokta olmayan seçenek ----------------
@pytest.mark.stokta_olmayan
@pytest.mark.pozitif
def test_stokta_olan_secenege_donulunce_sepete_ekle_butonu_gizli_kalmamali(app, adim):
    """[OLUMLU] Stokta olmayan seçenekten stokta olan seçeneğe dönüldüğünde 'Sepete ekle' butonu yeniden görünmeli."""
    product, profil, _ = flows.kategoride_urun_ac(app, STOKTA_OLMAYAN)
    stokta_olan = next(g.secili_deger for g in profil.gruplar.values()
                       if any(s.stokta_yok for s in g.secenekler))
    product.stokta_olmayan_secenegi_sec()
    adim("Stokta olmayan seçenek seçildi")
    product.secenek_sec(stokta_olan)
    adim(f"Stoktaki '{stokta_olan}' seçeneğine dönüldü")
    assert product.is_visible(product.ADD_TO_CART, 10), "'Sepete ekle' butonu geri gelmedi"
    assert product.is_absent(product.COMBINATION_MISSING, 2), "Stoktaki seçeneğe dönüldüğü halde 'ürün bulunmamaktadır' uyarısı hâlâ görünüyor"


@pytest.mark.stokta_olmayan
@pytest.mark.negatif
def test_stokta_olmayan_secenek_secildiginde_urun_sepete_eklenememeli(app, adim):
    """[OLUMSUZ] 'Stokta yok' seçeneği seçildiğinde 'Sepete ekle' butonu gösterilmemeli, uyarı mesajı gösterilmeli."""
    product, _, _ = flows.kategoride_urun_ac(app, STOKTA_OLMAYAN)
    secenek = product.stokta_olmayan_secenegi_sec()
    adim(f"Stokta olmayan '{secenek}' seçildi")
    assert product.is_absent(product.ADD_TO_CART, 3), "Stokta olmayan seçenekte 'Sepete ekle' görünüyor"
    assert product.is_visible(product.COMBINATION_MISSING, 5), "'Ürün bulunmamaktadır' uyarısı yok"
