import time

from config.capabilities import ANDROID_PACKAGE
from pages.base_page import BasePage, by_desc, by_id, by_text_contains


class HomePage(BasePage):
    SEARCH_BOX = by_id("SearchBoxView")
    BOTTOM_NAV = by_id("bottom_navigation_compose")
    NAV_HOME = by_desc("Ana Sayfam")
    NAV_CART = by_desc("Sepetim")
    NAV_ACCOUNT = by_desc("Hesabım")
    BOT_BLOCK_TEXT = by_text_contains("Olağan dışı erişim")
    ERROR_TEXT = by_text_contains("Yüklenemedi")

    def restart(self):
        """Uygulamayı kapatıp açar ve ana sayfanın hazır olmasını bekler."""
        self.driver.terminate_app(ANDROID_PACKAGE)
        self.driver.activate_app(ANDROID_PACKAGE)
        # Uygulama son açık ekranı (ör. sepet) geri yükleyebiliyor; wait_ready ana sayfaya döner
        return self.wait_ready()

    def wait_ready(self, attempts=6):
        """Gecikmeli açılan balon/izin pencerelerini kapatarak ana sayfanın kullanılabilir olmasını bekler."""
        for _ in range(attempts):
            time.sleep(2)
            self.dismiss_popups()
            if self.is_visible(self.SEARCH_BOX, 3) and self.is_visible(self.BOTTOM_NAV, 2):
                time.sleep(1)
                self.dismiss_popups()
                return self
            if self.is_visible(self.NAV_HOME, 1):
                self.click(self.NAV_HOME)
            else:
                # Kimliksiz Compose ipucu pencereleri yalnızca geri tuşuyla kapanıyor
                self.go_back()
                if self.driver.query_app_state(ANDROID_PACKAGE) != 4:  # 4 = ön planda
                    self.driver.activate_app(ANDROID_PACKAGE)
        raise AssertionError("Ana sayfa kullanılabilir hale gelmedi")

    def open_home(self):
        self.click(self.NAV_HOME)
        self.find(self.SEARCH_BOX)
        return self

    def open_search(self):
        from pages.search_page import SearchPage
        page = SearchPage(self.driver)
        for _ in range(3):
            self.click(self.SEARCH_BOX)
            if page.is_open(5):
                return page
            # Araya giren gecikmeli bir pencere tıklamayı yutmuş olabilir
            self.dismiss_popups()
        raise AssertionError("Arama ekranı açılmadı")

    def back_to_tabs(self, max_back=4):
        """Alt menü görünene kadar geri gider (sepet/ürün gibi alt menüsüz ekranlardan dönüş)."""
        for _ in range(max_back):
            if self.is_visible(self.NAV_CART, 2):
                return self
            self.go_back()
        raise AssertionError("Alt menüye dönülemedi")

    def open_cart(self):
        from pages.cart_page import CartPage
        self.click(self.NAV_CART)
        return CartPage(self.driver).wait_loaded()

    def open_account(self):
        from pages.account_page import AccountPage
        self.click(self.NAV_ACCOUNT)
        return AccountPage(self.driver).wait_loaded()

    def is_loaded(self) -> bool:
        return self.is_visible(self.SEARCH_BOX, 20) and self.is_visible(self.BOTTOM_NAV, 5)
