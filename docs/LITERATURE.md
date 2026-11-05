# Literatür

Her kaynak, sistemdeki hangi karara dayanak olduğuyla birlikte listelenir. Protokol: [PROTOCOL.md](PROTOCOL.md).

**Künye durumu:** ✓ = bibliyografik kayıtla doğrulandı · ~ = kısmen doğrulandı · ? = bellekten, doğrulanmadı.
Atıf yapmadan önce ? ve ~ işaretlileri kontrol edin.

## Okuma sırası

Her oturum bir soruya cevap verir. Okuma notları `docs/notes/` altında; her not "bizim projede neyi değiştirir" bölümüyle biter.

| Oturum | Soru | Kaynaklar |
|---|---|---|
| 1 ✓ | Bir tahmin sistemini nasıl dürüstçe değerlendiririz? | Gneiting & Raftery 2007; Tashman 2000; Diebold & Mariano 1995; Diebold 2015 → [notlar](notes/oturum-1-degerlendirme.md) |
| 2 ✓ | Kullandığımız model tam olarak neyi varsayıyor? | Glickman 1999; Glickman 2001 → [notlar](notes/oturum-2-glicko.md) |
| 3 | Alternatif modeller ve geçmiş/gelecek bilgisi | Herbrich vd. 2006; Coulom 2008; Landfried & Mocskos 2025 |
| 4 | Galibiyet farkı ve MMA'ya özgü bilgi | Kovalchik 2020; Hvattum & Arntzen 2010; Holmes, McHale & Żychaluk 2023 |
| 5 | Farklı gruplar ne zaman karşılaştırılabilir? (P4P) | Ford 1957; Berry, Reese & Larkey 1999; Batterham & George 1997 |

## Kaynaklar

### Değerlendirme yöntemi (PROTOCOL §3–§5)

| Kaynak | Künye | Neden önemli |
|---|---|---|
| Gneiting, T. & Raftery, A. E. (2007). Strictly proper scoring rules, prediction, and estimation. *JASA* 102(477), 359–378. doi:10.1198/016214506000001437 [PDF](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf) | ✓ (okundu) | Log loss'u birincil metrik seçmemizin gerekçesi: uygun skorlama kuralları dürüst olasılığı ödüllendirir. |
| Tashman, L. J. (2000). Out-of-sample tests of forecasting accuracy: an analysis and review. *International Journal of Forecasting* 16(4), 437–450. [RePEc](https://ideas.repec.org/a/eee/intfor/v16y2000i4p437-450.html) | ✓ (yalnızca özet okundu) | Kayan başlangıçlı değerlendirme ve örneklem dışı test tasarımı. |
| Diebold, F. X. & Mariano, R. S. (1995). Comparing predictive accuracy. *Journal of Business & Economic Statistics* 13(3), 253–263. | ✓ (orijinal okunmadı) | İki tahmin sisteminin farkının istatistiksel anlamlılığı (bizde kümelenmiş bootstrap ile). |
| Diebold, F. X. (2015). Comparing predictive accuracy, twenty years later: a personal perspective on the use and abuse of Diebold–Mariano tests. *Journal of Business & Economic Statistics* 33(1). [NBER w18391](https://www.nber.org/papers/w18391) | ✓ (okundu) | DM testi tahminleri karşılaştırır, modelleri değil; model seçiminde tam örneklem yöntemleri daha güçlüdür; veri sürümü (vintage) uyarısı. |
| Dawid, A. P. (1984). Present position and potential developments: some personal views. Statistical theory: the prequential approach. *JRSS Series A* 147(2), 278–292. | ? (Gneiting & Raftery'deki atıftan) | Tek adım ileri tahminlerin çarpımı = marjinal olabilirlik; log loss'u model karşılaştırma ölçütü yapan sonuç. |
| Inoue, A. & Kilian, L. In-sample or out-of-sample tests of predictability: which one should we use? (Çalışma makalesi 2002; *Econometric Reviews*'da yayımlandı) | ~ (dergi künyesi doğrulanmadı) | Örneklem içi testler en az o kadar güvenilir, çoğu durumda daha güçlü. |

### Derecelendirme modelleri (PROTOCOL §6)

| Kaynak | Künye | Neden önemli |
|---|---|---|
| Glickman, M. E. (1999). Parameter estimation in large dynamic paired comparison experiments. *JRSS Series C (Applied Statistics)* 48(3), 377–394. [RePEc](https://ideas.repec.org/a/bla/jorssc/v48y1999i3p377-394.html) · [PDF](http://www.glicko.net/research/glicko.pdf) | ✓ (okundu) | Glicko-1'in kaynağı (M1). Modelin durum-uzay varsayımı ve yaklaşık filtre. Kodumuz makaledeki sayısal örnekle test ediliyor. |
| Glickman, M. E. (2001). Dynamic paired comparison models with stochastic variances. *Journal of Applied Statistics* 28(6), 673–689. doi:10.1080/02664760120059219 [RePEc](https://ideas.repec.org/a/taf/japsta/v28y2001i6p673-689.html) · [PDF](http://www.glicko.net/research/dpcmsv.pdf) | ✓ (okundu) |
| Glickman, M. E. The Glicko system (uygulama notu). [PDF](http://www.glicko.net/glicko/glicko.pdf) | ✓ (ilgili bölümler okundu) | Dönem başına 5–10 maç önerisi; RD üst sınırı 350; minimum RD yok; `r ± 2·RD`'nin %95 aralık olarak yorumu. | Glicko-2 (M2): güçteki ani değişimleri (sakatlık, yaş) oynaklıkla yakalama. |
| Herbrich, R., Minka, T. & Graepel, T. (2006). TrueSkill: A Bayesian skill rating system. *NIPS 19*. | ? | M3; beraberliği modelin içinde ele alır. |
| Coulom, R. (2008). Whole-History Rating: A Bayesian rating system for players of time-varying strength. *Computers and Games*, LNCS 5131. | ? | Yumuşatma yaklaşımı; neden "o tarihte bilinen" sorusuna uymadığını anlamak için. |
| Landfried, G. & Mocskos, E. (2025). TrueSkill Through Time: Reliable initial skill estimates and historical comparability with Julia, Python, and R. *Journal of Statistical Software* 112(6), 1–41. [JSS](https://www.jstatsoft.org/article/view/v112i06) | ✓ | Elo/TrueSkill bilgiyi yalnızca ileri taşır; TTT geçmişi de kullanarak ilk tahminleri ve dönemler arası karşılaştırmayı iyileştirir. Olası "geriye dönük" liste için aday. Açık erişim, Python paketi var. |

### Galibiyet farkı ve MMA (PROTOCOL §7, H1)

| Kaynak | Künye | Neden önemli |
|---|---|---|
| Kovalchik, S. (2020). Extension of the Elo rating system to margin of victory. *International Journal of Forecasting* 36(4), 1329–1341. | ~ (başka makalelerde atıf doğrulandı, cilt/sayfa doğrulanmadı) | Galibiyet farkını Elo'ya ilkeli şekilde eklemek. Bizim elle seçilmiş KO/UD/SD değerlerimizin alternatifi. |
| Hvattum, L. M. & Arntzen, H. (2010). Using ELO ratings for match result prediction in association football. *International Journal of Forecasting* 26(3), 460–470. | ? | Elo'nun tahmin değişkeni olarak kullanımı ve farkla ölçeklenen güncelleme. |
| Holmes, B., McHale, I. G. & Żychaluk, K. (2023). A Markov chain model for forecasting results of mixed martial arts contests. *International Journal of Forecasting* 39(2), 623–640. doi:10.1016/j.ijforecast.2022.01.007 [RePEc](https://econpapers.repec.org/RePEc:eee:intfor:v:39:y:2023:i:2:p:623-640) | ✓ | MMA'da hakemli tahmin çalışması; bahis piyasasıyla karşılaştırma yapıyor. Maç içi istatistik kullanıyor (bizde yalnızca UFC'de var). |

### Gruplar arası karşılaştırma ve P4P (PROTOCOL §8)

| Kaynak | Künye | Neden önemli |
|---|---|---|
| Ford, L. R. (1957). Solution of a ranking problem from binary comparisons. *American Mathematical Monthly* 64(8), 28–33. | ? (sonuç ikincil kaynaklardan doğrulandı: [arXiv 1411.1168](https://ar5iv.labs.arxiv.org/html/1411.1168)) | Karşılaştırma grafiği bağlı değilse güçler ortak ölçekte tanımlanamaz. Sıkletler arası karşılaştırmanın matematiksel şartı. |
| Berry, S. M., Reese, C. S. & Larkey, P. D. (1999). Bridging different eras in sports. *JASA*. [PDF](https://www.vanderbilt.edu/psychological_sciences/graduate/programs/quantitative-methods/quantitative-content/berry_reese_larkey_1999.pdf) | ~ (yıl PDF başlığından; cilt/sayfa doğrulanmadı) | Farklı dönemleri, iki döneme yayılan oyuncular üzerinden köprüleme. P4P'deki "sıklet değiştirenler" köprüsünün en yakın benzeri. |
| Batterham, A. M. & George, K. P. (1997). Allometric modeling does not determine a dimensionless power function ratio for maximal muscular function. *Journal of Applied Physiology*. [PubMed](https://pubmed.ncbi.nlm.nih.gov/9390994) | ✓ | Mutlak performans ölçüsü olan halterde bile vücut ağırlığı düzeltmesi tartışmalı; MMA için kilo formülü olmamasının gerekçesi. |
| Vanderburgh, P. M. & Batterham, A. M. (1999). Validation of the Wilks powerlifting formula. *Medicine & Science in Sports & Exercise*. [PubMed](https://pubmed.ncbi.nlm.nih.gov/10613442/) | ✓ | Aynı konu, Wilks formülü özelinde. |

### Hakemli ama dolaylı

| Kaynak | Neden önemli |
|---|---|
| Kilo geri alma çalışmaları: [PMC12379698](https://pmc.ncbi.nlm.nih.gov/articles/PMC12379698/), [Bellator, PubMed 39981492](https://pubmed.ncbi.nlm.nih.gov/39981492/) | Tartı sonrası kilo ile kazanma arasında tutarlı ilişki yok; vücut kütlesinin etkisi hakkında dolaylı bilgi. |

### Hakemli olmayan (yalnızca hipotez üretmek için)

| Kaynak | İddia | Neden temkinli |
|---|---|---|
| [FightMatrix](https://fightmatrix.com/?p=1941) | Üst sıklete çıkan erkek dövüşçü ≈%17 kaybeder; karar türü ağırlıkları | 2009 tarihli, yöntem yayımlanmamış |
| [UFC Calendar](https://www.ufcalendar.com/blog/when-do-ufc-fighters-get-washed), [AgentMMA](https://agentmma.com/mma-lab/ufc-fighter-peak-age) | Yaşla kademeli düşüş, zirve ≈30 yaş | Hakemli değil, seçilim yanlılığı kontrol edilmemiş (H5) |
