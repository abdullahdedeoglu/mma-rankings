# Veri denetimi (Aşama 1)

**Tarih:** 2026-11-05 · **Veri sürümü:** `db-2026-11-04-1837` (SHA-256 `e0ea391f…858cf6`, son olay 2026-11-01) ·
**İlgili:** [PROTOCOL.md](PROTOCOL.md) §2, §7, §8

Bu belge, deneylere başlamadan önce veride neyin güvenilir, neyin sorunlu olduğunu kaydeder. Tamamen **betimseldir**:
hiçbir derece ya da tahmin hesaplanmadı, hiçbir model sonucu görülmedi.

**Yeniden üretmek için:**

```bash
uv run python -m mmarank.audit
```

Betik ([src/mmarank/audit.py](../src/mmarank/audit.py)) tüm sayıları `build/audit/<sürüm>/audit.json` dosyasına, elle inceleme
listelerini aynı klasöre CSV olarak yazar. Derecelendirilen maç kümesi, derecelerin kullandığı `data.load()` fonksiyonundan gelir.
Rastgele örneklemlerin tohumu 20261105.

---

## Özet

| # | Bulgu | Önem | Ne yapılacak |
|---|---|---|---|
| 1 | Maç sonuçları yapısal olarak temiz: her maçta 2 katılımcı, sonuç çiftleri tutarlı, tarihsiz olay yok | — | — |
| 2 | 6.062 maçta "vuruşlara teslim olma" (ör. "TKO (Submission to Punches)", "Submission (Punches)") SUB olarak sınıflanıyor | Düşük (KO ve SUB aynı değeri alıyor; H1b bitişleri birleştiriyor) | Araştırma kodunda KO/TKO'ya taşınır; yayındaki sistemde Aşama 3'te |
| 3 | Erkek maçlarının sıklet bilgisi 2010 öncesinde %5 | Yüksek (P4P, H4, H8) | Protokolde zaten kural var (§8) |
| 4 | Ardışık maçlarda 3+ sıklet atlayan 3.198 geçiş; pilot incelemede 8/8 tek maçlık etiket tutarsızlığı, kimlik birleşmesi yok | Yüksek (H4 ve sıklet ataması) | H4 için "kalıcı sıklet değişimi" tanımı; sıklet atamasında tek maçlık sıçramalar gürültü sayılır |
| 5 | Derecelendirilen maçların 15.231'inde (%4,2) iki dövüşçünün de cinsiyeti bilinmiyor | Orta | Birincil popülasyonun dışında kalıyor; bu kaybın yapısı raporlanır |
| 6 | Doğum tarihine göre 16 yaş altı 356, 55 yaş üstü 28 maç; bazı yaşlar negatif | Orta (H5) | H5'te bu maçlar doğum tarihi hatası sayılıp dışarıda bırakılır |
| 7 | Aynı ad ve aynı doğum tarihine sahip 15 kimlik çifti (muhtemel bölünmüş kimlik) | Düşük | Kaydedildi; düzeltme Fight Canon'a bildirilebilir |
| 8 | 11.045 maçın profesyonel olup olmadığı kontrol edilmemiş (`bout_type` boş) | Düşük-orta | Duyarlılık analizi: bu maçlar çıkarılınca sonuç değişiyor mu |
| 9 | Yalnızca tek bir veri sürümü arşivde | Orta (vintage, §9) | Aylık arşiv devam ediyor; karşılaştırma ileride |

---

## 1. Ham tablolar

| Tablo | Satır |
|---|---|
| fighters | 180.506 |
| events | 61.576 |
| fights | 372.990 |
| fight_participants | 745.980 |
| odds | 51.722 |
| judge_scores | 111.066 (6.617 maç) |
| round_stats | 76.174 (16.080 maç) |

- Her maçta tam 2 katılımcı var. Sonuç çiftleri yalnızca W/L (365.639), D/D (5.121) ve NC/NC (2.230); tutarsız çift yok.
- Tarihi boş olay yok; son olaydan sonra tarihli olay yok; 1990 öncesi 8 olay var.
- Aynı organizasyonun aynı gündeki birden fazla olayı: 410 grup. Örneklere bakıldığında çoğu gerçek (ör. aynı gün iki ayrı KOTC kartı,
  ana kart ve akademi kartı). Bunlardan 28'inde aynı dövüşçü iki olayda da görünüyor (turnuva ya da yinelenen kayıt).
- Hiç maçı olmayan 395 dövüşçü kaydı var (etkisiz).
- Kartların %99,2'si kaynakta "tam" işaretli.

## 2. Derecelendirilen maç kümesi

`data.load()` sonrası:

| Adım | Maç |
|---|---|
| Okunan | 372.990 |
| NC / üstü çizilmiş | 2.247 |
| DQ | 1.787 |
| Sonucu belirsiz (N/A) | 1.677 |
| Yöntemi eksik | 558 |
| Yakın-tekrar olarak birleştirilen | 236 |
| **Derecelendirilen** | **366.496** (5.036 beraberlik) |

- Döneme göre: 1990'lar 5.558, 2000–09 75.324, 2010–19 181.996, 2020+ 103.618.
- **Yakın-tekrar birleştirmeleri:** 236 maç. 17'si aynı gün (yinelenen olay kaydı), 35'i 1–7 gün, 184'ü 8–30 gün arayla; 107'si farklı
  organizasyonlarda. Liste: `near_duplicates.csv`. 8–30 günlük birleştirmelerin bir kısmı gerçek rövanş olabilir; kural yalnızca sonucu
  aynı olan çiftleri birleştiriyor.
- **Aynı gün birden fazla maç:** 8.851 dövüşçü-gün (en fazla 5 maç). Çoğu 2010 öncesi turnuvalar. Protokoldeki "aynı gündeki maçlar günün
  başındaki derecelerle tahmin edilir" kuralı bu maçları sızıntısız ele alıyor.
- **Cinsiyet:** derecelendirilen maçların 336.612'si erkek-erkek, 14.648'i kadın-kadın, 5'i karışık (çıkarım çatışması), **15.231'inde
  iki tarafın da cinsiyeti bilinmiyor.** Bunlar, rakip ağıyla bağlantısı olmayan ya da çok az olan dövüşçüler. Birincil popülasyon
  "her iki taraf da en az 3 maçlı erkek" olduğundan bu maçların çoğu zaten dışarıda; ama bu kaybın rastgele olmadığı yazılmalı.
- **Profesyonellik:** 11.045 maçın `bout_type` alanı boş (kontrol edilmemiş); profesyonel sayılıyor.

## 3. Bitiş şekli sınıflaması

1.810 farklı yöntem metni var. Sınıflama `src/mmarank/methods.py`. Tam liste: `method_classes.csv`.

**Vuruşlara teslim olma SUB sayılıyor (6.062 maç):**

| Metin | Maç |
|---|---|
| TKO (Submission to Punches) | 3.268 |
| Submission (Punches) | 1.544 |
| TKO (Submission to Strikes) | 461 |
| Submission (Strikes) | 428 |
| TKO (Submission to Elbows / Knees / Slam) | 147 |

Bu maçlarda dövüşçü vuruşlar yüzünden pes ediyor; kavrama tekniğiyle değil. Kaynakların kendi yazımı bile tutarsız ("TKO" ya da
"Submission" önekiyle). Doğru sınıf KO/TKO.

**Etkisi:** Mevcut sistemde KO ve SUB aynı değeri (1,0) aldığı için dereceler değişmiyor. H1b'de bitişler tek kategori olduğu için
oradaki sonucu da değiştirmiyor. Yalnızca KO ile SUB'ı ayıran betimsel analizleri etkiler (ör. 4. oturumdaki dönem tablosunda
SUB payı ≈ %1,7 puan fazla).

**"OTHER" (66 maç):** yazım hataları ("Desicion", "Dcotor Stoppade", "No Conest"), "Could Not Continue" (48) ve anlamsız değerler.
Etki ihmal edilebilir.

## 4. Dövüşçü kimlikleri ve yaş

- Derecelendirilen maçı olan 178.201 dövüşçünün 83.294'ünün (%47) **tek** maçı var; 2.053'ünün 30 ve daha fazla maçı var.
- **Muhtemel bölünmüş kimlik:** aynı (normalleştirilmiş) ad ve aynı doğum tarihi taşıyan 15 çift. Örnek: Turrell Galloway (1 + 18 maç),
  Luis Gonzalez (9 + 13 maç). Liste: `identity_same_name_dob.csv`. Sayı küçük; doğum tarihi yalnızca dövüşçülerin bir kısmında bilindiği
  için gerçek sayı daha büyük olabilir.
- **Ad çakışması:** 5.317 ad birden fazla kimliğe ait; bunların 2.278 çiftinde kariyerler zaman olarak çakışıyor. Çoğu yaygın adlar
  (farklı kişiler). Bu yolla birleşme ya da bölünme ayırt edilemiyor.
- **Kimlik birleşmesi (iki kişinin tek kimlikte olması):** uç sıklet geçişi yapan 2.364 dövüşçünün hiçbiri birden fazla Sherdog kimliğine bağlı
  değil; pilot incelemede de birleşme bulunmadı (§5).
- **Yaş:** doğum tarihi bilinen maçlarda 16 yaş altı 356, 55 yaş üstü 28 maç; bir kısmında yaş negatif. Bunlar doğum tarihi hatası.
  Liste: `implausible_ages.csv`.
- Kariyeri 25 yıldan uzun 40 dövüşçü var (olası ama kontrol edilebilir).

## 5. Sıklet etiketleri

Erkeklerin kararlı maçları (331.914):

| Dönem | Sıklet bilgisi olan pay |
|---|---|
| 1990'lar | %4 |
| 2000–09 | %5 |
| 2010–19 | %69,5 |
| 2020+ | %89 |

Sıklete atanamayan etiketlerin başında boş etiket (114.037), "Catchweight" ve sayısal catchweight'ler (ör. "150lb Catchweight"),
erkek "Strawweight" (1.638; erkek sıklet listemizde yok) ve "Open Weight" geliyor.

**Ardışık iki etiketli maç arasındaki sıklet değişimi:**

| Atlanan sıklet | Geçiş |
|---|---|
| 1 | 82.511 |
| 2 | 10.994 |
| 3 | 2.296 |
| 4 | 581 |
| 5–7 | 321 |

- A → B → A deseni (tek maçlık değişim) 25.993 kez; 23.674'ü komşu sıklete. Komşu sıklete tek maçlık geçiş gerçek olabilir
  (kısa sürede kabul edilen maç), uzak olanlar şüpheli.
- **Rakip temelli otomatik kontrol işe yaramadı.** 3+ sıklet atlayan geçişlerde rakiplerin kendi asıl sıkleti etiketle karşılaştırıldı.
  Ancak pilotta "iki etiket de rakiplerle uyumlu" çıkan geçişler de etiket hatası çıktı. Muhtemel neden: aynı olaydaki diğer maçların
  etiketleri de hatalı olabiliyor. Bu kontrol karar için kullanılmıyor.

### Pilot elle inceleme (3+ sıklet atlayan geçişler)

Tohumla seçilen 30 geçişlik örneklemin (`division_moves_check_sample.csv`) ilk 8'i Sherdog profilleriyle incelendi:

| Dövüşçü | Etiketler | Sherdog profil sıkleti | Değerlendirme |
|---|---|---|---|
| Fernando Rodrigues Jr. | WW → HW | HW, 253 lb | WW etiketi tutarsız |
| Antonio Cesar | FLW → LW | FW, 139 lb | İki etiket de profil sıkletinden farklı |
| Jun Ando | HW → WW | MW, 185 lb | İki etiket de bir sıklet uzakta |
| Caio Cesar | BW → LHW | LHW, 205 lb | BW etiketi tutarsız |
| Grzegorz Bialas | HW → WW | LW, 155 lb | HW etiketi tutarsız |
| Zhenia Nikolaev | MW → BW | BW, 135 lb | MW etiketi tutarsız |
| Chris Stone | LW → FLW | LW, 155 lb | FLW etiketi tutarsız |
| Delbert Lamark | FLW → WW | WW, 170 lb | FLW etiketi tutarsız |

**Sonuç: 8/8 geçişte profil tek bir kişiye ait ve en az bir etiket profil sıkletiyle çelişiyor. Kimlik birleşmesi örneği yok.**

Sınırlar: Sherdog profil sıkleti, dövüşçünün **bugünkü** sıkletidir, o maçtaki kilo değil. Tek seferlik olağandışı bir maç (bir hafif sıkletin
ağır sıklette dövüşmesi) bölgesel organizasyonlarda olabilir. Fight Canon'daki maç etiketleri büyük olasılıkla Sherdog olay sayfalarından geldiği
için, maç etiketlerini Sherdog ile doğrulamak döngüsel olur. Sekiz gözlemle oran tahmini kaba: 8/8 için %95 güven aralığının alt sınırı ≈ %63.

### Sonuçlar

1. **Sıklet değişimi tek maçın etiketine göre tanımlanamaz.** H4 (sıklet değişimi etkisi) bu gürültüyle ölçülürse etki sıfıra doğru
   yanlanır ve uzak "değişimler" sahte gözlem olur. H4 için kalıcı değişim tanımı gerekir (protokol 0.7).
2. **Sıklet ataması da tek maça bakmamalı.** Sıralama katmanında (Aşama 3) dövüşçünün sıkleti son etiketli maçlarının çoğunluğuyla
   belirlenmeli; tek maçlık uzak sıçramalar yok sayılmalı. Bu bir politika kararıdır ve Aşama 3'te yazılacak.
3. **Sıkletler arası köprüler (P4P)** bu gürültüden etkilenmez: dereceler sıkletten bağımsız hesaplanıyor. Ancak 5. oturumdaki
   "ağır ile sinek sıklet arasında 25 doğrudan geçiş" bulgusu büyük olasılıkla etiket gürültüsüdür, gerçek köprü değil.

## 6. Ek veri kapsamı

- **Bahis oranları:** tek kaynak (BestFightOdds, kitaplar arası kapanış). Maç sayısı 2007'de 134, 2008–2020 arası yılda 470–1.070,
  2021'den beri yılda 2.300–2.850.
- Hakem kartları 6.617 maçta, maç içi istatistikler 16.080 maçta (%4,3).

## 7. Sıklet denetimi örneklemi (PROTOCOL §8)

`division_check_sample.csv`: 2010–14, 2015–19 ve 2020+ katmanlarından tohumla seçilmiş **200 dövüşçü-ay** (67/67/66). 2010 öncesi, sıklet
bilgisi %5 olduğu için örneklenmedi.

**Henüz kontrol edilmedi.** Doğrulama için Sherdog'dan **bağımsız** bir kaynak gerekiyor (Tapology, organizasyonun kendi sayfası, Wikipedia),
çünkü maç etiketlerinin kaynağı büyük olasılıkla Sherdog. Her satır için `external_div` ve `agrees` sütunları doldurulacak; doğruluk oranı
%95 güven aralığıyla raporlanacak.

## 8. Yapılmayanlar ve sınırlar

- **Veri sürümleri arası karşılaştırma (vintage):** arşivde yalnızca bu sürüm var. Sonraki aylık sürümlerle geçmişe dönük eklenen ve
  değiştirilen maçların oranı ölçülecek.
- Kimlik birleşmesi yalnızca Sherdog kimlik sayısı ve 8 örnekle kontrol edildi; Sherdog'un kendisinin iki kişiyi birleştirdiği durumlar
  bu yolla görülemez.
- Sonuçların doğruluğu (yanlış kazanan) bu denetimde kontrol edilmedi. Protokoldeki "en kötü skorlanan 50 maçın elle incelenmesi" (§3) bu işi
  model aşamasında yapacak.
