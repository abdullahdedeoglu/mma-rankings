# Araştırma Protokolü (ön kayıt)

**Sürüm:** 0.3 · **Tarih:** 2026-11-05 · **Durum:** taslak, deneylerden önce yazıldı

Bu belge, derecelendirme sisteminin matematiğini baştan kurarken **deneylere başlamadan önce**
neyi nasıl ölçeceğimizi ve hangi kurala göre karar vereceğimizi sabitler. Amaç, sonuçları
gördükten sonra kuralları değiştirmeyi (bilinçli ya da bilinçsiz) engellemektir. Deneyler
başladıktan sonra yapılan her değişiklik, tarih ve gerekçesiyle en alttaki *Değişiklik günlüğü*ne yazılır.
Yapılan her deney, başarısız olanlar da dahil, [EXPERIMENTS.md](EXPERIMENTS.md) dosyasına kaydedilir.
Okuma listesi ve kaynakların hangi karara dayanak olduğu [LITERATURE.md](LITERATURE.md) dosyasındadır.

---

## 1. Araştırma soruları

Sistem iki katmandan oluşur ve bunlar ayrı ayrı ele alınır:

| Katman | Soru | Doğası |
|---|---|---|
| **Tahmin modeli** | Bir maçtan önce, *yalnızca o güne kadar bilinen bilgiyle*, A'nın B'yi yenme olasılığı nedir? | Bilimsel olarak sınanabilir |
| **Sıralama katmanı** | Tahmin modelinin çıktısından hangi listeler, hangi kurallarla üretilir? | Kısmen sınanabilir, büyük ölçüde politika |

- **S1 (birincil):** Hangi derecelendirme modeli, geleceğe sızmadan (filtreleme), maç sonuçlarını en iyi tahmin eder?
- **S2:** Hangi ek bilgiler (bitiş şekli, yaş, maç arası süre, sıklet değişimi…) tahmini anlamlı ölçüde iyileştirir? (Bkz. §7.)
- **S3:** Sıralama katmanının hangi kararları veriyle sınanabilir, hangileri açıkça politika olarak etiketlenmelidir? (Bkz. §8.)

**Derecelendirmenin tanımı:** Bir dövüşçünün *t* anındaki derecesi, *t* öncesindeki maçlardan
çıkarılan, gizli bir güç değişkeninin sonsal tahminidir (ortalama μ ve belirsizlik). Bu ölçek, maç
olasılıklarını belirleyen lojistik/normal bağlantı fonksiyonu üzerinden tanımlıdır; başka bir anlamı
(ör. "efsanelik", "kariyer başarısı") yoktur.

## 2. Veri

- **Kaynak:** Fight Canon SQLite, sürüm `db-2026-11-04-1837`
  - SHA-256: `e0ea391fff9ec2f9225407160f4407a499d42173cebbe371e306de2769858cf6`
  - Son olay tarihi: 2026-11-01
  - Bu sürüm, protokolün geliştirme aşamasında kullanılan **tek** veri sürümüdür. Yeni sürüm yalnızca
    ileriye dönük test (§4.3) için kullanılır.
- **Derecelendirilen maç:** sonucu galibiyet/mağlubiyet/beraberlik olan profesyonel maç.
  NC, DQ, sonucu belirsiz (N/A) ve yöntemi eksik maçlar dereceyi değiştirmez (aktiflik için sayılır).
  Aynı çift, farklı etkinlik, ≤30 gün arayla, aynı sonuç: yakın-tekrar kayıt olarak birleştirilir.
- **Ham sayılar (bu sürüm):** 366.496 derecelendirilen maç, bunların 5.036'sı beraberlik (%1,4).
- **Bilinen ölçüm sorunları:**
  1. Bölgesel organizasyonların kayıtları eksik; eksiklik ülkeye ve döneme göre değişir.
  2. Kayıtlar geriye dönük eklenebilir (gecikmeli doldurma). Bu, ileriye dönük test tasarımını etkiler (§4.3).
  3. Sıklet etiketleri dönem ve organizasyona göre farklı anlamlar taşır (eşleme tablosu: `src/mmarank/mappings/weight_class_overrides.csv`).
  4. Cinsiyet kısmen çıkarımla belirlenir (Fight Canon, Wikidata, rakip ağı).
- **Ek değişkenlerin kapsamı** (2010'dan beri maç yapmış dövüşçüler):

  | Değişken | Tüm dövüşçüler (145.986) | UFC dövüşçüleri (2.296) |
  |---|---|---|
  | Doğum tarihi | 33.878 (%23) | 2.292 (%99,8) |
  | Boy | 45.826 (%31) | — |
  | Kol açıklığı | 2.652 (%2) | 2.050 (%89) |
  | Uyruk | 75.002 (%51) | — |

  Eksiklik rastgele değildir (büyük organizasyonlarda yoğunlaşır). Bu değişkenlerle yapılan her
  analiz, eksikliğin yanlılık yaratabileceğini açıkça belirtir.

## 3. Değerlendirme görevi

- Her derecelendirilen maç için, maç tarihinden **önceki** derecelerle tek adım ileri olasılık üretilir.
  Aynı gündeki tüm maçlar günün başındaki derecelerle tahmin edilir.
- **Birincil metrik:** log loss (logaritmik skor), beraberlikler hariç sonuçlanmış maçlarda.
  Gerekçe: kesin uygun (strictly proper) bir skorlama kuralıdır; olasılıkların kendisini ödüllendirir
  (Gneiting & Raftery 2007). Ayrıca veri zaman sırasıyla geldiğinde tek adım ileri log skorların toplamı modelin
  log marjinal olabilirliğine eşittir (Dawid 1984; Gneiting & Raftery 2007 §7.1). Yani filtreleme modellerinde bu ölçüt
  tam örneklem Bayesçi model karşılaştırmasıdır (Glicko gibi yaklaşık filtrelerde yaklaşık olarak).
- **İkincil metrikler:** Brier skoru; kalibrasyon (güvenilirlik grafiği, ayrıca sonucun logit(p) üzerine
  lojistik regresyonundan kalibrasyon eğimi ve kesişimi). İsabet oranı uygun ama kesin uygun olmayan bir
  skordur; yalnızca betimleyici olarak raporlanır, karar için kullanılmaz. Beceri skorları (referansa göre
  normalize skorlar) genellikle uygun değildir; raporlanabilir ama karar ölçütü değildir.
- **Birincil popülasyon:** her iki dövüşçünün de en az 3 önceki derecelendirilmiş maçı olan **erkek** maçları
  (yayımlanan listeler bu dövüşçülerle ilgilidir).
- **İkincil popülasyonlar:** tüm maçlar; deneyim bantları (0, 1–2, 3–9, 10+ önceki maç); dönemler; bahis oranı olan alt küme;
  birleşik belirsizlik bantları (√(RD_A² + RD_B²): <100, 100–200, 200+).
- **Model karşılaştırması:** maç bazında eşleştirilmiş log loss farkı. Belirsizlik, **etkinlik düzeyinde
  kümelenmiş bootstrap** ile ölçülür (B = 2000, tohum = 20261105), %95 güven aralığı raporlanır.
  Aynı etkinlikteki maçlar bağımsız sayılmaz.
- **Dayanıklılık kontrolleri** (her karşılaştırmada):
  1. Brier skoru log loss ile aynı yönde mi? Farklıysa açıkça raporlanır.
  2. Ay düzeyinde kümelenmiş bootstrap (aynı dövüşçünün yakın tarihli maçları arasındaki bağımlılığı kabaca yakalamak için).
  3. Log loss uç olaylara çok sert olduğu için, en kötü skorlanan 50 maç veri hatası (yanlış kazanan, yanlış eşleşmiş dövüşçü) için elle incelenir.
     Bulunan hatalar düzeltilmez ama kaydedilir ve hatalı maçlar çıkarılarak sonuç tekrar raporlanır.

## 4. Veri bölmeleri ve sızıntı

### 4.1 Dürüst durum tespiti

Bu protokolden önce, 2016–2020 doğrulama ve 2021+ test dönemleri defalarca incelendi ve parametreler
bu incelemeler sırasında değiştirildi. **Bu veri sürümünde gerçekten görülmemiş bir tarihsel test dönemi
yoktur.** Bu nedenle tarihsel sonuçlar *geliştirme kanıtı* sayılır; asıl doğrulama ileriye dönük testtir (§4.3).

### 4.2 Geliştirme: iç içe kayan başlangıç (nested rolling-origin)

Filtreleme modelleri her maçı zaten yalnızca geçmiş bilgiyle tahmin eder; aşırı uyum riski yalnızca
**hiperparametre seçiminden** gelir. Bu yüzden:

1. Her aday ayar için model bir kez çalıştırılır ve tüm maçlar için tek adım ileri tahminler saklanır.
2. Her test yılı *Y* için (2008–2025), ayar yalnızca *Y*'den önceki yılların birincil popülasyonundaki
   log loss'a göre seçilir ve *Y* yılında değerlendirilir.
3. Yıllar boyunca toplanan sonuç, "model + ayar seçme yöntemi"nin dürüst performans tahminidir. Kararlar bu sayıya göre verilir.

2020 yılı (pandemi, düşük maç sayısı) dahil edilir ama ayrıca işaretlenir.

Ayrıca her model için, ayarlar tüm geliştirme dönemi (2008–2025) üzerinden seçilerek **tam dizi log skoru** raporlanır.
Hiperparametre sayısı az olduğunda (≤4) iki sonuç neredeyse aynı olmalıdır: BIC cezası parametre başına ½·ln(n) olup
n ≈ 78.600 maçta maç başına ≈0,00007'dir (Diebold 2015; Gneiting & Raftery 2007 §7.1). İç içe değerlendirme asıl olarak
çok parametreli bileşenlere (veriden tahmin edilen bitiş ağırlıkları, yaş eğrisi gibi) karşı koruma sağlar.
İki sonuç çelişirse bu açıkça raporlanır ve karar iç içe sonuca göre verilir.

### 4.3 Doğrulama: ileriye dönük test

1. Nihai model (kod + parametreler) bir git etiketiyle (`model-vX`) donmuş hale getirilir. Etiketin commit
   zaman damgası ön kayıt işlevi görür: modeli o tarihten sonraki maçlara göre ayarlamak imkânsızdır.
2. Dondurma tarihinden sonraki maçlar test kümesidir.
3. Gecikmeli doldurma nedeniyle değerlendirme, test penceresinin bitiminden **en az 90 gün sonra** yayımlanmış
   bir veri sürümüyle yapılır.
4. **Güç hesabı** (bu veri sürümünden, 2016+ birincil popülasyon): birbirine yakın iki modelin maç bazında log loss
   farkının standart sapması ≈ 0,114; yılda ≈ 7.900 uygun maç var. Buna göre:

   | Saptanacak fark (log loss) | Gereken maç | Yaklaşık süre |
   |---|---|---|
   | 0,010 | ≈ 500 | ~1 ay |
   | 0,005 | ≈ 2.000 | ~3 ay |
   | 0,002 | ≈ 12.600 | ~19 ay |

   Plan: ilk ara rapor 6 ay, ana rapor 12 ay sonra. Kümelenme gerçek gücü biraz düşürür; sayılar alt sınırdır.

5. **Piyasa karşılaştırması:** bahis oranı olan alt kümede (2021'den beri yılda ≈ 2.000 maç), vig'i ayıklanmış
   kapanış olasılıklarıyla. Piyasayı yenmek hedef değildir; aradaki fark raporlanır.

## 5. Karar kuralları

Bir bileşen (yeni model, yeni değişken, yeni parametre) ancak **aşağıdakilerin hepsi** sağlanırsa kabul edilir:

1. İç içe kayan başlangıç değerlendirmesinde birincil log loss iyileşmesinin %95 güven aralığı sıfırı içermez,
2. ortalama iyileşme **en az 0,001**dir (pratik anlamlılık eşiği; bundan küçük farklar sadelik lehine yok sayılır),
3. kalibrasyon eğimi 0,02'den fazla kötüleşmez.

Ek kurallar:

- Eşit performansta **daha az parametreli** model seçilir.
- Test edilecek hipotezler §7'de sabittir. Sonradan akla gelen her fikir "keşif" olarak etiketlenir ve
  ancak ileriye dönük testte doğrulanırsa kesinleşir.
- Kayda geçmemiş ayar denemesi yapılmaz. Her çalıştırma EXPERIMENTS.md'ye yazılır (komut, veri sürümü, parametre özeti, sonuç).

## 6. Aday modeller (önceden belirlenmiş)

| Kod | Model | Ayarlanacak parametreler | Not |
|---|---|---|---|
| M0 | Elo, sabit K | K, başlangıç puanı | Taban çizgisi |
| M1 | Glicko-1 (mevcut) | c, başlangıç RD, min RD (yok seçeneği dahil; makalede yok, bizim eklememiz) | Glickman 1999 |
| M2 | Glicko-2 | τ, başlangıç RD/oynaklık | Glickman 2001 |
| M3 | TrueSkill (yalnızca ileri geçiş) | β, τ, beraberlik payı | Herbrich vd. 2006 |

Hepsine aynı veri, aynı ilk maç kuralı ve aynı değerlendirme uygulanır. Ayar parametreleri, Glickman'ın (1999 §4) yaptığı gibi
tek adım ileri log loss toplamı en aza indirilerek seçilir (§4.2'deki iç içe düzende).

**Bilinen yaklaşım sorunu:** Glicko'nun yaklaşık filtresi dönem başına oyuncu başına 5–10 maç için önerilmiş ve en az 4 rakiple test edilmiştir.
MMA'da dövüşçü başına dönemde çoğunlukla tek maç vardır. Bu nedenle kalibrasyon birleşik RD düzeylerine göre ayrıca raporlanır (§3).

**Kapsam dışı (S1 için):** WHR ve TrueSkill Through Time gibi *yumuşatma* yöntemleri gelecekteki maçları
kullanır, dolayısıyla "o tarihte bilinen" sorusunu cevaplamaz. İleride ayrı ve açıkça etiketlenmiş bir
"geriye dönük tarihsel değerlendirme" listesi için ele alınabilir; tahmin modeli seçiminde yer almaz.

## 7. Hipotezler (ek bilgiler)

Sınama sırası aşağıdaki gibidir. Her biri, o ana kadar kabul edilmiş en iyi modele eklenerek sınanır.

| Kod | Hipotez | Sınama biçimi | Ön bulgu |
|---|---|---|---|
| H1 | Bitiş şekli (KO/SUB ve karar türü) bilgi taşır | Kesirli sonuç değerleri veya galibiyet farkı uzantısı (Kovalchik 2020); değerler veriden tahmin edilir. Kesirli sonuçlar tahmini "beklenen skor" ölçeğine kaydırdığı için, tahmin anında tek bir ölçek parametresi λ (p = lojistik(λ·Δ)) ile birlikte ve ayrı ayrı sınanır | E0.2'de "fightmatrix" şeması düz şemadan 0,0047 daha iyi (bkz. EXPERIMENTS.md) |
| H2 | İlk maç tahmini organizasyon düzeyine bağlıdır | Organizasyon önseli açık/kapalı, k ve ofset ayarı | Mevcut sistemde var, iç içe değerlendirmeyle yeniden sınanacak |
| H3 | Uzun ara performansı düşürür | Ara süresi ortalamaya etki eden değişken olarak; alternatif: yalnızca RD artışı | Yok |
| H4 | Sıklet değişimi performansı düşürür | Önceki sıkletten fark (±1, ±2+) değişken olarak | E0.1'de yukarı ve aşağı simetrik −3/−7 puan |
| H5 | Yaş performansı etkiler | İki biçim: (a) tahminde maç anındaki yaş (eğrisel) değişken olarak; (b) güç sürecinde yaşa bağlı ortalama kayma. Yalnızca doğum tarihi bilinen alt kümede; eksiklik yanlılığı raporlanır | Hakemli olmayan analizler 30'ların başından itibaren düşüş gösteriyor |
| H6 | Ev sahibi avantajı vardır | Uyruk ile etkinlik ülkesi eşleşmesi; uyruk kapsamı %51 olduğu için **keşif** düzeyinde | Yok |

## 8. Sıralama katmanı

Bu kararlar tahmin başarısıyla seçilemez. Her biri ya veriyle desteklenir ya da açıkça **politika** olarak yazılır.

| Karar | Tür | Nasıl ele alınacak |
|---|---|---|
| Liste puanı (μ − k·RD) | Politika + yorum | k'nın olasılık yorumu yazılır; alternatif: "1 numara olma olasılığı" gibi sonsal büyüklükler |
| İnaktivite | H3'e bağlı | Etki varsa modele girer; yoksa ceza kaldırılır, inaktivite yalnızca liste şartı olur |
| Liste şartları (3 maç, 24 ay, 18 ay) | Politika | Gerekçesiyle yazılır, duyarlılık gösterilir |
| Sıklet ataması | Ölçüm | Dönemlere göre tabakalı rastgele 200 dövüşçü-ay elle dış kaynaklarla kontrol edilir; doğruluk oranı güven aralığıyla raporlanır |
| P4P | Tanım | İki açık tanım: global güç ve sıklet hakimiyeti; karışım kullanılmaz |

## 9. Bilinen sınırlar

- Tarihsel dönemde temiz bir test kümesi yoktur (§4.1).
- Veri eksikliği rastgele değildir; modelin bölgesel dövüşçüler için belirsizliği raporlanandan büyük olabilir.
- Sıkletler arası karşılaştırma, sıklet değiştiren dövüşçülerin oluşturduğu bağlantılara dayanır; uzak sıkletler arasında hata birikebilir.
- Bahis piyasası, modelin göremediği bilgiyi (sakatlık, kamp, kilo verme) kullanır.
- Tarihsel değerlendirme bugünkü veri sürümüyle yapılır; sonradan eklenen maçlar ve düzeltmeler o tarihte bilinmiyordu
  (Diebold 2015 §4.2'deki "vintage" sorunu). Bu, gerçek zamanlı başarıyı olduğundan iyi gösterebilir. Kasım 2026'dan itibaren
  her ayın veri sürümü arşivleniyor; sürüm farkının etkisi ileride ölçülebilir.
- Maçlar arasındaki bağımlılık (aynı dövüşçünün farklı etkinliklerdeki maçları) kümelenmiş bootstrap ile yalnızca kısmen yakalanır.
- Eşli karşılaştırma verisi tüm havuzun ortalama düzeyindeki değişimi göremez (Glickman 1999 §5). Farklı dönemlerin puanları mutlak güç olarak
  karşılaştırılamaz; tarihsel listeler o dönemin rakiplerine görelidir.

## Değişiklik günlüğü

| Tarih | Sürüm | Değişiklik | Gerekçe |
|---|---|---|---|
| 2026-11-05 | 0.1 | İlk taslak | — |
| 2026-11-05 | 0.2 | Log skorun marjinal olabilirlik yorumu (§3); dayanıklılık kontrolleri: Brier, ay bazlı kümeleme, en kötü 50 maçın incelenmesi (§3); tam dizi log skoru raporu (§4.2); veri sürümü ve bağımlılık sınırları (§9) | Okuma oturumu 1 ([notlar](notes/oturum-1-degerlendirme.md)). Henüz hiçbir deney yapılmadı. |
| 2026-11-05 | 0.3 | M1 ayarına min RD'nin kaldırılması seçeneği ve ayar yöntemi (§6); RD bantlarına göre kalibrasyon (§3, §6); H1'e ölçek parametresi λ; H5'e iki biçim; dönemler arası karşılaştırma sınırı (§9) | Okuma oturumu 2 ([notlar](notes/oturum-2-glicko.md)). Henüz hiçbir deney yapılmadı. |
