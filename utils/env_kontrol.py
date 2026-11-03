""".env dosyasındaki test hesabı bilgilerinin doğru yazılıp yazılmadığını kontrol eder.

Şifreyi ve e-postayı ekrana YAZDIRMAZ; yalnızca dolu/boş durumu, uzunluğu ve yaygın yazım hatalarını gösterir.
Kullanım (proje klasöründe):  .venv/bin/python -m utils.env_kontrol
"""
import re
import sys
from pathlib import Path

ALANLAR = ("HB_EMAIL", "HB_PASSWORD")


def kontrol_et(yol: Path) -> bool:
    if not yol.exists():
        print(f"HATA: {yol.name} dosyası yok. Oluşturmak için:  cp .env.example .env")
        return False
    degerler = {}
    for satir in yol.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\s*(HB_EMAIL|HB_PASSWORD)\s*=(.*)$", satir)
        if m:
            degerler[m.group(1)] = m.group(2)
    sorunsuz = True
    for alan in ALANLAR:
        if alan not in degerler:
            print(f"✗ {alan}: satır bulunamadı ('{alan}=' satırı silinmiş olabilir)")
            sorunsuz = False
            continue
        ham = degerler[alan]
        deger = ham.strip()
        uyarilar = []
        if not deger:
            print(f"✗ {alan}: BOŞ")
            sorunsuz = False
            continue
        if deger[0] in "\"'" or deger[-1] in "\"'":
            uyarilar.append("başında/sonunda tırnak var, tırnakları silin")
        if ham != ham.lstrip():
            uyarilar.append("'=' işaretinden sonra boşluk var (otomatik temizlenir ama silmeniz önerilir)")
        if alan == "HB_EMAIL" and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", deger):
            uyarilar.append("e-posta biçimi hatalı görünüyor (ör. ad@ornek.com)")
        if alan == "HB_PASSWORD" and deger in ("sifreniz", "şifreniz"):
            uyarilar.append("örnek değer duruyor, kendi şifrenizi yazın")
        if alan == "HB_EMAIL" and deger.endswith("@ornek.com"):
            uyarilar.append("örnek adres duruyor, kendi e-postanızı yazın")
        durum = "✗" if uyarilar else "✓"
        print(f"{durum} {alan}: dolu ({len(deger)} karakter)" + "".join(f"\n    - {u}" for u in uyarilar))
        sorunsuz = sorunsuz and not uyarilar
    print("\nSonuç: .env hazır." if sorunsuz else "\nSonuç: .env'de düzeltilmesi gereken satır var.")
    return sorunsuz


if __name__ == "__main__":
    yol = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / ".env"
    sys.exit(0 if kontrol_et(yol) else 1)
