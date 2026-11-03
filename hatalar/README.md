# Bulunan hatalar

Testlerin Hepsiburada uygulamasında bulduğu hatalar. Her hatanın kendi klasörü vardır. Klasörde hata raporu (`rapor.md`) ve kanıt ekran görüntüleri bulunur.

| No | Başlık | Önem | Durum | Yeniden üreten test |
|---|---|---|---|---|
| [HB-001](HB-001-premium-fiyati-misafire-satis-fiyati-gibi-gosteriliyor/rapor.md) | Ürün sayfasında Premium fiyatı misafir kullanıcıya satış fiyatı gibi gösteriliyor (578,04 TL görünüyor, sepette 642,27 TL) | Orta | Açık | `tests/hatalar/test_bilinen_hatalar.py::test_hb001_…` |

## Yeni hata nasıl eklenir?
1. **Önce test kodunu doğrulayın.** Hatanın uygulamada olduğundan, testin yanlış okumasından kaynaklanmadığından emin olun: ekran görüntüsüne bakın, aynı adımları elle tekrarlayın.
2. `hatalar/HB-00N-kisa-aciklama/` klasörünü açın.
3. `rapor.md` dosyasını yazın: özet, yeniden üretme adımları, beklenen sonuç, gerçekleşen sonuç, ortam ve ekran görüntüleri. Biçim için HB-001'e bakın.
4. Kanıt ekran görüntülerini klasöre ekleyin. Kaynak: `reports/screenshots/<test>/`.
5. `tests/hatalar/test_bilinen_hatalar.py` içine hatayı yeniden üreten bir test ekleyin:
   - `@pytest.mark.xfail(strict=True, reason="HB-00N: …")` ile işaretleyin.
   - Hatanın oluşmadığı bir veriyle karşılaşırsa `pytest.skip(...)` ile atlasın.
6. Hatayı bulan testi, hatayı içermeyen asıl davranışı doğrulayacak şekilde düzenleyin ve docstring'ine hata numarasını yazın. Böylece çalıştırma o hatada durmaz.
7. Bu tabloya bir satır ekleyin.

## Hata düzeltildiğinde
`tests/hatalar` testi **XPASS** verir ve `strict=True` olduğu için başarısız sayılır. Şunları yapın:
1. Uygulamada düzeltmeyi elle doğrulayın.
2. Testteki `xfail` işaretini kaldırın. Test artık normal bir regresyon testi olarak kalır.
3. Bu tabloda durumu **Kapandı** yapın ve rapora düzeltildiği sürümü yazın.
