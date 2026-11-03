"""WHITE BOX (iç yapı): Uygulamanın dışarıdan görünmeyen iç bileşenleri doğrulanır.

Kullanıcı arayüzü yerine paket adı, sürüm, Android activity geçişleri ve
eleman kimlikleri (resource-id) gibi iç yapı bilgileri kontrol edilir.
"""
import os
import re
import subprocess

import pytest

from config.capabilities import ANDROID_PACKAGE
from pages import flows

pytestmark = pytest.mark.whitebox

TEST_EDILEN_SURUM = (5, 102, 1)
ADB = os.path.join(os.getenv("ANDROID_HOME", os.path.expanduser("~/Library/Android/sdk")),
                   "platform-tools", "adb")


def paket_bilgisi() -> str:
    return subprocess.run([ADB, "shell", "dumpsys", "package", ANDROID_PACKAGE],
                          capture_output=True, text=True, timeout=30).stdout


def yuklu_surum():
    match = re.search(r"versionName=([\d.]+)", paket_bilgisi())
    assert match, "Uygulama sürümü okunamadı"
    return tuple(int(p) for p in match.group(1).split("."))


@pytest.mark.pozitif
def test_yuklu_uygulama_surumu_test_edilen_surumden_eski_olmamali(app):
    """[OLUMLU] Cihazdaki uygulama sürümü, testlerin yazıldığı 5.102.1 sürümünden eski olmamalı."""
    assert app.driver.current_package == ANDROID_PACKAGE
    assert yuklu_surum() >= TEST_EDILEN_SURUM, f"Eski sürüm: {yuklu_surum()}"


@pytest.mark.negatif
def test_yuklu_uygulama_hata_ayiklama_surumu_olmamali(app):
    """[OLUMSUZ] Mağazadan yüklenen uygulama DEBUGGABLE (hata ayıklanabilir) bayrağı taşımamalı; taşırsa yanlış sürüm test ediliyordur."""
    bayraklar = re.search(r"pkgFlags=\[([^\]]*)\]", paket_bilgisi())
    assert bayraklar, "Paket bayrakları okunamadı"
    assert "DEBUGGABLE" not in bayraklar.group(1), f"Uygulama hata ayıklama sürümü: {bayraklar.group(1)}"


@pytest.mark.pozitif
def test_ana_sayfa_test_kimlikleri_kaldirilmamis_olmali(app, adim):
    """[OLUMLU] Testlerin dayandığı resource-id'ler (SearchBoxView, bottom_navigation_compose) uygulamadan kaldırılmamış olmalı."""
    adim("Ana sayfa iç yapısı")
    source = app.driver.page_source
    for rid in ("SearchBoxView", "searchTextField", "bottom_navigation_compose"):
        assert rid in source, f"'{rid}' kimliği sayfa kaynağında yok"


@pytest.mark.negatif
def test_ana_sayfa_test_kimlikleri_birden_fazla_elemanda_kullanilmamali(app, adim):
    """[OLUMSUZ] Testlerin dayandığı kimlikler ana sayfada tek bir elemana ait olmalı; birden fazla elemanda olursa locator yanlış elemanı bulur."""
    adim("Ana sayfa iç yapısı")
    source = app.driver.page_source
    for rid in ("SearchBoxView", "bottom_navigation_compose"):
        adet = len(re.findall(rf'resource-id="(?:[^"]*:id/)?{rid}"', source))
        assert adet == 1, f"'{rid}' kimliği {adet} elemanda kullanılıyor"


@pytest.mark.standart
@pytest.mark.negatif
def test_misafir_odeme_akisi_auth_activity_disina_cikmamali(bos_sepet, adim):
    """[OLUMSUZ] Misafir kullanıcı 'Ödemeye Geç'e bastığında AuthActivity dışında bir activity (ör. ödeme) açılmamalı."""
    cart, _ = flows.sepete_urun_ekle(bos_sepet)
    assert cart.activity.endswith("SuperAppActivity"), f"Sepet beklenmeyen activity'de: {cart.activity}"
    login = cart.checkout().wait_loaded()
    adim("Ödemeye Geç sonrası activity")
    assert login.activity.endswith("AuthActivity"), f"Beklenmeyen activity: {login.activity}"
    login.go_back()
