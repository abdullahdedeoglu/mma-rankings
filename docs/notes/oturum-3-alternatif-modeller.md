# Okuma oturumu 3: Alternatif modeller ve geçmiş/gelecek bilgisi

**Tarih:** 2026-11-05 · **İlgili:** [PROTOCOL.md](../PROTOCOL.md) §3, §6, §9 · [LITERATURE.md](../LITERATURE.md)

| Kaynak | Ne kadarı okundu |
|---|---|
| Herbrich, Minka & Graepel (2006), "TrueSkill™: A Bayesian skill rating system", *NIPS 19* | Tam metin ([NeurIPS](https://proceedings.neurips.cc/paper_files/paper/2006/file/f44ee263952e65b3610b8ba51229d1f9-Paper.pdf)) |
| Coulom (2008), "Whole-History Rating", *Computers and Games* | Tam metin, ekler dahil ([yazarın sayfası](https://www.remi-coulom.fr/WHR/WHR.pdf)) |
| Landfried & Mocskos (2025), "TrueSkill Through Time", *JSS* 112(6) | Giriş, model, ATP örneği, beraberlik, bilgi yayılımı, tahmin başarısı ve tartışma bölümleri; yazılım kullanım örnekleri ve türetmelerin bir kısmı atlandı ([JSS](https://www.jstatsoft.org/article/view/v112i06)) |
| Dangauthier, Herbrich, Minka & Graepel (2007), "TrueSkill Through Time: Revisiting the history of chess", *NIPS 20* | Yalnızca özet ([NeurIPS](https://proceedings.neurips.cc/paper_files/paper/2007/file/9f53d83ec0691550f7d2507d57f4f5a2-Paper.pdf)) |

---

## 1. TrueSkill (Herbrich vd. 2006)

- **Model:** Her dövüşçü maçta, gerçek gücü etrafında normal dağılan bir "performans" sergiler (varyans β²). Performansı yüksek olan kazanır.
  Bu, Glicko'nun lojistik (Bradley–Terry) bağlantısı yerine **normal (Thurstone)** bağlantı demek.
- **Beraberlik modelin içinde:** Performans farkı bir eşikten (ε) küçükse sonuç beraberlik. Eşik, gözlenen beraberlik oranından hesaplanıyor.
- **Güncelleme:** Tek bir maçtan sonra gerçek sonsal normal değil. TrueSkill bunu, aynı ortalama ve varyansa sahip normal dağılımla
  değiştiriyor (moment eşleştirme / expectation propagation). Bu, Glicko'nun "önsel ortalama etrafında Taylor açılımı"ndan daha ilkeli bir yaklaşım
  ve **tek maçlık güncellemede** tam olarak tanımlı. 2. oturumda Glicko için bulduğumuz sorunun doğrudan cevabı bu.
- **Zaman:** Xbox uygulamasında belirsizlik her **maçta** sabit bir miktar artıyor, geçen zamana göre değil. MMA için bu uygun değil;
  zamana bağlı artış kullanılmalı (TTT paketleri bunu destekliyor).
- **Liste puanı:** Xbox'ta liderlik tablosu `μ − 3σ` ile sıralanıyor (%1 alt sınır). Bizdeki μ − 2·RD ile aynı mantık; makale bunun bir
  **politika** olduğunu, oyuncuların puanlarını korumak için oynamayı bırakma gibi davranışlar geliştirdiğini açıkça yazıyor.
- **Gözlem:** Yeni oyuncular ilk maçlarını sürekli kaybedince tüm havuzun ortalaması önselin altına kayıyor. Bu, bizim ilk maç önseli (H2) için
  önemli: havuzun ortalama düzeyi zamanla izlenmeli.
- **Kanıtın niteliği:** Makalenin Elo karşılaştırması **isabet oranı** ve eşleştirme kalitesiyle yapılmış; uygun bir skor kullanılmamış.
  "TrueSkill Elo'dan daha doğru" iddiası bu yüzden bizim ölçütümüzle doğrudan karşılaştırılamaz.

## 2. Whole-History Rating (Coulom 2008)

- **Model:** Glicko ile aynı dinamik Bradley–Terry modeli (güç zaman içinde Wiener süreciyle değişir). Fark çözüm yönteminde:
  yaklaşık ve artımlı güncelleme yerine, **tüm geçmişin** en olası değerleri (MAP) Newton yöntemiyle tam olarak hesaplanıyor.
- **Artımlı sistemlerin sorunu** (makaledeki örnek): A ve B aynı anda sisteme girip yalnızca birbirleriyle dövüşsün. Sonra A deneyimli rakiplerle
  dövüşüp puanı değişsin. B'nin puanı da değişmeli, çünkü A ile ilişkisi biliniyor; ama Glicko/TrueSkill B'ye dokunmaz. WHR dokunur.
  MMA'da bu durum çok yaygın: bölgesel organizasyonlarda birbirleriyle dövüşen dövüşçüler sonradan büyük organizasyonlara geçiyor.
- **Önemli nokta:** WHR, tahmin için **yalnızca geçmiş maçlarla** kullanılmış: her yeni maçtan önce o ana kadarki maçlarla yeniden hesaplama.
  Yani "tüm geçmişi kullanmak" geleceği kullanmak demek değil.
- **Sonuçlar (Go, KGS sunucusu, 2,3 milyon test maçı):** isabet oranları Elo %55,1, Glicko %55,5, TrueSkill %55,5, WHR %55,8.
  En iyi ayarlarda güç değişim varyansı çok küçük çıkmış; zamanı hiç modellemeyen statik model bile artımlı sistemleri geçmiş.
- **Kanıtın niteliği:** Yine isabet oranı kullanılmış (uygun bir skor değil); farklar küçük ama test kümesi çok büyük.
- **Yazarın kendi saydığı eksikler:** aykırı sonuçlar ve yeni başlayanların deneyimlilerden hızlı gelişmesi modelde yok. İkisi de MMA'da geçerli.

## 3. TrueSkill Through Time (Landfried & Mocskos 2025; Dangauthier vd. 2007)

- **Model:** TrueSkill'in performans modeli + her dövüşçünün gücünün zaman içinde rastgele yürüyüşle (varyans γ² × geçen süre) değiştiği tek
  bir Bayes ağı. Bilgi hem ileriye hem geriye yayılıyor (ileri–geri mesaj geçişi, birkaç turda yakınsıyor).
- **Filtrelemenin eleştirisi:** Glicko ve TrueSkill bilgiyi yalnızca geçmişten geleceğe taşır. Sonuçları: kariyerin başındaki tahminler hep çok belirsiz,
  ve birbirine az bağlı gruplar (farklı dönemler, farklı bölgeler) arasındaki karşılaştırmalar yanlış olabilir.
- **Tahmin başarısı (§3.9):** Değerlendirmede her maç, **yalnızca bir önceki güne kadarki verilerle** tahmin ediliyor; model her gün bir kez
  güncelleniyor. Ölçüt, tahmin olasılıklarının geometrik ortalaması, yani exp(−log loss); karşılaştırma Bayes faktörüyle. Bu, bizim protokolümüzle aynı ölçüt.
  Hiperparametreler verinin ilk %70'inde ayarlanmış, son %30'da test edilmiş.

  Tenis (186.361 test maçı) sonuçlarını log loss'a çevirdim:

  | Model | Geometrik ortalama | Log loss |
  |---|---|---|
  | Sabit güç | 0,5593 | 0,581 |
  | Elo | 0,5695 | 0,563 |
  | TrueSkill (filtreleme) | 0,5722 | 0,558 |
  | KickScore | 0,5758 | 0,552 |
  | **TTT** | **0,5760** | **0,552** |

  Tenis'te TTT, TrueSkill'den maç başına ≈0,007, Elo'dan ≈0,011 log loss daha iyi; bu, bizim 0,001'lik eşiğimizin çok üstünde. Ama basketbolda
  TTT ile TrueSkill arasındaki fark çok küçük (0,5318'e karşı 0,5316). Yani kazanç spora göre değişiyor; MMA'da ne olacağını ancak deney gösterir.
- **Hiperparametreler:** önsel belirsizlik, zamana bağlı değişim (γ) ve beraberlik olasılığı; β ölçeği belirliyor. Yazarlar hiperparametreleri
  optimize ettiklerini, tam Bayesçi yaklaşımın bunları integre etmek olacağını kendileri not ediyor.
- **Yazılım:** Python, Julia ve R paketleri var; Julia sürümü dizi hesabında Python'dan yaklaşık 10 kat hızlı.

### Eleştirel not: "tarihsel karşılaştırılabilirlik" iddiası

TTT'nin farklı dönemleri karşılaştırabildiği iddiası, **her dövüşçünün gücünün yavaş ve birbirinden bağımsız değiştiği** varsayımına dayanıyor:
kariyerleri örtüşen dövüşçüler dönemler arasında köprü kuruyor (Berry, Reese & Larkey'in fikri, 5. oturum). Ama Glickman'ın (1999) belirttiği gibi,
tüm havuzun **aynı anda** güçlenmesini eşli karşılaştırma verisi doğrudan göremez. Dangauthier vd. (2007) satrançta genel gücün 150 yılda arttığı
sonucuna varıyor; bu sonuç verinin değil, modelin varsayımının ürünü olabilir. MMA'da 1997'den bugüne genel düzeyin arttığı neredeyse kesin;
TTT bunu kısmen yakalayabilir ama ölçebildiği şey varsayımlara bağlı.

---

## Bizim için en önemli çıkarım: protokolde bir düzeltme

Protokol 0.3'te WHR ve TTT'yi "geleceği kullanan yumuşatma yöntemleri" diye birincil sorudan (S1) dışarıda bırakmıştım. **Bu yanlış bir ayrımdı.**
Belirleyici olan algoritma değil, **hangi bilginin kullanıldığı**:

- WHR ve TTT, *t* anına kadarki verilerle çalıştırılırsa geleceği kullanmaz. Hem Coulom hem Landfried & Mocskos tahminlerini tam böyle değerlendirmiş.
- Bu durumda geçmişteki rakiplerin güçleri de geriye dönük düzeltilir (WHR'deki A–B örneği). Bu, geleceğe sızma değil, **geçmiş bilginin tam kullanımı**.
- "O tarihte bilinen" tanımımız korunur: Ay *m*'nin listesi, yalnızca *m* sonuna kadarki maçlarla yapılan bir TTT tahmininden üretilebilir.
- Tüm veriyle yapılan tam yumuşatma (gelecek dahil) ise ayrı ve açıkça etiketlenmiş bir "bugünkü bilgiyle geçmiş" görünümü olarak kalır.

**Pratik maliyet:** Her ay için ayrı bir TTT çözümü ağır olabilir (≈ 360 ay × 366 bin maç). Yazarların yaptığı gibi, her gün veri ekleyip tek tur
güncelleme yapan artımlı yaklaşım kullanılabilir. Bunun süresi ölçülmeden S1 karşılaştırmasına nasıl gireceği netleşmez.

## Protokole etkisi

Protokol 0.4 sürümüne güncellendi (bkz. PROTOCOL.md değişiklik günlüğü):

1. §6: Kapsam dışı notu düzeltildi. Aday listesine **M4: TrueSkill Through Time** (yalnızca *t* öncesi verilerle, artımlı) eklendi. WHR aynı modelin
   başka bir çözümü olduğu için ayrıca aday yapılmadı (aday sayısını az tutmak için).
2. M3 (TrueSkill) için belirsizlik artışının maç başına değil **zamana bağlı** olacağı yazıldı.
3. §3: Beraberliği modelleyen modellerde (M3, M4) ikili log loss için kazanma olasılığı, beraberlik dışı sonuçlara koşullandırılarak hesaplanacak:
   P(A kazanır) / (P(A kazanır) + P(B kazanır)).
4. §3: Tanı olarak, en az 3 maçlı dövüşçülerin ortalama puanı zaman içinde izlenecek (havuz düzeyindeki kayma).
5. §9: Yumuşatma modellerinin "dönemler arası karşılaştırılabilirlik" iddiasının varsayıma dayandığı eklendi.
6. M4 için önce bir **çalışma süresi pilotu** yapılacak. Bu bir başarı deneyi değil; EXPERIMENTS.md'ye "fizibilite" olarak kaydedilecek ve tahmin
   sonuçlarına bakılmayacak.

## Açık sorular

- TTT'nin Python paketini kullanmak mı, kendimiz yazmak mı? Paket bağımlılığı, sitenin "yalnızca standart kütüphane" ilkesini bozar.
- MMA'da bir dövüşçünün kariyeri tenise göre çok kısa (10–20 maç). Az veride geriye dönük bilgi yayılımının kazancı daha mı büyük olur?
  Bunu bilmiyoruz; deney gösterecek.
