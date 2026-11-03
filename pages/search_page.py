from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage, by_id

SEARCH_INPUT = (AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().className("android.widget.EditText").resourceIdMatches("(.*:id/)?searchTextField")')


class SearchPage(BasePage):
    SEARCH_INPUT = SEARCH_INPUT
    TRENDING_TITLE = by_id("trendingTermTitle")
    # Uyarı ~2 sn görünen bir Toast; UiAutomator2 Toast'ları android.widget.Toast olarak yakalar
    MIN_CHAR_WARNING = (AppiumBy.XPATH, '//android.widget.Toast[contains(@text,"en az iki karakter")]')

    def search(self, keyword: str):
        from pages.search_results_page import SearchResultsPage
        field = self.find(self.SEARCH_INPUT)
        field.click()
        if keyword:
            field.send_keys(keyword)
        self.press_enter()
        return SearchResultsPage(self.driver)

    def is_open(self, timeout=10) -> bool:
        return self.is_visible(self.SEARCH_INPUT, timeout)

    def shows_min_char_warning(self, timeout=4) -> bool:
        """Toast kaybolmadan yakalamak için search() sonrasında hemen çağrılmalı."""
        try:
            WebDriverWait(self.driver, timeout, poll_frequency=0.2).until(
                EC.presence_of_element_located(self.MIN_CHAR_WARNING))
            return True
        except TimeoutException:
            return False
