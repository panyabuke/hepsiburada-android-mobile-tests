import time

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage, by_id, by_text, by_text_contains
from utils.urun_profili import KOMBINASYON_YOK, profil_cikar, secenek_konumlari, sekme_gorunuyor

# "Ürün sepete başarılı bir şekilde eklenmiştir": uygulama içi bildirim ya da Android Toast
ADDED_TOAST_ANY = (AppiumBy.XPATH, '//*[contains(@text,"sepete başarılı") or contains(@text,"sepetinize başarı")]')
# Alt fiyat çubuğunun üst kenarı; bunun altında kalan seçenekler çubuğun arkasında kalır
ALT_CUBUK_Y = 2100


def secenek(ad: str, secili: bool):
    durum = "seçili" if secili else "seçili değil"
    return AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().description("{ad},{durum}")'


class ProductPage(BasePage):
    LOADED = by_id("summaryTitleComponent")
    ADD_TO_CART = by_id("pdpAddToCart")
    TOOLBAR_CART = by_id("toolbarCartButton")
    GO_TO_CART = by_text("Sepete git")
    CONTINUE_SHOPPING = by_text("Alışverişe devam et")
    ADDED_TOAST = by_text_contains("sepete başarılı")
    COMBINATION_MISSING = by_text_contains(KOMBINASYON_YOK)

    def wait_loaded(self):
        self.find(self.LOADED, 25)
        return self

    # ---- Fiyat ----
    def profil(self, kaydir=True):
        """Sayfanın ürün profilini (seçenek grupları, fiyatlar, stok) döner. Bkz. utils/urun_profili.py"""
        if kaydir:
            self.secenekleri_goster()
        profil = profil_cikar(self.driver.page_source)
        if kaydir and profil.gruplar:
            # İkinci grup (ör. beden) ekranın altında kalmış olabilir
            self.driver.swipe(540, 1600, 540, 1200, 400)
            time.sleep(1)
            profil.birlestir(profil_cikar(self.driver.page_source))
        return profil

    def en_uste_don(self):
        """Sayfanın başına (ürün görseli, Premium bandı) kaydırır."""
        for _ in range(4):
            self.driver.swipe(540, 600, 540, 1800, 400)
        time.sleep(1)
        return self

    def price_text(self) -> str:
        """Misafir kullanıcının ödeyeceği satış fiyatı ('578,04 TL')."""
        fiyat = profil_cikar(self.driver.page_source).satis_fiyati
        assert fiyat is not None, "Ürün sayfasında fiyat bulunamadı"
        return f"{fiyat:,.2f}".replace(",", "#").replace(".", ",").replace("#", ".") + " TL"

    # ---- Seçenekler ----
    def secenekleri_goster(self, deneme=6) -> bool:
        """Seçenek kutuları ekranın görünür kısmına gelene kadar sayfayı kaydırır."""
        for _ in range(deneme):
            xml = self.driver.page_source
            for (_, y1, _, y2), _ in secenek_konumlari(xml).values():
                if 300 < y1 and y2 < ALT_CUBUK_Y:
                    return True
            if sekme_gorunuyor(xml):
                # Açıklama/Özellikler sekmelerine gelindiyse seçenek alanı geçilmiştir
                return False
            self.driver.swipe(540, 1700, 540, 1100, 500)
            time.sleep(1)
        return False

    def _secenege_dokun(self, ad: str):
        self.secenekleri_goster()
        for _ in range(4):
            konum = secenek_konumlari(self.driver.page_source).get(ad)
            assert konum, f"'{ad}' seçeneği bulunamadı"
            (x1, y1, x2, y2), _ = konum
            if y2 > ALT_CUBUK_Y:
                # Seçenek alt fiyat çubuğunun arkasında; dokunma çubuğa gider
                self.driver.swipe(540, 1600, 540, 1200, 400)
            elif y1 < 300:
                self.driver.swipe(540, 1100, 540, 1500, 400)
            else:
                self.driver.tap([((x1 + x2) // 2, (y1 + y2) // 2)])
                return
            time.sleep(1)
        raise AssertionError(f"'{ad}' seçeneği ekranın görünür alanına getirilemedi")

    def secenek_sec(self, ad: str) -> bool:
        """Seçeneğe dokunur; seçenek seçili hale gelirse True döner.

        Sayfa kayarken yapılan dokunma yalnızca kaymayı durdurur, seçim yapmaz. Seçim görünmezse
        konum yeniden okunup bir kez daha dokunulur.
        """
        for _ in range(2):
            self._secenege_dokun(ad)
            if self.is_visible(secenek(ad, True), 5):
                return True
        return False

    def secili_secenege_dokun(self, ad: str):
        self._secenege_dokun(ad)
        time.sleep(2)
        return self

    def baska_secenek_sec(self, grup_adi: str) -> str:
        """Gruptaki seçili olmayan ve stokta olan bir seçeneği seçer.

        Seçilen renk/beden kombinasyonu bulunmuyorsa ('... kombinasyonunda ürün bulunmamaktadır')
        bir sonraki seçenek denenir. Seçilen seçeneğin adını döner.
        """
        grup = self.profil().gruplar[grup_adi]
        denenenler = []
        for s in grup.secenekler:
            if s.secili or s.stokta_yok:
                denenenler.append(f"{s.ad}: {'seçili' if s.secili else 'stokta yok'}")
                continue
            if not self.secenek_sec(s.ad):
                denenenler.append(f"{s.ad}: dokunuldu, seçilmedi")
            elif self.is_visible(self.ADD_TO_CART, 5) and self.is_absent(self.COMBINATION_MISSING, 1):
                return s.ad
            else:
                denenenler.append(f"{s.ad}: bu kombinasyon yok")
        raise AssertionError(f"'{grup_adi}' grubunda seçilebilecek başka seçenek yok: {denenenler}")

    def stokta_olmayan_secenegi_sec(self) -> str:
        s = self.profil().stokta_olmayan_secenekler()
        assert s, "Stokta olmayan seçenek yok"
        self.secenek_sec(s[0].ad)
        return s[0].ad

    # ---- Sepet ----
    def add_to_cart(self):
        """'Sepete ekle'ye basar ve eklendiğinin onayını bekler.

        Onay çoğunlukla 'Sepete git / Alışverişe devam et' penceresidir; ara sıra pencere çıkmaz,
        yalnızca 'Ürün sepete başarılı bir şekilde eklenmiştir' bildirimi görünür.
        """
        self.click(self.ADD_TO_CART)
        WebDriverWait(self.driver, 20).until(
            lambda d: d.find_elements(*self.GO_TO_CART) or d.find_elements(*ADDED_TOAST_ANY))
        return self

    def go_to_cart(self):
        from pages.cart_page import CartPage
        if self.is_visible(self.GO_TO_CART, 3):
            self.click(self.GO_TO_CART)
        else:
            # Onay penceresi çıkmadıysa sepete üstteki sepet simgesinden gidilir
            self.click(self.TOOLBAR_CART)
        return CartPage(self.driver).wait_loaded()

    def continue_shopping(self):
        self.click(self.CONTINUE_SHOPPING)
        return self

    def open_cart_from_toolbar(self):
        from pages.cart_page import CartPage
        self.click(self.TOOLBAR_CART)
        return CartPage(self.driver).wait_loaded()
