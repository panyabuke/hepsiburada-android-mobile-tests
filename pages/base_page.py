"""Tüm sayfaların ortak davranışları: eleman bulma, bekleme, açılır pencereleri kapatma."""
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

DEFAULT_TIMEOUT = 20


def by_id(name: str):
    """Hem native (paket:id/ad) hem Compose testTag (ad) kimliklerini eşler."""
    return AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().resourceIdMatches("(.*:id/)?{name}")'


def by_desc(desc: str):
    return AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().description("{desc}")'


def by_text(text: str):
    return AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")'


def by_text_contains(text: str):
    return AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{text}")'


class BasePage:
    # Uygulamanın zaman zaman gösterdiği ve testi engelleyen pencereler
    POPUPS = [
        by_text("Devam et"),            # bildirim izni tanıtım ekranı
        by_id("balloon_wrapper"),       # ipucu balonları ("Kategoriler artık anasayfada" vb.)
        by_text("İzin ver"),            # Android sistem izin penceresi
        by_text("Allow"),
        by_text("Got it"),              # Android tam ekran bilgilendirmesi
    ]

    def __init__(self, driver):
        self.driver = driver

    def find(self, locator, timeout=DEFAULT_TIMEOUT):
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))

    def find_all(self, locator):
        return self.driver.find_elements(*locator)

    def click(self, locator, timeout=DEFAULT_TIMEOUT):
        self.find(locator, timeout).click()

    def is_visible(self, locator, timeout=5) -> bool:
        try:
            self.find(locator, timeout)
            return True
        except TimeoutException:
            return False

    def is_absent(self, locator, timeout=5) -> bool:
        """Eleman belirtilen süre boyunca hiç görünmezse True döner."""
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))
            return False
        except TimeoutException:
            return True

    def dismiss_popups(self, rounds=2):
        self.driver.implicitly_wait(0)
        for _ in range(rounds):
            closed = False
            for locator in self.POPUPS:
                try:
                    self.driver.find_element(*locator).click()
                    closed = True
                except NoSuchElementException:
                    pass
            if not closed:
                break

    @property
    def activity(self) -> str:
        return self.driver.current_activity or ""

    def press_enter(self):
        self.driver.press_keycode(66)

    def go_back(self):
        self.driver.back()
