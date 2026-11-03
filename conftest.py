"""Ortak pytest ayarları: Appium oturumu, uygulamayı temiz başlatma, adım adım ekran görüntüsü."""
import base64
import os
import re
from pathlib import Path

import pytest
from appium import webdriver
from selenium.common.exceptions import TimeoutException

ROOT = Path(__file__).parent

# .env dosyasındaki değerleri (HB_EMAIL vb.) ortam değişkeni olarak yükle
if (ROOT / ".env").exists():
    for line in (ROOT / ".env").read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, _, value = line.partition("=")
            if value.strip():
                os.environ.setdefault(key.strip(), value.strip())

from config import capabilities  # noqa: E402  (.env okunduktan sonra yüklenmeli)
from pages.home_page import HomePage  # noqa: E402

SCREENSHOT_DIR = ROOT / "reports" / "screenshots"
# Testler her zaman bu sırayla çalışır: temel kontrol geçmeden ayrıntılı testlere başlanmaz
# "hatalar": bilinen hataları yeniden üreten testler (xfail), en sonda çalışır
KLASOR_SIRASI = ["smoke", "regression", "blackbox", "whitebox", "integration", "e2e", "hatalar"]


def test_tipi(item) -> str:
    """Testin olumlu/olumsuz etiketi: @pytest.mark.pozitif -> OLUMLU, @pytest.mark.negatif -> OLUMSUZ."""
    if item.get_closest_marker("pozitif"):
        return "OLUMLU"
    if item.get_closest_marker("negatif"):
        return "OLUMSUZ"
    return ""


def pytest_collection_modifyitems(config, items):
    # Her test olumlu ya da olumsuz olarak etiketlenmiş olmalı; etiketsiz test çalıştırılmaz
    etiketsiz = [item.nodeid for item in items if not test_tipi(item)]
    if etiketsiz:
        raise pytest.UsageError("Olumlu/olumsuz etiketi olmayan testler (@pytest.mark.pozitif veya "
                                "@pytest.mark.negatif ekleyin):\n  " + "\n  ".join(etiketsiz))

    # Gerçek hesapla giriş yapan testler yalnızca açıkça istendiğinde çalışır:  pytest -m hesap
    # (.env dolu olsa bile normal çalıştırmalar hesaba giriş yapmaz)
    secim = config.getoption("markexpr") or ""
    if "hesap" not in secim:
        atla = pytest.mark.skip(reason="Gerçek hesap testi; yalnızca 'pytest -m hesap' ile çalışır")
        for item in items:
            if item.get_closest_marker("hesap"):
                item.add_marker(atla)

    def klasor_sirasi(item):
        klasor = Path(item.fspath).parent.name
        return KLASOR_SIRASI.index(klasor) if klasor in KLASOR_SIRASI else len(KLASOR_SIRASI)
    # sort kararlıdır: aynı klasördeki testler dosyadaki sıralarını korur
    items.sort(key=klasor_sirasi)


def dosya_adi(metin: str) -> str:
    return re.sub(r"[^\w-]+", "_", metin).strip("_")[:80]


@pytest.fixture(scope="session")
def driver():
    if capabilities.PLATFORM == "ios":
        pytest.skip("iOS locator'ları henüz tanımlanmadı (bkz. README > iOS)")
    drv = webdriver.Remote(capabilities.APPIUM_URL, options=capabilities.options())
    yield drv
    drv.quit()


def uygulamayi_yeniden_baslat(driver) -> HomePage:
    return HomePage(driver).restart()


@pytest.fixture
def app(driver):
    """Her testi uygulamanın ana sayfasından, temiz bir açılışla başlatır."""
    return uygulamayi_yeniden_baslat(driver)


def sepeti_bosalt(home: HomePage, deneme=2) -> HomePage:
    """Sepeti boşaltıp ana sayfaya döner.

    Uygulama yeniden açıldıktan hemen sonra sepet ya da ana sayfa ara sıra zamanında yüklenmiyor;
    bu durumda uygulama yeniden başlatılıp bir kez daha denenir.
    """
    for kalan in range(deneme - 1, -1, -1):
        try:
            home.open_cart().clear()
            return home.open_home()
        except TimeoutException:
            if not kalan:
                raise
            home = uygulamayi_yeniden_baslat(home.driver)


@pytest.fixture
def bos_sepet(app):
    """Testten önce ve sonra sepeti boşaltır; testler birbirini etkilemez."""
    home = sepeti_bosalt(app)
    yield home
    # Test sepet/giriş ekranında bitebilir (alt menü yok); temiz açılışla ana sayfaya dönülür
    sepeti_bosalt(uygulamayi_yeniden_baslat(app.driver))


@pytest.fixture
def adim(request, driver):
    """Testteki her adımın ekran görüntüsünü alır ve HTML rapora ekler.

    Kullanım: adim("Arama sonuçları açıldı")
    """
    shots = []
    request.node._adim_goruntuleri = shots
    folder = SCREENSHOT_DIR / dosya_adi(request.node.name)
    folder.mkdir(parents=True, exist_ok=True)

    def _adim(aciklama: str):
        png = driver.get_screenshot_as_png()
        no = len(shots) + 1
        (folder / f"{no:02d}_{dosya_adi(aciklama)}.png").write_bytes(png)
        shots.append((f"Adım {no}: {aciklama}", base64.b64encode(png).decode()))

    return _adim


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    report.test_tipi = test_tipi(item)
    if report.when != "call":
        return
    pytest_html = item.config.pluginmanager.getplugin("html")
    if pytest_html is None:
        return
    extras = getattr(report, "extras", [])
    shots = list(getattr(item, "_adim_goruntuleri", []))
    drv = item.funcargs.get("driver")
    if report.failed and drv is not None:
        try:
            shots.append(("Hata anı", drv.get_screenshot_as_base64()))
        except Exception:
            pass
    for name, b64 in shots:
        extras.append(pytest_html.extras.image(b64, name))
    doc = (item.function.__doc__ or "").strip()
    if doc:
        extras.insert(0, pytest_html.extras.text(doc, "Senaryo"))
    report.extras = extras


def pytest_html_report_title(report):
    report.title = "Hepsiburada Android Test Raporu"


def pytest_html_results_table_header(cells):
    cells.insert(1, '<th class="sortable" data-column-type="tip">Tip</th>')


def pytest_html_results_table_row(report, cells):
    tip = getattr(report, "test_tipi", "")
    renk = "#1a7f37" if tip == "OLUMLU" else "#cf222e"
    cells.insert(1, f'<td class="col-tip" style="color:{renk};font-weight:bold">{tip}</td>')
