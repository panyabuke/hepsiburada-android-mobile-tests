"""Ürün detay sayfasının XML kaynağından (page_source) ürün profilini çıkarır ve ürünün kategorilerini belirler.

Saf Python'dur, cihaz gerektirmez. White box testleri bu kodun her dalını doğrudan test eder.

Sayfadaki yapı (Hepsiburada 5.102.1):
- Seçenek grubu başlığı:  TextView text="Renk: Krem" / "Beden: M" / "Ayakkabı Numarası: 37"
- Seçenek:                View content-desc="Krem,seçili" / "Lacivert,seçili değil"
- Stokta olmayan seçenek: seçeneğin içinde content-desc="Stokta yok"
- Alt fiyat çubuğu:       originalPriceComponent (eski/liste fiyatı), "%24" indirim etiketi,
                          satış fiyatı iki parça halinde: "578" + ",04 TL"
"""
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

from utils.price import parse_price

STANDART = "standart"
RENK = "renk_secimli"
BEDEN = "beden_secimli"
COKLU = "coklu_secimli"
INDIRIMLI = "indirimli"
STOKTA_OLMAYAN = "stokta_olmayan"
KATEGORILER = (STANDART, RENK, BEDEN, COKLU, INDIRIMLI, STOKTA_OLMAYAN)

ETIKET = re.compile(r"^([^:]{2,30}): (.+)$")
ETIKET_DISI = {"alt limit", "satıcı"}
SECENEK = re.compile(r"^(.+),(seçili|seçili değil)$")
# Ürün sayfasının alt sekmeleri de "Açıklama,seçili" biçiminde; seçenek sayılmamalı
SEKMELER = {"Açıklama", "Özellikler", "Soru & Cevap", "İptal & İade", "Değerlendirmeler"}
RENK_GRUBU = re.compile(r"renk", re.I)
BEDEN_GRUBU = re.compile(r"beden|numara", re.I)
KOMBINASYON_YOK = "kombinasyonunda ürün bulunmamaktadır"
# Ürün sayfasının üstündeki pembe bant: "Premium'a geç, 578,04 TL'ye al"
PREMIUM_TEKLIF = re.compile(r"Premium'a geç, (.+ TL)'ye al")
# Bir seçenek, kendisinden en fazla bu kadar piksel yukarıdaki başlığa ait sayılır
GRUP_MESAFESI = 450


@dataclass
class Secenek:
    ad: str
    secili: bool
    stokta_yok: bool = False


@dataclass
class Grup:
    ad: str
    secili_deger: str
    secenekler: list = field(default_factory=list)

    @property
    def secim_var(self) -> bool:
        return len(self.secenekler) > 1

    def secenek(self, ad):
        return next((s for s in self.secenekler if s.ad == ad), None)


@dataclass
class UrunProfili:
    gruplar: dict = field(default_factory=dict)
    eski_fiyat: float = None
    satis_fiyati: float = None
    indirim_orani: int = 0
    premium_indirimi: bool = False
    premium_teklif_fiyati: float = None
    sepete_eklenebilir: bool = False
    kombinasyon_yok: bool = False

    def secim_gruplari(self):
        return [g for g in self.gruplar.values() if g.secim_var]

    def grup(self, desen):
        return next((g for g in self.gruplar.values() if desen.search(g.ad)), None)

    @property
    def renk_grubu(self):
        return self.grup(RENK_GRUBU)

    @property
    def beden_grubu(self):
        return self.grup(BEDEN_GRUBU)

    def stokta_olmayan_secenekler(self):
        return [s for g in self.gruplar.values() for s in g.secenekler if s.stokta_yok]

    @property
    def indirimli(self) -> bool:
        # "Premium ile" indirimi misafir kullanıcıya uygulanmaz; indirimli sayılmaz
        return self.indirim_orani > 0 and not self.premium_indirimi

    def kategoriler(self) -> set:
        secim = self.secim_gruplari()
        sonuc = set()
        if not secim and not self.indirimli:
            sonuc.add(STANDART)
        if len(secim) == 1 and RENK_GRUBU.search(secim[0].ad):
            sonuc.add(RENK)
        if len(secim) == 1 and BEDEN_GRUBU.search(secim[0].ad):
            sonuc.add(BEDEN)
        if len(secim) >= 2:
            sonuc.add(COKLU)
        if self.indirimli:
            sonuc.add(INDIRIMLI)
        if self.stokta_olmayan_secenekler():
            sonuc.add(STOKTA_OLMAYAN)
        return sonuc

    def birlestir(self, diger: "UrunProfili") -> "UrunProfili":
        """Sayfa kaydırılarak alınan ikinci görünümdeki grup/seçenekleri bu profile ekler."""
        for ad, grup in diger.gruplar.items():
            if ad not in self.gruplar:
                self.gruplar[ad] = grup
                continue
            mevcut = self.gruplar[ad]
            for s in grup.secenekler:
                if mevcut.secenek(s.ad) is None:
                    mevcut.secenekler.append(s)
        self.kombinasyon_yok = self.kombinasyon_yok or diger.kombinasyon_yok
        return self


def _dugumler(xml: str):
    """Her düğüm için (dikdörtgen, text, content-desc, resource-id, sınıf) döner."""
    for n in ET.fromstring(xml).iter():
        b = n.get("bounds")
        if not b:
            continue
        x1, y1, x2, y2 = map(int, re.findall(r"-?\d+", b))
        yield (x1, y1, x2, y2), n.get("text") or "", n.get("content-desc") or "", \
            n.get("resource-id") or "", n.get("class") or ""


def _icinde(ic, dis) -> bool:
    return dis[0] <= ic[0] and ic[2] <= dis[2] and dis[1] <= ic[1] and ic[3] <= dis[3]


def _gruplar(dugumler) -> dict:
    etiketler, secenekler, stok_isaretleri = [], {}, []
    for rect, text, desc, _, cls in dugumler:
        m = ETIKET.match(text)
        if m and cls.endswith("TextView") and m.group(1).strip().lower() not in ETIKET_DISI:
            etiketler.append((rect[1], m.group(1).strip(), m.group(2).strip()))
        m = SECENEK.match(desc)
        if m and m.group(1) not in SEKMELER:
            # Aynı seçenek iç içe birden fazla düğümde görünebilir; en dıştaki tutulur
            secenekler.setdefault(m.group(1), (rect, m.group(2) == "seçili"))
        if desc == "Stokta yok":
            stok_isaretleri.append(rect)

    gruplar = {}
    for _, ad, deger in etiketler:
        gruplar.setdefault(ad, Grup(ad, deger))
    for secenek_adi, (rect, secili) in secenekler.items():
        ustteki = [e for e in etiketler if e[0] < rect[1] and rect[1] - e[0] <= GRUP_MESAFESI]
        if not ustteki:
            continue
        grup = gruplar[max(ustteki)[1]]
        stokta_yok = any(_icinde(s, rect) for s in stok_isaretleri)
        grup.secenekler.append(Secenek(secenek_adi, secili, stokta_yok))
    for grup in gruplar.values():
        if not grup.secenekler:
            # Tek seçenekli grup (ör. yalnızca "Renk: Siyah" yazan kutu): seçim yapılamaz
            grup.secenekler.append(Secenek(grup.secili_deger, True))
    return gruplar


def _fiyatlar(dugumler, profil: UrunProfili):
    alt = None
    for rect, *_ , rid, _ in dugumler:
        if rid.endswith("bottomBoxComposeView"):
            alt = rect
    if alt is None:
        return
    icerik = [(t, d, r) for rect, t, d, r, _ in dugumler if _icinde(rect, alt)]
    for i, (text, desc, rid) in enumerate(icerik):
        if rid == "originalPriceComponent" and i + 1 < len(icerik):
            profil.eski_fiyat = parse_price(icerik[i + 1][1])
        m = re.match(r"^%(\d+)$", desc)
        if m:
            profil.indirim_orani = int(m.group(1))
        if text == "Premium ile":
            profil.premium_indirimi = True
        # Satış fiyatı iki parça: "578" + ",04 TL" / "323" + ",90TL" (indirimsiz üründe boşluksuz) / "14.799" + "TL"
        kusurat = re.match(r"^(,\d{1,2})? ?TL$", icerik[i + 1][0]) if i + 1 < len(icerik) else None
        if re.match(r"^[\d.]+$", text) and kusurat:
            profil.satis_fiyati = parse_price(f"{text}{kusurat.group(1) or ''} TL")
        if rid.endswith("pdpAddToCart"):
            profil.sepete_eklenebilir = True
    # Fiyat tek parçaysa indirim yoktur; "Premium ile" fiyatı ise misafir kullanıcının ödediği fiyat değildir
    if profil.satis_fiyati is None or profil.premium_indirimi:
        profil.satis_fiyati = profil.eski_fiyat


def secenek_konumlari(xml: str) -> dict:
    """Seçenek adı -> (dikdörtgen, seçili mi). Sayfa sekmeleri dahil değildir.

    Elemanlar yerine tek seferlik sayfa kaynağı kullanılır: sayfa seçenek okunurken yeniden
    çizildiğinde eleman referansları geçersizleşiyor (StaleElementReferenceException).
    """
    konumlar = {}
    for rect, _, desc, _, _ in _dugumler(xml):
        m = SECENEK.match(desc)
        if m and m.group(1) not in SEKMELER:
            konumlar.setdefault(m.group(1), (rect, m.group(2) == "seçili"))
    return konumlar


def sekme_gorunuyor(xml: str) -> bool:
    return any(SECENEK.match(d) and SECENEK.match(d).group(1) in SEKMELER for _, _, d, _, _ in _dugumler(xml))


def profil_cikar(xml: str) -> UrunProfili:
    dugumler = list(_dugumler(xml))
    profil = UrunProfili(gruplar=_gruplar(dugumler))
    _fiyatlar(dugumler, profil)
    profil.kombinasyon_yok = any(KOMBINASYON_YOK in t for _, t, *_ in dugumler)
    for _, text, *_ in dugumler:
        m = PREMIUM_TEKLIF.search(text)
        if m:
            profil.premium_teklif_fiyati = parse_price(m.group(1))
    return profil
