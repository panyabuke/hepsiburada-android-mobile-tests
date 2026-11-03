# HB-001 · Ürün sayfasında Premium fiyatı, misafir kullanıcıya satış fiyatı gibi gösteriliyor

| Alan | Değer |
|---|---|
| **Durum** | Açık |
| **Önem** | Orta: kullanıcı ürün sayfasında gördüğü fiyattan daha yükseğini sepette görüyor |
| **Öncelik** | Yüksek: fiyat beyanı, müşteri güveni ve tüketici mevzuatı açısından hassas |
| **Bulan test** | `tests/regression/test_kategoriler.py::test_indirimli_urun_sepette_eski_fiyatindan_gosterilmemeli` |
| **Yeniden üreten test** | `tests/hatalar/test_bilinen_hatalar.py::test_hb001_urun_sayfasindaki_fiyat_misafirin_sepet_fiyatindan_dusuk_gosterilmemeli` (`xfail`) |
| **Bulunma tarihi** | 3 Kasım 2026 |
| **Ortam** | Hepsiburada Android 5.102.1 · Android 17 emülatörü · misafir (giriş yapılmamış) kullanıcı |
| **Ürün** | Grimelange Cultıvated Erkek 3'lü Kalın Dokulu Regular %100 Organik Pamuk T-Shirt · Koyu Vizon - Siyah / L |

## Özet
İndirimli bir üründe, ürün sayfasının alt fiyat çubuğunda büyük harfle **578,04 TL** yazıyor. Bu fiyat aslında **Premium üyelik fiyatı**: Sayfanın üstündeki pembe bantta "Premium'a geç, **578,04 TL**'ye al" yazıyor. Misafir kullanıcı ürünü sepete eklediğinde fiyat **642,27 TL** oluyor. Misafirin ödeyeceği 642,27 TL ürün sayfasında hiçbir yerde yazmıyor.

## Yeniden üretme adımları
1. Uygulamayı giriş yapmadan (misafir) açın.
2. "erkek tişört" aratın ve ilk ürünü (Grimelange 3'lü tişört) açın.
3. Renk **Koyu Vizon - Siyah**, beden **L** seçili olsun (varsayılan).
4. Alt fiyat çubuğundaki fiyata bakın: ~~755,61 TL~~ **%24**, "30 günün en düşük fiyatı" **578,04 TL**.
5. Sayfanın üstündeki pembe banda bakın: "Premium'a geç, 578,04 TL'ye al".
6. **Sepete ekle → Sepete git**.
7. Sepetteki ürün fiyatına bakın.

## Beklenen sonuç
Misafir kullanıcıya ürün sayfasında büyük ve vurgulu olarak gösterilen fiyat, sepette ödeyeceği fiyat olmalı (642,27 TL). Premium fiyatı gösterilecekse, kulaklık gibi diğer ürünlerde olduğu gibi **"Premium ile"** etiketiyle ayrıca belirtilmeli.

## Gerçekleşen sonuç
| Ekran | Fiyat |
|---|---|
| Ürün sayfası, alt çubuk (büyük, kırmızı) | **578,04 TL** (%24, "30 günün en düşük fiyatı") |
| Ürün sayfası, pembe Premium bandı | 578,04 TL |
| Ürün sayfası, taksit bilgisi | 3 × 192 TL (≈ 578 TL üzerinden) |
| **Sepet** | **642,27 TL** (755,61 − 113,34 kazanç) |

Fark: **64,23 TL**. Alt çubukta, kulaklıktaki gibi fiyatın Premium'a özel olduğunu belirten bir "Premium ile" etiketi **yok**.

## Ek gözlem (tutarsızlık)
Sepetteki pembe bantta "Anında **75,56 TL** indirim seni bekliyor! … Premium'a geç" yazıyor. 642,27 − 75,56 = **566,71 TL** ediyor, ama ürün sayfasındaki Premium fiyatı **578,04 TL**. Ürün sayfası ve sepet farklı bir Premium indirimi gösteriyor.

## Ekran görüntüleri
| | |
|---|---|
| [01_urun_sayfasi_ust.png](01_urun_sayfasi_ust.png) | Pembe bant "Premium'a geç, 578,04 TL'ye al" ve alt çubukta 578,04 TL |
| [02_urun_sayfasi_secenek_ve_fiyat.png](02_urun_sayfasi_secenek_ve_fiyat.png) | Seçili renk/beden (Koyu Vizon - Siyah / L) ve 578,04 TL; "Premium ile" etiketi yok |
| [03_sepet.png](03_sepet.png) | Sepette aynı ürün 642,27 TL; "Anında 75,56 TL indirim" bandı |

## Karşılaştırma: doğru etiketlenen ürün
Xiaomi Redmi Buds 6 Play kulaklıkta Premium fiyatı alt çubukta **"Premium ile 655,53 TL"** olarak etiketleniyor. Kullanıcı bunun kendi fiyatı olmadığını anlayabiliyor. HB-001'deki tişörtte bu etiket yerine "30 günün en düşük fiyatı" yazıyor.

## Test projesindeki etkisi
- Testlerde fiyat kontrolleri **sepette görünen fiyat** üzerinden yapılır. Ürün sayfasındaki fiyat yalnızca "eski fiyattan düşük mü" kontrolünde kullanılır.
- İndirimli ürün testi artık şunu doğrular: Sepet fiyatı + sepetteki "kazancınız var" tutarı = eski fiyat.
- Hata, `tests/hatalar/` altındaki `xfail(strict=True)` testiyle her çalıştırmada yeniden kontrol edilir:
  - Hata sürdükçe sonuç **XFAIL** olur ve çalıştırmayı durdurmaz.
  - Hata düzeltilirse test **XPASS** olur ve başarısız sayılır. Bu, kaydın kapatılması gerektiğini haber verir.
  - Seçilen indirimli üründe Premium bandı yoksa test **SKIPPED** olur, çünkü hata o ürünle yeniden üretilemez.
