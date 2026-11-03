"""Uygulamadaki fiyat metinlerini sayıya çeviren yardımcı (white box testlerin hedefi)."""
import re

_PRICE_RE = re.compile(r"^\s*(\d{1,3}(?:\.\d{3})*|\d+)(?:,(\d{1,2}))?\s*TL\s*$")


def parse_price(text: str) -> float:
    """'1.159 TL' -> 1159.0, '755,53 TL' -> 755.53.

    Geçersiz biçimde ValueError fırlatır.
    """
    if not isinstance(text, str):
        raise ValueError("Fiyat metni str olmalı")
    match = _PRICE_RE.match(text.replace("\xa0", " "))
    if not match:
        raise ValueError(f"Geçersiz fiyat metni: {text!r}")
    whole, fraction = match.groups()
    value = float(whole.replace(".", ""))
    if fraction:
        value += int(fraction.ljust(2, "0")) / 100
    return round(value, 2)
