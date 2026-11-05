# Okuma oturumu 4: Galibiyet farkı ve MMA'ya özgü bilgi

**Tarih:** 2026-11-05 · **İlgili:** [PROTOCOL.md](../PROTOCOL.md) §2, §6, §7 (H1, H7), §9 · [LITERATURE.md](../LITERATURE.md)

| Kaynak | Ne kadarı okundu |
|---|---|
| Kovalchik (2020), "Extension of the Elo rating system to margin of victory", *IJF* 36(4) | **Yalnızca özet** ([EconPapers](https://econpapers.repec.org/RePEc:eee:intfor:v:36:y:2020:i:4:p:1329-1341)) ve ikincil kaynaklar. Tam metin ücretli. |
| Hvattum & Arntzen (2010), "Using ELO ratings for match result prediction in association football", *IJF* 26(3) | **Yalnızca özet** ([EconPapers](https://econpapers.repec.org/RePEc:eee:intfor:v:26:y::i:3:p:460-470)). Tam metin ücretli. |
| Szczecinski (2022), "G-Elo: Generalization of the Elo algorithm by modeling the discretized margin of victory", *JQAS* | Tam metin ([arXiv 2010.11187v3](https://arxiv.org/abs/2010.11187)) |
| Szczecinski (2026), "New insights into Elo algorithm for practitioners and statisticians" | Ana bölümler ve sonuç ([arXiv 2604.03840](https://arxiv.org/abs/2604.03840)). **Hakemli değil** (ön baskı). |
| Holmes, McHale & Żychaluk (2023), "A Markov chain model for forecasting results of mixed martial arts contests", *IJF* 39(2) | Tam metin (kabul edilmiş makale) |

---

## 1. Galibiyet farkı: üç yaklaşım

Szczecinski (2022, §1.1) literatürü üç gruba ayırıyor. Bizim mevcut sistemimizin hangi gruba düştüğünü görmek önemli:

1. **Farkı doğrudan modellemek** (örneğin skor farkına normal ya da Skellam dağılımı). MMA'da sayısal bir skor farkı yok; bu yol bize uymuyor.
2. **Farkı sıralı kategorilere ayırmak** ve kategorilerin olasılığını güç farkına bağlayan bir model kurmak (G-Elo).
3. **Elo'yu farka göre ayarlamak:** güncelleme büyüklüğünü (K) ya da skoru farka göre değiştirmek. Hvattum & Arntzen (2010) ve Kovalchik (2020) bu grupta.
   Szczecinski bu yaklaşımları, açık bir olasılık modeline dayanmadıkları için **sezgisel (heuristic)** olarak sınıflıyor.

**Bizim KO 1,0 / UD 0,9 / SD 0,55 değerlerimiz 3. gruba giriyor:** sonucu kesirli bir skora çeviriyoruz, ama bu skorların hangi olasılık
modelinden geldiği tanımlı değil.

### Kovalchik (2020), özetten

- Dört varyant: doğrusal, ortak toplamsal (joint additive), çarpımsal ve lojistik. Tenis verisi, birkaç farklı fark tanımı.
- Set içi istatistik kullanan tüm fark yaklaşımları standart Elo'dan daha iyi tahmin etmiş.
- Simülasyonda **yalnızca ortak toplamsal model** yansız ve varyansı kararlı puanlar üretmiş.
- Varyantların formüllerini tam metin olmadan doğrulayamadım. Yazarın R paketi `elomov` bu dört varyantı uyguluyor; gerekirse kaynak kodundan okunabilir.

### Hvattum & Arntzen (2010), özetten

Elo puanlarından türetilen değişkenler sıralı lojit modele giriyor ve altı başka yöntemle, hem istatistiksel hem ekonomik ölçütlerle karşılaştırılıyor.
Özet sonuç vermiyor. Szczecinski'ye göre bu çalışma da K'yı gol farkına bağlıyor. Bu kaynağı protokolde bir karara dayanak yapmıyorum.

## 2. G-Elo (Szczecinski 2022): farkın ilkeli modeli

### Model

Sonuç sıralı kategorilere ayrılıyor (örneğin büyük mağlubiyet, küçük mağlubiyet, beraberlik, küçük galibiyet, büyük galibiyet).
Her kategorinin olasılığı **komşu kategoriler (adjacent categories, AC)** modeliyle güç farkına bağlanıyor:

`P(Y = h | z) ∝ 10^(α_h + δ_h · z/σ)`

- İki kategorinin olasılık oranının logaritması, güç farkıyla **doğrusal** artıyor.
- Standart Elo (ve beraberlikli Elo-Davidson), bu modelin üç kategorili özel hali.
- Güncelleme kuralı Elo ile **aynı biçimde**: `θ ← θ + K·(skor − beklenen skor)`. Yalnızca skor ve beklenen skorun tanımı değişiyor.
  Skor `δ_y` oluyor, beklenen skor ise modelin verdiği ağırlıklı ortalama.
- Katsayılar (α, δ) eğitim verisindeki **kategori sıklıklarından kapalı formda** hesaplanabiliyor. Optimizasyonla da bulunabiliyor;
  sıklık yöntemi test verisinde biraz daha iyi genellemiş (yazarın tahmini: optimizasyon aşırı uyuyor).

### Sonuçlar

Değerlendirme log skor, RPS ve doğruluk ile yapılıyor; tahmin her zaman **aynı üç sonuçlu hedefe** (ev/beraberlik/deplasman) indirgeniyor.
Bu doğru bir karşılaştırma: daha zengin model, daha fakir modelle aynı soru üzerinde ölçülüyor.

| Lig | Elo-Davidson (J = 2) | En iyi G-Elo | Fark (nat/maç) |
|---|---|---|---|
| EPL | 0,9740 | 0,9679 | −0,006 |
| NFL | 0,6304 | 0,6223 | −0,008 |

- Kazanç küçük ama yazar bunu "eğitimde artan uyum testte de iyileşme getirdi" diye yorumluyor.
- **Güven aralığı ya da anlamlılık testi yok.** Birkaç sezon üzerinden tek bir ortalama.
- EPL'de log skor iyileşirken **doğruluk düşüyor** (0,544 → 0,539). Oturum 1'deki sonucun bir örneği daha: doğruluk ve uygun skorlama kuralları ayrışabilir.
- Eşik (Δ) seçimi sonucu etkiliyor ve yazar "eşik ve katsayıları belirlemenin sağlam yolu için daha fazla araştırma gerekli" diyor.

## 3. Szczecinski (2026): sıralama modeli ile tahmin modelini ayırmak

Bu makale hakemli değil; bulgularını yöntem fikri olarak kullanıyorum, kanıt olarak değil.

- **İkili sonuçta:** Elo güncellemesi ile "stokastik gradyanla en çok olabilirlik" ancak beklenen skor lojistik olduğunda örtüşüyor.
- **Tahmin gürültüsü ölçeği değiştirir:** Puanlar gürültülü tahminler olduğu için, aynı ölçekle (s) olasılık hesaplamak modelin
  **tahmin gücünü abartır**. Tahminde kullanılacak etkin ölçek `ŝ = s·β` eğitim verisinden ayrıca tahmin edilmeli. Glicko'nun `g(RD)` terimi
  bu düzeltmenin model içi bir biçimi; Szczecinski ayrıca bunun yalnızca tahmin gürültüsüne değil, güçlerin dağılımına da bağlı olduğunu gösteriyor.
- **Yakınsama tanısı:** Maç sıklığı düşük olduğunda puanlar henüz yakınsamamış ve "sıkışık" kalır. O zaman tahmin edilen β, gürültü düzeltmesinin
  beklediği değerin **altına** düşer. FIFA verisinde takımların çoğunun puanı altı yılda yakınsamamış. MMA'da maç sıklığı FIFA'dan da düşük.
- **Kesirli skorlar:** Çok kategorili sonuçta, eşit aralıklı skorlar kullanan Elo, örtük bir AC modeline karşılık geliyor. Eşit aralıklı olmayan
  skorlarda (bizim 1,0/0,9/0,55 gibi) bu yalnızca yaklaşık. Öneri: puanları istediğin kuralla üret, ama **tahmin için** AC katsayılarını ve
  ölçeği (α̂, β̂) eğitim verisinden ayrıca tahmin et. Sentetik örnekte en önemli parametre β̂ çıkmış.

Bu, 2. oturumda protokole eklediğimiz **tahmin anı ölçek parametresi λ** fikrinin aynısı (λ = 1/β). Fark şu: Szczecinski bunu yalnızca kesirli
sonuçlara değil, **her modele** uygulanması gereken genel bir düzeltme olarak görüyor.

## 4. Holmes, McHale & Żychaluk (2023): MMA'da tahmin

### Ne yapıyorlar?

- **Veri:** UFC 2001–2018, 4.678 maç, 1.680 dövüşçü (ESPN ve UFCStats'tan kazınmış). Eğitim 2001–2017, test 2018.
  Test kümesi: ilk UFC maçına çıkanlar ve sonradan NC sayılanlar çıkarılınca **327 maç**.
- **Model:** 13 ayrı beceri modeli (vuruş hızı, isabet, nakavt/knockdown olasılığı, takedown, yerde kontrol süresi, submission). Her birinde
  saldırı ve savunma parametresi ve sıklet etkisi var; zayıf bilgilendirici önsellerle Bayesçi GLM. Bu beceriler saniye adımlı bir Markov
  zincirinin geçiş olasılıklarını belirliyor; her maç 10.000 kez simüle ediliyor. Karara giden maçlar için raunt düzeyinde bir hakem modeli var.
- **Karşılaştırma modelleri:** statik Bayesçi Bradley–Terry (zaman dinamiği yok, 2001–2017'ye tek sefer uyduruluyor) ve kümülatif istatistiklerle
  lojistik regresyon.

### Sonuçlar ve değerlendirme

| Model | Doğruluk (2018, n = 327) |
|---|---|
| Markov zinciri | %61,8 |
| Bahis piyasası | %61,2 (aynı alt küme) |
| Bradley–Terry | %54,1 |
| Lojistik regresyon | %47,7 |

Ayrıca sonuç ve yöntem pazarlarında bahis stratejileriyle pozitif getiri raporlanıyor.

**Eleştirel değerlendirme:**

- **Tek ölçüt doğruluk.** Log loss, Brier ya da kalibrasyon raporlanmıyor. Ayar parametreleri de (adj_ko, adj_sm, BT önseli) 2017 doğrulama
  yılında doğruluğa göre seçilmiş.
- **Belirsizlik yanlış kaynaktan ölçülüyor.** Raporlanan standart sapma (0,53 puan) yalnızca simülasyon tekrarlarından geliyor. Maçların
  örneklem değişkenliği hesaba katılmamış: 327 maçta %60 civarı bir doğruluğun standart hatası yaklaşık **2,7 puan**. Markov modeli ile piyasa
  arasındaki 0,6 puanlık fark bu belirsizliğin çok içinde.
- **Zayıf karşılaştırma modelleri.** Statik BT, 17 yıllık güçleri sabit sayıyor; lojistik regresyonun şans düzeyinin altında kalması bir sorun
  işareti. Dinamik bir derecelendirme modeliyle (Elo/Glicko) karşılaştırma yok. Yazarlar BT'nin şansa yakın sonucunu "UFC eşleştirmesi dengeli"
  diye yorumluyor; aynı veri dinamik modelin eksikliğiyle de açıklanabilir.
- **Bahis getirisi** tek yıl ve birkaç yüz bahisle, eşik doğrulama yılında seçilmiş; güven aralığı yok. Piyasayı yendiklerine dair kanıt zayıf.

### Bizim için kullanışlı olanlar

- **MMA tahmininin zorlukları** açık bir listeyle yazılmış: seyrek ve düzensiz maç aralıkları, stil eşleşmeleri (geçişsizlik), bağlantısı zayıf
  karşılaştırma ağı, ikili olmayan sonuçlar, "tek yumrukla kazanma" gürültüsü.
- **Bilgisiz ya da tartışmalı sonuçlar:** 2001–2018 UFC'de 13 DQ, 49 NC, 454 split ve 32 majority karar, 27 majority/split beraberlik:
  maçların **%12,3'ü**. Yazarlar ayrıca Jon Jones'un tek mağlubiyetinin, maça hükmettiği halde aldığı bir DQ olduğunu ve BT gibi modellerin bu
  bağlamı göremediğini not ediyor.
- **Hakem modeli:** raunt kazanma olasılığı, vuruş, takedown ve submission denemesi farklarıyla lojit (sabit terim yok). Split kararın
  "gürültülü sonuç" olduğu fikrine nicel destek.
- **Piyasa karşılaştırması:** vig'i ayıklanmış kapanış oranları; sonuç pazarında ortalama marj %4,25. Protokol §4.3'teki yöntemle aynı.

## 5. Bizim veriyle hızlı bakış (betimsel, tahmin yok)

Dondurulmuş veri sürümünde (`db-2026-11-04-1837`) galibi olan 365.635 maçın bitiş şekli (sınıflandırma `src/mmarank/methods.py`):

| Kategori | Pay | 2000–09 | 2010–19 | 2020+ |
|---|---|---|---|---|
| Submission | %37,5 | %45,1 | %37,8 | %30,4 |
| KO/TKO | %37,4 | %34,6 | %37,1 | %40,8 |
| Oybirliği karar | %18,6 | %12,5 | %19,1 | %22,7 |
| Split karar | %3,6 | %2,3 | %3,8 | %4,3 |
| Karar, türü belirtilmemiş | %0,9 | %2,2 | %0,5 | %0,6 |
| Majority karar | %0,8 | %1,1 | %0,9 | %0,6 |
| DQ | %0,5 | %0,6 | %0,5 | %0,5 |

Çıkarımlar:

1. **Bitiş şekli dağılımı döneme göre belirgin değişiyor** (submission %45 → %30, karar %16 → %28). Sıklık temelli kategori katsayıları
   sabit alınamaz; iç içe düzende her eğitim penceresinde yeniden hesaplanmalı.
2. Split ve majority kararlar toplam %4,4. H1'in kazancının büyük kısmı bu az sayıdaki maçtan gelmek zorunda. Beklenen etki küçük.
3. **Ölçüm hatası bulundu:** `classify` fonksiyonu "TKO (Submission to Punches)" ifadesini, içinde "submission" geçtiği için **SUB** olarak
   sınıflıyor. Bu, aslında TKO olan **3.268** maç. Şu an KO ve SUB aynı değeri (1,0) aldığı için dereceyi etkilemiyor; ama bitiş şeklini ayrı
   kullanacak her analiz için düzeltilmeli. Aşama 1'de ele alınacak.
4. **Maç içi istatistik kapsamı:** `round_stats` tablosunda 372.990 maçın yalnızca **16.080'i (%4,3)** var; bunların 8.961'i UFC.
   Holmes tipi bir model ancak bu alt kümede kurulabilir.

---

## Bizim için anlamı

1. **Kesirli sonuçlarımız sezgisel bir yöntem; bu bir hata değil ama ilkeli alternatifi var.** H1 artık iki ayrı biçimde sınanacak:
   - **H1a:** kesirli skorlar (değerler eğitim verisinden ayarlanır) ve tahminde ayrıca tahmin edilen ölçek λ. Szczecinski'nin "ayrık modeller" önerisi.
   - **H1b:** sıralı AC modeli (G-Elo türü). Kategoriler **şimdi** sabitleniyor: bitiş (KO/TKO + SUB), oybirliği karar, split/majority karar.
     Türü belirtilmemiş kararlar "herhangi bir karar" olarak olasılıkların toplamıyla olabilirliğe girer. Katsayılar her eğitim penceresinde
     sıklıklardan hesaplanır.
   - İkisi de mevcut birincil hedefte (kararlı maçlarda ikili log loss) ölçülür; G-Elo'nun yaptığı gibi zengin model fakir hedefte sınanır.
   - KO ile SUB'ı ayırmak bir "fark" ölçüsü değil, bir stil ayrımı. H1'e dahil edilmiyor.
2. **Tahmin anı ölçeği her modele uygulanır.** λ yalnızca H1'in parçası değil; §6'daki her model için eğitim penceresinde tahmin edilen bir
   seçenek olarak raporlanır (bir parametre sayılır). Test dönemindeki kalibrasyon eğimi aynı büyüklüğün dışarıdan ölçümü olarak kalır.
   Szczecinski'ye göre β'nın beklenenin altına düşmesi yakınsamamış puanlara işaret ediyor; MMA'da bunu tanı olarak raporlamak yararlı.
3. **DQ kuralı bir varsayım.** Şu an DQ dereceyi değiştirmiyor. Bu makul ama sınanmamış bir seçim. Yeni bir keşif hipotezi (H7) olarak:
   DQ'yu yok saymak ile normal galibiyet saymak karşılaştırılır (1.787 maç, %0,5; etkisi küçük olacak).
4. **Maç içi istatistikler S1'in dışında kalıyor.** Kapsam %4,3 ve büyük organizasyonlarda yoğunlaşıyor; tüm havuz için kullanılamaz. Holmes'un
   değerlendirmesi de bu yolun dinamik bir derecelendirme modelini geçtiğini göstermiyor. İleride yalnızca UFC alt kümesinde bir keşif olabilir.
5. **Holmes'tan alınan ders yöntemsel:** 327 maçlık bir test kümesi ve yalnızca doğrulukla, gerçek farklar görülemez. Bizim protokoldeki güç
   analizi (§4.3) ve maç örnekleminden gelen bootstrap belirsizliği tam olarak bu sorunu önlemek için var.

## Protokole etkisi

Protokol 0.5 sürümüne güncellendi (bkz. PROTOCOL.md değişiklik günlüğü):

1. §2'ye ölçüm sorunu olarak "TKO (Submission to Punches)" yanlış sınıflaması ve bitiş şekli dağılımının dönemsel değişimi eklendi.
2. §6'ya, her model için eğitim penceresinde tahmin edilen tahmin anı ölçeği λ eklendi.
3. §7'de H1, H1a (kesirli skor + λ) ve H1b (sıralı AC modeli, kategoriler sabitlendi) olarak ikiye ayrıldı.
4. §7'ye H7 (DQ kuralı, keşif) eklendi.
5. §9'a, maç içi istatistiklerin kapsam sınırı eklendi.

## Açık sorular

- Kovalchik'in dört varyantının formülleri ve "yalnızca ortak toplamsal model yansız" bulgusunun nedeni (tam metin ya da `elomov` kaynağı gerekir).
- AC modelinin kategori katsayıları sıklete göre değişmeli mi? (Holmes'a göre ağır sıkletlerde nakavt oranı daha yüksek.) Şimdilik **keşif**.
- AC modeli Glicko'nun Bayesçi güncellemesiyle nasıl birleşir? G-Elo bir Elo (stokastik gradyan) algoritması. Glicko/TrueSkill içinde çok kategorili
  olabilirlik için moment eşleştirme gerekir; uygulama Aşama 2'de tasarlanacak.
