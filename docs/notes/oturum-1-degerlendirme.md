# Okuma oturumu 1: Bir tahmin sistemini dürüstçe nasıl değerlendiririz?

**Tarih:** 2026-11-05 · **İlgili:** [PROTOCOL.md](../PROTOCOL.md) §3–§5 · [LITERATURE.md](../LITERATURE.md)

| Kaynak | Ne kadarı okundu |
|---|---|
| Gneiting & Raftery (2007), JASA | Tam metin ([yazarların PDF'i](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf)); §1, §2.3, §3, §7.1, §8 ayrıntılı |
| Diebold (2015), "Comparing predictive accuracy, twenty years later", JBES 33(1) | Tam metin ([NBER w18391](https://www.nber.org/papers/w18391)) |
| Diebold & Mariano (1995), JBES 13(3) | Yalnızca Diebold (2015)'teki özeti; orijinal okunmadı |
| Tashman (2000), IJF 16(4) | Yalnızca özet ve anahtar kelimeler ([RePEc](https://ideas.repec.org/a/eee/intfor/v16y2000i4p437-450.html)); tam metne erişilemedi |
| Inoue & Kilian, "In-sample or out-of-sample tests of predictability" | Çalışma makalesi sürümünün özeti ve girişi (2002) |

---

## 1. Gneiting & Raftery (2007): skorlama kuralları

**Ana fikirler**

- **Uygun (proper) skor:** Tahminci gerçekten inandığı olasılığı söylediğinde beklenen skoru en iyi olan kural.
  **Kesin uygun (strictly proper):** Bu en iyi nokta tektir, yani dürüst olmak tek en iyi stratejidir.
- **Hedef:** Makalenin ifadesiyle olasılıksal tahminin amacı, *kalibrasyon koşulu altında keskinliği en üst düzeye çıkarmaktır*.
  Kalibrasyon, tahmin edilen olasılıklarla gerçekleşen sıklıkların tutarlılığıdır. Keskinlik ise tahminlerin 0,5'ten ne kadar uzaklaştığıdır.
  Her zaman %50 diyen bir sistem kalibre olabilir ama işe yaramaz.
- **Logaritmik skor (log loss) ve Brier skoru** ikisi de kesin uygundur. Log loss'un iki özel durumu var:
  - *Yereldir:* yalnızca gerçekleşen sonuca verilen olasılığa bakar. Bernardo'nun (1979) sonucuna göre her uygun yerel skor, log skorun bir dönüşümüdür.
  - *Uç olaylara serttir:* %2 ihtimal verilen bir olay gerçekleşirse ceza çok büyüktür. Yazarlar kendi uygulamalarında bu yüzden aşırı uçlara karşı duyarlı olduğunu not ediyor.
- **İsabet oranı** (sıfır-bir skoru) uygundur ama **kesin uygun değildir**: %51 ile %99 demek arasında fark görmez.
- **Beceri skorları** (referansa göre normalize edilmiş skorlar) skor kuralı uygun olsa bile genellikle uygun değildir.
- **Önemli bağlantı (§7.1):** Veri zaman sırasıyla geliyorsa, bir modelin bütün veriye verdiği olasılık, her gözlemin *yalnızca öncekilere dayanarak*
  tahmin edilen olasılıklarının çarpımına eşittir (Dawid 1984'ün "prequential" ayrıştırması). Yani tek adım ileri tahminlerin log skorlarının toplamı,
  modelin log marjinal olabilirliğidir. İki model arasındaki fark da log Bayes faktörüdür.

**Bizim için anlamı**

1. Log loss'u birincil metrik seçmemiz doğru. Ayrıca bu seçim keyfi değil: filtreleme modellerinde tek adım ileri log loss toplamı,
   Bayesçi model karşılaştırmasının ta kendisi. (Glicko yaklaşık bir filtre olduğu için bu eşitlik yaklaşık.)
2. Log loss uç olaylara sert olduğu için, en kötü skorlanan maçlar çoğu zaman **veri hatasıdır** (yanlış kazanan, yanlış eşleşmiş dövüşçü).
   Bunlar protokolde ayrıca incelenmeli; ayrıca Brier skoru dayanıklılık kontrolü olarak raporlanmalı.
3. İsabet oranı karar için kullanılmamalı (zaten protokolde böyle). Beceri skoru raporlanabilir ama karar ölçütü olamaz.

## 2. Diebold (2015): tahmin karşılaştırması mı, model karşılaştırması mı?

**Ana fikirler**

- Diebold–Mariano testi **tahminleri** karşılaştırmak için tasarlandı: tahmin hatalarını veri gibi alır, modeli bilmesi gerekmez.
  Tek varsayımı, kayıp farkının durağan olması.
- Literatürün çoğu bunu **modelleri** karşılaştırmak için, "sahte örneklem dışı" (pseudo out-of-sample) düzenlerde kullanmış.
  Diebold'a göre bu hem gereksiz hem de verimsiz: model karşılaştırmasında en iyi yöntemler tüm veriyi kullanan yöntemlerdir (olabilirlik oranı, Bayes faktörü, AIC/BIC).
- "Örneklem dışı test aşırı uyuma karşı tek/en iyi sigortadır" sezgisinin büyük ölçüde yanlış olduğunu söylüyor. Hatta veri bölme noktası da seçilebildiği için
  örneklem dışı düzen veri madenciliği alanını *genişletebilir*.
- Örneklem dışı karşılaştırmanın yine de bir rolü var: performansın **dönemlere göre** nasıl değiştiğini anlamak.
- Önemli uyarı: gerçek zamanlı değerlendirme, o tarihte mevcut olan **veri sürümüyle** (vintage) yapılmalı. Sonradan düzeltilmiş veriyi
  o tarihte varmış gibi kullanmak gerçek zamanlı başarıyı olduğundan iyi gösterebilir.

Inoue & Kilian'ın çalışma makalesi de aynı yönde: uygun kritik değerlerle örneklem içi testler en az o kadar güvenilir ve çoğu durumda daha güçlü.

**Bizim için anlamı**

1. İlk bakışta protokolümüzü eleştiriyor gibi görünüyor, ama filtreleme modellerinde iki yaklaşım birleşiyor: Gneiting & Raftery §7.1'e göre
   tek adım ileri log skorların toplamı zaten **tam örneklem** olabilirliği. Yani biz veri atmıyoruz.
2. Aşırı uyum riski yalnızca hiperparametre seçiminden geliyor. BIC cezası parametre başına ½·ln(n); n ≈ 78.600 maçta bu, maç başına
   yaklaşık **0,00007** log loss demek. 3–4 hiperparametreli modellerde bu, 0,001'lik karar eşiğimizin çok altında.
   Dolayısıyla iç içe kayan başlangıç **asıl olarak çok parametreli bileşenler** (tahmin edilen bitiş ağırlıkları, yaş eğrisi) için önemli.
3. Veri sürümü uyarısı bizim için gerçek: Fight Canon kayıtları sonradan düzeltiliyor ve geriye dönük maç ekleniyor. Tarihsel değerlendirmemiz
   bugünkü sürümle yapılıyor; bu, gerçek zamanlı başarıyı olduğundan iyi gösterebilir. Kasım 2026'dan itibaren her ay veri sürümünü arşivliyoruz;
   ileride sürüm farkının etkisi ölçülebilir.
4. Maçlar bağımsız değil: aynı dövüşçü farklı etkinliklerde tekrar görünüyor. Etkinlik bazlı kümeleme bunu tam yakalamaz; ay bazlı kümeleme
   dayanıklılık kontrolü olarak eklenmeli.

## 3. Tashman (2000): örneklem dışı testlerin tasarımı

Yalnızca özete erişebildim. Özetin söylediği: tahmin çalışmaları hata ölçülerine ve veri seçimine odaklanmış, ama örneklem dışı testlerin
*nasıl uygulandığı* (veri bölme kuralı, sabit ya da kayan başlangıç, tek ya da çoklu test dönemi, yeniden ayarlama) açıkça raporlanmadığı için
sonuçlar tekrarlanamıyor. Bizim protokolümüz bu kararların hepsini açıkça yazıyor (§4). Ayrıntılı önerileri tam metin okunmadan aktarmıyorum.

---

## Protokole etkisi

Bu oturumun sonucunda protokol 0.2 sürümüne güncellendi (bkz. PROTOCOL.md değişiklik günlüğü):

1. Log loss seçiminin kuramsal dayanağı ve tek adım ileri log skor toplamının marjinal olabilirlik yorumu eklendi.
2. Dayanıklılık kontrolleri eklendi: Brier ile log loss farklı karar verirse bu raporlanır; en kötü skorlanan 50 maç veri hatası için elle incelenir;
   ay bazlı kümelenmiş bootstrap ikinci bir belirsizlik ölçüsü olarak eklenir.
3. Tam dizi üzerindeki toplam log skor da raporlanacak. İç içe kayan başlangıç sonucuyla çelişirse bu açıkça yazılacak.
4. Veri sürümü (vintage) sınırlılığı §9'a eklendi.

## Açık sorular (sonraki oturumlara)

- Glicko, durum-uzay modeline *yaklaşık* bir filtre. Yaklaşıklığın log skora etkisi ne kadar? (Oturum 2: Glickman 1999.)
- Beraberlikler birincil metrikte hariç. TrueSkill beraberliği modelin içinde ele alıyor; bu, karşılaştırmayı nasıl etkiler? (Oturum 3.)
