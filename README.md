# Hepsiburada Mobil Test Otomasyonu

Hepsiburada Android uygulamasının temel fonksiyonları için **Appium + Python (pytest)** ile yazılmış mobil test otomasyonu projesi.

**GitHub:** https://github.com/panyabuke/hepsiburada-android-mobile-tests

> **Gerçek hesapla giriş testleri** için gereken e-posta ve şifre bu depoda yoktur. Testleri çalıştırmak isteyenler bilgileri proje sahibinden **özel olarak** istemeli ve kendi `.env` dosyalarına yazmalıdır: [Projeyi başkası çalıştıracaksa](#projeyi-başkası-çalıştıracaksa-hesap-testleri).

Her test tipi ayrı bir klasörde yer alıyor. Her senaryonun **pozitif ve negatif** versiyonu var, test adları da **olumsuz cümle** kalıbıyla yazıldı. Her adım ekran görüntüsüyle kaydediliyor ve HTML raporda gösteriliyor.

Testler **ürün kategorilerine** göre planlandı: standart, renk seçimli, beden seçimli, çoklu seçimli, indirimli ve stokta olmayan ürün. Her kategori için uygulamadan uygun bir ürün otomatik bulunur (bkz. [Ürün kategorileri](#ürün-kategorileri)).

Testlerin uygulamada bulduğu hatalar **`hatalar/`** klasöründe raporlanır (bkz. [Bulunan hatalar](#bulunan-hatalar)).

Testler her zaman **aynı sırayla** çalışır (smoke → regresyon → black box → white box → entegrasyon → uçtan uca → bilinen hatalar) ve **bir test başarısız olduğunda çalıştırma durur**; hata düzeltilmeden sonraki teste geçilmez.

---

## İçindekiler
1. [Gereksinimler](#1-gereksinimler)
2. [Kapsam ve test edilen uygulama](#2-kapsam-ve-test-edilen-uygulama)
3. [Klasör yapısı](#3-klasör-yapısı)
4. [Test tipleri](#4-test-tipleri)
5. [Test senaryoları (pozitif / negatif)](#5-test-senaryoları-pozitif--negatif)
6. [Kurulum (adım adım)](#6-kurulum-adım-adım)
7. [Testleri çalıştırma](#7-testleri-çalıştırma)
8. [Raporlar ve ekran görüntüleri](#8-raporlar-ve-ekran-görüntüleri)
9. [Testleri yazarken dikkat edilmesi gerekenler](#9-testleri-yazarken-dikkat-edilmesi-gerekenler)
10. [Karşılaşılan sorunlar ve çözümleri](#10-karşılaşılan-sorunlar-ve-çözümleri)
11. [Sınırlamalar](#11-sınırlamalar)
12. [iOS desteği](#12-ios-desteği)
13. [Son çalıştırma sonuçları](#13-son-çalıştırma-sonuçları)
14. [GitHub'a yükleme](#14-githuba-yükleme)

---

## 1. Gereksinimler

| # | Gereksinim | Nerede karşılanıyor |
|---|---|---|
| 1 | Mobil test otomasyonu (Sahibinden / Hepsiburada) | Hepsiburada Android uygulaması (Sahibinden otomasyonu engelliyor, bkz. [Bölüm 10](#10-karşılaşılan-sorunlar-ve-çözümleri)) |
| 2 | Uygulamanın temel fonksiyonları için **regresyon seti**: Giriş, Arama barı, Sepete ekleme, Checkout | `tests/regression/` |
| 3 | **Smoke test** | `tests/smoke/` |
| 4 | **Black box test** | `tests/blackbox/` |
| 5 | **White box test** | `tests/whitebox/` |
| 6 | **Entegrasyon testi** | `tests/integration/` |
| 7 | Kullanıcının en basit haliyle tüm alışveriş adımlarının testi, görsel olarak izlenebilir şekilde | `tests/e2e/` + HTML rapordaki adım ekran görüntüleri |
| 8 | Her testin **olumsuz (negatif) versiyonu** | Her dosyada `@pytest.mark.negatif` testler |
| 9 | Test adlarının **olumsuz cümle** kalıbında yazılması | Tüm test adları "…olmamalı / …açılmamalı / …geçememeli" biçiminde |
| 10 | Her test tipi **ayrı klasörde** | [Bölüm 3](#3-klasör-yapısı) |
| 11 | Projenin **adım adım** anlatılması ve GitHub linki ile teslimi | Bu README |
| 12 | Testlerin **ürün kategorilerine** göre planlanması: beden seçimli, renk seçimli, indirimli, standart, stokta olmayan, çoklu seçimli | [Ürün kategorileri](#ürün-kategorileri), tüm klasörlerde kategori testleri |
| 13 | Bir test başarısız olduğunda düzeltilene kadar **diğer testlere geçilmemesi** | `pytest.ini` içinde `-x`, sıra: `conftest.py > KLASOR_SIRASI` |
| 14 | Fiyat kontrollerinin **sepette görünen fiyat** üzerinden yapılması; bulunan hatanın **ayrı bir hata klasörüne** eklenmesi | `hatalar/HB-001-…/rapor.md` + `tests/hatalar/` |

---

## 2. Kapsam ve test edilen uygulama

| Bilgi | Değer |
|---|---|
| Uygulama | Hepsiburada (`com.pozitron.hepsiburada`) |
| Test edilen sürüm | 5.102.1 |
| Platform | Android 17 (API 37) emülatörü, arm64, Google Play imajı |
| Araçlar | Appium 3.9.0, UiAutomator2 sürücüsü 8.7.3, Python 3.9, pytest 8.4, pytest-html 4.2 |
| Kullanıcı tipi | Misafir (giriş yapılmamış) kullanıcı |

**Gerçek sipariş verilmez.** Checkout ve uçtan uca testleri, kullanıcıdan kimlik veya ödeme bilgisi istenen adımda durur. Her sepet testi, başlamadan önce ve bittikten sonra sepeti boşaltır.

---

## 3. Klasör yapısı

```
hepsiburada-android-mobile-tests/
├── config/
│   ├── capabilities.py        # Appium bağlantı ayarları (Android + iOS)
│   └── urun_kategorileri.py   # Ürün kategorileri ve her kategori için arama kelimeleri
├── pages/                     # Page Object Model: her ekran için bir sınıf
│   ├── base_page.py           # Ortak bekleme, eleman bulma, açılır pencere kapatma
│   ├── home_page.py           # Ana sayfa + alt menü
│   ├── search_page.py         # Arama ekranı
│   ├── search_results_page.py # Arama sonuçları
│   ├── product_page.py        # Ürün detay
│   ├── cart_page.py           # Sepet
│   ├── account_page.py        # Hesabım
│   ├── login_page.py          # Giriş / misafir devam
│   └── flows.py               # Tekrar eden akışlar (ara, kategoride ürün bul, sepete ekle)
├── utils/
│   ├── price.py               # Fiyat metnini sayıya çeviren yardımcı (white box hedefi)
│   └── urun_profili.py        # Ürün sayfasından renk/beden/fiyat/stok bilgisini çıkarıp kategori belirler (white box hedefi)
├── tests/
│   ├── smoke/                 # 1) Smoke testler
│   ├── regression/            # 2) Regresyon seti: giriş, arama, sepet, checkout
│   ├── blackbox/              # 3) Black box: sınır değer + denklik sınıfları
│   ├── whitebox/              # 4) White box: kod yolları + uygulama iç yapısı
│   ├── integration/           # 5) Entegrasyon: arama → ürün → sepet veri tutarlılığı
│   ├── e2e/                   # 6) Uçtan uca alışveriş yolculuğu (görsel)
│   └── hatalar/               # 7) Bulunan hataları yeniden üreten testler (xfail)
├── hatalar/                   # Bulunan hataların raporları ve kanıt ekran görüntüleri
│   ├── README.md              # Hata listesi + yeni hata ekleme adımları
│   └── HB-001-…/              # rapor.md + ekran görüntüleri
├── reports/                   # Test çıktıları (git'e eklenmez)
│   ├── rapor.html             # Ekran görüntülü HTML rapor
│   └── screenshots/           # Her testin adım adım PNG'leri
├── conftest.py                # Ortak fixture'lar ve rapor kancaları
├── pytest.ini                 # pytest ayarları ve marker tanımları
├── requirements.txt
├── .env.example               # Test hesabı bilgileri için şablon
└── README.md
```

---

## 4. Test tipleri

| Tip | Klasör | Ne yapar | Bu projede nasıl uygulandı |
|---|---|---|---|
| **Smoke** | `tests/smoke` | Uygulama ayağa kalkıyor mu, en temel ekran çalışıyor mu? Diğer testlerden önce çalıştırılır. Başarısız olursa diğer testleri koşmanın anlamı yoktur. | Ana sayfa, arama kutusu ve alt menü yükleniyor mu; bot engeli veya "Yüklenemedi" hatası çıkıyor mu? |
| **Regresyon** | `tests/regression` | Her yeni sürümde temel fonksiyonların bozulmadığını doğrulayan sabit test seti. | Notta belirtilen 4 fonksiyon: **giriş, arama barı, sepete ekleme, checkout** |
| **Black box** | `tests/blackbox` | Uygulamanın iç yapısı bilinmeden, sadece girdi ve beklenen çıktı ile test. | **Sınır değer analizi** (arama en az 2 karakter istiyor: 0, 1 ve 2 karakter denenir), **denklik sınıfları** (büyük harf, Türkçe karakter, özel karakter, 150 karakter; 4 farklı geçersiz e-posta sınıfı) |
| **White box** | `tests/whitebox` | Kodun iç yapısı bilinerek, her kod yolunun (dalın) çalıştırıldığı test. | (a) `utils/price.py` içindeki tüm 7 kod yolu ayrı ayrı test edilir. (b) Uygulamanın iç yapısı: paket adı, sürüm, Android activity geçişleri (`SuperAppActivity` → `AuthActivity`), testlerin dayandığı `resource-id`'ler. |
| **Entegrasyon** | `tests/integration` | Birden fazla modülün birlikte doğru çalışıp veri aktardığını test eder. | Arama → Ürün → Sepet: seçilen ürün sepete doğru ürün olarak mı gidiyor, fiyat değişiyor mu, "Alışverişe devam et" sepeti bozuyor mu? |
| **Uçtan uca (E2E)** | `tests/e2e` | Gerçek bir kullanıcının baştan sona yolculuğu. | Ana sayfa → Arama → Sonuçlar → Ürün → Sepete ekle → Sepet → Ödemeye Geç. Her adım ekran görüntüsüyle rapora eklenir. |

### Pozitif / negatif ve olumsuz cümle kuralı
- **Pozitif test** (`@pytest.mark.pozitif`): Beklenen kullanıcı davranışı ("mutlu yol").
- **Negatif test** (`@pytest.mark.negatif`): Hatalı girdi veya yanlış kullanım; sistem bunu **engellemeli**.
- **Olumsuz cümle kalıbı:** Tüm test adları, sistemin **ne yapmaması gerektiğini** söyleyecek şekilde yazıldı. Böylece test başarısız olduğunda adı doğrudan hatayı anlatır.
  - Pozitif örnek: `test_gecerli_kelimeyle_aramada_sonuc_listesi_bos_olmamali`
  - Negatif örnek: `test_anlamsiz_kelimeyle_aramada_hicbir_urun_listelenmemeli`
- **Her olumlu testin bir olumsuz karşılığı vardır.** Her test dosyasında olumsuz test sayısı en az olumlu test sayısı kadardır.

### [OLUMLU] / [OLUMSUZ] etiketleri
Test okunurken tipi hemen anlaşılsın diye üç yerde etiket bulunur:

| Nerede | Nasıl görünür |
|---|---|
| Kod (test açıklaması) | `"""[OLUMLU] Geçerli kelimeyle aramada sonuç listesi boş olmamalı..."""` |
| HTML rapor | **Tip** sütunu: yeşil **OLUMLU** / kırmızı **OLUMSUZ**; "Senaryo" metni de etiketle başlar. Sütuna tıklayıp sıralanabilir. |
| pytest marker | `@pytest.mark.pozitif` → OLUMLU, `@pytest.mark.negatif` → OLUMSUZ |

```python
@pytest.mark.negatif
def test_anlamsiz_kelimeyle_aramada_hicbir_urun_listelenmemeli(app, adim):
    """[OLUMSUZ] Anlamsız bir kelime arandığında hiçbir ürün listelenmemeli ..."""
```

**Kural otomatik korunur:** `@pytest.mark.pozitif` veya `@pytest.mark.negatif` etiketi olmayan bir test eklenirse pytest hiçbir testi çalıştırmaz ve etiketsiz testleri listeler (`conftest.py > pytest_collection_modifyitems`).

Yalnızca olumlu ya da olumsuz testleri çalıştırmak için:
```bash
pytest -m pozitif
```
```bash
pytest -m negatif
```

### Ürün kategorileri
Testler tek bir sabit ürüne bağlı değildir. Ürünler davranışlarına göre 6 kategoriye ayrıldı:

| Kategori (marker) | Tanım | Uygulamada nasıl tanınır | Örnek aramalar |
|---|---|---|---|
| `standart` | Renk/beden seçimi olmayan, indirimsiz ürün | Seçenek grubu yok, alt çubukta tek fiyat | roman kitap, a4 fotokopi kağıdı |
| `renk_secimli` | Yalnızca renk seçimi olan ürün | Tek seçim grubu: "Renk: …" | kulaklık, telefon kılıfı |
| `beden_secimli` | Yalnızca beden/numara seçimi olan ürün | Tek seçim grubu: "Beden: …" / "Ayakkabı Numarası: …" | erkek spor ayakkabı |
| `coklu_secimli` | Renk ve beden gibi birden fazla seçimi olan ürün | En az iki seçim grubu | kadın kazak, erkek mont |
| `indirimli` | Eski fiyatı üstü çizili ürün | Alt çubukta eski fiyat + "%24" etiketi + satış fiyatı ("Premium ile" indirimi sayılmaz) | erkek tişört, kadın elbise |
| `stokta_olmayan` | En az bir seçeneği stokta olmayan ürün | Seçeneğin altında "Stokta yok" yazısı | erkek tişört, kadın kazak |

**Ürün nasıl seçiliyor?** `pages/flows.py > kategoride_urun_ac()`, kategorinin arama kelimelerini sırayla arar ve ilk 3 sonucu açar. Ürün sayfasının ekran kaynağı `utils/urun_profili.py` ile okunur: seçenek grupları, seçili değerler, stok durumu, eski/satış fiyatı ve indirim yüzdesi çıkarılır. Kategori koşulunu sağlayan ilk ürün kullanılır. Bulunan ürün (arama kelimesi + sıra) aynı çalıştırma boyunca hatırlanır; sonraki testler yeniden aramaz. Ürün yayından kalkar ya da kategorisi değişirse test kendiliğinden başka bir ürüne geçer.

Bir ürün birden fazla kategoriye uyabilir (ör. hem çoklu seçimli hem indirimli). Kategori koşulu sağlandığı sürece bu sorun değildir.

**Hangi klasörde hangi kategori testi var?**

| Klasör | standart | renk | beden | çoklu | indirimli | stokta olmayan |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| smoke | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| regression | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| blackbox | | ✔ | ✔ | | | |
| whitebox (cihazsız) | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| integration | ✔ | ✔ | ✔ | ✔ | ✔ | |
| e2e | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ (negatif) |

Kategori kullanmadan sepete ürün ekleyen eski testler (`test_sepet.py`, `test_checkout.py`, `test_arama_urun_sepet.py`) **standart** kategorideki ürünü kullanır.

---

## 5. Test senaryoları (pozitif / negatif)

### 5.1 Smoke — `tests/smoke/`
**Uygulama** (`test_smoke.py`)
| Tip | Test | Beklenen |
|---|---|---|
| Pozitif | `test_uygulama_acildiginda_ana_sayfa_eksik_yuklenmemeli` | Arama kutusu, alt menü ve Ana Sayfam / Sepetim / Hesabım sekmeleri eksik olmamalı |
| Negatif | `test_uygulama_acildiginda_erisim_engeli_veya_hata_ekrani_gorunmemeli` | "Olağan dışı erişim" ya da "Yüklenemedi" ekranı görünmemeli |

**Kategoriler** (`test_smoke_kategoriler.py`, 6 kategori × 2)
| Tip | Test | Beklenen |
|---|---|---|
| Pozitif | `test_kategoriye_uyan_urun_arama_sonuclarinda_eksik_olmamali[<kategori>]` | Her kategori için arama sonuçlarında koşulu sağlayan bir ürün bulunmalı |
| Negatif | `test_kategori_urun_sayfasi_fiyatsiz_veya_sepete_ekle_butonsuz_acilmamali[<kategori>]` | Ürün sayfasında fiyat ve (stoktaki varsayılan seçenekte) "Sepete ekle" olmalı |

### 5.2 Regresyon — `tests/regression/`
**Giriş** (`test_giris.py`)
| Tip | Test | Beklenen |
|---|---|---|
| Pozitif | `test_giris_ekrani_eposta_sifre_ve_giris_butonu_olmadan_acilmamali` | E-posta, şifre alanları ve Giriş yap butonu eksik olmamalı |
| Negatif | `test_bos_bilgilerle_giris_yapilamamali` | Boş formla giriş ekranından çıkılmamalı |
| Negatif | `test_gecersiz_eposta_formatiyla_giris_yapilamamali` | Geçersiz e-posta ile giriş ekranından çıkılmamalı |
| Pozitif · **hesap** | `test_gecerli_bilgilerle_giris_yapan_kullanici_giris_ekraninda_kalmamali` | Doğru bilgilerle giriş → Hesabım'da giriş yapılmış → Çıkış yap → Hesabım'da "Misafir kullanıcı" |
| Negatif · **hesap** | `test_dogru_eposta_yanlis_sifreyle_giris_yapilamamali` | Doğru e-posta + yanlış şifre: "E-posta adresi veya şifre hatalı." mesajı gösterilmeli, giriş ekranında kalınmalı, hesaba girilmemeli |

> **hesap** etiketli iki test gerçek bir test hesabı kullanır. Normal `pytest` çalıştırmasında **atlanır**; hesap sahibi tarafından `pytest -m hesap` ile ayrıca başlatılır. Nasıl yapılacağı: [6.6 Test hesabı](#66-isteğe-bağlı-test-hesabı).

**Arama barı** (`test_arama.py`)
| Tip | Test | Beklenen |
|---|---|---|
| Pozitif | `test_gecerli_kelimeyle_aramada_sonuc_listesi_bos_olmamali` | "kulaklık" için sonuç sayısı > 0, başlıkta aranan kelime var |
| Negatif | `test_anlamsiz_kelimeyle_aramada_hicbir_urun_listelenmemeli` | "xqzvbnmklpwr" için sonuç (0) ve "Aramana uygun ürün bulunamadı" mesajı |

**Sepete ekleme** (`test_sepet.py`)
| Tip | Test | Beklenen |
|---|---|---|
| Pozitif | `test_sepete_eklenen_urun_sepette_eksik_olmamali` | Sepette 1 ürün olmalı |
| Negatif | `test_sepet_silindiginde_sepette_urun_kalmamali` | Silme sonrası "Sepetin şu an boş" görünmeli, ürün kalmamalı |
| Negatif | `test_bos_sepette_odemeye_gec_butonu_gorunmemeli` | Boş sepette "Ödemeye Geç" butonu olmamalı |

**Checkout** (`test_checkout.py`)
| Tip | Test | Beklenen |
|---|---|---|
| Pozitif | `test_sepette_urun_varken_odemeye_gec_kullaniciyi_sepette_birakmamali` | Ödemeye Geç → giriş / "Üye olmadan devam et" adımı açılmalı |
| Negatif | `test_giris_yapmamis_kullanici_odeme_sayfasina_dogrudan_ulasamamali` | Misafir kullanıcı doğrudan ödeme sayfasına geçmemeli; geri dönünce sepet kaybolmamalı |

**Ürün kategorileri** (`test_kategoriler.py`)
| Kategori | Tip | Test | Beklenen |
|---|---|---|---|
| standart | Pozitif | `test_standart_urun_secim_yapilmadan_sepete_eklenirken_engellenmemeli` | Hiç seçim yapmadan sepete eklenebilmeli |
| standart | Negatif | `test_standart_urun_sayfasinda_renk_veya_beden_secimi_istenmemeli` | Seçim grubu ve "kombinasyon yok" uyarısı olmamalı |
| renk | Pozitif | `test_secilen_renk_sepette_farkli_gorunmemeli` | Başka renk seçilip eklenince sepette o renk yazmalı (ör. "Krem/S") |
| renk | Negatif | `test_renk_degistirildiginde_onceki_renk_secili_kalmamali` | Aynı anda iki renk seçili olmamalı |
| beden | Pozitif | `test_secilen_beden_sepette_farkli_gorunmemeli` | Başka beden seçilip eklenince sepette o beden yazmalı |
| beden | Negatif | `test_beden_degistirildiginde_onceki_beden_secili_kalmamali` | Aynı anda iki beden seçili olmamalı |
| çoklu | Pozitif | `test_secilen_renk_ve_beden_sepete_eksik_aktarilmamali` | Renk ve beden birlikte değiştirilince sepette ikisi de görünmeli |
| çoklu | Negatif | `test_coklu_secimde_beden_degisince_renk_secimi_kaybolmamali` | Sadece beden değişince seçili renk değişmemeli |
| indirimli | Pozitif | `test_indirimli_urunun_satis_fiyati_eski_fiyattan_yuksek_olmamali` | Satış fiyatı < eski fiyat; gösterilen % ile hesaplanan % en fazla 1 puan farklı |
| indirimli | Negatif | `test_indirimli_urun_sepette_eski_fiyatindan_gosterilmemeli` | Sepet fiyatı < eski fiyat; sepet fiyatı + sepetteki "kazancınız var" tutarı = eski fiyat (esas fiyat sepet fiyatıdır, bkz. HB-001) |
| stokta olmayan | Pozitif | `test_stokta_olan_secenege_donulunce_sepete_ekle_butonu_gizli_kalmamali` | Stokta olmayandan stoktaki seçeneğe dönülünce "Sepete ekle" geri gelmeli |
| stokta olmayan | Negatif | `test_stokta_olmayan_secenek_secildiginde_urun_sepete_eklenememeli` | "Sepete ekle" kaybolmalı, "… kombinasyonunda ürün bulunmamaktadır" uyarısı çıkmalı |

### 5.3 Black box — `tests/blackbox/`
**Arama girdileri** (`test_arama_girdileri.py`)
| Tip | Test | Girdi | Teknik |
|---|---|---|---|
| Negatif | `test_iki_karakterden_kisa_aramada_sonuc_sayfasi_acilmamali` | `""`, `"a"` | Sınır değer (0 ve 1 karakter) |
| Pozitif | `test_tam_iki_karakterli_aramada_sonuc_sayfasi_engellenmemeli` | `"tv"` | Sınır değer (tam 2 karakter) |
| Pozitif | `test_buyuk_harf_veya_turkce_karakterli_aramada_sonuc_bos_olmamali` | `"KULAKLIK"`, `"ütü"` | Denklik sınıfı |
| Negatif | `test_ozel_karakterli_veya_cok_uzun_aramada_uygulama_cokmemeli` | `"%&*!?<>"`, 150 × `"a"` | Uç değer / dayanıklılık |

**Giriş girdileri** (`test_giris_girdileri.py`)
| Tip | Test | Girdi |
|---|---|---|
| Negatif | `test_gecersiz_bicimli_eposta_ile_giris_ekranindan_cikilmamali` | `kullaniciornek.com`, `kullanici@`, `@ornek.com`, `kul lanici@ornek.com` |
| Pozitif | `test_giris_ekrani_misafir_kullaniciya_kapali_olmamali` | Misafir kullanıcı giriş ekranına ulaşabilmeli |

**Seçenek girdileri** (`test_secenek_girdileri.py`, renk ve beden kategorileri)
| Tip | Test | Girdi | Teknik |
|---|---|---|---|
| Pozitif | `test_seceneklere_art_arda_dokunuldugunda_birden_fazla_secim_kalmamali` | Seçili olmayan seçeneğe art arda 2 kez dokunma | Denklik sınıfı: seçili olmayan seçenek |
| Negatif | `test_secili_secenege_tekrar_dokunuldugunda_secim_kaldirilmamali` | Zaten seçili seçeneğe dokunma | Denklik sınıfı: seçili seçenek |

### 5.4 White box — `tests/whitebox/`
**Fiyat ayrıştırıcı** (`test_fiyat_ayristirici.py`, cihaz gerektirmez)
| Tip | Test | Kapsanan kod yolu |
|---|---|---|
| Pozitif | `test_gecerli_fiyat_metni_yanlis_sayiya_cevrilmemeli` | Kuruşsuz, kuruşlu, tek haneli kuruş, binlik ayraç, bölünmez boşluk |
| Negatif | `test_gecersiz_fiyat_metni_sessizce_kabul_edilmemeli` | Regex'e uymayan 7 farklı metin → `ValueError` |
| Negatif | `test_metin_olmayan_girdi_fiyat_olarak_islenmemeli` | `None`, sayı, liste → `ValueError` |

**Ürün profili ve kategori belirleme** (`test_urun_profili.py`, cihaz gerektirmez)

Kategori testlerinin hangi ürünü kullanacağı `utils/urun_profili.py`'ye bağlı. Testler, uygulamanın gerçek ekran yapısını taklit eden küçük XML örnekleriyle bu kodun 9 kod yolunu çalıştırır.

| Tip | Test | Kapsanan kod yolu |
|---|---|---|
| Pozitif | `test_urun_sayfasi_yanlis_kategoriye_atanmamali[<kategori>]` | 6 kategorinin örnek sayfası tam olarak beklenen kategorilere atanmalı |
| Pozitif | `test_indirimli_urunun_fiyatlari_yanlis_okunmamali` | Eski fiyat, % ve iki parçalı satış fiyatı |
| Pozitif | `test_iki_parcali_satis_fiyati_hicbir_yazimda_kacirilmamali` | `",04 TL"`, `",90TL"`, `"TL"` yazımları |
| Negatif | `test_tek_fiyatli_urun_indirimli_sayilmamali` | Tek fiyat → indirimsiz |
| Negatif | `test_premium_indirimi_misafir_icin_indirim_sayilmamali` | "Premium ile" fiyatı misafirin fiyatı değil |
| Negatif | `test_tek_secenekli_grup_secim_sayilmamali` | Sadece "Renk: Siyah" yazan kutu seçim değil |
| Negatif | `test_sayfa_sekmeleri_ve_alt_limit_secenek_sayilmamali` | "Açıklama,seçili" sekmesi ve "Alt limit:" başlığı |
| Negatif | `test_basliktan_uzaktaki_secenek_gruba_eklenmemeli` | 450 pikselden uzak seçenek |
| Negatif | `test_stokta_yok_isareti_komsu_secenege_tasinmamali` | "Stokta yok" yalnızca kendi seçeneğine ait |
| Negatif | `test_kaydirilmis_gorunum_birlestirilince_secenek_tekrarlanmamali` | Kaydırılmış iki görünümün birleştirilmesi |

**Uygulama iç yapısı** (`test_uygulama_ic_yapisi.py`)
| Tip | Test | Kontrol edilen iç bilgi |
|---|---|---|
| Pozitif | `test_yuklu_uygulama_surumu_test_edilen_surumden_eski_olmamali` | Paket adı ve `versionName` ≥ 5.102.1 |
| Negatif | `test_yuklu_uygulama_hata_ayiklama_surumu_olmamali` | Paket bayraklarında (`pkgFlags`) `DEBUGGABLE` olmamalı: mağaza sürümü test edilmeli |
| Pozitif | `test_ana_sayfa_test_kimlikleri_kaldirilmamis_olmali` | `SearchBoxView`, `searchTextField`, `bottom_navigation_compose` resource-id'leri |
| Negatif | `test_ana_sayfa_test_kimlikleri_birden_fazla_elemanda_kullanilmamali` | Aynı kimlik birden fazla elemanda olmamalı (locator yanlış elemanı bulmasın) |
| Negatif | `test_misafir_odeme_akisi_auth_activity_disina_cikmamali` | Ödemeye Geç sonrası açılan Android activity `AuthActivity` olmalı |

### 5.5 Entegrasyon — `tests/integration/`
**Arama → ürün → sepet** (`test_arama_urun_sepet.py`, standart ürün)
| Tip | Test | Beklenen |
|---|---|---|
| Pozitif | `test_aramada_secilen_urun_sepete_farkli_urun_olarak_eklenmemeli` | Sepetteki ürün adı, aramada seçilen ürünle eşleşmeli |
| Pozitif | `test_urun_sayfasindaki_fiyat_sepette_farkli_gorunmemeli` | Ürün sayfasındaki satış fiyatı = sepetteki fiyat |
| Negatif | `test_urun_adedi_artirildiginda_sepet_toplami_tek_urun_fiyatinda_kalmamali` | Sepette adet 2'ye çıkınca toplam fiyat artmalı, tek ürün fiyatında kalmamalı |
| Negatif | `test_alisverise_devam_et_secildiginde_kullanici_sepete_yonlendirilmemeli` | "Alışverişe devam et" sepete götürmemeli, ürün sepetten düşmemeli |

**Kategoriye göre sepet aktarımı** (`test_kategori_sepet_aktarimi.py`, standart / renk / beden / çoklu / indirimli)
| Tip | Test | Beklenen |
|---|---|---|
| Pozitif | `test_kategori_urunu_sepete_farkli_secenek_veya_fiyatla_aktarilmamali[<kategori>]` | Seçili renk/beden sepette aynı görünmeli; sepet fiyatı ürünün liste (eski) fiyatını aşmamalı |
| Negatif | `test_kategori_urunu_sepete_eklenmeden_sepette_gorunmemeli[<kategori>]` | Seçenek değiştirilse bile "Sepete ekle"ye basılmadıkça sepet boş kalmalı |

### 5.6 Uçtan uca — `tests/e2e/test_alisveris_yolculugu.py`
| Tip | Test | Adımlar (her biri ekran görüntülü) |
|---|---|---|
| Pozitif | `test_misafir_kullanici_alisveris_adimlarinin_hicbirinde_takilmamali[<kategori>]` (standart, renk, beden, çoklu, indirimli) | 1 Ana sayfa → 2 Kategori ürünü bulundu → 3 Renk/beden seçildi (seçimli ürünlerde) → 4 Sepete eklendi → 5 Sepet → 6 Ödeme öncesi giriş/misafir adımı |
| Negatif | `test_sepete_eklemeden_ilerleyen_kullanici_odeme_adimina_ulasmamali[<kategori>]` (standart, renk, beden, çoklu, indirimli) | 1 Ana sayfa → 2 Kategori ürünü bulundu → 3 Renk/beden seçildi → 4 "Sepete ekle"ye basmadan sepete geçildi: sepet boş, "Ödemeye Geç" yok |
| Negatif | `test_stokta_olmayan_secenekle_alisveris_sepete_ulasmamali[stokta_olmayan]` | 1 Ana sayfa → 2 Ürün → 3 Stokta olmayan seçenek seçildi ("Sepete ekle" yok) → 4 Sepet boş |
| Negatif | `test_sepet_bosken_kullanici_odeme_adimina_gecememeli` | Boş sepette ödeme adımına geçiş olmamalı |

---

### 5.7 Bilinen hatalar — `tests/hatalar/`
| Hata | Test | Sonuç |
|---|---|---|
| [HB-001](hatalar/HB-001-premium-fiyati-misafire-satis-fiyati-gibi-gosteriliyor/rapor.md) | `test_hb001_urun_sayfasindaki_fiyat_misafirin_sepet_fiyatindan_dusuk_gosterilmemeli` | Hata sürdükçe **XFAIL** (çalıştırmayı durdurmaz); düzeltilirse **XPASS → başarısız** (kaydı kapatma zamanı) |

### Bulunan hatalar
Ayrıntılar: [`hatalar/README.md`](hatalar/README.md).

| No | Hata | Kanıt |
|---|---|---|
| **HB-001** | İndirimli tişört (Koyu Vizon - Siyah / L) ürün sayfasında **578,04 TL** görünüyor. Bu aslında Premium fiyatı ("Premium'a geç, 578,04 TL'ye al"); misafir kullanıcı sepette **642,27 TL** görüyor. Diğer ürünlerdeki "Premium ile" etiketi bu üründe yok. | [rapor + 3 ekran görüntüsü](hatalar/HB-001-premium-fiyati-misafire-satis-fiyati-gibi-gosteriliyor/rapor.md) |

**Fiyat kuralı:** Bu hata nedeniyle testlerde fiyat kontrolleri **sepette görünen fiyat** üzerinden yapılır. Ürün sayfasındaki fiyat yalnızca "eski fiyattan düşük mü" kontrolünde kullanılır.

---

## 6. Kurulum (adım adım)

> Aşağıdaki adımlar macOS (Apple Silicon) üzerinde denendi. Windows/Linux'ta da aynı mantıkla çalışır.

### 6.1 Android Studio
1. [developer.android.com/studio](https://developer.android.com/studio) adresinden **Mac with Apple chip** sürümünü indirin. Canary veya Beta değil, ana butondaki kararlı sürümü seçin.
2. `.dmg` dosyasını açın ve Android Studio'yu **Applications** klasörüne sürükleyin.
3. İlk açılışta **Do not import → Next → Install type: Standard → Next** adımlarını izleyin, tüm lisansları **Accept** edip **Finish** deyin.
4. SDK, emülatör ve platform araçları otomatik olarak iner. Android Studio, Java'yı (JBR) da birlikte kurar.

### 6.2 Emülatör
1. Android Studio → **More Actions → Virtual Device Manager → +**
2. Bir telefon seçin (ör. Pixel / Medium Phone).
3. Sistem imajı olarak **"Google Play"** etiketli bir **arm64-v8a** imaj seçin. Play Store sadece bu etiketli imajlarda var.
4. **Önemli:** Son ekranda **Show Advanced Settings** bölümünü açın ve **CPU cores: 4**, **RAM: 4096 MB**, **Graphics: Hardware** olarak ayarlayın. Varsayılan 1 çekirdekle testler 10 kat yavaş çalışır (bkz. [Bölüm 10](#10-karşılaşılan-sorunlar-ve-çözümleri)).
   - Var olan bir emülatör için `~/.android/avd/<ad>.avd/config.ini` dosyasında `hw.cpu.ncore=4`, `hw.ramSize=4096`, `hw.gpu.mode=host` değerlerini girip emülatörü kapatıp açın.
5. Emülatörü başlatın, Play Store'a Google hesabınızla giriş yapın ve **Hepsiburada** uygulamasını yükleyin.
6. Uygulamayı bir kez elle açın ve bildirim izni ekranını geçin.

### 6.3 Ortam değişkenleri
```bash
printf '%s\n' 'export ANDROID_HOME="$HOME/Library/Android/sdk"' 'export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"' 'export PATH="$JAVA_HOME/bin:$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$PATH"' >> ~/.zshrc
```
Terminali kapatıp yeniden açın. Kontrol etmek için:
```bash
adb devices
```
Listede `emulator-5554  device` görünmeli.

### 6.4 Appium
Node.js gereklidir (v20+).
```bash
npm install -g appium
```
```bash
appium driver install uiautomator2
```

### 6.5 Python ortamı
```bash
git clone https://github.com/panyabuke/hepsiburada-android-mobile-tests.git
cd hepsiburada-android-mobile-tests
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 6.6 (İsteğe bağlı) Test hesabı
Gerçek hesapla giriş testleri (`@pytest.mark.hesap`):

- **Nerede:** `tests/regression/test_giris.py` (regresyon klasörü, giriş dosyası). Ayrı bir klasör yoktur; `hesap` etiketiyle ayrılırlar.
- **Kim çalıştırır:** Hesap sahibi ya da hesap bilgileri kendisiyle **özel olarak** paylaşılan kişi (bkz. [Projeyi başkası çalıştıracaksa](#projeyi-başkası-çalıştıracaksa-hesap-testleri)). Testler otomatiktir (giriş, çıkış ve kontroller kodla yapılır), ama gerçek bir şifre kullandıkları için **elle başlatılır**. Tek elle yapılan iş, ilk girişteki doğrulama kodunu bir kez girmektir (adım 4).
- **Rapor:** `reports/hesap.html` (ekran görüntülü), konsol çıktısı `reports/hesap.log`.

| Tip | Test | Beklenen |
|---|---|---|
| Olumlu | `test_gecerli_bilgilerle_giris_yapan_kullanici_giris_ekraninda_kalmamali` | 1 Doğru bilgilerle giriş → 2 Hesabım'da giriş yapılmış görünüm → 3 Çıkış yap → Hesabım yeniden açılınca **Misafir kullanıcı** (her adım ekran görüntülü). Çıkıştan sonra uygulama Hesabım'da kalmaz; misafir görünümü Hesabım yeniden açılınca görünür. |
| Olumsuz | `test_dogru_eposta_yanlis_sifreyle_giris_yapilamamali` | Kayıtlı e-posta + yanlış şifre: hata mesajı ("E-posta adresi veya şifre hatalı.") gösterilmeli ve giriş ekranında kalınmalı. Ekran görüntüsü mesaj göründükten sonra alınır. |

Test yarıda kalsa bile sonunda **hesaptan çıkılır** (`oturumu_kapat` fixture'ı, güvenlik ağı). Böylece sonraki misafir kullanıcı testleri etkilenmez.

**Adımlar:**
1. Hepsiburada'da **yalnızca test için** bir hesap açın. Kayıtlı kart veya adres eklemeyin.
2. `.env` dosyasını açın (yoksa `cp .env.example .env` ile oluşturun). Dosya adı noktayla başladığı için Finder'da gizlidir; Finder'da **Cmd + Shift + .** ile görünür olur. Terminalden açmak için:
   ```bash
   open -e ~/Documents/hepsiburada-android-mobile-tests/hepsiburada-android-mobile-tests/.env
   ```
3. İki satırı doldurun. Tırnak işareti ve `=` etrafında boşluk kullanmayın:
   ```
   HB_EMAIL=test-hesabiniz@ornek.com
   HB_PASSWORD=sifreniz
   ```
   Kaydedip kapatın. `.env`, `.gitignore` içinde olduğu için GitHub'a yüklenmez.
   **Kontrol edin.** Şu komut değerleri ekrana yazdırmadan dolu mu, biçimi doğru mu kontrol eder:
   ```bash
   cd ~/Documents/hepsiburada-android-mobile-tests/hepsiburada-android-mobile-tests && .venv/bin/python -m utils.env_kontrol
   ```
   Çıktının sonunda `Sonuç: .env hazır.` görünmeli.
4. **İlk girişi bir kez elle yapın.** Emülatörde Hepsiburada → Hesabım → Giriş yap. Doğrulama kodu (SMS/e-posta) gelirse girin. Sonra Hesabım → **Çıkış yap** ile çıkın. Yeni cihazdan ilk girişte kod istenebilir, otomasyon bu kodu giremez.
5. Emülatör ve Appium açıkken hesap testlerini çalıştırın:
   ```bash
   cd ~/Documents/hepsiburada-android-mobile-tests/hepsiburada-android-mobile-tests && .venv/bin/pytest -m hesap --html=reports/hesap.html --self-contained-html 2>&1 | tee reports/hesap.log
   ```
   Sonunda `2 passed` görünmeli. Raporlarda test hesabının e-postası görünür; `reports/` GitHub'a yüklenmez, raporu paylaşırken dikkat edin.

#### Projeyi başkası çalıştıracaksa (hesap testleri)
Bu depoyu inceleyen biri hesap testlerini de çalıştırmak isterse:

> ⚠️ **Test hesabının e-postası ve şifresi bu depoda YOKTUR ve hiçbir zaman eklenmemelidir.** Depo herkese açıktır; GitHub'a yazılan bir şifre silinse bile commit geçmişinde kalır.

**Hesap bilgilerini paylaşan (proje sahibi):**
1. E-posta ve şifreyi yalnızca testi yapacak kişiye, **özel bir kanaldan** gönderin: doğrudan mesaj, e-posta ya da yüz yüze. GitHub'a, README'ye, Issue'lara ya da herkese açık bir yere yazmayın.
2. Bu hesap **yalnızca test hesabı** olmalı: kayıtlı kart, adres veya gerçek sipariş içermemeli.
3. **Doğrulama koduna hazır olun.** Testi yapan kişi kendi emülatöründen ilk kez giriş yaptığında Hepsiburada doğrulama kodunu hesabın e-postasına/telefonuna, yani **size** gönderebilir. O sırada kodu ona iletmeniz gerekir.
4. Testler bittikten sonra hesabın **şifresini değiştirin**.

**Testi yapan kişi:**
1. Projeyi kurun: [6.1–6.5](#6-kurulum-adım-adım) ve `git clone https://github.com/panyabuke/hepsiburada-android-mobile-tests.git`.
2. Hesap bilgilerini proje sahibinden **özel olarak** isteyin.
3. Proje klasöründe `.env` dosyasını oluşturun ve iki satırı doldurun (yukarıdaki 2. ve 3. adım):
   ```bash
   cp .env.example .env && open -e .env
   ```
   ```
   HB_EMAIL=<proje sahibinin verdiği e-posta>
   HB_PASSWORD=<proje sahibinin verdiği şifre>
   ```
4. Kontrol edin; çıktı `Sonuç: .env hazır.` olmalı:
   ```bash
   .venv/bin/python -m utils.env_kontrol
   ```
5. Emülatörde bir kez elle giriş yapın (yukarıdaki 4. adım). Doğrulama kodu istenirse kodu proje sahibinden alın, sonra **Çıkış yap**.
6. Testleri çalıştırın; sonunda `2 passed` görünmeli:
   ```bash
   .venv/bin/pytest -m hesap --html=reports/hesap.html --self-contained-html
   ```
7. İş bitince `.env` dosyasındaki e-posta ve şifreyi silin. `reports/` içindeki raporlarda hesabın e-postası görünür; raporu paylaşacaksanız buna dikkat edin.

`.env` dosyası `.gitignore` içindedir: Testi yapan kişi kendi bilgisayarından `git push` yapsa bile şifre GitHub'a gitmez.

**Neden ayrı çalışıyor?** `.env` dolu olsa bile `pytest` ya da `pytest tests/regression` hesap testlerini **atlar** ("yalnızca 'pytest -m hesap' ile çalışır"). Hesaba giriş yalnızca bilerek istendiğinde yapılır. Bu sayede:
- Normal çalıştırmalar hesaba hiç dokunmaz.
- Çok sayıda başarısız giriş denemesiyle hesabın kilitlenmesi önlenir.

---

## 7. Testleri çalıştırma

Önce iki ön koşul gerekiyor:

**1. Emülatörü başlatın** (DNS parametresi için bkz. [Bölüm 10](#10-karşılaşılan-sorunlar-ve-çözümleri)):
```bash
emulator -avd Medium_Phone_API_37.0 -dns-server 8.8.8.8,1.1.1.1
```

**2. Ayrı bir terminalde Appium sunucusunu başlatın:**
```bash
appium --port 4723
```

### Tüm testler
```bash
pytest
```
Bu komut testleri her zaman şu sırayla çalıştırır: **smoke → regression → blackbox → whitebox → integration → e2e** (`conftest.py > KLASOR_SIRASI`).

### Bir test başarısız olursa
`pytest.ini` içinde `-x` ayarı var: **ilk başarısız testte çalıştırma durur**, sonraki testlere geçilmez. Yapılması gereken:
1. HTML rapordaki **"Hata anı"** ekran görüntüsüne ve hata mesajına bakın.
2. Hatayı düzeltin (test kodu, locator ya da uygulamadaki gerçek bir hata ise kaydedin).
3. Başarısız testi tek başına çalıştırıp geçtiğini görün:
```bash
pytest "tests/smoke/test_smoke_kategoriler.py::test_kategoriye_uyan_urun_arama_sonuclarinda_eksik_olmamali[coklu_secimli]"
```
4. Sonra o klasörü **baştan** çalıştırın ve sıradaki klasöre ancak o zaman geçin.

Durmadan tüm testleri görmek gerekirse (ör. genel durum raporu için) `-x` geçici olarak kapatılabilir:
```bash
pytest -o addopts="-v --html=reports/rapor.html --self-contained-html"
```

### Test tipine (klasöre) göre
```bash
pytest tests/smoke
```
```bash
pytest tests/regression
```
```bash
pytest tests/blackbox
```
```bash
pytest tests/whitebox
```
```bash
pytest tests/integration
```
```bash
pytest tests/e2e
```

### Marker'a göre
```bash
pytest -m negatif
```
```bash
pytest -m "regression and pozitif"
```

### Ürün kategorisine göre
```bash
pytest -m beden_secimli
```
```bash
pytest -m "stokta_olmayan or indirimli"
```
Kategori marker'ları: `standart`, `renk_secimli`, `beden_secimli`, `coklu_secimli`, `indirimli`, `stokta_olmayan`.

---

## 8. Raporlar ve ekran görüntüleri

- **HTML rapor:** `reports/rapor.html` dosyası her çalıştırmada yenilenir. Tarayıcıda açın. Her testin satırına tıklayınca şunlar görünür:
  - **Senaryo:** testin olumsuz cümleyle yazılmış açıklaması
  - **Adım 1, Adım 2, …:** her adımın ekran görüntüsü
  - Test başarısızsa ek olarak **"Hata anı"** ekran görüntüsü
- **PNG dosyaları:** `reports/screenshots/<test_adi>/01_….png, 02_….png …` (örneğin uçtan uca alışveriş yolculuğunun 7 adımı ayrı ayrı)
- Farklı bir rapor adı vermek için:
```bash
pytest tests/e2e --html=reports/e2e.html --self-contained-html
```

---

## 9. Testleri yazarken dikkat edilmesi gerekenler

### Yapı ve okunabilirlik
1. **Page Object Model kullanın.** Eleman tanımları (`locator`) sadece `pages/` içinde dursun. Uygulama arayüzü değişince tek yerden güncellenir.
2. **Her test tek bir şeyi doğrulasın.** Test adı neyi doğruladığını söylesin; olumsuz cümle kalıbı kullanın (`…olmamalı`).
3. **Her pozitif testin bir negatif karşılığı olsun.** Sadece "çalışıyor mu?" değil, "yanlış kullanımı engelliyor mu?" sorusu da test edilmeli.
4. **Assert mesajı yazın.** `assert x, "Sepet boş görünüyor"` gibi bir mesaj, raporda hatanın ne olduğunu doğrudan söyler.
5. **Tekrar eden akışları fonksiyonlaştırın** (`pages/flows.py`): ara, ürün aç, sepete ekle.

### Eleman bulma (locator) stratejisi
6. Öncelik sırası: **resource-id** → **content-desc (accessibility id)** → **metin** → **XPath** (son çare).
7. **Koordinatla tıklamayın.** Ekran boyutu ve reklam alanları değişince bozulur.
8. Hepsiburada'da iki tür kimlik var: native ekranlarda `com.pozitron.hepsiburada:id/tvTitle`, Jetpack Compose ekranlarında sadece `SearchBoxView`. `by_id()` yardımcısı ikisini de eşler.
9. Reklam/sponsorlu ürünler listenin başında çıkabilir. Ürün seçerken normal liste kartlarını (`composeProductBoxView`) hedefleyin.

### Bekleme ve kararlılık
10. **`time.sleep` yerine açık bekleme (`WebDriverWait`) kullanın.** `find()`, `is_visible()`, `is_absent()` yardımcıları bunu yapar.
11. **"Görünmemeli" kontrollerinde süre sınırı koyun** (`is_absent(locator, 3)`). Yoksa test gereksiz yere uzun bekler.
12. **Beklenmeyen açılır pencereleri merkezi yönetin** (`BasePage.POPUPS` ve `HomePage.wait_ready()`): bildirim izni, ipucu balonları, sistem pencereleri.

### Test verisi ve bağımsızlık
13. **Testler birbirine bağımlı olmasın.** Her test uygulamayı yeniden başlatır (`app` fixture) ve sepeti başta/sonda boşaltır (`bos_sepet` fixture).
14. **Canlı veriye bağlı kesin değerler beklemeyin.** Ürün adı, fiyat, sonuç sayısı değişir. "Sonuç sayısı > 0" veya "ürün sayfası fiyatı = sepet fiyatı" gibi göreli kontroller yapın.
15. **Şifre ve hesap bilgilerini koda yazmayın.** `.env` kullanın ve `.env`'i git'e eklemeyin.

### Canlı sistemde test etiği
16. **Gerçek sipariş vermeyin.** Testler ödeme bilgisi istenen adımda durur.
17. **Bot korumalarını aşmaya çalışmayın.** "Olağan dışı erişim" benzeri bir ekran çıkarsa o uygulamada otomasyon yapılmamalı.
18. **Sistemi yormayın.** Testleri makul aralıklarla çalıştırın, paralel yük üretmeyin.

### Ürün kategorileri
19. **Ürünü sabitlemeyin, kategorisini tarif edin.** Ürün adı yerine "renk seçimi olan ürün" gibi bir koşul yazın (`utils/urun_profili.py > kategoriler()`). Ürün yayından kalkınca test başka bir ürünle devam eder.
20. **Kategori koşulunu da test edin.** Kategori belirleme kodu yanlışsa o kategorinin tüm testleri yanlış ürünle çalışır; bu yüzden `tests/whitebox/test_urun_profili.py` var.
21. **Esas fiyat sepet fiyatıdır.** Ürün sayfasında büyük yazılan fiyat bazı ürünlerde Premium üyelik fiyatıdır (HB-001). Kullanıcının ödeyeceği fiyatı sepetten okuyun.
22. **Satış fiyatı ile eski fiyatı karıştırmayın.** İndirimli üründe `originalPriceComponent` üstü çizili **eski** fiyattır; satış fiyatı ayrı iki parça halinde yazılır ("578" + ",04 TL"). "Premium ile" fiyatı misafir kullanıcının ödediği fiyat değildir.
23. **Sepete özel kampanyaları hesaba katın.** Sepette ek indirim uygulanabilir ("1 ve üzeri %50 indirim"). Bu yüzden indirimli ürünlerde "sepet fiyatı ≤ ürün sayfası fiyatı" kontrol edilir, eşitlik değil.
24. **Seçenek değişince sayfa yeniden çizilir.** Seçeneklerin konumu tek seferde alınan sayfa kaynağından (`page_source`) okunur; eleman referansı tutulmaz.

### Çalıştırma disiplini
25. **İlk hatada durun.** Bir test başarısızken sonraki testleri çalıştırmak, aynı kök nedenin onlarca hata üretmesine ve gerçek sorunun gözden kaçmasına yol açar.
26. **Düzeltmeden sonra klasörü baştan çalıştırın.** Sadece başarısız testin geçmesi yeterli değildir; düzeltme diğer testleri bozmuş olabilir.
27. **Hatanın testte mi uygulamada mı olduğunu ayırın.** Test kodu hatasıysa testi düzeltin. Uygulama hatasıysa `hatalar/` altına raporlayın, `tests/hatalar/` altına `xfail(strict=True)` testi ekleyin ve asıl testi hatayı içermeyen davranışı doğrulayacak şekilde düzenleyin (bkz. `hatalar/README.md`).

---

## 10. Karşılaşılan sorunlar ve çözümleri

| Sorun | Neden | Çözüm |
|---|---|---|
| **Sahibinden** "Olağan dışı erişim tespit ettik" ekranı | Uygulama otomasyonu/emülatörü bot olarak algılıyor | Bu koruma aşılmadı (etik ve kullanım koşulları gereği). Proje Hepsiburada ile yapıldı. |
| Her Appium komutu ~10 sn sürüyor (2 test 6 dk) | Ana sayfadaki kayan banner'lar ekranı hiç "boşta" bırakmıyor, UiAutomator2 boşta olmayı bekliyor | `appium:settings[waitForIdleTimeout] = 0` (`config/capabilities.py`) |
| Eleman aramaları 10–35 sn, regresyon seti 47 dk sürüyor | Emülatör **1 CPU çekirdeğiyle** tanımlıydı; Hepsiburada ağır bir uygulama, emülatör CPU'nun %64'ünü sistem işlerine harcıyor ve swap kullanıyordu | Emülatöre 4 çekirdek, 4 GB RAM ve donanım grafik verildi. Ana sayfa hazır olma süresi 183 sn → 16 sn, arama ekranı açılışı 26 sn → 0,2 sn |
| Ürün kartı bulunamıyor | Native kimlikler `com.pozitron.hepsiburada:id/…` önekiyle geliyor ve ürün kartı doğrudan alt eleman değil, daha derinde | XPath'te `contains(@resource-id, …)` ve `//` (tüm alt elemanlar) kullanıldı |
| Sonuç sayısı -1 okunuyor | Başlık önce sadece kelimeyle gelir, "(10.000+)" birkaç sn sonra eklenir | `result_count()` sayı gelene kadar bekler |
| Ürün kartına tıklanıyor ama ürün sayfası açılmıyor (ara sıra) | Kartın ortası kaydırılabilir resim galerisi; tıklamayı bazen yutuyor | Kartın alt kısmındaki ürün adına dokunulur, açılmazsa 3 kez denenir |
| `StaleElementReferenceException` (ara sıra) | Sonuç listesi, kart bulunduktan hemen sonra yeniden çiziliyor | Kartı bulma, okuma ve dokunma adımları bu hataya karşı 5 kez yeniden denenir |
| "Minimum karakter" uyarısı yakalanamıyor | Uyarı ~2 sn görünen bir **Toast**; test önce ekran görüntüsü alınca kaçırıyordu | `//android.widget.Toast` ile hemen, ekran görüntüsünden önce kontrol edilir |
| Test bitince temizlik (sepeti boşaltma) hata veriyor | Test sepet/giriş ekranında bitiyor, bu ekranlarda alt menü yok | Temizlikten önce uygulama yeniden başlatılır |
| Giriş butonu bulunamıyor | `hide_keyboard()` Android'de geri tuşuna basıp giriş ekranını kapatıyor | Klavye kapatılmadan butona basılıyor (buton klavyenin üstünde) |
| Uygulama "Connection problem" gösteriyor | Mac'in ağı değişince (ör. hotspot → Wi-Fi) emülatör eski DNS'i kullanmaya devam ediyor | Emülatörü `-dns-server 8.8.8.8,1.1.1.1` ile başlatın |
| Ana sayfada test takılıyor | Gecikmeli açılan "Kategoriler artık anasayfada" gibi ipucu balonları ekranı kapatıyor; bazılarının kimliği yok | `HomePage.wait_ready()` önce bilinen pencereleri kapatır, sonra gerekirse geri tuşuna basar |
| Uygulama son ekranı (ör. sepet) geri yüklüyor | Uygulama durumu saklıyor | `wait_ready()` ana sayfa görünmezse alt menüden Ana Sayfam'a döner |
| Kategori ürünü seçerken `StaleElementReferenceException` (ara sıra) | Renk/beden seçenekleri okunurken ürün sayfası yeniden çiziliyor | Seçenek konumları elemanlardan değil, tek seferlik sayfa kaynağından okunur; dokunma koordinatla yapılır |
| Standart üründe fiyat okunamıyor | İndirimsiz üründe kuruş kısmı boşluksuz yazılıyor (`",90TL"`), indirimli üründe boşluklu (`",04 TL"`) | Fiyat okuyucu iki yazımı da kabul eder; white box testi eklendi |
| Ürün sayfasında eski fiyat okunuyordu | `originalPriceComponent` indirimli üründe üstü çizili eski fiyat | Satış fiyatı ayrı okunur (`ProductPage.price_text()`, `UrunProfili.satis_fiyati`) |
| Kulaklık "indirimli" görünüyor ama misafire indirim yok | İndirim yalnızca Premium üyelere ("Premium ile") | "Premium ile" indirimi indirimli sayılmaz |
| Çoklu seçimde renk değişince beden seçilemiyor (ara sıra) | Renk değişince uygulama farklı bir ürün sayfası açıyor (ör. VR071 → VR033) ve sayfa yeniden yüklenip kayıyor; kayma sırasındaki dokunma seçim yapmıyor, sadece kaymayı durduruyor | `secenek_sec()` seçim 5 sn içinde görünmezse konumu yeniden okuyup bir kez daha dokunur. Hata mesajı artık her seçeneğin neden seçilemediğini listeliyor |
| İndirimli ürünün sepet fiyatı, ürün sayfasındakinden yüksek (578,04 → 642,27 TL) | **Uygulama hatası:** Ürün sayfasında Premium fiyatı etiketsiz gösteriliyor | `hatalar/HB-001` olarak raporlandı; testler sepet fiyatını esas alıyor; hata `tests/hatalar` ile izleniyor |
| Varsayılan seçilen bedenin stoğu yok | Renk değişince seçili beden o renkte bulunmayabiliyor ("Krem / XL kombinasyonunda ürün bulunmamaktadır") | `baska_secenek_sec()` bu uyarıyı görürse bir sonraki seçeneği dener |
| Gerçek hesap testinden sonra çıkış "başarısız" görünüyor | Çıkış yapılıyor ama uygulama Hesabım'da kalmayıp ana sayfaya dönüyor; test misafir görünümünü yanlış sayfada arıyordu | `AccountPage.logout()` çıkıştan sonra Hesabım sekmesini yeniden açıp kontrol ediyor |
| Xcode kurulamıyor | App Store'daki son Xcode daha yeni bir macOS istiyor | developer.apple.com/download/all üzerinden macOS sürümüne uygun eski Xcode indirilebilir ya da macOS güncellenebilir |

---

## 11. Sınırlamalar

- **White box:** Hepsiburada'nın kaynak koduna erişim olmadığı için uygulama kodu üzerinde gerçek bir white box testi yapılamaz. Bu yüzden white box testleri iki şekilde uygulandı: (a) kaynağı projede bulunan `utils/price.py` için tam kod yolu kapsaması, (b) uygulamanın iç yapısı (paket, sürüm, activity geçişleri, resource-id'ler).
- **Giriş:** Gerçek giriş testi bir test hesabı gerektirir (`.env`). Hesap tanımlı değilse bu test atlanır. Negatif giriş testlerinde gerçek bir şifre kullanılmaz.
- **Gerçek giriş testinde çıkış adımı yok:** Test giriş yaptıktan sonra hesaptan çıkmıyor. Uygulama oturumu hatırladığı için, `.env` doldurulup test çalıştırılırsa sonraki "misafir kullanıcı" testleri bozulur. Hesapla çalıştırmadan önce teste "Hesabım → Çıkış yap" temizlik adımı eklenmeli. "Çıkış yap" butonu ancak giriş yapılınca göründüğü için bu adım bir test hesabıyla doğrulanmalı.
- **Checkout:** Ödeme bilgisi girişi ve sipariş onayı test edilmez (gerçek sipariş oluşmaması için).
- **Kategori ürünleri canlı veriye bağlı:** Kategoriye uyan ürün, arama kelimelerinin ilk 3 sonucunda bulunamazsa smoke testi bunu açıkça raporlar. Bu durumda `config/urun_kategorileri.py` içine yeni arama kelimeleri eklenmelidir.
- **Bedeni zorunlu seçtiren ürün bulunamadı:** İncelenen beden seçimli ürünlerin hepsinde (ayakkabı, kazak, mont, tişört) bir beden önceden seçili geliyordu. Bu yüzden "beden seçmeden sepete eklenememeli" senaryosu bu uygulamada test edilemiyor; bunun yerine seçilen bedenin sepete doğru aktarılması test ediliyor.
- **Canlı veri:** Testler canlı uygulamaya karşı çalışır. Kampanya ekranları, A/B testleri veya yeni açılır pencereler testleri etkileyebilir. Bu durumda `BasePage.POPUPS` güncellenmelidir.

---

## 12. iOS desteği

`config/capabilities.py` içinde iOS (XCUITest) ayarları hazır. Ancak iOS testleri şu an **atlanıyor**, çünkü:
1. Bu makinede Xcode yok (macOS sürümü App Store'daki Xcode için eski).
2. App Store uygulamaları iOS Simulator'a yüklenemez; Hepsiburada iOS için **gerçek bir iPhone** gerekir.
3. iOS ekran kimlikleri (locator'lar) cihaz bağlanınca Appium Inspector ile çıkarılmalı.

iOS'u eklemek için:
1. Uyumlu bir Xcode kurun ve `sudo xcode-select -s /Applications/Xcode.app` çalıştırın.
2. `appium driver install xcuitest` ile iOS sürücüsünü kurun.
3. iPhone'u kabloyla bağlayın ve WebDriverAgent'ı kendi Apple ID'nizle imzalayın.
4. `pages/` sınıflarına iOS locator'larını ekleyin.
5. Testleri `PLATFORM=ios IOS_UDID=<cihaz-udid> pytest` ile çalıştırın.

---

## 13. Son çalıştırma sonuçları

**Tarih:** 3 Kasım 2026 · **Ortam:** Android 17 emülatörü (4 çekirdek, 4 GB RAM), Hepsiburada 5.102.1

### Son tam çalıştırma (son kodla, tek seferde)
`pytest` komutuyla tüm testler, belirlenen sırada ve ilk hatada durma kuralıyla (`-x`) **tek seferde** çalıştırıldı:

```
118 passed, 2 skipped, 1 xfailed in 1942.82s (0:32:22)
```

| Sıra | Klasör | Test sayısı | Geçti | Atlandı | Beklenen hata (XFAIL) | Başarısız |
|---|---|---|---|---|---|---|
| 1 | `smoke` | 14 | 14 | 0 | 0 | 0 |
| 2 | `regression` | 24 | 22 | 2 | 0 | 0 |
| 3 | `blackbox` | 16 | 16 | 0 | 0 | 0 |
| 4 | `whitebox` | 40 | 40 | 0 | 0 | 0 |
| 5 | `integration` | 14 | 14 | 0 | 0 | 0 |
| 6 | `e2e` | 12 | 12 | 0 | 0 | 0 |
| 7 | `hatalar` | 1 | 0 | 0 | 1 | 0 |
| | **Toplam** | **121** | **118** | **2** | **1** | **0** |
| ayrı | `pytest -m hesap` (gerçek hesap) | 2 | 2 | 0 | 0 | 0 |

- **Rapor:** `reports/rapor.html` (tüm testler, ekran görüntülü, yaklaşık 90 MB; tarayıcıda açılması birkaç saniye sürebilir). Konsol çıktısı: `reports/tam_calistirma.log`.
- Bu çalıştırmada **yeni bir uygulama hatası çıkmadı**; `hatalar/` klasörüne yeni kayıt eklenmedi.

### Klasör klasör çalıştırma (geliştirme sırasında)
Testler geliştirilirken her klasör ayrı ayrı çalıştırıldı. Hata çıkan klasör, düzeltmeden sonra **baştan** çalıştırıldı. Klasör raporları: `reports/1_smoke.html` … `reports/7_hatalar.html`.

- **Atlanan testler:** İki gerçek hesap testi normal çalıştırmada bilerek atlanır; yalnızca `pytest -m hesap` ile çalışırlar (bkz. [6.6](#66-isteğe-bağlı-test-hesabı)).
- **Gerçek hesap testleri** test hesabı sahibi tarafından `pytest -m hesap` ile ayrıca çalıştırıldı: **2 passed** (son kodla, olumsuz testte hata mesajı kontrolüyle tekrarlandı: 2 passed, 1 dk 12 sn; çıktı `reports/hesap.log`). Olumsuz testte uygulamanın gösterdiği mesaj: "E-posta adresi veya şifre hatalı." Olumlu test: giriş → Hesabım'da giriş yapılmış görünüm → çıkış → Hesabım'da "Misafir kullanıcı". Olumsuz test: doğru e-posta + yanlış şifre ile giriş ekranında kalındı. Rapor: `reports/hesap.html`.
- **Beklenen hata:** [HB-001](hatalar/HB-001-premium-fiyati-misafire-satis-fiyati-gibi-gosteriliyor/rapor.md). Uygulamadaki fiyat hatası yeniden üretildi.
- Parametreli testler ayrı ayrı sayıldı (ör. 6 kategori = 6 test).
- Olumlu/olumsuz dağılımı (test fonksiyonu olarak): 28 olumlu, 39 olumsuz. 17 test dosyasının her birinde olumsuz test sayısı en az olumlu test sayısı kadar.

**Çalıştırma sırasında çıkan ve düzeltilen hatalar** (ilk hatada durma kuralı sayesinde tek tek yakalandı):

| Klasör | Hata | Kaynağı | Çözüm |
|---|---|---|---|
| smoke | Seçenek okunurken `StaleElementReferenceException` | Test kodu | Seçenek konumları tek seferlik sayfa kaynağından okunuyor |
| smoke | Standart üründe fiyat okunamadı (`",90TL"`) | Test kodu | Fiyat okuyucu boşluksuz yazımı da kabul ediyor |
| regression | Çoklu seçimde renk değişince beden seçilemedi | Test kodu (kayan sayfaya dokunma) | Seçim görünmezse yeniden dokunma |
| regression | İndirimli ürün sepette sayfadakinden pahalı (578,04 → 642,27 TL) | **Uygulama** | HB-001 olarak raporlandı; fiyat kontrolleri sepet fiyatına göre |
| regression | Sepete eklendi penceresi çıkmadı | Uygulama davranışı (ara sıra) | Bildirim de onay sayılıyor; sepete simgeden gidiliyor |
| regression | Sepeti boşaltma adımında zaman aşımı | Uygulama yavaş açılışı (ara sıra) | Uygulama yeniden açılıp bir kez daha deneniyor |
| integration | Standart üründe sepette seçenek satırı arandı | Test kodu | Seçenek satırı yalnızca seçenekli ürünlerde okunuyor |

Ekran görüntüleri: `reports/screenshots/<test_adi>/`.

> Testler canlı uygulamaya karşı çalıştığı için uygulamadaki kampanya ekranları, stok durumu veya arayüz değişiklikleri sonuçları etkileyebilir. Bir test başarısız olursa önce HTML rapordaki **"Hata anı"** ekran görüntüsüne bakın.

---

## 14. GitHub'a yükleme

**Depo:** https://github.com/panyabuke/hepsiburada-android-mobile-tests (herkese açık, `main` dalı)

`.gitignore` şunları **dışarıda bırakır**:
- `.env`: test hesabı bilgileri
- `.venv/`: Python ortamı
- `reports/`: raporlar ve ekran görüntüleri; içlerinde test hesabının e-postası görünebilir
- `__pycache__/`, `.pytest_cache/`, `.DS_Store`

Kanıt ekran görüntüleri `hatalar/` klasöründe olduğu için depoya dahildir.

### Değişiklikleri GitHub'a göndermek
**GitHub Desktop ile:**
1. Sol üstte **Current Repository: hepsiburada-android-mobile-tests** seçili olsun.
2. **Changes** sekmesinde değişen dosyalar görünür. Sol alttaki **Summary** kutusuna kısa bir açıklama yazıp **Commit to main**'e basın. Değişiklik zaten commit edildiyse bu adım atlanır.
3. Üstteki **Push origin**'e basın.

**Terminal ile:**
```bash
cd ~/Documents/hepsiburada-android-mobile-tests/hepsiburada-android-mobile-tests && git add -A && git commit -m "Açıklama" && git push
```

### Projeyi başka bir bilgisayara kurmak
[6. Kurulum](#6-kurulum-adım-adım) adımlarını izleyin. Depoyu indirmek için:
```bash
git clone https://github.com/panyabuke/hepsiburada-android-mobile-tests.git
```
