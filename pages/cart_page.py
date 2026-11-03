import re

from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage, by_desc, by_id, by_text, by_text_contains
from utils.price import parse_price

TOTAL_PRICE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionStartsWith("Toplam fiyat.")')
# Ürün adının hemen altındaki satır: seçenekli ürünlerde "Krem/S", diğerlerinde kargo bilgisi
VARIANT_TEXT = (AppiumBy.XPATH, '//*[@resource-id="productName"]/following-sibling::android.widget.TextView[1]')
QUANTITY = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionStartsWith("Ürün sayısı ")')
INCREASE_QUANTITY = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("Ürün sayısını artır")')


class CartPage(BasePage):
    HEADER = by_id("basketPage_headerText")
    PRODUCT_NAME = by_id("productName")
    CHECKOUT = by_desc("Ödemeye Geç")
    DELETE_ALL = by_desc("Sepeti sil")
    CONFIRM_DELETE_ALL = by_text("Tümünü sil")
    EMPTY_TEXT = by_text("Sepetin şu an boş")
    ITEM_COUNT = by_text_contains("Ürün)")

    def wait_loaded(self):
        self.find(self.HEADER, 20)
        return self

    def is_empty(self, timeout=10) -> bool:
        return self.is_visible(self.EMPTY_TEXT, timeout)

    def item_names(self):
        return [e.text for e in self.find_all(self.PRODUCT_NAME)]

    def item_count(self) -> int:
        """Başlıktaki '(N Ürün)' bilgisinden sepet adedini okur."""
        if self.is_empty(3):
            return 0
        match = re.search(r"\d+", self.find(self.ITEM_COUNT, 10).text)
        return int(match.group()) if match else 0

    def first_item_price_text(self) -> str:
        name_y = self.find(self.PRODUCT_NAME).location["y"]
        for el in self.find_all((AppiumBy.ANDROID_UIAUTOMATOR,
                                 'new UiSelector().descriptionMatches("^[0-9.]+(,[0-9]+)? TL$")')):
            if el.location["y"] > name_y:
                return el.get_attribute("content-desc")
        raise AssertionError("Sepette ürün fiyatı bulunamadı")

    def first_item_variant_text(self) -> str:
        """Sepetteki ilk ürünün seçenek bilgisi, ör. 'Krem/S'."""
        return self.find(VARIANT_TEXT, 10).text

    def increase_first_item_quantity(self):
        """İlk ürünün adedini 1 artırır ve yeni adedin görünmesini bekler."""
        adet = int(re.search(r"\d+", self.find(QUANTITY).get_attribute("content-desc")).group())
        self.click(INCREASE_QUANTITY)
        self.find((AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().description("Ürün sayısı {adet + 1}")'), 15)
        return adet + 1

    def first_item_savings(self):
        """Sepetteki ilk ürünün 'Bu üründen 113,34 TL kazancınız var' tutarı; gösterilmiyorsa None."""
        el = self.find_all((AppiumBy.ANDROID_UIAUTOMATOR,
                            'new UiSelector().descriptionMatches("Bu üründen .+ TL kazancınız var")'))
        if not el:
            return None
        m = re.search(r"Bu üründen (.+ TL) kazancınız var", el[0].get_attribute("content-desc"))
        return parse_price(m.group(1))

    def total_price_text(self) -> str:
        return self.find(TOTAL_PRICE).get_attribute("content-desc").replace("Toplam fiyat.", "").strip()

    def clear(self):
        if self.is_empty(3):
            return self
        self.click(self.DELETE_ALL)
        self.click(self.CONFIRM_DELETE_ALL)
        self.find(self.EMPTY_TEXT, 15)
        return self

    def checkout(self):
        from pages.login_page import LoginPage
        self.click(self.CHECKOUT)
        return LoginPage(self.driver)
