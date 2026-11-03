import time

from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage, by_desc, by_text

# "Çıkış yap" / "Çıkış Yap": hesaba giriş yapılmışken Hesabım sayfasının altında görünür
LOGOUT = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textMatches("(?i)çıkış yap")')
NAV_ACCOUNT = by_desc("Hesabım")
# Çıkış onay penceresindeki buton (uygulama sürümüne göre farklı yazılabiliyor)
LOGOUT_CONFIRM = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textMatches("(?i)(çıkış yap|çıkış|evet|tamam)")')


class AccountPage(BasePage):
    LOGIN_LINK = by_text("Giriş yap")
    REGISTER_LINK = by_text("Üye ol")
    GUEST_LABEL = by_text("Misafir kullanıcı")
    ORDERS = by_text("Siparişlerim")

    def wait_loaded(self):
        self.find(self.ORDERS, 20)
        return self

    def is_guest(self, timeout=5) -> bool:
        return self.is_visible(self.GUEST_LABEL, timeout)

    def is_logged_in(self) -> bool:
        return not self.is_guest(3) and self.is_absent(self.LOGIN_LINK, 2)

    def open_login(self):
        from pages.login_page import LoginPage
        self.click(self.LOGIN_LINK)
        return LoginPage(self.driver).wait_loaded()

    def logout(self):
        """Hesaptan çıkar ve sayfanın misafir kullanıcı görünümüne döndüğünü bekler."""
        for _ in range(8):
            if self.find_all(LOGOUT):
                break
            # "Çıkış yap" sayfanın en altında
            self.driver.swipe(540, 1800, 540, 700, 500)
            time.sleep(1)
        self.click(LOGOUT, 5)
        time.sleep(1)
        # Onay penceresi çıkarsa onaylanır (pencerede yine "Çıkış yap" ya da "Evet" yazar)
        onay = self.find_all(LOGOUT_CONFIRM)
        if onay:
            onay[-1].click()
        time.sleep(2)
        # Çıkıştan sonra uygulama Hesabım'da kalmayıp ana sayfaya dönüyor;
        # misafir görünümü Hesabım sekmesi yeniden açılarak kontrol edilir
        for _ in range(3):
            if self.is_visible(self.GUEST_LABEL, 5) or self.is_visible(self.LOGIN_LINK, 2):
                return self
            if self.find_all(NAV_ACCOUNT):
                self.click(NAV_ACCOUNT)
        raise AssertionError("Çıkış yapıldıktan sonra Hesabım sayfası misafir görünümüne dönmedi")
