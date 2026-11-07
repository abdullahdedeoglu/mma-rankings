# Deney Kaydı

Her deney buraya, başarısız olanlar da dahil, yapıldığı sırayla yazılır. Kurallar için bkz. [PROTOCOL.md](PROTOCOL.md).

Biçim: kod · tarih · veri sürümü · amaç · yöntem · sonuç · durum (`ön-protokol`, `geliştirme`, `keşif`, `doğrulama`).

---

## E0 · Protokol öncesi bulgular

Aşağıdakiler protokol yazılmadan önce yapıldı. Hipotez üretmek için kullanılabilirler ama kanıt sayılmazlar.

### E0.1 · Sıklet değiştirenler

- **Tarih / veri:** 2026-11-05 · `db-2026-11-04-1837`
- **Amaç:** Global puan ölçeği ağır veya hafif sıkletler lehine sistematik olarak bozuk mu?
- **Yöntem:** Önceki etiketli sıkleti mevcut maçtan farklı olan dövüşçüler, rakipleri o sıkletin yerlisiyken
  (rakibin önceki sıkleti = maçın sıkleti), iki tarafın da ≥3 önceki maçı varsa. Kalıntı = gerçek galibiyet oranı − ortalama tahmin.
- **Sonuç:**

  | Durum | Maç | Ortalama tahmin | Galibiyet oranı | Kalıntı |
  |---|---|---|---|---|
  | 1 sıklet yukarı | 12.744 | 0,488 | 0,456 | −0,031 |
  | 1 sıklet aşağı | 14.058 | 0,454 | 0,425 | −0,029 |
  | 2+ yukarı | 1.473 | 0,447 | 0,381 | −0,066 |
  | 2+ aşağı | 1.533 | 0,418 | 0,350 | −0,068 |

- **Yorum:** Kalıntılar yönden bağımsız (simetrik), yani belirli bir sıklet yönünde ölçek sapması görülmüyor.
  Sıklet değiştirmenin kendisinin bir maliyeti (veya seçilim etkisi) var. Verinin neredeyse tamamı 2010 sonrası.
  → H4'ün kaynağı.
- **Durum:** ön-protokol

### E0.2 · Karar türü ağırlıkları

- **Tarih / veri:** 2026-11-05 · `db-2026-11-04-1837`
- **Amaç:** Karar türüne göre kesirli sonuç (UD 0,9 · MD 0,6 · SD 0,55) düz şemadan (tüm galibiyetler 1,0) daha iyi mi tahmin ediyor?
- **Yöntem:** Şema, daha önce ≤2015 eğitim döneminde 3 aday arasından seçilmişti. 2016+ birincil popülasyonda
  (iki taraf ≥3 önceki maç, n = 78.573) maç bazında eşleştirilmiş log loss farkı; etkinlik düzeyinde kümelenmiş bootstrap (B = 500).
- **Sonuç:** fark −0,00474, %95 GA [−0,00553, −0,00393]; maç bazında farkın standart sapması 0,114 (§4.3 güç hesabında kullanıldı).
- **Yorum:** Etki gerçek görünüyor ve §5'teki 0,001 eşiğinin üstünde. Ancak ağırlıklar veriden tahmin edilmedi;
  H1'de tahmin edilmiş değerlerle yeniden sınanacak.
- **Durum:** ön-protokol

---

## E1 · Aşama 2 hazırlığı

### E1.1 · Altyapının sentetik veriyle doğrulanması

- **Tarih / veri:** 2026-11-06 · yalnızca sentetik veri (`src/mmarank/research/synthetic.py`, tohum 1). Gerçek veride hiçbir model çalıştırılmadı.
- **Amaç:** Değerlendirme altyapısının (§6.1) doğru çalıştığını gerçek sonuçlara bakmadan göstermek.
- **Yöntem:**
  1. Modellerin güncelleme formülleri yayımlanmış sayısal örneklerle karşılaştırıldı: Glickman (1999) ve (2001) örnekleri,
     TrueSkill'in varsayılan ayarlarla bilinen değerleri.
  2. Sızıntı testi: her model için, *D* gününe kadarki tahminler sonraki maçlar silindiğinde birebir aynı kalıyor mu?
  3. Aynı gün içinde maç sırası Elo, Glicko-1 ve Glicko-2'nin tahminlerini değiştiriyor mu?
  4. Bilinen λ ve kalibrasyon eğimi simüle veriden geri kazanılıyor mu?
  5. Sentetik dünya: dövüşçüler gelir, gücü aylık rastgele yürüyüşle değişir, emekli olur. Eşleştirme gürültülü gerçek güce göre yapılır;
     P(A kazanır) = lojistik(güç farkı); maçların %1,4'ü beraberlik. 78.716 kararlı maç, 10.647 dövüşçü.
     Bütün ızgaralar (455 ayar) çalıştırılıp iç içe seçim yapıldı.
- **Sonuç:**
  - 1–4: hepsi geçti (`tests/test_research.py`, 16 test).
  - 5: birincil popülasyonda, 2008–2025 (n = 41.892):

    | | Kendi formülüyle | λ ile | λ (2025 penceresi) |
    |---|---|---|---|
    | Gerçek olasılıklar (kâhin) | 0,5977 | — | — |
    | M0 Elo | 0,6708 | 0,6680 | 0,50 |
    | M1 Glicko-1 | 0,6694 | 0,6611 | 0,43 |
    | M2 Glicko-2 | 0,6693 | 0,6611 | 0,43 |
    | M3 TrueSkill | 0,6697 | 0,6629 | 0,32 |

  - Durağan bir dünyada (güç değişmiyor, rastgele eşleştirme, 20'den fazla önceki maç) modeller kâhine yaklaşıyor
    (Glicko-1 0,566, kâhin 0,546). Aradaki fark, dövüşçü başına maç sayısının azlığından geliyor.
- **Yorum:**
  1. Altyapıda hata bulunmadı.
  2. **λ belirgin biçimde 1'in altında.** Bu dünyada eşleştirmeyi yapan taraf gerçek gücü derecelerden iyi biliyor. Eşleşen iki dövüşçünün gerçek
     farkı, derece farkının gösterdiğinden küçük; bu yüzden modeller aşırı özgüvenli. §6'daki λ yorumuna bir ekleme: **λ < 1 yalnızca tahmin
     gürültüsünden değil, bilgili eşleştirmeden de gelebilir.** Gerçek MMA'da maç yapımcıları derecelerin göremediği bilgiyi kullanır;
     gerçek verideki λ bu iki etkiyi ayırt edemez.
  3. Seçilen ayarlar sık sık ızgara sınırına dayandı (ör. λ'sız Glicko'da en küçük başlangıç RD'si: model, özgüvenini başka yoldan düşürüyor).
     Bu nedenle §6.1'deki genişletme kuralına üst sınır eklendi (protokol v0.9, deneyden önce).
  4. Sentetik sonuçlar gerçek MMA hakkında kanıt değildir.
- **Durum:** geliştirme (altyapı doğrulaması)

---

## E2 · Aşama 2: model karşılaştırması (S1)

Ortak bilgiler: 2026-11-06 · `db-2026-11-04-1837` · ön kayıt commit'i `bce4796` (protokol v0.9).
Komutlar: `uv run python -m mmarank.research grid M0 M1 M2 M3`, ardından `select` ve `report` (aynı model listesiyle).

### E2.1 · Izgara genişletmeleri (§6.1, madde 5)

| Tur | Genişletme | Neden |
|---|---|---|
| 1 | M1 başlangıç RD 550; M2 τ 1,6 ve başlangıç RD 550; M3 beraberlik olasılığı %4,6 | Seçilen ayar üst sınırda |
| 2 | M2 τ 2,0; M3 beraberlik olasılığı %6,2 | Hâlâ üst sınırda |
| 3 | M3 beraberlik olasılığı %7,8 | Hâlâ üst sınırda (son izinli tur) |

**Sınırda kalanlar:**

- M3 (λ'lı) beraberlik olasılığı %7,8'de, üç genişletme kullanıldı. Gerçek beraberlik oranı %1,4 olduğu için bu parametre artık beraberlik
  olasılığı gibi değil, galibiyet güncellemelerini küçülten bir ayar gibi davranıyor.
- M3 (kendi formülüyle) %0,5'te ve M2 (λ'lı) τ 0,2'de kaldı; bir adım daha geçersiz bir değere düşüyor.

Toplam 589 ayar çalıştırıldı.

### E2.2 · M0–M3 iç içe karşılaştırma

**Birincil popülasyon, 2008–2025, n = 114.911 maç, 34.749 etkinlik.** Yazı tura: 0,6931.

| Yöntem | Log loss (iç içe) | Tam dizi | Brier | İsabet | Kalibrasyon eğimi | Kesişim |
|---|---|---|---|---|---|---|
| M0 Elo | 0,59579 | 0,59579 | 0,20568 | %67,3 | 1,049 | −0,148 |
| M0 Elo + λ | 0,59540 | 0,59534 | 0,20551 | %67,3 | 1,035 | −0,140 |
| **M1 Glicko-1** | **0,58649** | 0,58603 | 0,20176 | %68,1 | 1,058 | −0,116 |
| M1 + λ | 0,58609 | 0,58564 | 0,20161 | %68,1 | 1,040 | −0,111 |
| M2 Glicko-2 | 0,58633 | 0,58596 | 0,20169 | %68,1 | 1,061 | −0,115 |
| M2 + λ | 0,58613 | 0,58558 | 0,20162 | %68,1 | 1,041 | −0,109 |
| M3 TrueSkill | 0,58633 | 0,58584 | 0,20184 | %68,1 | 1,002 | −0,113 |
| M3 + λ | 0,58545 | 0,58521 | 0,20143 | %68,1 | 1,048 | −0,101 |

**Seçilen ayarlar** (18 test yılı):

- M0: K = 128 (λ'lı: 160).
- M1: c = 30, başlangıç RD 350, en küçük RD yok (16 yıl). Sitedeki ayar c = 35, en küçük RD 30; en küçük RD sınırı veriyle desteklenmedi.
- M2: τ = 1,2–1,6, başlangıç RD 350, σ₀ = 0,12–0,2.
- M3: σ₀ = 1,5–2, γ = 0,15, beraberlik olasılığı yıllara göre %0,5 ile %3 arasında gidip geliyor (parametre neredeyse etkisiz).

**λ (eğitim pencerelerinde):**

| Model | λ aralığı | Yorum |
|---|---|---|
| M0 | 0,84–0,89 | Aşırı özgüvenli |
| M1 | 0,87–1,03 | 1'e yakın |
| M2 | 0,89–1,06 | 1'e yakın |
| M3 | 0,78–0,84 | Aşırı özgüvenli |

Tam dizi ile iç içe sonuç arasındaki fark M1'de 0,00046 (§4.2'de "neredeyse aynı" beklenmişti). Nedeni ayarın zamanla kayması:
son yıllar c = 20'yi, önceki yıllar c = 30'u seçiyor.

**Eşleştirilmiş farklar** (a − b; negatif: a daha iyi; etkinlik ve ay düzeyinde kümelenmiş bootstrap, B = 2000):

| Karşılaştırma | Fark | %95 GA (etkinlik) | %95 GA (ay) | Brier farkı | Profesyonelliği kontrol edilmiş maçlarda |
|---|---|---|---|---|---|
| M0 − M1 | +0,00930 | [+0,00852, +0,01005] | [+0,00865, +0,00998] | +0,00392 | +0,00877 |
| M2 − M1 | −0,00016 | [−0,00036, +0,00005] | [−0,00040, +0,00008] | −0,00007 | −0,00012 |
| M3 − M1 | −0,00016 | [−0,00051, +0,00016] | [−0,00055, +0,00025] | +0,00008 | −0,00031 |
| M0+λ − M0 | −0,00039 | [−0,00061, −0,00019] | [−0,00062, −0,00017] | −0,00017 | −0,00022 |
| M1+λ − M1 | −0,00040 | [−0,00059, −0,00023] | [−0,00062, −0,00020] | −0,00015 | −0,00041 |
| M2+λ − M2 | −0,00020 | [−0,00044, +0,00003] | [−0,00042, +0,00002] | −0,00007 | −0,00018 |
| M3+λ − M3 | −0,00088 | [−0,00114, −0,00063] | [−0,00115, −0,00062] | −0,00041 | −0,00065 |
| M3+λ − M1 | −0,00104 | [−0,00132, −0,00077] | [−0,00135, −0,00074] | −0,00033 | −0,00096 |

**§5 kurallarına göre:**

- **M0** M1'den açıkça kötü (0,0093).
- **M2 ve M3** M1'den ayrılmıyor: güven aralıkları sıfırı içeriyor, farklar 0,001 eşiğinin çok altında.
- **λ** hiçbir modelde kabul edilmiyor. M0, M1 ve M3'te iyileşme istatistiksel olarak sıfırdan farklı, ama 0,001 eşiğinin altında
  (en büyüğü M3'te 0,00088).
- **M3+λ − M1** farkı eşiğin hemen üstünde (−0,00104). Ancak iki bileşenden oluşuyor ve tek tek ikisi de eşiği geçmiyor:
  M3 − M1 anlamlı değil, λ ise eşiğin altında. Protokol bileşenleri tek tek sınadığı için (§6.1, madde 4) M3+λ kabul edilmiyor.
  Profesyonelliği kontrol edilmiş maçlarda fark −0,00096'ya iniyor.
- **Dayanıklılık:** ay düzeyinde kümeleme bütün sonuçları aynı bırakıyor. Brier yönü, işareti tutarsız olan tek karşılaştırmada
  (M3 − M1) iki fark da sıfıra çok yakın.

**İkincil popülasyonlar (log loss):**

| Popülasyon | n | M0 | M1 | M2 | M3 | M3+λ |
|---|---|---|---|---|---|---|
| Tüm maçlar | 296.208 | 0,61818 | 0,61284 | 0,61274 | 0,61289 | 0,61308 |
| Erkek, 0 önceki maç (en az bir taraf) | 91.357 | 0,64026 | 0,63764 | 0,63761 | 0,63862 | 0,64002 |
| 1–2 | 65.279 | 0,61130 | 0,60820 | 0,60812 | 0,60717 | 0,60770 |
| 3–9 | 79.351 | 0,59832 | 0,58921 | 0,58901 | 0,58935 | 0,58863 |
| 10+ | 35.560 | 0,59014 | 0,58042 | 0,58037 | 0,57960 | 0,57836 |
| Birincil, 2008–09 | 9.036 | 0,59161 | 0,58248 | 0,58227 | 0,58328 | 0,58222 |
| Birincil, 2010–14 | 30.769 | 0,59202 | 0,58355 | 0,58398 | 0,58467 | 0,58381 |
| Birincil, 2015–19 | 36.749 | 0,59493 | 0,58584 | 0,58636 | 0,58636 | 0,58478 |
| Birincil, 2020–25 | 38.357 | 0,60063 | 0,59042 | 0,58915 | 0,58835 | 0,58818 |

M3+λ'nın üstünlüğü deneyimli dövüşçülerde ve son yıllarda; ilk maçlarda daha kötü. Ayarlar ve λ birincil popülasyonda seçildiği için
bu tabloda başka popülasyonlara aktarılabilirlik sınanmıyor.

**Belirsizlik bantlarına göre kalibrasyon** (birleşik RD = √(RD_A² + RD_B²), birincil popülasyon):

| Birleşik RD | M1 n | M1 eğim | M3 n | M3 eğim |
|---|---|---|---|---|
| < 200 | 199 | 1,39 | 4.317 | 1,17 |
| 200–250 | 12.391 | 1,23 | 39.199 | 1,07 |
| 250–300 | 50.441 | 1,07 | 49.387 | 0,99 |
| ≥ 300 | 51.880 | 1,01 | 22.008 | 0,90 |

- M1'de birleşik RD hiç 150'nin altına inmiyor ve RD düştükçe eğim 1'in üstüne çıkıyor. Yani **M1, belirsizliğin az olduğu yerde
  fazla temkinli**. Güvenilirlik tablosu da aynı şeyi gösteriyor: favorinin tahmini %92,2 iken gözlenen %94,8; tahmini %96,4 iken
  gözlenen %98,6.
- Olası neden: Glicko-1'de tek bir parametre (c) hem gücün değişme hızını hem tahmin anındaki belirsizliği belirliyor. c'nin güç
  değişimini izleyecek kadar büyük seçilmesi RD'yi şişiriyor ve g(RD) tahminleri yarıya doğru çekiyor (§6'daki "bilinen yaklaşım sorunu").
- M3'ün güvenilirlik tablosu bütün aralıkta köşegene daha yakın.

**Keşif: kariyere erken başlayanın dezavantajı.** Kalibrasyon için maçlar, dövüşçü numarası küçük olan taraf açısından yönlendirildi (§6.1, madde 7).
Fight Canon'da dövüşçü numarası ilk maç tarihiyle neredeyse aynı sırada (korelasyon 0,987). Bu yüzden kesişim, **kariyerine daha önce başlamış
tarafın** modelin tahmininden ne kadar az ya da çok kazandığını ölçüyor.

- Bütün modellerde kesişim −0,10 ile −0,15 arasında: kariyerine daha önce başlamış dövüşçü, beklenenden yaklaşık 0,11 logit (p = 0,5
  civarında ≈ 2,7 yüzde puanı) daha az kazanıyor. Belirsizlik bantlarının hepsinde görülüyor.
- En yakın açıklama yaşlanma ya da kariyer evresi (H5). Rakipten daha önce başlamış olmak yaş, yıpranma ve "zirveyi geçmiş olma" ile ilişkili.
- λ'nın 1'in altında çıkmasının bir kısmı da bu olabilir: kesişimsiz λ, açıklanmayan bir sistematik etkiyi ölçeği küçülterek karşılıyor
  (kesişimli kalibrasyon eğimi 1'in üstünde).
- Önceden kayıtlı bir hipotez testi değil; **H5'in önemli olabileceğine dair bir işaret**.

**En kötü skorlanan maçlar** (§3, dayanıklılık kontrolü 3):

- **Kapsam:** sekiz yöntemin her birinin en kötü 50 maçının birleşimi, 102 maç (19'u sekiz yöntemin hepsinde var). Kazananın tahmini
  olasılığı yaklaşık %2–7.
- **Yöntem:** Tapology'de kazanan (bulunamazsa kaybeden) arandı. Maç, tarih ±2 gün ve rakip adı ile eşleştirildi; Tapology'deki sonuç ve
  profesyonellik okundu. Kullanıcının Chrome tarayıcısında, istekler arası 2,5–4 saniye. İki satır hız sınırına (HTTP 429) takılıp yeniden denendi.
- **Sonuç:**
  - **Bulunan 94 maçın hepsinde kazanan aynı ve hepsi profesyonel.**
  - 8 maç bulunamadı (çoğu 2008–2013 bölgesel organizasyonlar). Biri "MMA Sanda Combat" etkinliği; bu maçın kuralları ayrıca incelenmeye değer.
  - Bir eşleşmede Tapology profili farklı bir adla kayıtlı (Ren Sugiyama ↔ "YA-MAN"); tarih ve rakip tutuyor.
- **Yorum:** En kötü tahminler veri hatasından değil, gerçek sürprizlerden geliyor (ör. Lesnar–Couture 2008, Cannonier–Branch 2018,
  Asakura–Horiguchi 2019, Pereira–Adesanya 2022, Suzuki–Pitbull 2023). Düzeltilecek ya da çıkarılacak maç olmadığı için sonuçlar
  yeniden hesaplanmadı.
- Satır satır: [audit/worst_bouts_tapology.csv](audit/worst_bouts_tapology.csv).

**Karar (S1):**

- Hiçbir aday, mevcut sade Glicko-1'den (M1) §5 kurallarına göre ayrılmıyor. **M1 kalıyor.**
- M1, M2 ve M3'ün parametre sayısı aynı (3). Eşitlik durumunda hangisinin seçileceği protokolde yazılı değildi; mevcut model olduğu ve en basit
  hesaplandığı için M1 seçildi. Bu, önceden kayıtlı olmayan bir karar olarak not edilir.
- **M3+λ** eşiğin hemen altında kalan bileşenlerle eşiğin hemen üstünde bir fark veriyor ve kalibrasyonu daha iyi. Hipotezler sınanırken temel
  model M1 olur; M3+λ ileriye dönük testte (§4.3) "meydan okuyucu" olarak izlenmeye aday.
- **Durum:** geliştirme

**Bu aşamada yapılmayanlar:**

- Havuz düzeyi tanısı (§3).
- Sıkletler arası kalibrasyon tanısı (§3; P4P ile birlikte, Aşama 3).
- M4 (TTT) fizibilite pilotu.

---

## E3 · M4 (TrueSkill Through Time)

### E3.1 · Fizibilite pilotu (§6, "M4 fizibilitesi")

- **Tarih / veri:** 2026-11-06 · `db-2026-11-04-1837`. Yalnızca süre ölçüldü; hiçbir tahmin skorlanmadı.
- **Uygulama:** `src/mmarank/research/ttt.py`, bizim yazdığımız saf Python uygulaması.
  - Her dövüşçünün maç yaptığı her gün bir düğüm; ardışık düğümler γ²·ay varyanslı kaymayla bağlı.
  - Çıkarım beklenti yayılımıyla (EP) yapılıyor: zaman boyunca geri ve ileri geçiş, maç mesajları TrueSkill güncellemesiyle yenileniyor.
- **Doğrulama** (`tests/test_research.py`, 3 yeni test):
  1. Yalnızca ileri geçiş, M3 ile birebir aynı sonucu veriyor (en büyük fark 3·10⁻¹⁴).
  2. Çevrimiçi kullanımda sızıntı yok.
  3. Tekrarlanan turlarda değişim düzenli olarak küçülüyor. Yakınsama yavaş: her turda değişim yaklaşık üçte bir azalıyor.
- **Süre** (tek çekirdek, 366.496 maç, 7.862 gün):

  | Geçmiş | Maç | Bir tur (geri + ileri) |
  |---|---|---|
  | 2000'e kadar | 5.558 | 0,02 sn |
  | 2010'a kadar | 80.882 | 0,35 sn |
  | 2020'ye kadar | 262.878 | 0,94 sn |
  | Tamamı | 366.496 | 1,32 sn |

  Süre maç sayısıyla doğrusal artıyor (maç başına yaklaşık 3,6 mikrosaniye).

  | Yeniden yumuşatma sıklığı | Bir ayar, bütün tarih |
  |---|---|
  | **Her gün** (protokoldeki tanım) | **≈ 1,2 saat** |
  | Haftada bir | ≈ 0,2 saat |
  | Ayda bir | ≈ 3 dakika |
  | Yılda bir | ≈ 1 dakika |

- **Yorum:**
  - Protokoldeki tanım (her gün veri eklenip tek tur) **yaklaşıklamaya gerek kalmadan uygulanabilir.**
  - 108 ayarlık bir ızgara 11 çekirdekte ≈ 11–12 saat sürer.
  - Her gün yalnızca bir tur yapılsa da önceki durumdan devam edildiği için eski geçmiş yüzlerce tur almış oluyor. Yakınsamadan en uzak kısım
    son haftalar.
- **Durum:** fizibilite


### E3.2 · M4 ızgarası ve karşılaştırma (S1)

- **Tarih / veri:** 2026-11-07 · `db-2026-11-04-1837` · ön kayıt commit'i `b97a8df` (protokol v0.10).
- **Komutlar:** `uv run python -m mmarank.research grid M4`, `select M4`, `report M1 M3 M4` (rapor: `report_s1_M1_M3_M4.json`;
  E2.2'nin `report_s1.json` dosyası değişmedi, M1 ve M3 satırları onunla birebir aynı).
- **Süre:** 108 ayar, 11 çekirdek, ayar başına ≈ 2,2 saat, toplam ≈ 28 saat. Pilotun tahmini (≈ 1,2 saat) tek çekirdek, boş makine içindi;
  11 paralel işte ayar başına süre neredeyse iki katına çıktı.
- **Sızıntı denetimi (sonuçlar görüldükten sonra, ek):** fark beklenenden büyük çıktığı için `tests/test_research.py`'deki sızıntı testi bu kez
  günlük yeniden yumuşatmayla (grid'deki tanım) üç kesim tarihinde tekrarlandı; kesimden sonraki maçlar silindiğinde de sonuçları rastgele
  ters çevrildiğinde de kesim öncesi tahminler bit düzeyinde aynı kaldı.

**Birincil popülasyon, 2008–2025, n = 114.911 maç** (M1 ve M3 satırları E2.2'den):

| Yöntem | Log loss (iç içe) | Tam dizi | Brier | İsabet | Kalibrasyon eğimi | Kesişim |
|---|---|---|---|---|---|---|
| M1 Glicko-1 | 0,58649 | 0,58603 | 0,20176 | %68,1 | 1,058 | −0,116 |
| M3 TrueSkill | 0,58633 | 0,58584 | 0,20184 | %68,1 | 1,002 | −0,113 |
| M3 + λ | 0,58545 | 0,58521 | 0,20143 | %68,1 | 1,048 | −0,101 |
| **M4 TTT** | **0,57910** | 0,57905 | 0,19880 | %68,7 | 0,944 | −0,154 |
| M4 + λ | 0,57845 | 0,57841 | 0,19850 | %68,8 | 1,038 | −0,138 |

**Seçilen ayarlar:**

- M4: σ₀ = 2, γ = 0,15 (yalnızca 2008'de 0,2), beraberlik olasılığı %0,5 bütün yıllarda. Tam dizide de aynı ayar seçiliyor.
- M4 + λ: σ₀ = 3, γ = 0,2, beraberlik olasılığı %3 bütün yıllarda; λ 0,717 (2008) → 0,749 (2025), yıllar içinde genel olarak artıyor.
- λ'nın 0,72–0,75 çıkması M4'ün **belirgin biçimde aşırı özgüvenli** olduğunu gösteriyor (M3'te 0,78–0,84, M1'de ≈ 1).
  λ'sız M4'ün kalibrasyon eğimi de 1'in altında (0,944).

**Izgara sınırı (§6.1, madde 5):**

- λ'sız M4: beraberlik olasılığı alt sınırda (%0,5); bir adım geçersiz bir değere düşüyor, **sınırda kaldı**.
- M4 + λ: beraberlik olasılığı üst sınırda (%3); kural %4,6 ile genişletmeyi gerektiriyor. **Bu genişletme ertelendi** (2026-11-07):
  makine müsait olduğunda çalıştırılacak (tur başına 36 ayar, ≈ 9 saat; en fazla üç tur).
  Seçilen σ₀ ve γ için beraberlik olasılığının bir adımı log loss'u yalnızca 0,00002–0,00003 değiştiriyor (tam dizi: %0,5 → 0,57844,
  %1,4 → 0,57843, %3 → 0,57841); genişletmenin aşağıdaki λ kararını değiştirmesi beklenmiyor, ama kural uygulanana kadar M4 + λ satırı geçicidir.

**Eşleştirilmiş farklar** (a − b; negatif: a daha iyi; etkinlik ve ay düzeyinde kümelenmiş bootstrap, B = 2000):

| Karşılaştırma | Fark | %95 GA (etkinlik) | %95 GA (ay) | Brier farkı | Profesyonelliği kontrol edilmiş maçlarda |
|---|---|---|---|---|---|
| M4 − M1 | −0,00739 | [−0,00819, −0,00660] | [−0,00824, −0,00656] | −0,00296 | −0,00757 |
| M4 − M3 | −0,00723 | [−0,00797, −0,00649] | [−0,00805, −0,00645] | −0,00304 | −0,00727 |
| M4+λ − M4 | −0,00065 | [−0,00104, −0,00024] | [−0,00107, −0,00024] | −0,00030 | −0,00033 |

**§5 kurallarına göre:**

- **M4, M1'den açıkça daha iyi:** fark 0,001 eşiğinin yedi katından büyük, güven aralığı sıfırdan çok uzak. Ay düzeyinde kümeleme, Brier ve
  profesyonelliği kontrol edilmiş maçlar aynı yönü veriyor. Büyüklük olarak M0 ile M1 arasındaki farka (0,0093) yakın.
- **Kazancın neredeyse tamamı yumuşatmadan geliyor:** M4 − M3 = −0,00723. Aynı model, aynı ızgara; tek fark, geçmişin her gün yeniden
  hesaplanması. Rakiplerin geçmişteki güçleri sonradan gelen maçlarla düzeltildiği için bir galibiyetin değeri de geriye dönük düzeliyor;
  ileri yönlü filtre (M1, M3) bunu yapamaz.
- **λ kabul edilmiyor:** iyileşme sıfırdan farklı ama eşiğin altında (0,00065); profesyonelliği kontrol edilmiş maçlarda güven aralığı sıfırı
  içeriyor (−0,00033). Izgara genişletmesi bekleniyor (yukarıda).

**İkincil popülasyonlar (log loss):**

| Popülasyon | n | M1 | M3 | M3+λ | M4 | M4+λ |
|---|---|---|---|---|---|---|
| Tüm maçlar | 296.208 | 0,61284 | 0,61289 | 0,61308 | 0,60720 | 0,60802 |
| Erkek, 0 önceki maç (en az bir taraf) | 91.357 | 0,63764 | 0,63862 | 0,64002 | 0,63223 | 0,63541 |
| 1–2 | 65.279 | 0,60820 | 0,60717 | 0,60770 | 0,60451 | 0,60503 |
| 3–9 | 79.351 | 0,58921 | 0,58935 | 0,58863 | 0,58267 | 0,58166 |
| 10+ | 35.560 | 0,58042 | 0,57960 | 0,57836 | 0,57114 | 0,57127 |
| Birincil, 2008–09 | 9.036 | 0,58248 | 0,58328 | 0,58222 | 0,57594 | 0,57445 |
| Birincil, 2010–14 | 30.769 | 0,58355 | 0,58467 | 0,58381 | 0,57543 | 0,57476 |
| Birincil, 2015–19 | 36.749 | 0,58584 | 0,58636 | 0,58478 | 0,57841 | 0,57812 |
| Birincil, 2020–25 | 38.357 | 0,59042 | 0,58835 | 0,58818 | 0,58346 | 0,58267 |

- M4 her popülasyonda ve her dönemde M1'den iyi; ilk maçlarda bile (0,0054). Fark deneyim arttıkça büyüyor (10+ maçta 0,0093).
- λ ilk maçlarda kötüleştiriyor (0,63223 → 0,63541); M3'te de aynıydı. Ölçek küçültme, yeni dövüşçüler için zaten belirsiz olan tahmini fazla
  yarıya çekiyor.

**Kesişim:** M4'te −0,154, bütün modellerin en büyüğü. Kariyerine daha önce başlamış tarafın beklenenden daha az kazanması (E2.2'deki keşif)
M4'te kaybolmuyor, büyüyor. Yumuşatma eski güçleri düzelttiği hâlde bu etkiyi açıklamıyor; H5 (yaş) için işaret güçleniyor.

**Yapılmayanlar:**

- Belirsizlik bantlarına göre kalibrasyon: M4 için uygulanmadı (`models.run_ttt` bantları üretmiyor).
- En kötü skorlanan maçların denetimi: M4'ün en kötü 50 maçı E2.2'deki birleşime eklenmedi.
- M4 + λ'nın ızgara genişletmesi (beraberlik olasılığı %4,6): ertelendi, makine müsait olduğunda.

**Karar (S1):**

- **M4, §5 ve §6.1 madde 8'e göre seçilen model.** Parametre sayısı M1 ile aynı (3) olduğu için eşitlik kuralına gerek kalmıyor.
- λ kabul edilmiyor (ertelenen genişletme yapılınca yeniden bakılacak; kararın değişmesi beklenmiyor).
- Sonraki hipotezler (§7) M4 temel alınarak sınanır. Her ayar ≈ 2,2 saat sürdüğü için bu, Aşama 2'nin geri kalanını belirgin biçimde
  uzatır; protokolde bu maliyet için önceden yazılmış bir kural yok.
- **Site henüz değişmedi:** sıralamalar hâlâ M1 (Glicko-1) ile hesaplanıyor. Siteye geçiş ayrı bir karardır (ölçek, belirsizlik çubukları ve
  sıralama puanı formülü TrueSkill ölçeğine taşınmalı).
- **Durum:** geliştirme
