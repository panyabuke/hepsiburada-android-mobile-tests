import time

from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import StaleElementReferenceException

from pages.base_page import BasePage, by_id

EMAIL_INPUT = (AppiumBy.XPATH, '//*[@resource-id="emailInput"]//android.widget.EditText | '
                               '//android.widget.EditText[@resource-id="emailInput"]')
PASSWORD_INPUT = (AppiumBy.XPATH, '//*[@resource-id="passwordInput"]//android.widget.EditText | '
                                  '//android.widget.EditText[@resource-id="passwordInput"]')

# Giriş başarısız olduğunda gösterilen mesaj: ekranda bir yazı ya da Android Toast
ERROR_MESSAGE = (AppiumBy.XPATH,
                 '//*[(self::android.widget.TextView or self::android.widget.Toast) and '
                 '(contains(@text,"hatalı") or contains(@text,"Hatalı") or contains(@text,"yanlış") or '
                 'contains(@text,"Yanlış") or contains(@text,"geçersiz") or contains(@text,"Geçersiz") or '
                 'contains(@text,"eşleşmiyor") or contains(@text,"bulunamadı") or contains(@text,"tekrar deneyin"))]')
LOADING = (AppiumBy.CLASS_NAME, "android.widget.ProgressBar")


class LoginPage(BasePage):
    AUTH_ACTIVITY = "AuthActivity"
    EMAIL_AREA = by_id("emailInput")
    PASSWORD_AREA = by_id("passwordInput")
    LOGIN_BUTTON = by_id("loginButton")
    GUEST_CONTINUE = by_id("continueWithoutRegisterTxt")

    def wait_loaded(self):
        self.find(self.LOGIN_BUTTON, 20)
        return self

    def is_open(self) -> bool:
        return self.AUTH_ACTIVITY in self.activity and self.is_visible(self.LOGIN_BUTTON, 10)

    def type_email(self, email: str):
        self.click(self.EMAIL_AREA)
        self.find(EMAIL_INPUT).send_keys(email)
        return self

    def type_password(self, password: str):
        self.click(self.PASSWORD_AREA)
        self.find(PASSWORD_INPUT).send_keys(password)
        return self

    def submit(self):
        # hide_keyboard() Android'de geri tuşuna basıp giriş ekranını kapatabiliyor; buton klavyenin üstünde kalıyor
        self.click(self.LOGIN_BUTTON)
        return self

    def login(self, email: str, password: str):
        return self.type_email(email).type_password(password).submit()

    def hata_mesajini_bekle(self, timeout=12):
        """Giriş denemesinden sonra yükleme bitip hata mesajı görünene kadar bekler; mesaj metnini döner.

        Mesaj ekranda bir yazı ya da kısa süreli Android bildirimi (Toast) olabilir. Süre içinde
        mesaj çıkmazsa None döner (yükleme yine de bitmiş olur, ekran görüntüsü sonrasında alınabilir).
        """
        self.driver.implicitly_wait(0)
        bitis = time.time() + timeout
        while time.time() < bitis:
            yukleniyor = self.find_all(LOADING)
            for el in self.find_all(ERROR_MESSAGE):
                try:
                    metin = el.text
                except StaleElementReferenceException:
                    continue
                if metin and (not yukleniyor or "Toast" in (el.get_attribute("className") or "")):
                    return metin
            time.sleep(0.3)
        return None
