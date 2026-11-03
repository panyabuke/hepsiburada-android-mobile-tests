"""Test edilen ürün kategorileri ve her kategori için ürün aranacak kelimeler.

Testler sabit bir ürüne bağlı değildir: her kategori için aşağıdaki kelimeler sırayla aranır,
ilk birkaç sonuç açılır ve sayfası kategorinin koşulunu sağlayan ilk ürün kullanılır
(bkz. pages/flows.py > kategoride_urun_ac, koşullar: utils/urun_profili.py > kategoriler).
Ürün yayından kalkar ya da kategorisi değişirse test kendiliğinden başka bir ürüne geçer.
"""
import pytest

from utils.urun_profili import BEDEN, COKLU, INDIRIMLI, RENK, STANDART, STOKTA_OLMAYAN

KATEGORILER = {
    STANDART: {
        "aciklama": "Renk/beden gibi seçimi olmayan, indirimsiz ürün",
        "aramalar": ["roman kitap", "a4 fotokopi kağıdı", "çay bardağı", "deterjan"],
    },
    RENK: {
        "aciklama": "Yalnızca renk seçimi olan ürün",
        "aramalar": ["kulaklık", "telefon kılıfı", "akıllı telefon"],
    },
    BEDEN: {
        "aciklama": "Yalnızca beden/numara seçimi olan ürün",
        "aramalar": ["erkek spor ayakkabı", "kadın spor ayakkabı", "erkek çorap"],
    },
    COKLU: {
        "aciklama": "Renk ve beden gibi birden fazla seçimi olan ürün",
        "aramalar": ["kadın kazak", "erkek mont", "erkek tişört"],
    },
    INDIRIMLI: {
        "aciklama": "Eski fiyatı üstü çizili, indirim yüzdesi gösterilen ürün",
        "aramalar": ["erkek tişört", "kadın elbise", "roman kitap"],
    },
    STOKTA_OLMAYAN: {
        "aciklama": "En az bir seçeneği 'Stokta yok' olan ürün",
        "aramalar": ["erkek tişört", "kadın kazak", "erkek mont"],
    },
}


def kategori_parametreleri(*adlar):
    """pytest.mark.parametrize için kategori listesi; her parametreye kategori adıyla bir marker ekler.

    Böylece yalnızca bir kategori şöyle çalıştırılabilir:  pytest -m beden_secimli
    """
    return [pytest.param(ad, marks=getattr(pytest.mark, ad), id=ad) for ad in (adlar or KATEGORILER)]
