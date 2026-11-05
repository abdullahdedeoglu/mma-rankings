# Araştırma Protokolü (ön kayıt)

**Sürüm:** 0.8 · **Tarih:** 2026-11-05 · **Durum:** taslak, deneylerden önce yazıldı

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
  5. Bitiş şekli sınıflamasında hata: "TKO (Submission to Punches)" (3.268 maç) içinde "submission" geçtiği için SUB sayılıyor.
     KO ve SUB şu an aynı değeri aldığı için dereceyi etkilemiyor; bitiş şeklini ayrı kullanan her analizden önce düzeltilir (Aşama 1).
  6. Bitiş şekli dağılımı döneme göre değişir: submission %45 (2000–09) → %30 (2020+), karar %16 → %28. Sonuç kategorilerinden
     tahmin edilen her katsayı yalnızca ilgili eğitim penceresinden hesaplanır.
  7. Sıklet bilgisi döneme göre çok farklı: erkek kararlı maçların 2000–09'da %5'inde, 2010–19'da %69'unda, 2020'den beri %89'unda
     sıklet ataması var. Ardışık maçlar arasında ağır sıklet ile sinek sıklet arasında 25 doğrudan geçiş ve 25.985 tek maçlık
     A → B → A sıklet değişimi var; bu köprülerin bir kısmı etiket gürültüsüdür (§8 sıklet denetimi).
- **Veri denetimi (Aşama 1):** ayrıntılar ve yeniden üretme komutu [AUDIT.md](AUDIT.md) dosyasında. Bu bölümü etkileyen bulgular:
  1. 3+ sıklet atlayan ardışık geçişlerin pilot incelemesinde 8/8'i tek maçlık etiket tutarsızlığı çıktı; kimlik birleşmesi bulunmadı.
  2. Derecelendirilen maçların 15.231'inde (%4,2) iki tarafın da cinsiyeti bilinmiyor; bu maçlar erkek popülasyonunun dışında kalır.
     Kayıp rastgele değildir (rakip ağına az bağlı dövüşçüler).
  3. Doğum tarihine göre 16 yaşından küçük ya da 55 yaşından büyük görünen maçlar (384) doğum tarihi hatası sayılır.
  4. 11.045 maçın profesyonelliği kaynakta kontrol edilmemiş; birincil karşılaştırmalar bu maçlar çıkarılarak bir kez de tekrarlanır
     (duyarlılık analizi).
  5. "Vuruşlara teslim olma" (6.062 maç) araştırma kodunda KO/TKO olarak sınıflanır.
  6. Sıklet denetimi (§8): maç etiketleri Tapology ile %89,3 uyumlu (109/122; %95 GA %82,5–94,2), uyumsuzlukların çoğu komşu sıklet;
     örneklemin %39'u doğrulanamadı.
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
- **Beraberliği modelleyen modeller** (M3, M4) üç sonuç için olasılık üretir. İkili log loss için kazanma olasılığı, beraberlik dışı sonuçlara
  koşullandırılır: P(A kazanır) / (P(A kazanır) + P(B kazanır)). Böylece tüm modeller aynı olay üzerinden karşılaştırılır.
- **Havuz düzeyi tanısı:** En az 3 maçlı aktif dövüşçülerin ortalama puanı her model için zaman içinde çizilir. Yeni dövüşçülerin
  sistematik kaybı havuzu aşağı kaydırabilir (Herbrich vd. 2006, §4.2); bu, ilk maç önselinin (H2) yan etkisi olarak izlenir.
- **Sıkletler arası kalibrasyon tanısı:** Asıl sıkletleri (en çok maç yaptıkları sıklet, yalnızca o ana kadarki maçlarla) farklı iki
  dövüşçünün maçlarında kalibrasyon kesişimi ve eğimi, sıklet çiftine ve yöne göre (daha ağır sıkletten gelen taraf açısından) raporlanır.
  Sıklet düzeyleri doğru tahmin ediliyorsa sistematik sapma beklenmez. Bu, "global güç" P4P tanımının (§8) geçerlilik ölçüsüdür;
  Batterham & George (1997)'nin vücut kütlesine göre artık incelemesinin bizdeki karşılığıdır.

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
| M3 | TrueSkill (yalnızca ileri geçiş) | β, γ (geçen zamana bağlı, maç başına değil), beraberlik payı | Herbrich vd. 2006 |
| M4 | TrueSkill Through Time, yalnızca *t* öncesi verilerle (her gün veri eklenip tek tur güncellenir) | önsel belirsizlik, γ, beraberlik olasılığı | Landfried & Mocskos 2025 |

Hepsine aynı veri, aynı ilk maç kuralı ve aynı değerlendirme uygulanır. Ayar parametreleri, Glickman'ın (1999 §4) yaptığı gibi
tek adım ileri log loss toplamı en aza indirilerek seçilir (§4.2'deki iç içe düzende).

**Tahmin anı ölçeği:** Puanlar gürültülü tahminler olduğu için, puanı üreten modelin ölçeğiyle hesaplanan olasılıklar tahmin gücünü
abartabilir (Szczecinski 2026, hakemli değil). Bu nedenle her model iki biçimde raporlanır: olasılık modelin kendi formülüyle ve
eğitim penceresinde tahmin edilen tek bir ölçek parametresiyle (p = lojistik(λ·Δ), Glicko'da g(RD) korunarak). λ bir parametre sayılır.
Eğitim penceresindeki λ, yakınsama tanısı olarak da raporlanır: tahmin gürültüsü tek başına λ'yı 1'in altına çeker; λ'nın 1'in üzerinde
çıkması puan farklarının "sıkışık" kaldığına, yani puanların henüz yakınsamadığına işaret eder.

**Bilinen yaklaşım sorunu:** Glicko'nun yaklaşık filtresi dönem başına oyuncu başına 5–10 maç için önerilmiş ve en az 4 rakiple test edilmiştir.
MMA'da dövüşçü başına dönemde çoğunlukla tek maç vardır. Bu nedenle kalibrasyon birleşik RD düzeylerine göre ayrıca raporlanır (§3).

**Bilgi kümesi kuralı:** Sızıntıyı belirleyen algoritma değil, kullanılan bilgidir. Geçmişin tamamını yeniden tahmin eden yöntemler
(WHR, TTT) yalnızca *t* anından önceki maçlarla çalıştırıldığında geleceği kullanmaz ve S1'e dahildir; Coulom (2008) ve
Landfried & Mocskos (2025) tahminlerini böyle değerlendirmiştir. Ay *m*'nin listesi, bu modellerde de yalnızca *m* sonuna kadarki
maçlarla üretilir. Tüm veriyle (gelecek dahil) yapılan tam yumuşatma S1'in dışındadır; ileride ayrı ve açıkça etiketlenmiş bir
"bugünkü bilgiyle geçmiş" görünümü olarak sunulabilir. WHR, M4 ile aynı modelin başka bir çözümü olduğundan ayrıca aday yapılmamıştır.

**M4 fizibilitesi:** M4'ün tam veri üzerindeki çalışma süresi önce bir pilotla ölçülür. Pilot yalnızca süreyi ölçer, tahmin başarısına bakılmaz;
EXPERIMENTS.md'ye "fizibilite" olarak kaydedilir. Süre makul değilse M4'ün nasıl yaklaşıklanacağı bu belgeye bir değişiklik olarak yazılır.

## 7. Hipotezler (ek bilgiler)

Sınama sırası aşağıdaki gibidir. Her biri, o ana kadar kabul edilmiş en iyi modele eklenerek sınanır.

| Kod | Hipotez | Sınama biçimi | Ön bulgu |
|---|---|---|---|
| H1a | Bitiş şekli bilgi taşır: kesirli skor biçimi | Kesirli sonuç değerleri (bitiş / oybirliği / split-majority / türü belirtilmemiş karar) eğitim penceresinde ayarlanır; tahminde λ (§6) ile birlikte. Kesirli skorlar tahmini "beklenen skor" ölçeğine kaydırdığı için λ'sız sürüm ayrıca raporlanır | E0.2'de "fightmatrix" şeması düz şemadan 0,0047 daha iyi (bkz. EXPERIMENTS.md) |
| H1b | Bitiş şekli bilgi taşır: sıralı model biçimi | Komşu kategoriler (AC) modeli, G-Elo türü (Szczecinski 2022). Kategoriler: bitiş (KO/TKO + SUB), oybirliği karar, split/majority karar; her biri iki yön için. Türü belirtilmemiş karar "herhangi bir karar" olarak olasılıkların toplamıyla girer. Katsayılar her eğitim penceresinde sıklıklardan hesaplanır. KO ile SUB ayrımı bir fark ölçüsü sayılmaz ve dahil edilmez | G-Elo'nun futbolda kazancı 0,006–0,008 nat/maç; MMA'da split/majority kararlar maçların yalnızca %4,4'ü |
| H2 | İlk maç tahmini organizasyon düzeyine bağlıdır | Organizasyon önseli açık/kapalı, k ve ofset ayarı | Mevcut sistemde var, iç içe değerlendirmeyle yeniden sınanacak |
| H3 | Uzun ara performansı düşürür | Ara süresi ortalamaya etki eden değişken olarak; alternatif: yalnızca RD artışı | Yok |
| H4 | Sıklet değişimi performansı düşürür | Önceki sıkletten fark (±1, ±2+) değişken olarak. Tek maç etiketleri gürültülü olduğu için (AUDIT.md §5) değişken yalnızca geçmiş bilgiyle tanımlanır: maçın etiketi ile dövüşçünün **yerleşik sıkleti** (önceki son 3 etiketli maçının çoğunluğu) arasındaki fark. 3 ve daha fazla sıklet farkı büyük olasılıkla etiket hatası olduğundan eksik sayılır. Sonraki maçlara bakarak "kalıcı değişim" tanımlamak geleceği kullanır; yalnızca betimsel analizde kullanılabilir. Etiketlerin yaklaşık %10'u komşu sıklete kaydığı için (AUDIT.md §7) ölçüm hatası etkiyi sıfıra doğru küçültür; tahmin bir alt sınır olarak yorumlanır. Sıklet değişimi yaş ve kariyer evresiyle karışır (Berry vd. 1999); H5 kabul edilirse H4 yaş kontrol edilerek yeniden raporlanır | E0.1'de yukarı ve aşağı simetrik −3/−7 puan |
| H5 | Yaş performansı etkiler | İki biçim: (a) tahminde maç anındaki yaş (eğrisel) değişken olarak; (b) güç sürecinde yaşa bağlı ortalama kayma. Yalnızca doğum tarihi bilinen alt kümede; eksiklik yanlılığı raporlanır. 16 yaşından küçük ya da 55'ten büyük yaşlar doğum tarihi hatası sayılıp dışarıda bırakılır | Hakemli olmayan analizler 30'ların başından itibaren düşüş gösteriyor |
| H6 | Ev sahibi avantajı vardır | Uyruk ile etkinlik ülkesi eşleşmesi; uyruk kapsamı %51 olduğu için **keşif** düzeyinde | Yok |
| H7 | DQ sonucu güç hakkında bilgi taşımaz | DQ'yu yok saymak (mevcut kural) ile normal galibiyet saymak karşılaştırılır; 1.787 maç (%0,5), **keşif** düzeyinde | Holmes vd. (2023) DQ'yu "bilgisiz sonuç" sayıyor |
| H8 | Her sıklete yeni gelenlerin ortalama gücü farklıdır | İlk maç önselinin ortalaması sıklete göre ayrı tahmin edilir (eğitim penceresinde); ortak önsel (mevcut) ile karşılaştırılır. Berry vd. (1999)'un döneme özgü hiyerarşik dağılımlarının karşılığı. Bu düzeyler yalnızca sıklet değiştirenler üzerinden tanımlıdır | Yok; ortak önsel şu an yazılı olmayan bir varsayım |

H1a ve H1b birbirinin alternatifidir; ikisi de kabul ölçütünü geçerse daha az parametreli olan seçilir (§5). İkisi de birincil hedefte
(kararlı maçlarda ikili log loss) ölçülür: zengin sonuç modeli, mevcut modelle aynı soru üzerinde karşılaştırılır.

## 8. Sıralama katmanı

Bu kararlar tahmin başarısıyla seçilemez. Her biri ya veriyle desteklenir ya da açıkça **politika** olarak yazılır.

| Karar | Tür | Nasıl ele alınacak |
|---|---|---|
| Liste puanı (μ − k·RD) | Politika + yorum | k'nın olasılık yorumu yazılır; alternatif: "1 numara olma olasılığı" gibi sonsal büyüklükler |
| İnaktivite | H3'e bağlı | Etki varsa modele girer; yoksa ceza kaldırılır, inaktivite yalnızca liste şartı olur |
| Liste şartları (3 maç, 24 ay, 18 ay) | Politika | Gerekçesiyle yazılır, duyarlılık gösterilir |
| Sıklet ataması | Ölçüm | Dönemlere göre tabakalı rastgele 200 dövüşçü-ay elle dış kaynaklarla kontrol edilir (örneklem: AUDIT.md §7). Maç etiketleri büyük olasılıkla Sherdog'dan geldiği için doğrulama Sherdog dışı bir kaynakla yapılır (Tapology, organizasyon sayfası, Wikipedia). Sıralama katmanında dövüşçünün sıkleti tek maçın etiketiyle değil, son etiketli maçlarının çoğunluğuyla belirlenir; doğruluk oranı güven aralığıyla raporlanır. Ayrıca uzak sıkletler arasındaki (iki ve daha fazla sıklet atlayan) tüm ardışık geçişler ayrı bir örneklemle incelenir |
| Sıklet listeleri (2010 öncesi) | Veri yeterliliği | Sıklet bilgisi bu dönemde maçların %5'inde var; sıklet listeleri ve sıklet hakimiyeti P4P'si 2010 öncesi için üretilmez ya da "yetersiz veri" olarak işaretlenir |
| P4P | Tanım | İki açık tanım: global güç ve sıklet hakimiyeti; karışım kullanılmaz. Global güç listesi varsayımlarıyla (bağlantı, ortak ya da H8'deki önsel, etkileşim yok) ve sıkletler arası kalibrasyon tanısının (§3) sonucuyla birlikte yayımlanır. Vücut ağırlığına dayalı bir düzeltme formülü kullanılmaz (Batterham & George 1997; Vanderburgh & Batterham 1999) |

## 9. Bilinen sınırlar

- Tarihsel dönemde temiz bir test kümesi yoktur (§4.1).
- Veri eksikliği rastgele değildir; modelin bölgesel dövüşçüler için belirsizliği raporlanandan büyük olabilir.
- Sıkletler arası karşılaştırma, sıklet değiştiren dövüşçülerin oluşturduğu bağlantılara dayanır; uzak sıkletler arasında hata birikebilir.
  Bağlantı grafiği Ford (1957) şartını sağlasa da, bağlantı zayıf olan yerlerde sıkletlerin göreli düzeyi veriden çok ilk maç önselinden gelir.
  Model "etkileşim yok" varsayar (Berry vd. 1999): bir dövüşçünün göreli gücü, ortalama bir sıklet değişimi etkisi dışında her sıklette aynıdır.
  Boyut ile stil arasındaki etkileşimler modellenmez. Sıklet değiştiren dövüşçüler rastgele seçilmez (kayıp serisi, yaş, kilo verme zorluğu).
  "Global güç" listesi, iki dövüşçünün belirli bir kiloda karşılaşması halinde ne olacağını söylemez; yalnızca gözlenen sıkletler arası
  maçlara dayanan ortak bir ölçek tanımlar.
- Bahis piyasası, modelin göremediği bilgiyi (sakatlık, kamp, kilo verme) kullanır.
- Maç içi istatistikler (vuruş, takedown, kontrol süresi) maçların yalnızca %4,3'ünde var ve büyük organizasyonlarda yoğunlaşır.
  Holmes vd. (2023) türü beceri modelleri bu yüzden S1'in dışındadır; ileride yalnızca UFC alt kümesinde keşif olarak denenebilir.
- Tarihsel değerlendirme bugünkü veri sürümüyle yapılır; sonradan eklenen maçlar ve düzeltmeler o tarihte bilinmiyordu
  (Diebold 2015 §4.2'deki "vintage" sorunu). Bu, gerçek zamanlı başarıyı olduğundan iyi gösterebilir. Kasım 2026'dan itibaren
  her ayın veri sürümü arşivleniyor; sürüm farkının etkisi ileride ölçülebilir.
- Maçlar arasındaki bağımlılık (aynı dövüşçünün farklı etkinliklerdeki maçları) kümelenmiş bootstrap ile yalnızca kısmen yakalanır.
- Eşli karşılaştırma verisi tüm havuzun ortalama düzeyindeki değişimi göremez (Glickman 1999 §5). Farklı dönemlerin puanları mutlak güç olarak
  karşılaştırılamaz; tarihsel listeler o dönemin rakiplerine görelidir. Yumuşatma modellerinin (TTT) "dönemler arası karşılaştırılabilirlik"
  iddiası, her dövüşçünün gücünün yavaş ve bağımsız değiştiği varsayımına dayanır; havuz düzeyindeki ortak kaymayı veriden ölçmez.

## Değişiklik günlüğü

| Tarih | Sürüm | Değişiklik | Gerekçe |
|---|---|---|---|
| 2026-11-05 | 0.1 | İlk taslak | — |
| 2026-11-05 | 0.2 | Log skorun marjinal olabilirlik yorumu (§3); dayanıklılık kontrolleri: Brier, ay bazlı kümeleme, en kötü 50 maçın incelenmesi (§3); tam dizi log skoru raporu (§4.2); veri sürümü ve bağımlılık sınırları (§9) | Okuma oturumu 1 ([notlar](notes/oturum-1-degerlendirme.md)). Henüz hiçbir deney yapılmadı. |
| 2026-11-05 | 0.3 | M1 ayarına min RD'nin kaldırılması seçeneği ve ayar yöntemi (§6); RD bantlarına göre kalibrasyon (§3, §6); H1'e ölçek parametresi λ; H5'e iki biçim; dönemler arası karşılaştırma sınırı (§9) | Okuma oturumu 2 ([notlar](notes/oturum-2-glicko.md)). Henüz hiçbir deney yapılmadı. |
| 2026-11-05 | 0.4 | S1'den dışlama kuralı yerine bilgi kümesi kuralı; M4 (TTT, yalnızca geçmiş veriyle) ve fizibilite pilotu (§6); M3'te zamana bağlı γ; üç sonuçlu modellerde ikili log loss tanımı ve havuz düzeyi tanısı (§3); yumuşatmanın karşılaştırılabilirlik iddiasının sınırı (§9) | Okuma oturumu 3 ([notlar](notes/oturum-3-alternatif-modeller.md)). 0.3'teki dışlama gerekçesi yanlıştı: Coulom ve Landfried & Mocskos bu modelleri yalnızca geçmiş veriyle değerlendirmiş. Henüz hiçbir deney yapılmadı. |
| 2026-11-05 | 0.5 | Bitiş şekli sınıflama hatası ve dönemsel dağılım (§2); her model için tahmin anı ölçeği λ ve yakınsama tanısı (§6); H1'in H1a (kesirli skor + λ) ve H1b (sıralı AC modeli, kategoriler sabitlendi) olarak ayrılması; H7 (DQ kuralı, keşif) (§7); maç içi istatistik kapsamı sınırı (§9) | Okuma oturumu 4 ([notlar](notes/oturum-4-galibiyet-farki-mma.md)). Kovalchik 2020 ve Hvattum & Arntzen 2010 yalnızca özetten okundu; λ önerisinin dayanağı hakemli olmayan bir ön baskı (Szczecinski 2026). Henüz hiçbir deney yapılmadı. |
| 2026-11-05 | 0.6 | Sıklet bilgisinin dönemsel kapsamı ve uç sıklet geçişleri (§2); sıkletler arası kalibrasyon tanısı (§3); H8 (sıklete özgü ilk maç önseli) ve H4'e yaş karıştırıcısı notu (§7); P4P varsayımlarıyla yayım, ağırlık formülü yok, 2010 öncesi sıklet listeleri kuralı, uzak geçişlerin denetimi (§8); etkileşim yok varsayımı ve önselin sıklet düzeylerine etkisi (§9) | Okuma oturumu 5 ([notlar](notes/oturum-5-gruplar-arasi-p4p.md)). Ford 1957'nin orijinali okunmadı (sonuç Yan 2014'ten); Batterham & George ve Vanderburgh & Batterham yalnızca özetten. Henüz hiçbir deney yapılmadı. |
| 2026-11-05 | 0.7 | Veri denetimi bulguları (§2); H4'te yalnızca geçmiş bilgiyle tanımlanan yerleşik sıklet ve 3+ sıklet farkının eksik sayılması; H5'te yaş aralığı kuralı; sıklet denetiminde bağımsız kaynak şartı (§8) | Aşama 1 veri denetimi ([AUDIT.md](AUDIT.md)). Yalnızca betimsel sayılar görüldü; henüz hiçbir model sonucu görülmedi. |
| 2026-11-05 | 0.8 | Sıklet denetimi sonucu (§2); H4'te ölçüm hatası yorumu (§7) | 200 dövüşçü-aylık sıklet denetimi Tapology ile yapıldı (AUDIT.md §7). Karşılaştırma kuralı sonuçlar okunmadan sabitlendi. Henüz hiçbir model sonucu görülmedi. |
