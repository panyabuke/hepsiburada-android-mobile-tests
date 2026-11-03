import re

from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage, by_id, by_text_contains

PRODUCT_CARD = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceIdMatches("productBox.[0-9]+.")')
# Reklam/sponsor alanında olmayan, normal liste içindeki ürün kartları
LISTED_PRODUCT = (AppiumBy.XPATH,
                  '//*[contains(@resource-id,"composeProductBoxView")]//*[starts-with(@resource-id,"productBox[")]')


class SearchResultsPage(BasePage):
    TITLE = by_id("tvTitle")
    PRODUCT_LIST = by_id("rvPlp")
    NO_RESULT = by_text_contains("Aramana uygun ürün bulunamadı")

    def title(self, timeout=20) -> str:
        return self.find(self.TITLE, timeout).text

    def is_open(self, timeout=20) -> bool:
        return self.is_visible(self.TITLE, timeout)

    def result_count(self, timeout=15) -> int:
        """Başlıktaki '(10.000+)' / '(0)' bilgisini sayıya çevirir.

        Başlık önce yalnızca aranan kelimeyle gelir, sayı birkaç saniye sonra eklenir.
        """
        pattern = re.compile(r"\(([\d.]+)\+?\)")
        WebDriverWait(self.driver, timeout).until(lambda _: pattern.search(self.title(5)))
        return int(pattern.search(self.title()).group(1).replace(".", ""))

    def shows_no_result(self, timeout=10) -> bool:
        return self.is_visible(self.NO_RESULT, timeout)

    def listed_products(self):
        return self.find_all(LISTED_PRODUCT)

    def open_first_product(self):
        """İlk normal ürünü açar; (ürün sayfası, kart metni) döner."""
        return self.open_product(0)

    def open_product(self, sira=0):
        """Listedeki `sira`'ncı normal (reklam olmayan) ürünü açar; (ürün sayfası, kart metni) döner."""
        from pages.product_page import ProductPage
        self.find(self.PRODUCT_LIST)
        product = ProductPage(self.driver)
        card_text = ""
        for _ in range(5):
            # Önceki dokunma geç de olsa ürün sayfasını açmış olabilir; listeyi kaydırmadan önce bakılır
            if product.is_visible(product.LOADED, 1):
                return product, card_text
            try:
                cards = sorted(self.find_all(LISTED_PRODUCT), key=lambda c: (c.rect["y"], c.rect["x"]))
                if len(cards) <= sira:
                    # Büyük reklam alanı normal ürünleri ekranın altına itmiş olabilir
                    self.driver.swipe(540, 1800, 540, 900, 600)
                    continue
                card_text, rect = cards[sira].text, cards[sira].rect
            except StaleElementReferenceException:
                # Liste, kart bulunduktan hemen sonra yeniden çizilebiliyor
                continue
            if rect["y"] + rect["height"] > 2250:
                # Kartın alt kısmı ekran dışında; dokunulacak yer görünür olmalı
                self.driver.swipe(540, 1600, 540, 1000, 500)
                continue
            # Kartın ortası kaydırılabilir resim galerisi ve tıklamayı bazen yutuyor;
            # bu yüzden kartın alt kısmındaki ürün adına dokunulur.
            self.driver.tap([(rect["x"] + rect["width"] // 2, rect["y"] + int(rect["height"] * 0.72))])
            if product.is_visible(product.LOADED, 12):
                return product, card_text
        raise AssertionError("Ürün sayfası açılamadı")
