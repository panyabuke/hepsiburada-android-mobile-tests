"""Birden fazla testte tekrar eden kullanıcı akışları."""
from config.urun_kategorileri import KATEGORILER
from utils.urun_profili import STANDART

# Bir kategoride uygun ürün bulunduğunda (arama kelimesi, sıra) burada saklanır;
# aynı çalıştırmadaki sonraki testler ürünü yeniden aramadan doğrudan açar.
_bulunan_urunler = {}
DENENECEK_URUN_SAYISI = 3


def ara(home, kelime):
    return home.open_search().search(kelime)


def kategoride_urun_ac(home, kategori=STANDART):
    """Kategoriye uyan bir ürünün sayfasını açar. (ürün sayfası, profil, kart metni) döner."""
    adaylar = []
    if kategori in _bulunan_urunler:
        adaylar.append(_bulunan_urunler[kategori])
    adaylar += [(k, i) for k in KATEGORILER[kategori]["aramalar"] for i in range(DENENECEK_URUN_SAYISI)]
    denenenler = []
    onceki_kelime = product = results = None
    for kelime, sira in adaylar:
        if kelime == onceki_kelime:
            # Aynı aramanın bir sonraki ürünü: ürün sayfasından sonuç listesine dönülür
            product.go_back()
            results.is_open(10)
        else:
            if onceki_kelime is not None:
                home.restart()
            results = ara(home, kelime)
            assert results.is_open(), "Arama sonuç sayfası açılmadı"
            onceki_kelime = kelime
        product, card_text = results.open_product(sira)
        profil = product.profil()
        if kategori in profil.kategoriler():
            _bulunan_urunler[kategori] = (kelime, sira)
            return product, profil, card_text
        denenenler.append(f"{kelime}#{sira + 1}: {sorted(profil.kategoriler())}")
    raise AssertionError(f"'{kategori}' kategorisine uyan ürün bulunamadı. Denenenler: {denenenler}")


def urun_ac(home, kategori=STANDART):
    """Kategoriye uyan ürünü açar. (ürün sayfası, kart metni) döner."""
    product, _, card_text = kategoride_urun_ac(home, kategori)
    return product, card_text


def sepete_urun_ekle(home, kategori=STANDART):
    """Kategoriye uyan ürünü sepete ekler ve sepete gider. (sepet sayfası, kart metni) döner."""
    product, card_text = urun_ac(home, kategori)
    product.add_to_cart()
    return product.go_to_cart(), card_text
