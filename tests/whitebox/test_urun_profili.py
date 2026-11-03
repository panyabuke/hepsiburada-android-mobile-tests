"""WHITE BOX (kategoriler): utils/urun_profili.py kategori belirleme kodunun dalları test edilir.

Kategori testlerinin hangi ürünü kullanacağı bu koda bağlıdır; yanlış kategoriye atanan bir ürün,
o kategorinin tüm testlerini anlamsız hale getirir. Testler, uygulamanın gerçek ekran yapısını
taklit eden küçük XML örnekleriyle çalışır; cihaz/Appium gerektirmez.

Kod yolları:
  1) seçenek grubu başlığı ("Renk: X")            -> grup oluşturma
  2) başlığa ait seçenekler                       -> gruba ekleme (en yakın üst başlık, en fazla 450 px)
  3) seçeneksiz başlık                            -> tek seçenekli grup (seçim sayılmaz)
  4) "Stokta yok" işareti seçeneğin içindeyse     -> stokta_yok = True
  5) alt çubukta tek fiyat                        -> indirimsiz, satış = eski fiyat
  6) alt çubukta eski fiyat + %N + iki parçalı fiyat -> indirimli
  7) "Premium ile" fiyatı                         -> indirimli sayılmaz, satış = eski fiyat
  8) sayfa sekmeleri / "Alt limit:" başlığı       -> seçenek/grup sayılmaz
  9) birleştirme (kaydırılmış ikinci görünüm)      -> aynı seçenek iki kez eklenmez
"""
import pytest

from config.urun_kategorileri import kategori_parametreleri
from utils.urun_profili import (BEDEN, COKLU, INDIRIMLI, RENK, STANDART, STOKTA_OLMAYAN,
                                profil_cikar)

pytestmark = pytest.mark.whitebox


# ---- Ekran yapısını taklit eden küçük XML parçaları ----
def _dugum(x1, y1, x2, y2, text="", desc="", rid="", cls="android.view.View", ic=""):
    return (f'<node class="{cls}" bounds="[{x1},{y1}][{x2},{y2}]" text="{text}" '
            f'content-desc="{desc}" resource-id="{rid}">{ic}</node>')


def etiket(y, metin):
    return _dugum(42, y, 500, y + 40, text=metin, cls="android.widget.TextView")


def secenekler(y, adlar, secili, stokta_yok=()):
    parca = ""
    for i, ad in enumerate(adlar):
        x = 10 + i * 200
        isaret = _dugum(x, y + 140, x + 180, y + 170, desc="Stokta yok") if ad in stokta_yok else ""
        durum = "seçili" if ad == secili else "seçili değil"
        parca += _dugum(x, y, x + 180, y + 170, desc=f"{ad},{durum}", ic=isaret)
    return parca


def alt_cubuk(eski="349,00 TL", yuzde=None, satis=None, premium=False):
    ic = _dugum(21, 2168, 153, 2210, rid="originalPriceComponent",
                ic=_dugum(21, 2168, 153, 2210, desc=eski))
    if yuzde:
        ic += _dugum(169, 2170, 225, 2208, desc=f"%{yuzde}")
    if premium:
        ic += _dugum(21, 2224, 179, 2259, text="Premium ile", cls="android.widget.TextView")
    if satis:
        ic += _dugum(21, 2259, 110, 2316, text=satis[0], cls="android.widget.TextView")
        ic += _dugum(110, 2276, 198, 2311, text=satis[1], cls="android.widget.TextView")
    ic += _dugum(378, 2178, 1059, 2304, rid="com.pozitron.hepsiburada:id/pdpAddToCart")
    return _dugum(0, 2144, 1080, 2337, rid="com.pozitron.hepsiburada:id/bottomBoxComposeView", ic=ic)


def sayfa(*parcalar):
    return _dugum(0, 0, 1080, 2400, ic="".join(parcalar))


ORNEK_SAYFALAR = {
    STANDART: sayfa(alt_cubuk()),
    RENK: sayfa(etiket(1500, "Renk: Siyah"), secenekler(1560, ["Siyah", "Beyaz", "Mavi"], "Siyah"),
                alt_cubuk()),
    BEDEN: sayfa(etiket(1400, "Renk: Siyah"),
                 etiket(1500, "Ayakkabı Numarası: 37"), secenekler(1560, ["36", "37", "38"], "37"),
                 alt_cubuk()),
    COKLU: sayfa(etiket(1200, "Renk: Krem"), secenekler(1260, ["Krem", "Lacivert"], "Krem"),
                 etiket(1500, "Beden: M"), secenekler(1560, ["S", "M", "L"], "M"),
                 alt_cubuk()),
    INDIRIMLI: sayfa(alt_cubuk("755,61 TL", 24, ("578", ",04 TL"))),
    STOKTA_OLMAYAN: sayfa(etiket(1500, "Renk: Siyah"),
                          secenekler(1560, ["Siyah", "Beyaz"], "Siyah", stokta_yok=["Beyaz"]),
                          alt_cubuk()),
}
BEKLENEN = {
    STANDART: {STANDART},
    RENK: {RENK},
    BEDEN: {BEDEN},
    COKLU: {COKLU},
    INDIRIMLI: {INDIRIMLI},
    STOKTA_OLMAYAN: {RENK, STOKTA_OLMAYAN},
}


@pytest.mark.pozitif
@pytest.mark.parametrize("kategori", kategori_parametreleri())
def test_urun_sayfasi_yanlis_kategoriye_atanmamali(kategori):
    """[OLUMLU] Her kategorinin örnek sayfası tam olarak beklenen kategorilere atanmalı (yol 1-6)."""
    assert profil_cikar(ORNEK_SAYFALAR[kategori]).kategoriler() == BEKLENEN[kategori]


@pytest.mark.pozitif
def test_indirimli_urunun_fiyatlari_yanlis_okunmamali():
    """[OLUMLU] Eski fiyat, indirim yüzdesi ve iki parçalı satış fiyatı doğru okunmalı (yol 6)."""
    p = profil_cikar(ORNEK_SAYFALAR[INDIRIMLI])
    assert (p.eski_fiyat, p.satis_fiyati, p.indirim_orani) == (755.61, 578.04, 24)
    assert p.sepete_eklenebilir


@pytest.mark.pozitif
@pytest.mark.parametrize("tam, kusurat, beklenen", [
    ("578", ",04 TL", 578.04),     # indirimli üründe boşluklu
    ("323", ",90TL", 323.90),      # indirimsiz üründe boşluksuz
    ("14.799", "TL", 14799.0),     # kuruşsuz
])
def test_iki_parcali_satis_fiyati_hicbir_yazimda_kacirilmamali(tam, kusurat, beklenen):
    """[OLUMLU] Satış fiyatı, kuruş kısmı hangi biçimde yazılırsa yazılsın okunmalı (yol 5-6)."""
    xml = sayfa(_dugum(0, 2144, 1080, 2337, rid="com.pozitron.hepsiburada:id/bottomBoxComposeView",
                       ic=_dugum(21, 2242, 113, 2299, text=tam, cls="android.widget.TextView")
                       + _dugum(113, 2259, 193, 2294, text=kusurat, cls="android.widget.TextView")))
    assert profil_cikar(xml).satis_fiyati == beklenen


@pytest.mark.negatif
def test_tek_fiyatli_urun_indirimli_sayilmamali():
    """[OLUMSUZ] Alt çubukta tek fiyat varsa ürün indirimli sayılmamalı, satış fiyatı o fiyat olmalı (yol 5)."""
    p = profil_cikar(ORNEK_SAYFALAR[STANDART])
    assert not p.indirimli and p.satis_fiyati == p.eski_fiyat == 349.0


@pytest.mark.negatif
def test_premium_indirimi_misafir_icin_indirim_sayilmamali():
    """[OLUMSUZ] 'Premium ile' gösterilen indirimli fiyat misafir kullanıcının fiyatı sayılmamalı (yol 7)."""
    p = profil_cikar(sayfa(alt_cubuk("755,53 TL", 13, ("655", ",53 TL"), premium=True)))
    assert not p.indirimli and INDIRIMLI not in p.kategoriler()
    assert p.satis_fiyati == 755.53


@pytest.mark.pozitif
def test_premium_teklif_bandindaki_fiyat_kacirilmamali():
    """[OLUMLU] Üstteki "Premium'a geç, 578,04 TL'ye al" bandındaki fiyat okunmalı (HB-001'in tespiti için)."""
    bant = _dugum(0, 1160, 1080, 1250, text="Premium'a geç, 578,04 TL'ye al", cls="android.widget.TextView")
    assert profil_cikar(sayfa(bant, alt_cubuk())).premium_teklif_fiyati == 578.04


@pytest.mark.negatif
def test_premium_bandi_olmayan_sayfada_premium_fiyati_uydurulmamali():
    """[OLUMSUZ] Premium bandı yoksa Premium teklif fiyatı boş kalmalı."""
    assert profil_cikar(ORNEK_SAYFALAR[INDIRIMLI]).premium_teklif_fiyati is None


@pytest.mark.negatif
def test_tek_secenekli_grup_secim_sayilmamali():
    """[OLUMSUZ] Yalnızca 'Renk: Siyah' yazan, seçeneği olmayan grup seçim yapılabilir sayılmamalı (yol 3)."""
    p = profil_cikar(sayfa(etiket(1500, "Renk: Siyah"), alt_cubuk()))
    assert p.renk_grubu.secenekler[0].ad == "Siyah" and not p.renk_grubu.secim_var
    assert p.kategoriler() == {STANDART}


@pytest.mark.negatif
def test_sayfa_sekmeleri_ve_alt_limit_secenek_sayilmamali():
    """[OLUMSUZ] 'Açıklama,seçili' gibi sekmeler ve 'Alt limit:' başlığı renk/beden seçeneği sayılmamalı (yol 8)."""
    p = profil_cikar(sayfa(etiket(1500, "Alt limit: 1.250 TL"),
                           secenekler(1560, ["Açıklama", "Özellikler"], "Açıklama"), alt_cubuk()))
    assert p.gruplar == {} and p.kategoriler() == {STANDART}


@pytest.mark.negatif
def test_basliktan_uzaktaki_secenek_gruba_eklenmemeli():
    """[OLUMSUZ] Başlıktan 450 pikselden daha aşağıdaki seçenek o başlığın grubuna eklenmemeli (yol 2)."""
    p = profil_cikar(sayfa(etiket(1000, "Renk: Siyah"), secenekler(1600, ["Siyah", "Beyaz"], "Siyah"),
                           alt_cubuk()))
    assert [s.ad for s in p.renk_grubu.secenekler] == ["Siyah"]


@pytest.mark.negatif
def test_stokta_yok_isareti_komsu_secenege_tasinmamali():
    """[OLUMSUZ] 'Stokta yok' işareti yalnızca içinde bulunduğu seçeneğe ait olmalı (yol 4)."""
    p = profil_cikar(ORNEK_SAYFALAR[STOKTA_OLMAYAN])
    assert {s.ad: s.stokta_yok for s in p.renk_grubu.secenekler} == {"Siyah": False, "Beyaz": True}


@pytest.mark.negatif
def test_kaydirilmis_gorunum_birlestirilince_secenek_tekrarlanmamali():
    """[OLUMSUZ] Aynı sayfanın iki görünümü birleştirildiğinde aynı seçenek iki kez eklenmemeli (yol 9)."""
    ust = profil_cikar(sayfa(etiket(1500, "Renk: Krem"), secenekler(1560, ["Krem", "Lacivert"], "Krem")))
    alt = profil_cikar(sayfa(etiket(1100, "Renk: Krem"), secenekler(1160, ["Krem", "Lacivert"], "Krem"),
                             etiket(1400, "Beden: M"), secenekler(1460, ["S", "M"], "M")))
    p = ust.birlestir(alt)
    assert [s.ad for s in p.renk_grubu.secenekler] == ["Krem", "Lacivert"]
    assert p.kategoriler() == {COKLU}
