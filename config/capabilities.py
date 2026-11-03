"""Appium bağlantı ayarları. Değerler ortam değişkenleriyle değiştirilebilir."""
import os

from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions

APPIUM_URL = os.getenv("APPIUM_URL", "http://127.0.0.1:4723")
PLATFORM = os.getenv("PLATFORM", "android").lower()

ANDROID_PACKAGE = "com.pozitron.hepsiburada"
ANDROID_ACTIVITY = "com.hepsiburada.ui.startup.SplashActivity"
IOS_BUNDLE_ID = os.getenv("IOS_BUNDLE_ID", "com.pozitron.hepsiburada")


def android_options() -> UiAutomator2Options:
    opts = UiAutomator2Options()
    opts.platform_name = "Android"
    opts.device_name = os.getenv("ANDROID_DEVICE", "emulator-5554")
    opts.app_package = ANDROID_PACKAGE
    opts.app_activity = ANDROID_ACTIVITY
    opts.app_wait_activity = "*"
    # Uygulama verisi silinmez; çerez/izin ekranları her testte tekrar çıkmaz.
    opts.no_reset = True
    opts.auto_grant_permissions = True
    opts.new_command_timeout = 300
    opts.set_capability("appium:disableIdLocatorAutocompletion", True)
    # Ana sayfadaki kayan banner'lar ekranı hiç "boşta" bırakmıyor; beklenirse her komut ~10 sn gecikir
    opts.set_capability("appium:settings[waitForIdleTimeout]", 0)
    return opts


def ios_options() -> XCUITestOptions:
    opts = XCUITestOptions()
    opts.platform_name = "iOS"
    opts.device_name = os.getenv("IOS_DEVICE", "iPhone")
    if os.getenv("IOS_UDID"):
        opts.udid = os.getenv("IOS_UDID")
    opts.bundle_id = IOS_BUNDLE_ID
    opts.no_reset = True
    opts.auto_accept_alerts = True
    opts.new_command_timeout = 300
    return opts


def options():
    return ios_options() if PLATFORM == "ios" else android_options()
