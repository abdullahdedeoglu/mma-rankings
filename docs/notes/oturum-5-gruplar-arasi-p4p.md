# Okuma oturumu 5: Farklı gruplar ne zaman karşılaştırılabilir? (P4P)

**Tarih:** 2026-11-05 · **İlgili:** [PROTOCOL.md](../PROTOCOL.md) §2, §3, §7 (H4, H8), §8, §9 · [LITERATURE.md](../LITERATURE.md)

| Kaynak | Ne kadarı okundu |
|---|---|
| Ford (1957), "Solution of a ranking problem from binary comparisons", *American Mathematical Monthly* 64(8) | **Orijinal okunmadı** (ücretli). Sonuç ikincil kaynaktan: Yan (2014), [arXiv 1411.1168](https://arxiv.org/abs/1411.1168) |
| Berry, Reese & Larkey (1999), "Bridging different eras in sports", *JASA* | Tam metin ([arşiv kopyası](https://web.archive.org/web/2020/https://www.vanderbilt.edu/psychological_sciences/graduate/programs/quantitative-methods/quantitative-content/berry_reese_larkey_1999.pdf)) |
| Batterham & George (1997), *J. Applied Physiology* 83(6), 2158–2166 | Özet ([PubMed](https://pubmed.ncbi.nlm.nih.gov/9390994)) |
| Vanderburgh & Batterham (1999), *Med. Sci. Sports Exerc.* 31(12), 1869–1875 | Özet ([PubMed](https://pubmed.ncbi.nlm.nih.gov/10613442/)) |

---

## 1. Ford (1957): ortak ölçeğin matematiksel şartı

Bradley–Terry modelinde güçlerin en çok olabilirlik tahmini **ancak ve ancak** galibiyet grafiği **güçlü bağlıysa** vardır ve tektir.
Eşdeğer ifadesi: oyuncuları hangi iki gruba ayırırsan ayır, her iki gruptan da en az bir oyuncu öbür gruptan birini en az bir kez yenmiş olmalı.

Bu şart sağlanmadığında yöntemler bir önsel ya da düzenleme terimi ekleyerek tahmini yine de üretir (Conner & Grant 2000; Caron & Doucet 2012).
Ama Yan (2014) basit bir örnekte, düzenleme teriminin büyüklüğü (ε = 0,1 ya da 0,5) değişince **sıralamanın değiştiğini** gösteriyor.

**Bizim için anlamı:** Glicko her yeni dövüşçüye aynı önseli (ortalama 1500) verdiği için puan hep üretilir. Ama iki sıklet arasındaki
bağlantı zayıfsa, bu iki sıkletin ortalama düzeyleri arasındaki fark **veriden değil, büyük ölçüde önselden** gelir. Önsel "her sıklete yeni
gelenlerin ortalama gücü aynıdır" diyor. Bu bir varsayım ve şu an hiçbir yerde yazılı değil.

## 2. Berry, Reese & Larkey (1999): köprüleme

### Ne yapıyorlar?

Hokey (NHL sayıları), golf (büyük turnuva skorları) ve beyzbol (vuruş ve home run oranları) verisinde farklı dönemlerin oyuncularını
karşılaştırıyorlar. Kariyerleri çakışan oyuncular dönemler arasında **köprü** oluyor: 1900'lerin oyuncusu bugünküyle oynamadı, ama oynadığı
biri, oynadığı biriyle oynadı ... ve bu zincir bugüne ulaşıyor.

Model toplamsal: oyuncunun doğuştan yeteneği + o yılın zorluğu + yaş eğrisi (oyuncuya özgü rastgele sapmalarla). Oyuncu yetenekleri,
**her on yıl için ayrı** bir hiyerarşik dağılımdan geliyor; böylece "yetenek havuzunun" değişmesine izin veriliyor.

### Dikkat çektikleri iki kritik varsayım

1. **Bağımsızlık:** maçlar, turlar ve vuruşlar birbirinden bağımsız.
2. **Etkileşim yok:** A bugün B'den iyiyse, ikisi de 50 yıl önce oynasaydı A yine B'den iyi olurdu. Model toplamsal olduğu için
   bir dönemin etkisi herkese aynı şekilde uygulanır.

Hokeyde model en kötü uyumu veriyor; yazarlar bunu güçlü etkileşimlere bağlıyor (oyuncunun sayısı takım arkadaşlarına bağlı;
Gretzky'nin takım arkadaşı bir sezonda 78'den 150 sayıya çıkmış).

### Karıştırıcı etki: yaş

Köprü kuran oyuncular dönem değiştirirken **yaşlanıyor da.** Yaş etkisi modellenmeden köprü yanlı olur. Bu yüzden yaş eğrisi modelin
zorunlu parçası.

### Bizim durumumuzla en önemli fark

Berry vd.'nin verisi **ortak bir ölçek** üzerinde: golfte vuruş sayısı, beyzbolda vuruş oranı. Bu yüzden "yılın zorluğu" ile "oyuncunun
yeteneği" ayrıştırılabiliyor. Eşli karşılaştırmada (MMA) böyle bir ölçek yok: yalnızca kimin kimi yendiği var. Glickman (1999)'un dediği gibi
**havuzun ortalama düzeyindeki ortak değişim tanımlanamaz** (2. oturum). Sıkletler için de aynısı geçerli: bir sıkletin "mutlak" gücü yok,
yalnızca sıklet değiştirenler üzerinden diğer sıkletlere göre bir düzeyi var.

## 3. Batterham & George (1997) ve Vanderburgh & Batterham (1999): vücut ağırlığı düzeltmesi

Halterde performans **mutlak** bir ölçü (kaldırılan kilo). Yine de:

- Batterham & George: 1995 Dünya Şampiyonası madalyalılarında basit allometrik model (T = a·M^b) ortak üs b ≈ 0,47 veriyor.
  Ama artıklarda boyuta bağlı sistematik desenler var; üs boyuttan bağımsız değil, ikinci derece polinom daha iyi uyuyor.
  Sonuç: allometrik ölçekleme ancak tüm varsayımları sınandıktan sonra kullanılmalı.
- Vanderburgh & Batterham: Wilks formülü bench press ve toplamda yansız, ama kadın squat'ta orta sıkletlere, deadlift'te ağırlara karşı
  yanlı. Yani tek bir formül her hareket için geçerli değil.

**Bizim için anlamı:** Mutlak ölçüsü olan bir sporda bile ağırlık düzeltmesi tartışmalıysa, MMA'da bir ağırlık formülü uydurmak savunulamaz.
Ama makalelerin yöntemi bize uyarlanabilir: **artıkları (kalibrasyonu) sıklete göre incelemek.** Bir düzeltme ya da ortak ölçek doğruysa
tahmin hataları sıklete göre sistematik desen göstermemeli.

## 4. Bizim veriyle hızlı bakış (betimsel, tahmin yok)

Dondurulmuş veri sürümünde, erkeklerin kararlı ve derecelendirilen maçları (sıklet ataması `src/mmarank/divisions.py`, yerel çalışma kopyasıyla):

| Ölçüm | Değer |
|---|---|
| Erkek kararlı maç | 331.914 |
| Sıkleti bilinen | 200.723 (%60,5) |
| Sıkleti bilinen pay, 2000–09 | **%5** (74.415 maç) |
| Sıkleti bilinen pay, 2010–19 | %69 |
| Sıkleti bilinen pay, 2020+ | %89 |
| Birden fazla sıklette maç yapan dövüşçü | 38.535 / 100.601 (%38) |
| Ardışık iki maç arasında sıklet değişimi | 96.700 |
| Asıl sıkletleri farklı iki dövüşçünün maçı | 72.509 (%36) |
| A → B → A deseni (tek maçlık sıklet değişimi) | 25.985 |

En çok bağlantı komşu sıkletler arasında (FW–LW 19.216, BW–FW 16.154, LW–WW 14.650 değişim). Uzak sıkletler arasında da doğrudan
değişim görünüyor: ağır sıklet ile sinek sıklet arasında **25**, ağır ile hafif sıklet arasında 130.

Çıkarımlar:

1. **Grafik bağlı, hatta fazlasıyla.** Ford'un şartı sağlanıyor. Asıl sorun bağlantı eksikliği değil, **bağlantıların kalitesi.**
2. Ağır sıkletten sinek sıklete doğrudan geçiş fiziksel olarak inandırıcı değil (sıklet sınırları arasında en az ≈80 lb fark). A-B-A deseninin bu kadar sık olması da
   catchweight ya da etiket gürültüsüne işaret ediyor. Bu "köprülerin" bir kısmı **ölçüm hatası.** §8'deki sıklet denetimi bu yüzden öncelikli.
3. **2010 öncesi için sıklet bilgisi neredeyse yok** (%5). O döneme ait sıklet listeleri ve "sıklet hakimiyeti" P4P'si veriyle desteklenemez.

## 5. Mevcut P4P tanımımızın varsayımları

Bu üç kaynağı birleştirince, "global güç" P4P listesinin dayandığı varsayımlar açıkça yazılabiliyor:

| Varsayım | Kaynak | Şu anki durum |
|---|---|---|
| Sıkletler bir bağlantı grafiğiyle birbirine bağlı | Ford 1957 | Sağlanıyor, ama bağlantıların bir kısmı etiket gürültüsü |
| Her sıklete yeni gelenlerin ortalama gücü aynı (ortak önsel 1500) | Glicko önseli | Yazılı değil, sınanmamış |
| Etkileşim yok: dövüşçünün göreli gücü her sıklette aynı, yalnızca değişim cezası var | Berry vd. 1999 | Sınanmamış; H4 yalnızca ortalama cezayı ölçüyor |
| Sıklet değişimi rastgele değil ama karıştırıcıları (yaş, kariyer evresi, kayıp serisi) kontrol edilmiş | Berry vd. (yaş karıştırıcısı) | Kontrol edilmemiş |
| Ağırlık için bir düzeltme formülü yok | Batterham & George 1997 | Doğru, formül yok |

Bir de algoritmik bir nokta var: Glicko yalnızca **ileri** yönde güncelliyor. Bir sıklet değiştiren dövüşçünün sonucu yalnızca kendisini ve
rakibini günceller; iki sıkletin genel düzey farkı ancak sonraki maçlarla yavaşça yayılır. TTT gibi yumuşatma yöntemleri bu bilgiyi geriye de
yayar (3. oturum), ama S1'deki bilgi kümesi kuralı gereği yalnızca geçmiş veriyle.

### Bunların hepsini sınayan tek bir tanı

Sıklet düzeyleri yanlışsa, bu hata **asıl sıkletleri farklı iki dövüşçünün maçlarında** görünür: model, düzeyini abarttığı sıkletten gelen
dövüşçüye sistematik olarak fazla olasılık verir. Batterham'ın artık analizinin bizdeki karşılığı bu:

- Bu maçlarda kalibrasyon kesişimi ve eğimi, sıklet çiftine ve yöne göre (yukarı ya da aşağı çıkan taraf) raporlanır.
- Sistematik sapma yoksa, "global güç" P4P'si en azından veriyle çelişmiyordur. Sapma varsa P4P listesi bu sapmayla birlikte yayımlanır ya da
  model düzeltilir (H8).

---

## Bizim için anlamı

1. **"Global güç" P4P tanımı varsayımlarıyla birlikte yayımlanmalı.** Ford'un şartı sağlanıyor; ama sıklet düzeyleri, ortak önsel varsayımına ve
   gürültülü köprülere dayanıyor. Sıkletler arası maçlardaki kalibrasyon, bu listenin geçerliliğinin doğrudan ölçüsü. Liste, bu tanı yapılmadan
   "en iyi dövüşçü" iddiasıyla sunulmamalı.
2. **"Sıklet hakimiyeti" P4P'si** sıklet ataması güvenilir olduğunda anlamlı. 2010 öncesinde sıklet bilgisi %5 olduğu için bu liste o dönem için
   üretilmemeli ya da açıkça "yetersiz veri" olarak işaretlenmeli.
3. **Yeni hipotez (H8):** her sıklete yeni gelenlerin önsel ortalaması sıklete göre farklıdır ve eğitim penceresinden tahmin edilir. Bu, Berry vd.'nin
   on yıla özgü hiyerarşik dağılımlarının bizdeki karşılığı. Bu düzeyler yalnızca sıklet değiştirenler üzerinden tanımlanır.
4. **H4'ün yorumu daraltıldı.** Sıklet değiştirmenin etkisi yaş ve kariyer evresiyle karışıyor. H5 (yaş) kabul edilirse H4 yaş kontrol edilerek
   yeniden raporlanır. Kontrol edilmemiş seçilim (kimin neden sıklet değiştirdiği) sınır olarak yazılır.
5. **Sıklet denetiminin önceliği arttı.** Ağır sıklet ile sinek sıklet arasındaki 25 doğrudan geçiş ve 26 bin A-B-A deseni, köprülerin bir kısmının
   gürültü olduğunu gösteriyor. Aşama 1'de uç sıklet geçişleri ayrıca elle incelenir.
6. **Ağırlık formülü yok.** Halterde bile tek bir formül her hareket için yansız değil; MMA'da mutlak ölçü de yok.

## Protokole etkisi

Protokol 0.6 sürümüne güncellendi (bkz. PROTOCOL.md değişiklik günlüğü):

1. §2'ye ölçüm sorunu olarak sıklet bilgisinin döneme göre kapsamı ve uç sıklet geçişleri eklendi.
2. §3'e sıkletler arası kalibrasyon tanısı eklendi.
3. §7'ye H8 (sıklete özgü önsel ortalama) eklendi; H4'e yaş karıştırıcısı notu eklendi.
4. §8'de P4P satırı, sıklet denetimi satırı ve 2010 öncesi sıklet listeleri kuralı güncellendi.
5. §9'a "etkileşim yok" varsayımı ve önselin sıklet düzeylerine etkisi eklendi.

## Açık sorular

- Sıklet değiştirmenin etkisi simetrik çıktı (E0.1: yukarı ve aşağı −3/−7 puan). Saf bir boyut etkisi asimetrik olurdu. Simetrik etki bir
  "uyum maliyeti" mi, yoksa seçilim mi (kaybeden dövüşçülerin sıklet değiştirmesi)? Aşama 2'de, değişimden önceki form kontrol edilerek ayrıştırılabilir.
- "Global güç" P4P'si ne tür bir varsayımsal maçı temsil ediyor? İki dövüşçü hangi kiloda dövüşecek? Model buna cevap vermiyor; yalnızca
  sıklet değiştirenlerin gözlenen maçlarına göre bir ortak ölçek tanımlıyor. Bu yorum sınırı yöntem belgesine (Aşama 5) yazılmalı.
