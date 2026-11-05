# Okuma oturumu 2: Kullandığımız model tam olarak neyi varsayıyor?

**Tarih:** 2026-11-05 · **İlgili:** [PROTOCOL.md](../PROTOCOL.md) §6 (M1, M2), §7 (H1, H2, H5) · [LITERATURE.md](../LITERATURE.md)

| Kaynak | Ne kadarı okundu |
|---|---|
| Glickman (1999), "Parameter estimation in large dynamic paired comparison experiments", *Applied Statistics* 48(3) | Tam metin, ekler dahil ([yazarın sayfası](http://www.glicko.net/research/glicko.pdf)) |
| Glickman (2001), "Dynamic paired comparison models with stochastic variances", *J. Applied Statistics* 28(6) | Tam metin ([yazarın sayfası](http://www.glicko.net/research/dpcmsv.pdf)) |
| Glickman, "The Glicko system" (uygulama notu) | İlgili bölümler ([glicko.net](http://www.glicko.net/glicko/glicko.pdf)) |

---

## 1. Glickman (1999): Glicko-1

### Model

Glicko aslında bir algoritma değil, bir **istatistiksel modelin yaklaşık çözümü**. Model üç parçadan oluşuyor:

1. **Maç sonucu:** Bradley–Terry modeli. A'nın B'yi yenme olasılığı `1 / (1 + 10^(−(θA − θB)/400))`.
   400 ve 10 tabanı yalnızca ölçeği satranç puanlarına benzetmek için seçilmiş.
2. **Zaman içinde güç değişimi:** rastgele yürüyüş. Maç yapılmayan her zaman biriminde güç, ortalaması sıfır ve varyansı `ν²·t`
   olan normal bir şokla değişir. Bizdeki c parametresi bu ν'dür (ay başına).
3. **Yeni oyuncu önseli:** güç, ortalaması 1500 ve varyansı σ₀² olan normal dağılımdan çekilir. σ₀ **veriden tahmin edilecek** bir parametredir.
   Makale ayrıca yaş gibi bilgilerin bu önseli daha bilgilendirici yapabileceğini söylüyor.

### Yaklaşımlar (algoritmanın modelden saptığı yerler)

- Rakibin gücü, rakibin **sonsal değil önsel** dağılımı üzerinden integre ediliyor. Yani rakibin aynı dönemdeki diğer maçlarından gelen bilgi kullanılmıyor.
- Oyuncular arasındaki sonsal korelasyonlar yok sayılıyor.
- Sonsal, normal dağılımla yaklaşıklanıyor ve ortalama, önsel ortalama etrafında Taylor açılımıyla bulunuyor.
- Simülasyonlarda (dönem başına 4–50 rakip) aralıklar nominal kapsama yakın ama **kesinliği hafifçe abartıyor**.
- Hem makale hem uygulama notu, algoritmanın en iyi **dönem başına oyuncu başına ortalama 5–10 maçla** çalıştığını söylüyor.

### Beraberlik ve kesirli sonuç

Beraberlik ayrı bir sonuç olarak modellenmiyor. Bunun yerine "iki beraberlik, bir galibiyet ve bir mağlubiyetle aynı bilgiyi taşır" varsayımıyla
beraberliğin olabilirliğe katkısı `√(p(1−p))` alınıyor, yani s = 0,5. Bu, sonucun olabilirliğe `p^s (1−p)^(1−s)` olarak girdiği anlamına geliyor.

### Parametre tahmini

σ₀ ve ν, **tüm maçlar üzerindeki tek adım ileri log loss toplamı** en aza indirilerek (Nelder–Mead) tahmin ediliyor. Makaleye göre bu ölçüt
çapraz doğrulama niteliğinde olduğu için aşırı uyuma yol açması beklenmez. Bu, 1. oturumdaki sonuçla (Dawid'in prequential yaklaşımı) birebir aynı.

### Diğer önemli noktalar

- **Ortalama düzeydeki kayma tanımlanamaz:** Herkes aynı miktarda güçlenirse eşli karşılaştırma verisi bunu göremez. Bu yüzden farklı
  dönemlerdeki puanlar doğrudan karşılaştırılamaz. Makale kendi "tüm zamanların en iyileri" tablosunu "dönemindeki rakiplere göre üstünlük" olarak yorumluyor.
- **Geriye dönük yumuşatma:** Kalman yumuşatıcısıyla geçmiş dönemler gelecek verisiyle yeniden tahmin edilebilir. Bu, TrueSkill Through Time ile aynı fikir
  ve geleceği kullanır (3. oturum).
- **Ev sahibi avantajı** gibi sıra etkileri modele eklenebilir (Davidson & Beaver 1977).

## 2. Glickman (2001): Glicko-2 (stokastik varyans)

- Sabit varyanslı modelin sorunu: ani güç değişimlerini (sakatlık, hızlı gelişim) yakalayamaz. Ayrıca bu modelde **gözlemden sonra belirsizlik hep azalır**.
- Çözüm: her oyuncunun güç değişim varyansı da zamanla rastgele değişir (`log σ²` rastgele yürüyüş, varyansı s²). Beklenmedik bir sonuç gelince
  oynaklık artar ve belirsizlik gözlemden sonra **artabilir**.
- NFL örneğinde ayrıca **ortalamaya dönüş** (otoregresif katsayı ρ) ve ev sahibi avantajı modellenmiş; ikisi de verinin desteklediği büyüklükte çıkmış.
- Satranç örneğinde iki model benzer çıkarımlar veriyor; Glicko-2 tahminleri daha sıçramalı.
- Yaklaşık filtrenin simülasyonlarında kapsama nominale yakın; oynaklık çok yüksek ve rakip sayısı çok fazlayken aralıklar biraz dar.
- Tartışma bölümü, oynaklığın değişiminin **yaşa bağlanabileceğini** öneriyor.

## 3. Bizim uygulamamızla karşılaştırma

| Konu | Makale | Bizim sistem | Değerlendirme |
|---|---|---|---|
| Kazanma olasılığı | `g(√(RD_A² + RD_B²))` ile (1999, denklem 16) | Aynı | Uyumlu |
| RD artışı | `√(RD² + c²·t)`, üst sınır 350 | Aynı (t ay) | Uyumlu |
| Parametre tahmini | σ₀ ve ν, tüm maçlarda tek adım ileri log loss ile | c ve başlangıç RD, ≤2015'te yalnızca iki tarafı ≥3 maçlı maçlarda, küçük ızgarayla | Yöntem aynı ruhta; popülasyon ve arama daha dar |
| **Minimum RD (30)** | Makalede de uygulama notunda da **yok** | Var | Bizim eklediğimiz, gerekçesiz bir sayı. Tahmin edilmeli ya da kaldırılmalı |
| **Dönem uzunluğu** | Dönem başına 5–10 maç önerilir; yaklaşım ≥4 rakiple test edilmiş | Her tarih ayrı dönem, dövüşçü başına çoğunlukla **1 maç** | Algoritma, makalede test edilmemiş bir rejimde çalışıyor. MMA'da dönemi uzatmak da çözmez (yılda 2–3 maç). |
| **Kesirli sonuç** | Yalnızca beraberlik için gerekçelendirilmiş (s = 0,5) | KO 1,0, UD 0,9, SD 0,55 … | Aynı olabilirlik kalıbının genellemesi, ama 0,9 gibi değerlerin "bilgi eşdeğerliği" anlamı test edilmemiş |
| Yeni dövüşçü önseli | N(1500, σ₀²); yaş gibi bilgilerin eklenebileceği belirtiliyor | Organizasyona göre ortalama (H2) | Makalenin önerdiği yönde bir genişletme |
| Zaman içinde güç | Ortalaması sıfır rastgele yürüyüş (yaşlanma yok) | Aynı | MMA'da yaşla düşüş biliniyor (H5); 2001'deki ortalamaya dönüş ve yaşa bağlı oynaklık seçenek |
| Liste puanı | `r ± 2·RD`, %95 aralığın sınırları olarak özet | Sıralama ölçütü olarak μ − 2·RD | Makale bunu sıralama kuralı olarak önermiyor; bizde politika (§8) |

### En önemli iki bulgu

**1. Kesirli sonuçlar tahmin olasılığının anlamını değiştiriyor.** Puanlar 0,9 gibi değerlere göre güncellenince model, "beklenen skoru"
tahmin edecek şekilde ölçekleniyor. Ama biz bu olasılığı "kazanma olasılığı" olarak değerlendiriyoruz. İkisi aynı şey değil.
Sonuç olarak tahminler sistematik olarak fazla temkinli ya da fazla iddialı olabilir. Bunu ancak kalibrasyon eğimi gösterir. Gerekirse tahmin anında tek bir ölçek
parametresi (λ) eklenebilir. E0.2'deki iyileşmenin ne kadarının bu ölçek etkisinden geldiği de bu sayede ayrıştırılabilir.

**2. Glicko'nun yaklaşımı bizim kullanım biçimimizde doğrulanmamış.** Makale dönem başına en az 4 rakiple test ediyor; biz hep 1 maçla
güncelliyoruz. Tek bir ikili sonucun olabilirliği normal dağılıma hiç benzemiyor. Bu, maç başına moment eşleştirme (expectation propagation) yapan
TrueSkill'i (M3) daha da ilginç bir aday yapıyor. Doğrudan bir kontrol de mümkün: tahmin kalibrasyonunu belirsizlik (RD) düzeylerine göre ayrı ayrı incelemek.

---

## Protokole etkisi

Protokol 0.3 sürümüne güncellendi (bkz. PROTOCOL.md değişiklik günlüğü):

1. M1'in ayar parametrelerine **minimum RD** (kaldırma seçeneği dahil) eklendi; M1 ve M2'nin parametreleri tüm popülasyondaki tek adım ileri log loss ile tahmin edilecek.
2. Kalibrasyon, birleşik RD düzeylerine göre ayrıca raporlanacak (yaklaşımın doğruluğu için tanı).
3. H1'e, kesirli sonuçların ölçek etkisini ayıran **tahmin anı ölçek parametresi λ** eklendi.
4. H5 (yaş) için iki biçim tanımlandı: tahminde değişken olarak ve güç sürecinde yaşa bağlı ortalama kayma olarak.
5. §9'a "dönemler arası mutlak düzey tanımlanamaz" sınırı eklendi: tarihsel listeler o dönemin rakiplerine görelidir.

## Açık sorular

- Tek maçlık güncellemede normal yaklaşım ne kadar bozuluyor? TrueSkill'in moment eşleştirmesi burada daha mı iyi? (Oturum 3.)
- Kesirli sonuçlar yerine galibiyet farkını modellemenin ilkeli yolu ne? (Oturum 4, Kovalchik 2020.)
